#!/usr/bin/env python3
"""
Integrated CLI test harness for the NotebookLM Enterprise API.
Allows executing single operations or running full integration tests in Live or Mock modes.
"""

import os
import sys
import argparse
import json
from dotenv import load_dotenv
from notebooklm_client import NotebookLMClient

def main():
    load_dotenv()
    
    # Configure argument parser
    parser = argparse.ArgumentParser(
        description="CLI Test Harness and Playground for the NotebookLM Enterprise API.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode", 
        choices=["mock", "live"], 
        default=os.getenv("DEFAULT_MODE", "mock").lower(),
        help="Select execution mode: 'mock' (local emulation) or 'live' (real GCP calls). Defaults to 'mock'."
    )
    
    parser.add_argument(
        "--project", 
        default=os.getenv("GCP_PROJECT_NUMBER", "123456789012"),
        help="Google Cloud Project Number. Defaults to GCP_PROJECT_NUMBER from .env."
    )

    parser.add_argument(
        "--token", 
        default=os.getenv("GCP_ACCESS_TOKEN"),
        help="Google Cloud OAuth2 Access Token. Defaults to GCP_ACCESS_TOKEN from .env."
    )

    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress verbose HTTP headers, payloads, and curl logging outputs."
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: self-test
    subparsers.add_parser(
        "self-test", 
        help="Run the complete suite of scenario integration tests (lifecycle and admin recovery)."
    )

    # Command: list
    subparsers.add_parser(
        "list", 
        help="List recently viewed notebooks."
    )

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create a new notebook.")
    create_parser.add_argument("title", help="Title of the new notebook.")

    # Command: get
    get_parser = subparsers.add_parser("get", help="Retrieve notebook details & sources.")
    get_parser.add_argument("id", help="Notebook ID.")

    # Command: delete
    delete_parser = subparsers.add_parser("delete", help="Delete a notebook.")
    delete_parser.add_argument("id", help="Notebook ID.")

    # Command: share
    share_parser = subparsers.add_parser("share", help="Share a notebook / manage roles.")
    share_parser.add_argument("id", help="Notebook ID.")
    share_parser.add_argument("email", help="Target user's email address.")
    share_parser.add_argument(
        "role", 
        choices=["PROJECT_ROLE_OWNER", "PROJECT_ROLE_WRITER", "PROJECT_ROLE_READER", "PROJECT_ROLE_NOT_SHARED"],
        help="Role to assign."
    )

    # Command: add-source
    add_src_parser = subparsers.add_parser("add-source", help="Add a text or web URL source in batch.")
    add_src_parser.add_argument("id", help="Notebook ID.")
    add_src_parser.add_argument("type", choices=["text", "url"], help="Type of source.")
    add_src_parser.add_argument("title", help="Display name of the source.")
    add_src_parser.add_argument("content", help="Raw text content or Web page URL.")

    # Command: upload-file
    upload_parser = subparsers.add_parser("upload-file", help="Stream upload a local file.")
    upload_parser.add_argument("id", help="Notebook ID.")
    upload_parser.add_argument("path", help="Local absolute or relative path to the file.")
    upload_parser.add_argument("title", help="Display name inside the notebook.")
    upload_parser.add_argument("content_type", help="MIME Content Type (e.g. text/plain, application/pdf).")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute Programmatic Self-Tests
    if args.command == "self-test":
        import unittest
        os.environ["DEFAULT_MODE"] = args.mode
        os.environ["INTEGRATION_TEST_MODE"] = args.mode
        os.environ["VERBOSE_LOGGING"] = str(not args.quiet)
        
        # Load test scenarios and execute via unittest runner
        import tests.test_scenarios
        suite = unittest.TestLoader().loadTestsFromModule(tests.test_scenarios)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    # Initialize Client
    client = NotebookLMClient(
        project_number=args.project,
        token=args.token,
        default_mode=args.mode,
        verbose=not args.quiet
    )

    try:
        if args.command == "list":
            res = client.list_recently_viewed()
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "create":
            res = client.create_notebook(title=args.title)
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "get":
            res = client.get_notebook(notebook_id=args.id)
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "delete":
            client.delete_notebook(notebook_id=args.id)
            print(f"Notebook ID {args.id} deletion requested successfully.")
            
        elif args.command == "share":
            roles = [{"email": args.email, "role": args.role}]
            client.share_notebook(notebook_id=args.id, accounts_and_roles=roles)
            print(f"Notebook sharing role for {args.email} set to {args.role}.")
            
        elif args.command == "add-source":
            if args.type == "text":
                src = {"textContent": {"sourceName": args.title, "content": args.content}}
            else:
                src = {"webContent": {"url": args.content, "sourceName": args.title}}
                
            res = client.batch_create_sources(notebook_id=args.id, sources_list=[src])
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "upload-file":
            res = client.upload_source_file(
                notebook_id=args.id,
                file_path=args.path,
                display_name=args.title,
                content_type=args.content_type
            )
            if args.quiet:
                print(json.dumps(res, indent=2))

    except Exception as e:
        print(f"\033[91mError executing command '{args.command}': {e}\033[0m", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
