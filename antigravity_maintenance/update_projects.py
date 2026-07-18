import os
import json
import glob
import uuid
import sqlite3

# Ruta al directorio de proyectos de Gemini/Antigravity.
# Aquí es donde el ejecutor del agente busca las configuraciones asociadas a cada folder.
PROJECTS_DIR = os.path.expanduser("~/.gemini/config/projects")
PROJECTS_JSON = os.path.expanduser("~/.gemini/projects.json")
VSCDB_PATH = os.path.expanduser("~/.config/Antigravity/User/globalStorage/state.vscdb")
APP_STORAGE_JSON = os.path.expanduser("~/.config/Antigravity/app_storage.json")

# Configuración por defecto requerida por el ejecutor del agente para resolver de forma correcta
# el ID del proyecto GCP "uk-bh-experiments-argolis" y evitar el error 'invalid project ID: ""'.
DEFAULT_SETTINGS = {
    "fileAccessPolicy": "AGENT_SETTING_POLICY_ASK",
    "internetPolicy": "AGENT_SETTING_POLICY_ASK",
    "autoExecutionPolicy": "CASCADE_COMMANDS_AUTO_EXECUTION_OFF",
    "artifactReviewMode": "ARTIFACT_REVIEW_MODE_ALWAYS",
    "enterpriseGcpProjectId": "uk-bh-experiments-argolis",
    "enterpriseGcpProjectRegion": "global"
}

def load_existing_projects():
    # Escaneamos los proyectos existentes en ~/.gemini/config/projects/*.json
    # Mapeamos cada folderUri a la ruta del archivo JSON correspondiente para evitar duplicados.
    existing = {}
    search_pattern = os.path.join(PROJECTS_DIR, "*.json")
    for file_path in glob.glob(search_pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            resources = data.get("projectResources", {}).get("resources", [])
            for res in resources:
                uri = res.get("folderUri", "") or res.get("gitFolder", {}).get("folderUri", "")
                if uri:
                    existing[uri.rstrip("/")] = file_path
        except Exception as e:
            print(f"Error al leer proyecto existente {file_path}: {e}")
    return existing

def get_folders_from_projects_json():
    # Extraemos todos los folders registrados en ~/.gemini/projects.json
    # para asegurar que tengan su archivo de configuración correspondiente.
    folders = {}
    if os.path.exists(PROJECTS_JSON):
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            for path, name in data.get("projects", {}).items():
                uri = f"file://{path}"
                folders[uri.rstrip("/")] = name
        except Exception as e:
            print(f"Error al leer projects.json: {e}")
    return folders

def get_folders_from_vscdb():
    # Extraemos los directorios recientemente abiertos desde la base de datos SQLite
    # de Antigravity (state.vscdb) para cubrir de forma proactiva carpetas abiertas recientemente.
    folders = {}
    if os.path.exists(VSCDB_PATH):
        try:
            conn = sqlite3.connect(f"file:{VSCDB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key='history.recentlyOpenedPathsList'")
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                for entry in data.get("entries", []):
                    uri = entry.get("folderUri", "")
                    if uri:
                        name = os.path.basename(uri.rstrip("/")) or "project"
                        folders[uri.rstrip("/")] = name
            conn.close()
        except Exception as e:
            print(f"Error al leer state.vscdb: {e}")
    return folders

def create_project_config(folder_uri, name):
    # Generamos un nuevo ID único (UUID) y creamos un archivo JSON de configuración.
    # Esto asegura que incluso los subdirectorios abiertos por primera vez tengan
    # configuraciones válidas con el enterpriseGcpProjectId correcto.
    pid = str(uuid.uuid4())
    file_path = os.path.join(PROJECTS_DIR, f"{pid}.json")
    folder_path = folder_uri[7:] if folder_uri.startswith("file://") else folder_uri
    
    data = {
        "id": pid,
        "name": name,
        "projectResources": {
            "resources": [
                {
                    "folderUri": folder_uri
                }
            ]
        },
        "permissionGrants": {
            "permissionGrants": {
                "allow": [
                    "command(ls)",
                    f"read_file({folder_path})",
                    f"write_file({folder_path})",
                    "command(uv)",
                    "command(git status)",
                    "command(git add)",
                    "command(git commit)"
                ]
            }
        },
        "settings": DEFAULT_SETTINGS.copy()
    }
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Creado nuevo archivo de configuración para {folder_uri} -> {file_path}")
        return file_path
    except Exception as e:
        print(f"Error al escribir configuración para {folder_uri}: {e}")
        return None

def update_app_storage(new_pids):
    # Añadimos los nuevos IDs de proyecto creados a app_storage.json.
    # Esto mantiene la consistencia de la base de datos de proyectos internos de Antigravity.
    if not new_pids:
        return
    if os.path.exists(APP_STORAGE_JSON):
        try:
            with open(APP_STORAGE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            p_order_str = data.get("projectsOrder", "[]")
            p_order = json.loads(p_order_str)
            
            modified = False
            for pid in new_pids:
                if pid not in p_order:
                    p_order.append(pid)
                    modified = True
                    
            if modified:
                data["projectsOrder"] = json.dumps(p_order)
                with open(APP_STORAGE_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Se agregaron {len(new_pids)} IDs a app_storage.json")
        except Exception as e:
            print(f"Error al actualizar app_storage.json: {e}")

def main():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    # 1. Cargamos proyectos configurados actualmente.
    existing_projects = load_existing_projects()
    
    # 2. Recopilamos carpetas candidatas de projects.json y state.vscdb.
    candidate_folders = {}
    candidate_folders.update(get_folders_from_projects_json())
    candidate_folders.update(get_folders_from_vscdb())
    
    new_pids = []
    
    # 3. Para cada carpeta candidata, si no tiene un archivo de proyecto JSON, lo creamos.
    for folder_uri, name in candidate_folders.items():
        if folder_uri not in existing_projects:
            file_path = create_project_config(folder_uri, name)
            if file_path:
                pid = os.path.splitext(os.path.basename(file_path))[0]
                new_pids.append(pid)
                existing_projects[folder_uri] = file_path
                
    # 4. Sincronizamos app_storage.json si es necesario.
    update_app_storage(new_pids)
    
    # 5. Finalmente, actualizamos todos los archivos de configuración existentes para asegurar
    # de que hereden y tengan los valores GCP del proyecto correctos y estén al día.
    search_pattern = os.path.join(PROJECTS_DIR, "*.json")
    for file_path in glob.glob(search_pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            modified = False
            if "settings" not in data or not isinstance(data["settings"], dict):
                data["settings"] = DEFAULT_SETTINGS.copy()
                modified = True
                print(f"Añadiendo settings por defecto a: {os.path.basename(file_path)}")
            else:
                settings = data["settings"]
                if settings.get("enterpriseGcpProjectId") != "uk-bh-experiments-argolis":
                    settings["enterpriseGcpProjectId"] = "uk-bh-experiments-argolis"
                    modified = True
                if settings.get("enterpriseGcpProjectRegion") != "global":
                    settings["enterpriseGcpProjectRegion"] = "global"
                    modified = True
                for key, val in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = val
                        modified = True
            
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"Valores corregidos en: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error al actualizar archivo existente {file_path}: {e}")

if __name__ == "__main__":
    main()
