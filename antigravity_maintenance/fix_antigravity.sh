#!/usr/bin/env bash

# Este script de diagnóstico y reparación (troubleshooting) ayuda a resolver de forma manual
# el error 'invalid project ID: ""' si vuelve a ocurrir en el futuro.
# La razón de este script es proporcionar una herramienta centralizada que detenga procesos
# colgados de la aplicación y sincronice correctamente los archivos de configuración de Gemini.

echo "======================================================"
echo " Iniciando diagnóstico y reparación de Antigravity..."
echo "======================================================"

# 1. Buscamos y detenemos de forma segura cualquier proceso huérfano de la aplicación (como 'language_server' o 'antigravity')
# que pueda estar bloqueando archivos o manteniendo en caché configuraciones obsoletas de ID de proyecto.
# Excluimos de la búsqueda el proceso actual de bash ($$) para garantizar la estabilidad de la terminal activa.
CURRENT_PID=$$
STALE_PIDS=$(ps aux | grep -E -i "antigravity|language_server" | grep -v grep | grep -v "$CURRENT_PID" | awk '{print $2}')

if [ -n "$STALE_PIDS" ]; then
  echo "[+] Se encontraron procesos activos de Antigravity en ejecución. Limpiando caché..."
  for PID in $STALE_PIDS; do
    kill -9 "$PID" 2>/dev/null
  done
  echo "[+] Procesos colgados detenidos correctamente."
else
  echo "[+] No se encontraron procesos colgados en ejecución."
fi

# 2. Obtenemos el directorio donde reside el script para localizar el actualizador en Python de forma dinámica.
# Esto asegura que el script funcione correctamente sin importar dónde esté instalado en el sistema.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [ -f "${SCRIPT_DIR}/update_projects.py" ]; then
  echo "[+] Sincronizando configuraciones de proyectos con gcloud..."
  python3 "${SCRIPT_DIR}/update_projects.py"
else
  echo "[-] Error: No se encontró el script de actualización en ${SCRIPT_DIR}/update_projects.py"
fi

echo "======================================================"
echo " ¡Reparación completada! Puedes abrir Antigravity."
echo "======================================================"
