import base64
import requests

def download_mermaid(graph, filename):
    graphbytes = graph.encode("utf8")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    url = "https://mermaid.ink/img/" + base64_string
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}: {response.status_code}")

arch_diagram = """
graph TD
    User([Applicant]) --> UI[Streamlit / Web App]
    UI --> Guard[Security Guardian]
    Guard --> Manager[Loan Manager]
    
    Manager --> Invest[Investigator Agent]
    Manager --> Policy[Policy Expert Agent]
    Manager --> Risk[Risk Analyst Agent]

    %% Internal Tools (Secure Boundary)
    Manager -- "Raw ID" --> Vault[Token Vault / DLP Service]
    Vault -- "Token" --> Manager
    
    Invest -- "Token" --> BureauTool[Credit Tool]
    Invest -- "Token" --> EmployTool[Employment Tool]
    Invest -- "Token" --> FraudTool[Fraud Tool]
    
    %% External APIs (No Direct Agent Access)
    BureauTool -- "API Call" --> BureauAPI[Equifax/Experian API]
    EmployTool -- "API Call" --> EmployAPI[Workday API]
    FraudTool -- "API Call" --> FraudAPI[Sift/Fraud.net API]
    
    Policy -- "RAG" --> VectorDB[(Policy Vector Store)]
    
    %% Audit Logging (All Internal Components)
    Manager -.-> Audit[Audit Logger]
    Invest -.-> Audit
    BureauTool -.-> Audit
    EmployTool -.-> Audit
    FraudTool -.-> Audit
    Policy -.-> Audit
    
    Audit --> Logs[(Audit Log / JSONL)]
    
    classDef secure fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class Invest,Policy,Risk,BureauTool,EmployTool,FraudTool,VectorDB,Vault,Audit secure;
    
    classDef external fill:#fff3e0,stroke:#ff6f00,stroke-width:2px,stroke-dasharray: 5 5;
    class BureauAPI,EmployAPI,FraudAPI external;
"""

flow_diagram = """
sequenceDiagram
    participant User
    participant Manager as Loan Manager
    participant Vault as Token Vault / DLP
    participant Invest as Investigator
    participant IntTool as Internal Tool (e.g. Credit)
    participant Audit as Audit Log
    participant ExtAPI as External API (Equifax)

    User->>Manager: "Apply for Loan (ID: 900-00-1234)"
    Manager->>Audit: Log Intake Event (PII Masked)
    Manager->>Vault: Register Application
    Vault-->>Manager: Returns Token (token_900...)
    
    Manager->>Invest: "Get financial profile for token_900..."
    Invest->>IntTool: get_credit_report(token)
    
    rect rgb(240, 248, 255)
        note right of IntTool: Secure Boundary
        IntTool->>Vault: Detokenize (Secure)
        IntTool->>Audit: Log Access START (User: token_900...)
        IntTool->>ExtAPI: Fetch Report (Real ID)
        ExtAPI-->>IntTool: Return Raw Data
        IntTool->>Audit: Log Access SUCCESS
    end
    
    IntTool-->>Invest: Return Risk Signals (No PII)
    Invest-->>Manager: "Profile: 720 Score, Employed"
    
    Manager->>Audit: Log Final Decision
    Manager->>User: "Application Approved/Declined"
"""

download_mermaid(arch_diagram, "docs/architecture.png")
download_mermaid(flow_diagram, "docs/flow.png")
