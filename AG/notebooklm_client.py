import os
import json
import requests
from typing import Dict, Any, List, Optional

class NotebookLMClient:
    """
    A robust Python SDK client wrapping the NotebookLM Enterprise API using the requests library.
    Supports both Live and Mock execution modes, and provides an optional verbose HTTP auditor
    that pretty-prints exact requests, responses, and copy-pasteable curl commands.
    """

    # In-memory mock database to support fully-interactive Offline Mode across separate client instances
    _mock_db = {
        "notebooks": {},     # notebook_id -> notebook_dict
        "sharing": {},       # notebook_id -> list of account_and_role dicts
        "sources": {}        # notebook_id -> dict of source_id -> source_dict
    }

    def __init__(
        self,
        project_number: str,
        location: str = "global",
        endpoint_location: str = "us",
        token: Optional[str] = None,
        default_mode: str = "mock",
        verbose: bool = True
    ):
        self.project_number = project_number
        self.location = location
        self.endpoint_location = endpoint_location
        self.token = token
        self.mode = default_mode.lower()
        self.verbose = verbose

        if self.verbose:
            self._log_info(f"Initialized NotebookLMClient in [ {self.mode.upper()} ] mode.")
            self._log_info(f"GCP Project: {self.project_number} | Location: {self.location} | Endpoint Region: {self.endpoint_location}")

    def _log_info(self, msg: str):
        print(f"\033[94m[NotebookLM SDK] {msg}\033[0m")

    def _log_success(self, msg: str):
        print(f"\033[92m[SDK SUCCESS] {msg}\033[0m")

    def _log_http(self, method: str, url: str, headers: Dict[str, str], payload: Any = None, curl_cmd: str = "", response_status: int = 200, response_body: Any = None):
        """Pretty-prints details of the HTTP exchange for educational purposes."""
        print("\n" + "="*80)
        print(f"\033[95mHTTP REQUEST: {method} {url}\033[0m")
        print("="*80)
        print("\033[93mHEADERS:\033[0m")
        for k, v in headers.items():
            # Mask authorization token for privacy
            val = f"Bearer ya" + f"29.***[truncated]***" if k.lower() == "authorization" else v
            print(f"  {k}: {val}")
        
        if payload is not None:
            print("\033[93mBODY PAYLOAD:\033[0m")
            print(json.dumps(payload, indent=2))
        
        if curl_cmd:
            print("\033[96mEQUIVALENT CURL COMMAND:\033[0m")
            print(f"  {curl_cmd}")
            
        print("="*80)
        print(f"\033[95mHTTP RESPONSE STATUS: {response_status}\033[0m")
        print("="*80)
        if response_body is not None:
            print("\033[93mRESPONSE BODY:\033[0m")
            print(json.dumps(response_body, indent=2))
        print("="*80 + "\n")

    def _get_auth_token(self, token_override: Optional[str] = None) -> str:
        tok = token_override or self.token
        if not tok and self.mode == "live":
            raise ValueError("GCP Access Token is required for Live mode, but none was provided.")
        return tok or "mock-bearer-token"

    def _get_mock_email(self, token_override: Optional[str] = None) -> str:
        """Resolves a mock token to a clean, human-readable email address."""
        user = self._get_auth_token(token_override)
        
        # Load mock tokens from mock_tokens.json if present
        mock_tokens = {}
        tokens_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_tokens.json")
        if os.path.exists(tokens_file):
            try:
                with open(tokens_file, "r") as f:
                    mock_tokens = json.load(f)
            except Exception:
                pass
        
        p = "ya" + "29."
        alice_t = mock_tokens.get("alice_token", p + "departed_employee_alice_token")
        bob_t = mock_tokens.get("bob_token", p + "peer_employee_bob_token")
        admin_t = mock_tokens.get("admin_token", p + "administrator_admin_token")
        clara_t = mock_tokens.get("clara_token", p + "new_employee_clara_token")
        
        mapping = {
            alice_t: "alice.departed@enterprise.com",
            bob_t: "bob.peer@enterprise.com",
            admin_t: "admin@enterprise.com",
            clara_t: "clara.new@enterprise.com",
            "mock-token-admin": "admin@enterprise.com",
            "mock-bearer-token": "your_token_here@enterprise.com"
        }
        if user in mapping:
            return mapping[user]
        if "admin" in user.lower():
            return "admin@enterprise.com"
        if "@" in user:
            return user
        return f"{user}@enterprise.com"

    def _generate_curl(self, method: str, url: str, headers: Dict[str, str], json_payload: Any = None, is_upload: bool = False, file_path: str = "") -> str:
        """Constructs an equivalent curl command for the user to copy/paste directly."""
        curl_parts = [f"curl -X {method} \"{url}\""]
        for k, v in headers.items():
            val = "$(gcloud auth print-access-token)" if k.lower() == "authorization" else v
            curl_parts.append(f"-H \"{k}: {val}\"")
        
        if json_payload is not None:
            payload_str = json.dumps(json_payload).replace("'", "'\\''")
            curl_parts.append(f"-d '{payload_str}'")
        elif is_upload and file_path:
            curl_parts.append(f"--data-binary \"@{file_path}\"")
            
        return " \\\n  ".join(curl_parts)

    def _execute_request(
        self,
        method: str,
        path: str,
        json_payload: Any = None,
        data_payload: Any = None,
        token_override: Optional[str] = None,
        is_upload: bool = False,
        file_path: str = "",
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a real REST call via python 'requests' library, handles verbose auditing,
        and constructs equivalent curl commands.
        """
        token = self._get_auth_token(token_override)
        
        # Build Endpoint Base URL
        base_sub = "upload/v1alpha" if is_upload else "v1alpha"
        
        # Determine endpoint prefix to avoid location mismatch errors (e.g. 400 errors)
        endpoint_loc = self.endpoint_location
        if self.location == "global":
            # Global location must use the global endpoint (no regional prefix)
            endpoint_loc = ""
            
        if endpoint_loc in ("global", "none", "", None):
            endpoint_prefix = ""
        else:
            endpoint_prefix = f"{endpoint_loc}-"
            
        base_url = f"https://{endpoint_prefix}discoveryengine.googleapis.com/{base_sub}/projects/{self.project_number}/locations/{self.location}"
        url = f"{base_url}/{path}"

        headers = {
            "Authorization": f"Bearer {token}",
        }
        if not is_upload and json_payload is not None:
            headers["Content-Type"] = "application/json"
        
        if custom_headers:
            headers.update(custom_headers)

        curl_cmd = self._generate_curl(method, url, headers, json_payload, is_upload, file_path)

        try:
            if is_upload:
                response = requests.post(url, headers=headers, data=data_payload)
            else:
                response = requests.request(method, url, headers=headers, json=json_payload)

            status_code = response.status_code
            try:
                resp_json = response.json()
            except ValueError:
                resp_json = {"message": response.text or "[Empty Response]"}

            if self.verbose:
                self._log_http(method, url, headers, json_payload, curl_cmd, status_code, resp_json)

            response.raise_for_status()
            return resp_json

        except requests.exceptions.HTTPError as e:
            if not self.verbose:
                # Still output minimum debug in case of failures if verbose was False
                self._log_http(method, url, headers, json_payload, curl_cmd, e.response.status_code, resp_json)
            raise e
        except Exception as e:
            print(f"\033[91m[SDK ERROR] Connection/Request Failure: {e}\033[0m")
            raise e

    # =========================================================================
    # Notebook Management API
    # =========================================================================

    def create_notebook(self, title: str, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new notebook.
        REST Method: POST /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks
        """
        if self.mode == "mock":
            import uuid
            notebook_id = str(uuid.uuid4())[:8]
            user_email = self._get_mock_email(token_override)
            
            notebook = {
                "title": title,
                "notebookId": notebook_id,
                "emoji": "📓",
                "metadata": {
                    "userRole": "PROJECT_ROLE_OWNER",
                    "isShared": False,
                    "isShareable": True,
                    "createdBy": user_email
                },
                "name": f"projects/{self.project_number}/locations/{self.location}/notebooks/{notebook_id}"
            }
            self._mock_db["notebooks"][notebook_id] = notebook
            self._mock_db["sharing"][notebook_id] = [
                {"email": user_email, "role": "PROJECT_ROLE_OWNER"}
            ]
            self._mock_db["sources"][notebook_id] = {}
            
            if self.verbose:
                self._log_info(f"[MOCK] Created notebook ID {notebook_id} with title '{title}'")
            return notebook

        # Live Mode
        payload = {"title": title}
        return self._execute_request("POST", "notebooks", json_payload=payload, token_override=token_override)

    def get_notebook(self, notebook_id: str, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve details of a notebook.
        REST Method: GET /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}
        """
        if self.mode == "mock":
            user_email = self._get_mock_email(token_override)
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())
            
            notebook = dict(self._mock_db["notebooks"][notebook_id])
            
            # Check sharing permissions
            sharing_list = self._mock_db["sharing"].get(notebook_id, [])
            user_role = "PROJECT_ROLE_NOT_SHARED"
            
            # Project Owners or Administrators can bypass individual sharing records in an enterprise setting.
            # Here we simulate that admin token has universal read access.
            if "admin" in user_email.lower():
                user_role = "PROJECT_ROLE_OWNER"
            else:
                for entry in sharing_list:
                    if entry["email"] == user_email:
                        user_role = entry["role"]
                        break
            
            if user_role == "PROJECT_ROLE_NOT_SHARED":
                raise PermissionError(f"Access Denied: User {user_email} has no access to notebook {notebook_id}.")

            notebook["metadata"]["userRole"] = user_role
            notebook["metadata"]["isShared"] = len(sharing_list) > 1
            
            # Embed source references
            notebook_sources = list(self._mock_db["sources"][notebook_id].values())
            if notebook_sources:
                notebook["sources"] = notebook_sources

            if self.verbose:
                self._log_info(f"[MOCK] Retrieved notebook ID {notebook_id} (Role: {user_role})")
            return notebook

        # Live Mode
        return self._execute_request("GET", f"notebooks/{notebook_id}", token_override=token_override)

    def list_recently_viewed(self, page_size: int = 500, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        List notebooks that were recently viewed in this project.
        REST Method: GET /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks:listRecentlyViewed
        """
        if self.mode == "mock":
            user_email = self._get_mock_email(token_override)
            visible_notebooks = []

            for n_id, notebook in self._mock_db["notebooks"].items():
                sharing_list = self._mock_db["sharing"].get(n_id, [])
                is_visible = False
                user_role = "PROJECT_ROLE_NOT_SHARED"
                
                if "admin" in user_email.lower():
                    is_visible = True
                    user_role = "PROJECT_ROLE_OWNER"
                else:
                    for entry in sharing_list:
                        if entry["email"] == user_email:
                            is_visible = True
                            user_role = entry["role"]
                            break
                
                if is_visible:
                    nb_copy = dict(notebook)
                    nb_copy["metadata"]["userRole"] = user_role
                    nb_copy["metadata"]["isShared"] = len(sharing_list) > 1
                    visible_notebooks.append(nb_copy)

            if self.verbose:
                self._log_info(f"[MOCK] Listed {len(visible_notebooks)} notebooks for user {user_email}")
            return {"notebooks": visible_notebooks[:page_size]}

        # Live Mode
        return self._execute_request("GET", "notebooks:listRecentlyViewed", token_override=token_override, custom_headers={"Content-Type": "application/json"})

    def delete_notebook(self, notebook_id: str, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a notebook.
        REST Method: POST /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks:batchDelete
        """
        notebook_name = f"projects/{self.project_number}/locations/{self.location}/notebooks/{notebook_id}"
        
        if self.mode == "mock":
            user_email = self._get_mock_email(token_override)
            
            if notebook_id not in self._mock_db["notebooks"]:
                return {} # Deleting non-existent notebook returns empty json

            # Check if Owner or Admin
            sharing_list = self._mock_db["sharing"].get(notebook_id, [])
            is_authorized = "admin" in user_email.lower()
            for entry in sharing_list:
                if entry["email"] == user_email and entry["role"] in ["PROJECT_ROLE_OWNER", "PROJECT_ROLE_WRITER"]:
                    is_authorized = True
                    break
            
            if not is_authorized:
                raise PermissionError(f"Access Denied: User {user_email} cannot delete notebook {notebook_id}.")

            del self._mock_db["notebooks"][notebook_id]
            del self._mock_db["sharing"][notebook_id]
            del self._mock_db["sources"][notebook_id]
            
            if self.verbose:
                self._log_info(f"[MOCK] Deleted notebook ID {notebook_id} by user {user_email}")
            return {}

        # Live Mode
        payload = {"names": [notebook_name]}
        return self._execute_request("POST", "notebooks:batchDelete", json_payload=payload, token_override=token_override)

    def share_notebook(self, notebook_id: str, accounts_and_roles: List[Dict[str, str]], token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Share a notebook.
        REST Method: POST /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}:share
        """
        if self.mode == "mock":
            user_email = self._get_mock_email(token_override)
            
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())

            # Only Owner or Admin can share
            sharing_list = self._mock_db["sharing"].get(notebook_id, [])
            is_authorized = "admin" in user_email.lower()
            for entry in sharing_list:
                if entry["email"] == user_email and entry["role"] == "PROJECT_ROLE_OWNER":
                    is_authorized = True
                    break
            
            if not is_authorized:
                raise PermissionError(f"Access Denied: Only owners can manage sharing for notebook {notebook_id}.")

            # Update mock sharing list
            for new_entry in accounts_and_roles:
                email = new_entry["email"]
                role = new_entry["role"]
                
                # If set to NOT_SHARED, remove them
                if role == "PROJECT_ROLE_NOT_SHARED":
                    self._mock_db["sharing"][notebook_id] = [e for e in self._mock_db["sharing"][notebook_id] if e["email"] != email]
                else:
                    # Update existing or add new
                    existing = False
                    for e in self._mock_db["sharing"][notebook_id]:
                        if e["email"] == email:
                            e["role"] = role
                            existing = True
                            break
                    if not existing:
                        self._mock_db["sharing"][notebook_id].append({"email": email, "role": role})

            if self.verbose:
                self._log_info(f"[MOCK] Shared notebook {notebook_id} with: {accounts_and_roles}")
            return {}

        # Live Mode
        payload = {"accountAndRoles": accounts_and_roles}
        return self._execute_request("POST", f"notebooks/{notebook_id}:share", json_payload=payload, token_override=token_override)

    # =========================================================================
    # Source Management API
    # =========================================================================

    def batch_create_sources(self, notebook_id: str, sources_list: List[Dict[str, Any]], token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Add data sources in a batch.
        REST Method: POST /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:batchCreate
        """
        if self.mode == "mock":
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())

            added_sources = []
            import uuid
            for idx, content in enumerate(sources_list):
                source_id = f"src-{str(uuid.uuid4())[:6]}"
                
                # Determine title/display name from structure
                title = f"Source {idx+1}"
                if "textContent" in content:
                    title = content["textContent"].get("sourceName", "Text Input")
                elif "webContent" in content:
                    title = content["webContent"].get("sourceName", "Web Link")
                elif "videoContent" in content:
                    title = content["videoContent"].get("youtubeUrl", "YouTube Video")
                elif "googleDriveContent" in content:
                    title = content["googleDriveContent"].get("sourceName", "Google Drive File")

                source = {
                    "sourceId": {"id": source_id},
                    "title": title,
                    "metadata": {
                        "wordCount": 150,
                        "tokenCount": 180
                    },
                    "settings": {
                        "status": "SOURCE_STATUS_COMPLETE"
                    },
                    "name": f"projects/{self.project_number}/locations/{self.location}/notebooks/{notebook_id}/source/{source_id}"
                }
                
                self._mock_db["sources"][notebook_id][source_id] = source
                added_sources.append(source)

            if self.verbose:
                self._log_info(f"[MOCK] Batch created {len(added_sources)} sources for notebook {notebook_id}")
            return {"sources": added_sources}

        # Live Mode
        payload = {"userContents": sources_list}
        return self._execute_request("POST", f"notebooks/{notebook_id}/sources:batchCreate", json_payload=payload, token_override=token_override)

    def upload_source_file(self, notebook_id: str, file_path: str, display_name: str, content_type: str, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a local binary file (.pdf, .txt, .md, .docx, etc.) as a source.
        REST Method: POST /upload/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:uploadFile
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        if self.mode == "mock":
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())

            import uuid
            source_id = f"src-{str(uuid.uuid4())[:6]}"
            source = {
                "sourceId": {"id": source_id},
                "title": display_name,
                "metadata": {
                    "wordCount": 420,
                    "tokenCount": 512,
                    "file_size": os.path.getsize(file_path)
                },
                "settings": {
                    "status": "SOURCE_STATUS_COMPLETE"
                },
                "name": f"projects/{self.project_number}/locations/{self.location}/notebooks/{notebook_id}/source/{source_id}"
            }
            
            self._mock_db["sources"][notebook_id][source_id] = source
            
            if self.verbose:
                self._log_info(f"[MOCK] Stream-uploaded file '{display_name}' ({content_type}) to notebook {notebook_id} -> assigned ID {source_id}")
            return {"sourceId": {"id": source_id}}

        # Live Mode
        with open(file_path, "rb") as f:
            binary_data = f.read()

        custom_headers = {
            "X-Goog-Upload-File-Name": display_name,
            "X-Goog-Upload-Protocol": "raw",
            "Content-Type": content_type
        }

        return self._execute_request(
            "POST",
            f"notebooks/{notebook_id}/sources:uploadFile",
            data_payload=binary_data,
            token_override=token_override,
            is_upload=True,
            file_path=file_path,
            custom_headers=custom_headers
        )

    def get_source(self, notebook_id: str, source_id: str, token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve a specific source.
        REST Method: GET /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources/{SOURCE_ID}
        """
        if self.mode == "mock":
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())
            if source_id not in self._mock_db["sources"][notebook_id]:
                raise requests.exceptions.HTTPError("Source not found", response=requests.Response())
            
            source = self._mock_db["sources"][notebook_id][source_id]
            if self.verbose:
                self._log_info(f"[MOCK] Retrieved source ID {source_id} for notebook {notebook_id}")
            return {"sources": [source]}

        # Live Mode
        return self._execute_request("GET", f"notebooks/{notebook_id}/sources/{source_id}", token_override=token_override)

    def delete_sources(self, notebook_id: str, source_resource_names: List[str], token_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete data sources in bulk from a notebook.
        REST Method: POST /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:batchDelete
        """
        if self.mode == "mock":
            if notebook_id not in self._mock_db["notebooks"]:
                raise requests.exceptions.HTTPError("Notebook not found", response=requests.Response())

            deleted_count = 0
            for name in source_resource_names:
                # Extract source ID from full name path
                source_id = name.split("/")[-1]
                if source_id in self._mock_db["sources"][notebook_id]:
                    del self._mock_db["sources"][notebook_id][source_id]
                    deleted_count += 1

            if self.verbose:
                self._log_info(f"[MOCK] Bulk deleted {deleted_count} sources from notebook {notebook_id}")
            return {}

        # Live Mode
        payload = {"names": source_resource_names}
        return self._execute_request("POST", f"notebooks/{notebook_id}/sources:batchDelete", json_payload=payload, token_override=token_override)
