import requests
from lxml import etree
import logging

# Configuration
SOAP_URL = "http://localhost:8000/soap"
NAMESPACES = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "tns": "cebank.compliance.mock"
}

class SoapClient:
    def __init__(self, username, password):
        self.auth = (username, password)
        
    def _send_request(self, operation, query=""):
        payload = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="cebank.compliance.mock">
            <soapenv:Body>
                <tns:{operation}>
                    <tns:query>{query}</tns:query>
                </tns:{operation}>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        try:
            response = requests.post(SOAP_URL, auth=self.auth, data=payload, headers={'Content-Type': 'text/xml'})
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"SOAP request failed: {e}")
            raise

    def get_trading_rules(self):
        content = self._send_request("GetTradingRules")
        return self._parse_items(content, "TradingRule")

    def get_regulatory_filings(self):
        content = self._send_request("GetRegulatoryFilings")
        return self._parse_items(content, "RegulatoryFiling")

    def get_audit_logs(self):
        content = self._send_request("GetAuditLogs")
        return self._parse_items(content, "AuditLog")
        
    def _parse_items(self, xml_content, item_tag):
        root = etree.fromstring(xml_content)
        items = root.findall(f".//tns:{item_tag}", namespaces=NAMESPACES)
        parsed_items = []
        
        for item in items:
            item_dict = {}
            # Extract standard fields
            for child in item:
                tag = etree.QName(child).localname
                if tag == "acl":
                    # Extract ACL entries
                    acl_entries = [entry.text for entry in child.findall("tns:entry", namespaces=NAMESPACES)]
                    item_dict["acl"] = acl_entries
                else:
                    item_dict[tag] = child.text
            parsed_items.append(item_dict)
            
        return parsed_items
