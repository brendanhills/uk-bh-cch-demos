from connector_app.soap_client import SoapClient
from connector_app.indexer import Indexer
from connector_app import config
import argparse
import sys
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  

def main():
    parser = argparse.ArgumentParser(description="Gemini Enterprise Custom Connector for CEBank")
    parser.add_argument("--project-id", default=config.PROJECT_ID, help="Google Cloud Project ID")
    parser.add_argument("--location", default=config.LOCATION, help="Vertex AI Search Location")
    parser.add_argument("--dry-run", action="store_true", help="Print JSONs instead of pushing")
    
    args = parser.parse_args()
    
    logging.info(f"Starting Connector for Project: {args.project_id}")
    
    # 1. Initialize Clients
    # In a real app, credentials would be in env vars or secrets manager
    soap_client = SoapClient("gemini.connector", "password123")
    indexer = Indexer(args.project_id, args.location)
    
    # 2. Fetch Data
    try:
        logging.info("Fetching Trading Rules...")
        rules = soap_client.get_trading_rules()
        logging.info(f"Fetched {len(rules)} Trading Rules.")
        
        logging.info("Fetching Regulatory Filings...")
        filings = soap_client.get_regulatory_filings()
        logging.info(f"Fetched {len(filings)} Regulatory Filings.")
        
        logging.info("Fetching Audit Logs...")
        logs = soap_client.get_audit_logs()
        logging.info(f"Fetched {len(logs)} Audit Logs.")
        
    except Exception as e:
        logging.error(f"Failed to fetch data from Mock App: {e}")
        logging.error("Ensure the Mock App is running: `uv run python app.py`")
        sys.exit(1)
        
    # 3. Push Data (Simulate Indexing)
    logging.info("Indexing Data...")
    
    for rule in rules:
        indexer.process_and_push(rule, "TradingRule", dry_run=args.dry_run)
        
    for filing in filings:
        indexer.process_and_push(filing, "RegulatoryFiling", dry_run=args.dry_run)
        
    for log in logs:
         indexer.process_and_push(log, "AuditLog", dry_run=args.dry_run)
        
    logging.info("Connector Run Complete.")

if __name__ == "__main__":
    main()
