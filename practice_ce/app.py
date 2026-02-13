import multiprocessing
import subprocess
import time
import sys

def start_soap_service():
    """Starts the FastAPI mock SOAP service on port 8000 using Uvicorn."""
    import uvicorn
    from compliance_soap_service import app
    
    print("Starting CEBank International SOAP Service on http://0.0.0.0:8000")
    print("WSDL is available at http://0.0.0.0:8000/?wsdl")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def start_streamlit_app():
    """Starts the Streamlit dashboard."""
    print("Starting Streamlit Dashboard...")
    # Give the SOAP service a moment to start so the logs look orderly
    time.sleep(2)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    print(f"--- CEBank International Compliance System ---")
    
    soap_process = multiprocessing.Process(target=start_soap_service)
    streamlit_process = multiprocessing.Process(target=start_streamlit_app)
    
    try:
        soap_process.start()
        streamlit_process.start()
        
        # Wait for both processes
        soap_process.join()
        streamlit_process.join()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        soap_process.terminate()
        streamlit_process.terminate()
        soap_process.join()
        streamlit_process.join()
        print("Shutdown complete.")
