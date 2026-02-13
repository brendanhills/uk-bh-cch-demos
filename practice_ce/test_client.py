import logging.config
import requests
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport

def test_endpoint(username, password, query=""):
    print(f"\n--- Testing API with User: {username} | Role: {password} ---")
    
    url = 'http://localhost:8000/soap'
    namespaces = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/', 'tns': 'cebank.compliance.mock'}

    def send_soap_request(operation, query=""):
        payload = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="cebank.compliance.mock">
            <soapenv:Body>
                <tns:{operation}>
                    <tns:query>{query}</tns:query>
                </tns:{operation}>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        response = requests.post(url, auth=HTTPBasicAuth(username, password), data=payload, headers={'Content-Type': 'text/xml'})
        return response

    try:
        from lxml import etree
        
        # Test GetTradingRules
        print("\n=> Calling GetTradingRules...")
        resp = send_soap_request("GetTradingRules", query)
        if resp.status_code == 200:
            root = etree.fromstring(resp.content)
            rules = root.findall(".//tns:TradingRule", namespaces=namespaces)
            print(f"   Found {len(rules)} rules.")
            for r in rules:
                r_id = r.find("tns:id", namespaces=namespaces).text
                r_title = r.find("tns:title", namespaces=namespaces).text
                print(f"    - ID: {r_id}, Title: {r_title}")
        else:
             print(f"   [ERROR] Request failed (Status {resp.status_code}): {resp.text}")
                
        # Test GetRegulatoryFilings
        print("\n=> Calling GetRegulatoryFilings...")
        resp = send_soap_request("GetRegulatoryFilings", query)
        if resp.status_code == 200:
            root = etree.fromstring(resp.content)
            filings = root.findall(".//tns:RegulatoryFiling", namespaces=namespaces)
            print(f"   Found {len(filings)} filings.")
            for f in filings:
                f_id = f.find("tns:id", namespaces=namespaces).text
                f_title = f.find("tns:title", namespaces=namespaces).text
                print(f"    - ID: {f_id}, Title: {f_title}")
        else:
            pass

        # Test GetAuditLogs
        print(f"\n=> Calling GetAuditLogs(query='{query}')...")
        resp = send_soap_request("GetAuditLogs", query)
        if resp.status_code == 200:
            root = etree.fromstring(resp.content)
            logs = root.findall(".//tns:AuditLog", namespaces=namespaces)
            print(f"   Found {len(logs)} logs.")
            for l in logs[-3:]:
                 l_ts = l.find("tns:timestamp", namespaces=namespaces).text
                 l_action = l.find("tns:action", namespaces=namespaces).text
                 print(f"    - [{l_ts}] {l_action}")
            if len(logs) > 3: print(f"      ... and {len(logs) - 3} more")
        else:
            pass
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection failed. Is the SOAP mock service running? Standard port is 8000.")
        print("Run `uv run python app.py` first.")
    except Exception as e:
         print(f"\n[ERROR] Request failed: {e}")

if __name__ == "__main__":
    import json
    import os
    
    db_path = os.path.join(os.path.dirname(__file__), "data", "mock_db.json")
    try:
        with open(db_path, 'r') as f:
            db_data = json.load(f)
            users = db_data.get("users", [])
    except FileNotFoundError:
        print("[ERROR] Mock database not found. Run `uv run python generate_mock_data.py` first.")
        users = []
        
    for user in users:
        # For simplicity, testing almost everyone for 'violation' queries which hits the Audit Logs
        test_endpoint(user["username"], user["password"], query="violation")
    
    # Test one unauthorized scenario mapping to "hacker"
    test_endpoint("bad_actor_99", "wrongpassword", query="")
    
