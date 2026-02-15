import sys
from connector_app.indexer import map_identity

roles_to_test = ["Compliance", "Trader", "Auditor", "Manager", "Executive", "HR", "brendan", "system.admin", "unknown.user", "tim.trader", "cathy.compliance"]

print("--- ACL Mapping Test ---")
for role in roles_to_test:
    mapped = map_identity(role)
    print(f"'{role}' -> '{mapped}'")
    
print("\n--- Verification ---")
if map_identity("Compliance") == "cathy.compliance@brendanhills.altostrat.com":
    print("✅ Compliance mapped correctly")
else:
    print("❌ Compliance mapping FAILED")

if map_identity("Trader") == "tim.trader@brendanhills.altostrat.com":
    print("✅ Trader mapped correctly")
else:
    print("❌ Trader mapping FAILED")
