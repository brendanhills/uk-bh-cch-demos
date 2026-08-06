import sys
import os

# Add parent directory to sys.path so we can import demo.web_server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from demo.web_server import load_and_format_glossary

print("=== PATIENT TO NURSE GLOSSARY ===")
p_to_n = load_and_format_glossary("German", direction="p_to_n", exclude_descriptions=True)
print(p_to_n)

print("\n=== NURSE TO PATIENT GLOSSARY ===")
n_to_p = load_and_format_glossary("German", direction="n_to_p", exclude_descriptions=True)
print(n_to_p)
