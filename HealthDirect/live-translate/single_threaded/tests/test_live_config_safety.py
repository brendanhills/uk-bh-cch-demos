import ast
import os
import pytest

def test_no_unsupported_language_codes_in_ast():
    """
    Ensure we never use language_codes in AudioTranscriptionConfig inside web_server.py,
    as it is only supported in Gemini Enterprise Agent Platform mode and crashes the Developer API.
    """
    web_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../demo/web_server.py"))
    assert os.path.exists(web_server_path), f"web_server.py not found at {web_server_path}"

    with open(web_server_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    class AudioTranscriptionConfigVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Call(self, node):
            # Check for types.AudioTranscriptionConfig(...) or AudioTranscriptionConfig(...)
            is_config_call = False
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "AudioTranscriptionConfig":
                    is_config_call = True
            elif isinstance(node.func, ast.Name):
                if node.func.id == "AudioTranscriptionConfig":
                    is_config_call = True

            if is_config_call:
                # Check keywords (e.g. language_codes=...)
                for keyword in node.keywords:
                    if keyword.arg == "language_codes":
                        self.violations.append(node.lineno)
            
            self.generic_visit(node)

    visitor = AudioTranscriptionConfigVisitor()
    visitor.visit(tree)

    assert not visitor.violations, (
        f"CRITICAL SAFETY VIOLATION: Found unsupported 'language_codes' parameter inside "
        f"AudioTranscriptionConfig on line(s): {visitor.violations}. "
        f"This parameter is only supported in Gemini Enterprise Agent Platform mode and will crash the Developer API!"
    )
