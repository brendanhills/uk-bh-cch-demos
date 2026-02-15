import unittest
from data_store import DataStore

class TestPBAC(unittest.TestCase):
    def setUp(self):
        self.db = DataStore()
        # Mock some docs for consistent testing if needed, or use loaded data
        self.trading_rule_internal = {
            "id": "TR-TEST-1",
            "category": "TradingRule",
            "sensitivity": "Internal"
        }
        self.trading_rule_restricted = {
            "id": "TR-TEST-2",
            "category": "TradingRule",
            "sensitivity": "Restricted"
        }
        self.sar_restricted = {
            "id": "RF-TEST-1",
            "category": "RegulatoryFiling",
            "sensitivity": "Restricted"
        }

    def test_trader_access(self):
        # Trader can see Internal Trading Rules
        self.assertTrue(self.db.is_authorized(self.trading_rule_internal, "tim.trader", "Trader"))
        # Trader CANNOT see Restricted Trading Rules
        self.assertFalse(self.db.is_authorized(self.trading_rule_restricted, "tim.trader", "Trader"))
        # Trader CANNOT see Restricted SARs
        self.assertFalse(self.db.is_authorized(self.sar_restricted, "tim.trader", "Trader"))

    def test_compliance_access(self):
        # Compliance can see Restricted Trading Rules
        self.assertTrue(self.db.is_authorized(self.trading_rule_restricted, "cathy.compliance", "Compliance"))
        # Compliance can see Restricted SARs
        self.assertTrue(self.db.is_authorized(self.sar_restricted, "cathy.compliance", "Compliance"))

    def test_audit_log_owner_access(self):
        log = {
            "id": "AUD-TEST",
            "userId": "tim.trader",
            "category": "AuditLog",
            "sensitivity": "Confidential"
        }
        # Owner should access
        self.assertTrue(self.db.is_authorized(log, "tim.trader", "Trader"))
        # Non-owner Trader should NOT access
        self.assertFalse(self.db.is_authorized(log, "tina.trader", "Trader"))
        # Compliance should access (due to policy)
        self.assertTrue(self.db.is_authorized(log, "cathy.compliance", "Compliance"))

if __name__ == '__main__':
    unittest.main()
