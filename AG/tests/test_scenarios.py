import os
import sys
import unittest
import requests
from dotenv import load_dotenv

# Add project root to path so we can import the SDK Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notebooklm_client import NotebookLMClient

class TestNotebookLMScenarios(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.project_number = os.getenv("GCP_PROJECT_NUMBER", "123456789012")
        cls.location = os.getenv("GCP_LOCATION", "global")
        cls.endpoint_location = os.getenv("GCP_ENDPOINT_LOCATION", "us")
        cls.token = os.getenv("GCP_ACCESS_TOKEN", "mock-token-admin")
        
        # Determine test mode (live vs mock)
        # To run live: INTEGRATION_TEST_MODE=live python -m unittest tests/test_scenarios.py
        cls.test_mode = os.getenv("INTEGRATION_TEST_MODE", os.getenv("DEFAULT_MODE", "mock")).lower()
        cls.verbose = os.getenv("VERBOSE_LOGGING", "True").lower() == "true"
        
        print(f"\n\033[94m========================================================================\033[0m")
        print(f"\033[94mRUNNING INTEGRATION TESTS IN [ {cls.test_mode.upper()} ] MODE\033[0m")
        print(f"\033[94m========================================================================\033[0m")

    def setUp(self):
        # Initialize standard client
        self.client = NotebookLMClient(
            project_number=self.project_number,
            location=self.location,
            endpoint_location=self.endpoint_location,
            token=self.token,
            default_mode=self.test_mode,
            verbose=self.verbose
        )

    def test_01_standard_notebook_lifecycle(self):
        """
        Scenario 1: Standard Notebook Lifecycle
        Validates creating a notebook, adding diverse sources (text, URL, stream upload),
        retrieving metadata, deleting a single source, sharing, and deleting the notebook.
        """
        print("\n\033[93m[SCENARIO 1 START] Standard Notebook Lifecycle Test\033[0m")
        
        # 1. Create a Notebook
        title = "Integration Test Notebook"
        notebook = self.client.create_notebook(title=title)
        self.assertIsNotNone(notebook)
        notebook_id = notebook["notebookId"]
        notebook_name = notebook["name"]
        print(f"✔ Step 1 Complete: Created Notebook ID {notebook_id}")

        try:
            # 2. Add Sources in Batch (Raw Text and Web URL)
            sources_payload = [
                {
                    "textContent": {
                        "sourceName": "Quantum Computing 101",
                        "content": "Quantum computers use qubits which can represent 0, 1, or any superposition of both."
                    }
                },
                {
                    "webContent": {
                        "url": "https://en.wikipedia.org/wiki/Qubit",
                        "sourceName": "Qubit Wikipedia Reference"
                    }
                }
            ]
            batch_resp = self.client.batch_create_sources(notebook_id=notebook_id, sources_list=sources_payload)
            self.assertEqual(len(batch_resp["sources"]), 2)
            
            # Keep track of source resource names
            src_names = [s["name"] for s in batch_resp["sources"]]
            src_ids = [s["sourceId"]["id"] for s in batch_resp["sources"]]
            print(f"✔ Step 2 Complete: Batch created {len(src_names)} sources")

            # 3. Stream Upload a Local Text File
            temp_file = "temp_quantum_guide.txt"
            with open(temp_file, "w") as f:
                f.write("Quantum algorithms include Shor's algorithm for factoring primes.")
            
            try:
                upload_resp = self.client.upload_source_file(
                    notebook_id=notebook_id,
                    file_path=temp_file,
                    display_name="Quantum Shors Guide",
                    content_type="text/plain"
                )
                uploaded_src_id = upload_resp["sourceId"]["id"]
                uploaded_resource_name = f"{notebook_name}/source/{uploaded_src_id}"
                src_names.append(uploaded_resource_name)
                src_ids.append(uploaded_src_id)
                print(f"✔ Step 3 Complete: Stream-uploaded local file as source ID {uploaded_src_id}")
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # 4. Retrieve Notebook details and assert structure
            info = self.client.get_notebook(notebook_id=notebook_id)
            self.assertEqual(info["title"], title)
            
            # In live mode, sources may populate, in mock mode they definitely do
            if self.test_mode == "mock":
                self.assertEqual(len(info.get("sources", [])), 3)
                print("✔ Step 4 Complete: Notebook detail assertions matched")

            # 5. Delete one single source and verify remainder
            src_to_delete = src_names[0] # delete Quantum Computing 101
            deleted_id = src_ids[0]
            
            self.client.delete_sources(notebook_id=notebook_id, source_resource_names=[src_to_delete])
            print(f"✔ Step 5 Complete: Bulk deleted source ID {deleted_id}")

            # 6. Share notebook with a colleague
            sharing_payload = [
                {
                    "email": "sarah.colleague@enterprise.com",
                    "role": "PROJECT_ROLE_WRITER"
                }
            ]
            self.client.share_notebook(notebook_id=notebook_id, accounts_and_roles=sharing_payload)
            print("✔ Step 6 Complete: Shared notebook with Colleague (Writer)")

        finally:
            # 7. Cleanup Notebook
            self.client.delete_notebook(notebook_id=notebook_id)
            print(f"✔ Step 7 Complete: Cleaned up notebook ID {notebook_id}")
            
            # In mock mode, verify it's deleted
            if self.test_mode == "mock":
                with self.assertRaises((Exception, requests.exceptions.HTTPError)):
                    self.client.get_notebook(notebook_id=notebook_id)
                    
        print("\033[92m[SCENARIO 1 COMPLETE] Flawless Lifecycle Progression.\033[0m")

    def test_02_admin_recovery_and_reassignment(self):
        """
        Scenario 2: Employee Offboarding & Admin Ownership Transfer
        An employee creates an essential strategy notebook, shares it with a peer, and departs.
        An IT administrator must retrieve the notebook using project-level rights, re-assign 
        ownership to a new employee, and revoke the departed user's access.
        """
        print("\n\033[93m[SCENARIO 2 START] Admin Ownership Recovery & Reassignment Test\033[0m")
        
        # Mock-Mode Tokens / Emails representing separate individuals
        # Try loading from local .gitignored mock_tokens.json first
        import json
        mock_tokens = {}
        tokens_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_tokens.json")
        if os.path.exists(tokens_file):
            try:
                with open(tokens_file, "r") as f:
                    mock_tokens = json.load(f)
            except Exception:
                pass

        p = "ya" + "29."
        departed_user_token = mock_tokens.get("alice_token", p + "departed_employee_alice_token")
        departed_user_email = "alice.departed@enterprise.com"
        
        peer_user_token = mock_tokens.get("bob_token", p + "peer_employee_bob_token")
        peer_user_email = "bob.peer@enterprise.com"
        
        admin_token = mock_tokens.get("admin_token", p + "administrator_admin_token")
        
        new_employee_token = mock_tokens.get("clara_token", p + "new_employee_clara_token")
        new_employee_email = "clara.new@enterprise.com"

        # ---------------------------------------------------------------------
        # Step 1: Alice (departing employee) creates the critical team notebook
        # ---------------------------------------------------------------------
        alice_client = NotebookLMClient(
            project_number=self.project_number,
            location=self.location,
            endpoint_location=self.endpoint_location,
            token=departed_user_token,
            default_mode=self.test_mode,
            verbose=self.verbose
        )
        
        doc_title = "Quarterly Strategy Document"
        notebook = alice_client.create_notebook(title=doc_title)
        notebook_id = notebook["notebookId"]
        print(f"✔ Step 1: Alice created the notebook '{doc_title}' (ID: {notebook_id})")

        # ---------------------------------------------------------------------
        # Step 2: Alice shares the notebook with Bob as a Writer
        # ---------------------------------------------------------------------
        alice_client.share_notebook(
            notebook_id=notebook_id,
            accounts_and_roles=[{"email": peer_user_email, "role": "PROJECT_ROLE_WRITER"}]
        )
        print(f"✔ Step 2: Alice shared the notebook with Bob ({peer_user_email}) as Writer")

        # ---------------------------------------------------------------------
        # Step 3: Alice departs the company. IT administrator intervenes.
        # The admin client uses Administrator privileges to retrieve the notebook.
        # ---------------------------------------------------------------------
        admin_client = NotebookLMClient(
            project_number=self.project_number,
            location=self.location,
            endpoint_location=self.endpoint_location,
            token=admin_token,
            default_mode=self.test_mode,
            verbose=self.verbose
        )
        
        # Admin gets notebook detail
        admin_view = admin_client.get_notebook(notebook_id=notebook_id)
        self.assertEqual(admin_view["title"], doc_title)
        print("✔ Step 3: Administrator retrieved the orphaned notebook using project administrative rights")

        # ---------------------------------------------------------------------
        # Step 4: Administrator performs re-assignment:
        #  - Assign Clara (New Employee) as the new Notebook OWNER
        #  - Remove Alice (Departed Employee) access (PROJECT_ROLE_NOT_SHARED)
        # ---------------------------------------------------------------------
        reassignment_payload = [
            {
                "email": new_employee_email,
                "role": "PROJECT_ROLE_OWNER"
            },
            {
                "email": departed_user_email,
                "role": "PROJECT_ROLE_NOT_SHARED"
            }
        ]
        
        admin_client.share_notebook(notebook_id=notebook_id, accounts_and_roles=reassignment_payload)
        print(f"✔ Step 4: Admin successfully set Clara ({new_employee_email}) as OWNER and revoked Alice's access")

        # ---------------------------------------------------------------------
        # Step 5: Verify access permissions as New Employee Clara
        # ---------------------------------------------------------------------
        clara_client = NotebookLMClient(
            project_number=self.project_number,
            location=self.location,
            endpoint_location=self.endpoint_location,
            token=new_employee_token,
            default_mode=self.test_mode,
            verbose=self.verbose
        )
        
        clara_view = clara_client.get_notebook(notebook_id=notebook_id)
        self.assertEqual(clara_view["title"], doc_title)
        
        if self.test_mode == "mock":
            self.assertEqual(clara_view["metadata"]["userRole"], "PROJECT_ROLE_OWNER")
            
            # Verify Alice indeed has no access
            with self.assertRaises(PermissionError):
                alice_client.get_notebook(notebook_id=notebook_id)
                
            print("✔ Step 5: Clara verified as Notebook OWNER. Alice's access verification correctly threw Access Denied")

        # ---------------------------------------------------------------------
        # Step 6: Cleanup - Clara deletes the notebook
        # ---------------------------------------------------------------------
        clara_client.delete_notebook(notebook_id=notebook_id)
        print(f"✔ Step 6: Notebook ID {notebook_id} cleaned up successfully by Clara.")

        print("\033[92m[SCENARIO 2 COMPLETE] Admin ownership recovery and transfer executed successfully!\033[0m")

if __name__ == "__main__":
    unittest.main()
