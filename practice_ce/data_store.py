import json
import os

class DataStore:
    def __init__(self, db_path="data/mock_db.json"):
        self.db_path = db_path
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Mock DB not found at {self.db_path}. Please run generate_mock_data.py first.")
        
        with open(self.db_path, "r") as f:
            self.data = json.load(f)

    def get_user_role(self, username):
        """Helper to get a user's role, simulating LDAP group lookup."""
        for user in self.data.get("users", []):
            if user["username"] == username:
                return user["role"]
        return None

    def authenticate(self, username, password):
        """Simulate legacy authentication against the mock DB."""
        for user in self.data.get("users", []):
            if user["username"] == username and user["password"] == password:
                return True
        return False
        
    def is_authorized(self, document_acl, username, role):
        """
        Check if the user or their role is in the document's ACL.
        """
        if role in document_acl:
            return True
        if username in document_acl:
            return True
        return False

    def get_trading_rules(self, username, role):
        """Return all trading rules the user is authorized to see."""
        results = []
        for rule in self.data.get("trading_rules", []):
            if self.is_authorized(rule.get("acl", []), username, role):
                results.append(rule)
        return results

    def get_regulatory_filings(self, username, role):
        """Return all regulatory filings the user is authorized to see."""
        results = []
        for filing in self.data.get("regulatory_filings", []):
            if self.is_authorized(filing.get("acl", []), username, role):
                results.append(filing)
        return results

    def get_audit_logs(self, username, role):
        """Return all audit logs the user is authorized to see."""
        results = []
        for log in self.data.get("audit_logs", []):
            if self.is_authorized(log.get("acl", []), username, role):
                results.append(log)
        return results
