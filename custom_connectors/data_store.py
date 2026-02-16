import json
import os

class DataStore:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data = {}
        self._load_data()

    def _load_data(self):
        # Load Users
        try:
            with open(os.path.join(self.data_dir, "users.json"), "r") as f:
                self.data["users"] = json.load(f)
        except FileNotFoundError:
             self.data["users"] = []

        # Load Trading Rules
        try:
            with open(os.path.join(self.data_dir, "trading_rules.json"), "r") as f:
                self.data["trading_rules"] = json.load(f)
        except FileNotFoundError:
             self.data["trading_rules"] = []

        # Load Regulatory Filings
        try:
            with open(os.path.join(self.data_dir, "regulatory_filings.json"), "r") as f:
                self.data["regulatory_filings"] = json.load(f)
        except FileNotFoundError:
             self.data["regulatory_filings"] = []

        # Load Audit Logs
        try:
            with open(os.path.join(self.data_dir, "audit_logs.json"), "r") as f:
                self.data["audit_logs"] = json.load(f)
        except FileNotFoundError:
             self.data["audit_logs"] = []
             
         # Load ACLs
        try:
            with open(os.path.join(self.data_dir, "acls.json"), "r") as f:
                self.data["acls"] = json.load(f)
        except FileNotFoundError:
             self.data["acls"] = {}

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
        
    def is_authorized(self, document, username, role):
        """
        Check if the user is authorized to view the document based on PBAC.
        """
        # 0. System Admins and Connectors see all
        if role in ["System Admin", "Connector"]:
            return True

        # 1. Owner Access (for Audit Logs)
        if document.get("userId") == username:
            return True

        # 2. Role-Based Policy Access
        policy = self.data.get("acls", {}).get("roles", {}).get(role)
        if not policy:
            return False # Role not defined in policy

        doc_category = document.get("category")
        doc_sensitivity = document.get("sensitivity", "Restricted") # Default to Restricted if missing
        
        sensitivity_levels = self.data.get("acls", {}).get("sensitivity_levels", {})
        doc_sensitivity_level = sensitivity_levels.get(doc_sensitivity, 99) # Default to high if unknown

        for permission in policy.get("permissions", []):
            if permission["category"] == doc_category:
                max_sensitivity = permission["max_sensitivity"]
                max_level = sensitivity_levels.get(max_sensitivity, -1)
                
                if doc_sensitivity_level <= max_level:
                    return True
                    
        return False

    def get_trading_rules(self, username, role):
        """Return all trading rules the user is authorized to see."""
        # Connector and Admin get everything
        if role in ["Connector", "System Admin"]:
            return self.data.get("trading_rules", [])

        results = []
        for rule in self.data.get("trading_rules", []):
            if self.is_authorized(rule, username, role):
                results.append(rule)
        return results

    def get_regulatory_filings(self, username, role):
        """Return all regulatory filings the user is authorized to see."""
        if role in ["Connector", "System Admin"]:
            return self.data.get("regulatory_filings", [])

        results = []
        for filing in self.data.get("regulatory_filings", []):
            if self.is_authorized(filing, username, role):
                results.append(filing)
        return results

    def get_audit_logs(self, username, role):
        """Return all audit logs the user is authorized to see."""
        if role in ["Connector", "System Admin"]:
            return self.data.get("audit_logs", [])

        results = []
        for log in self.data.get("audit_logs", []):
            if self.is_authorized(log, username, role):
                results.append(log)
        return results

    def add_audit_log(self, username, action, details, category="AuditLog", sensitivity="Confidential"):
        """Append a new audit log and persist to DB."""
            
        new_id = f"AUD-{1000 + len(self.data.get('audit_logs', [])) + 1}"
        from datetime import datetime
        
        new_log = {
            "id": new_id,
            "timestamp": datetime.now().isoformat(),
            "userId": username,
            "action": action,
            "details": details,
            "category": category,
            "sensitivity": sensitivity
        }
        
        self.data.setdefault("audit_logs", []).append(new_log)
        self._save_audit_logs()
        return new_log

    def _save_audit_logs(self):
        """Persist audit logs to JSON."""
        with open(os.path.join(self.data_dir, "audit_logs.json"), "w") as f:
            json.dump(self.data["audit_logs"], f, indent=4)
