import base64
import requests
import os

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

# Ensure docs directory exists
os.makedirs("docs", exist_ok=True)

import glob

def render_all_diagrams():
    # Ensure output directory exists
    output_dir = "docs/diagrams"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all .mmd files in docs/diagrams
    mmd_files = glob.glob(os.path.join(output_dir, "*.mmd"))
    
    if not mmd_files:
        print(f"No .mmd files found in {output_dir}")
        return

    for mmd_file in mmd_files:
        try:
            with open(mmd_file, "r") as f:
                graph = f.read()

            # Strip markdown code blocks if present
            if graph.startswith("```mermaid"):
                graph = graph.replace("```mermaid", "").replace("```", "").strip()
            elif graph.startswith("```"):
                graph = graph.replace("```", "").strip()
            
            # Create output filename: docs/diagrams/filename.mmd -> docs/diagrams/filename.png
            base_name = os.path.splitext(os.path.basename(mmd_file))[0]
            output_filename = os.path.join(output_dir, f"{base_name}.png")
            
            print(f"Rendering {mmd_file} -> {output_filename}...")
            download_mermaid(graph, output_filename)
        except Exception as e:
            print(f"Error rendering {mmd_file}: {e}")

if __name__ == "__main__":
    render_all_diagrams()
