import logging
import base64
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from lxml import etree

from data_store import DataStore

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="CEBank International Compliance System")
db = DataStore()
security = HTTPBasic()

# Namespace definitions
SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
TNS = "cebank.compliance.mock"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if not db.authenticate(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Please provide valid credentials.",
            headers={"WWW-Authenticate": 'Basic realm="CEBank International Compliance System"'},
        )
    role = db.get_user_role(credentials.username)
    return {"username": credentials.username, "role": role}

def build_soap_response(body_element: etree.Element) -> Response:
    """Wraps an XML element in a standard SOAP Envelope."""
    envelope = etree.Element(f"{{{SOAP_ENV}}}Envelope", nsmap={"soapenv": SOAP_ENV, "tns": TNS})
    body = etree.SubElement(envelope, f"{{{SOAP_ENV}}}Body")
    body.append(body_element)
    
    xml_str = etree.tostring(envelope, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return Response(content=xml_str, media_type="text/xml")

@app.post("/soap")
@app.post("/")
async def soap_endpoint(request: Request, user_info: dict = Depends(verify_credentials)):
    """The main SOAP entrypoint that parses requested operations."""
    try:
        raw_body = await request.body()
        root = etree.fromstring(raw_body)
        
        # Find the Body element
        body = root.find(f".//{{{SOAP_ENV}}}Body")
        if body is None or len(body) == 0:
            raise ValueError("Invalid SOAP Envelope: Missing or empty Body.")
            
        operation = body[0]
        op_name = etree.QName(operation).localname
        
        # Extract query if present
        query_elem = operation.find(".//query")
        query = query_elem.text if query_elem is not None and query_elem.text else ""
        
        # Route to logic
        if op_name == "GetTradingRules":
            return handle_get_trading_rules(query, user_info)
        elif op_name == "GetRegulatoryFilings":
            return handle_get_regulatory_filings(query, user_info)
        elif op_name == "GetAuditLogs":
            return handle_get_audit_logs(query, user_info)
        else:
            raise ValueError(f"Unknown operation: {op_name}")
            
    except Exception as e:
        logging.error(f"SOAP Error: {e}")
        # Build SOAP Fault
        fault_elem = etree.Element(f"{{{SOAP_ENV}}}Fault")
        faultcode = etree.SubElement(fault_elem, "faultcode")
        faultcode.text = "soapenv:Server"
        faultstring = etree.SubElement(fault_elem, "faultstring")
        faultstring.text = str(e)
        return build_soap_response(fault_elem)

def get_effective_acl(document):
    """
    Computes which roles can see a document based on its category and sensitivity.
    Used by the Connector to populate the 'acl' field for the search index.
    """
    allowed_roles = []
    # We need to iterate over all roles defined in the policy
    # Since we don't have a direct 'get_all_roles' method exposed, we can read from the internal data
    # or just iterate a known list of standard roles.
    # A cleaner way is to use the DataStore to check authorization for each role.
    
    # We can fetch roles from the loaded ACLs if available, or hardcode the standard set
    # Using hardcoded set for safety and simplicity in this mock context, but ideally would be dynamic.
    all_roles = ["Trader", "Compliance", "HR", "Executive", "Auditor", "InvestmentBanking"]
    
    for role in all_roles:
         if db.is_authorized(document, "system_check", role):
             allowed_roles.append(role)
             
    return allowed_roles

def handle_get_trading_rules(query, user_info):
    rules = db.get_trading_rules(user_info["username"], user_info["role"])
    if query:
        rules = [r for r in rules if query.lower() in r.get('title', '').lower() or query.lower() in r.get('content', '').lower()]
        
    response_elem = etree.Element(f"{{{TNS}}}GetTradingRulesResponse")
    rules_array = etree.SubElement(response_elem, f"{{{TNS}}}GetTradingRulesResult")
    
    for r in rules:
        rule_elem = etree.SubElement(rules_array, f"{{{TNS}}}TradingRule")
        
        # If Connector, we must COMPUTE and INJECT the effective ACL
        if user_info["role"] == "Connector":
             effective_acl = get_effective_acl(r)
             acl_elem = etree.SubElement(rule_elem, f"{{{TNS}}}acl")
             for item in effective_acl:
                 entry = etree.SubElement(acl_elem, f"{{{TNS}}}entry")
                 entry.text = item
        
        for k, v in r.items():
            if k == "acl": continue # Should not exist anymore, but just in case
            
            elem = etree.SubElement(rule_elem, f"{{{TNS}}}{k}")
            elem.text = str(v)
            
    return build_soap_response(response_elem)

def handle_get_regulatory_filings(query, user_info):
    filings = db.get_regulatory_filings(user_info["username"], user_info["role"])
    if query:
        filings = [f for f in filings if query.lower() in f.get('title', '').lower() or query.lower() in f.get('summary', '').lower()]
        
    response_elem = etree.Element(f"{{{TNS}}}GetRegulatoryFilingsResponse")
    filings_array = etree.SubElement(response_elem, f"{{{TNS}}}GetRegulatoryFilingsResult")
    
    for f in filings:
        filing_elem = etree.SubElement(filings_array, f"{{{TNS}}}RegulatoryFiling")
        
        if user_info["role"] == "Connector":
             effective_acl = get_effective_acl(f)
             acl_elem = etree.SubElement(filing_elem, f"{{{TNS}}}acl")
             for item in effective_acl:
                 entry = etree.SubElement(acl_elem, f"{{{TNS}}}entry")
                 entry.text = item

        for k, v in f.items():
             if k == "acl": continue 

             elem = etree.SubElement(filing_elem, f"{{{TNS}}}{k}")
             elem.text = str(v)
            
    return build_soap_response(response_elem)

def handle_get_audit_logs(query, user_info):
    logs = db.get_audit_logs(user_info["username"], user_info["role"])
    if query:
        logs = [l for l in logs if query.lower() in l.get('details', '').lower() or query.lower() in l.get('action', '').lower()]
        
    response_elem = etree.Element(f"{{{TNS}}}GetAuditLogsResponse")
    logs_array = etree.SubElement(response_elem, f"{{{TNS}}}GetAuditLogsResult")
    
    for l in logs:
        log_elem = etree.SubElement(logs_array, f"{{{TNS}}}AuditLog")
        
        if user_info["role"] == "Connector":
             # For Audit Logs, owner also has access.
             effective_acl = get_effective_acl(l)
             # Add the specific user owner if not already covered (though roles covers groups)
             # The connector usually maps external groups. 
             # If mapping userId -> userId, we can add it.
             if l.get("userId") and l.get("userId") not in effective_acl:
                 effective_acl.append(l.get("userId"))
                 
             acl_elem = etree.SubElement(log_elem, f"{{{TNS}}}acl")
             for item in effective_acl:
                 entry = etree.SubElement(acl_elem, f"{{{TNS}}}entry")
                 entry.text = item

        for k, v in l.items():
             if k == "acl": continue

             elem = etree.SubElement(log_elem, f"{{{TNS}}}{k}")
             elem.text = str(v)
            
    return build_soap_response(response_elem)

@app.get("/")
@app.get("/wsdl")
def get_wsdl():
    """Returns a basic WSDL representation for the mock service."""
    wsdl = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/" 
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" 
             xmlns:tns="{TNS}" 
             targetNamespace="{TNS}">
    
    <types>
        <schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="{TNS}">
            <element name="GetTradingRules">
                <complexType><sequence><element name="query" type="string" minOccurs="0"/></sequence></complexType>
            </element>
            <element name="GetTradingRulesResponse">
                <complexType><sequence><any minOccurs="0" maxOccurs="unbounded" processContents="skip"/></sequence></complexType>
            </element>
            <element name="GetRegulatoryFilings">
                <complexType><sequence><element name="query" type="string" minOccurs="0"/></sequence></complexType>
            </element>
            <element name="GetRegulatoryFilingsResponse">
                <complexType><sequence><any minOccurs="0" maxOccurs="unbounded" processContents="skip"/></sequence></complexType>
            </element>
            <element name="GetAuditLogs">
                <complexType><sequence><element name="query" type="string" minOccurs="0"/></sequence></complexType>
            </element>
            <element name="GetAuditLogsResponse">
                <complexType><sequence><any minOccurs="0" maxOccurs="unbounded" processContents="skip"/></sequence></complexType>
            </element>
        </schema>
    </types>

    <message name="GetTradingRulesRequest"><part name="parameters" element="tns:GetTradingRules"/></message>
    <message name="GetTradingRulesResponse"><part name="parameters" element="tns:GetTradingRulesResponse"/></message>
    
    <message name="GetRegulatoryFilingsRequest"><part name="parameters" element="tns:GetRegulatoryFilings"/></message>
    <message name="GetRegulatoryFilingsResponse"><part name="parameters" element="tns:GetRegulatoryFilingsResponse"/></message>

    <message name="GetAuditLogsRequest"><part name="parameters" element="tns:GetAuditLogs"/></message>
    <message name="GetAuditLogsResponse"><part name="parameters" element="tns:GetAuditLogsResponse"/></message>

    <portType name="CompliancePort">
        <operation name="GetTradingRules">
            <input message="tns:GetTradingRulesRequest"/>
            <output message="tns:GetTradingRulesResponse"/>
        </operation>
        <operation name="GetRegulatoryFilings">
            <input message="tns:GetRegulatoryFilingsRequest"/>
            <output message="tns:GetRegulatoryFilingsResponse"/>
        </operation>
        <operation name="GetAuditLogs">
            <input message="tns:GetAuditLogsRequest"/>
            <output message="tns:GetAuditLogsResponse"/>
        </operation>
    </portType>

    <binding name="ComplianceBinding" type="tns:CompliancePort">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="GetTradingRules">
            <soap:operation soapAction="GetTradingRules"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
         <operation name="GetRegulatoryFilings">
            <soap:operation soapAction="GetRegulatoryFilings"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
         <operation name="GetAuditLogs">
            <soap:operation soapAction="GetAuditLogs"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
    </binding>

    <service name="ComplianceService">
        <port name="CompliancePort" binding="tns:ComplianceBinding">
            <soap:address location="http://0.0.0.0:8000/soap"/>
        </port>
    </service>
</definitions>"""
    return Response(content=wsdl, media_type="text/xml")
