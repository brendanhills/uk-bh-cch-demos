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
    %% Top Level
    User([Applicant])
    Human([Human Underwriter])

    User --> UI[Streamlit UI]
    UI --> Guard[Security Guardian]
    Guard --> Manager

    subgraph Secure [Secure Internal Environment]
        direction TB
        
        subgraph Agents [Expert Agents]
            direction LR
            Manager[Loan Manager]
            Invest[Investigator]
            Policy[Policy Expert]
            Risk[Risk Analyst]
            Underwriter[Underwriter]
        end

        subgraph Tools [Internal Tools]
            direction LR
            T_Reg[Registration]
            T_DTI[DTI Calc]
            T_RAG[Policy RAG]
           
        end

        Agents ~~~~ Tools
        Manager --> Underwriter
        Manager --> Invest & Policy & Risk 
               
        Manager --- T_Reg
        Invest --- T_DTI
        Policy --- T_RAG
        Underwriter --- PDF
        
        
        Audit[Audit Logger]
        PDF[Descision Register]
        Agents & Tools -.-> Audit
    end

    %% External Connections
    Risk -- "Escalate" --> Human
    %%T_DTI --> External

    subgraph External [External Data Providers]
        Equifax[Equifax API]
        Workday[Workday API]
        FraudNet[Fraud.net API]
    end

    %% Link specific investigation tools to APIs
    %% We use a generic 'Invest' link here to keep it tidy
    Invest --> Equifax & Workday & FraudNet

    %% FORCE External to be below Secure box
    Secure ~~~~ External

    %% Styling
    classDef secure fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class Secure,Agents,Underwriter,Tools,Manager,Invest,Policy,Risk,T_Reg,T_DTI,T_RAG,T_Log,Audit secure;
    
    classDef external fill:#fff3e0,stroke:#ff6f00,stroke-width:2px,stroke-dasharray: 5 5;
    class External,Equifax,Workday,FraudNet external;

    classDef human fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    class User,Human human;
"""

flow_diagram = """
sequenceDiagram
    actor User
    participant Manager as Loan Manager
    participant Vault as Token Vault / DLP
    participant Invest as Investigator Agent
    participant Tools as Investigation Tools
    participant Policy as Policy Expert
    participant RAG as Policy: Confluence
    participant Under as Underwriter
    participant Audit as Audit Log
    participant ExtAPI as External APIs (Equifax/Workday/Fraud.net)
    

    User->>Manager: "Apply for Loan"
    Manager->>Audit: Log Intake Event
    Manager->>Vault: register_application (tokenize)
    Vault-->>Manager: Returns APP-ID & Token
    
    Manager->>Invest: "Investigate Profile"
    
    rect rgb(240, 248, 255)
        note right of Invest: Secure Boundary Exit
        Invest->>Tools: get_credit_report (Token)
        Tools->>ExtAPI: get_credit_report (RealID)
        ExtAPI-->>Tools: Raw Credit Data
        Tools->>Audit: EXTERNAL_API_RESPONSE (Equifax)
        Tools->>Invest: credit_report
                
        Invest-->>ExtAPI: verify_employment (Real ID)
        ExtAPI-->>Invest: emploment_verification (Workday)

        Invest-->>ExtAPI: check_fraud_risk (Real ID)
        ExtAPI-->>Invest: fraud_report(fraud.net)
    end

    Invest->>Invest: calculate_dti
    Invest->>Audit: log_investigation_finding
    Invest-->>Manager: Investigation Report

    Manager->>Policy: "Review Eligibility"
    Policy->>RAG: consult_policy_docs (query)
    RAG->>Policy: policy_match (PDF)
    Policy-->>Manager: Policy Assessment

    Manager->>Under: "Final Decision"
    Under->>Audit: record_decision_start
    Under->>Under: record_decision (Generate PDF)
    Under-->>Manager: APPROVE / DENY / ESCALATE
    
    Manager->>User: Display Decision & PDF
"""

if __name__ == "__main__":
    download_mermaid(arch_diagram, "docs/architecture.png")
    download_mermaid(flow_diagram, "docs/flow.png")
