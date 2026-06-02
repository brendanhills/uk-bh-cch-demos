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
        default=os.getenv("DEFAULT_MODE", "live").lower(),
        help="Select execution mode: 'mock' (local emulation) or 'live' (real GCP calls). Defaults to 'live'."
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

    # Command: clone
    clone_parser = subparsers.add_parser("clone", help="Clone/duplicate a notebook to transfer ownership.")
    clone_parser.add_argument("id", help="Source Notebook ID.")
    clone_parser.add_argument("--title", help="Optional custom title for the cloned notebook.")

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
        location=os.getenv("GCP_LOCATION", "global"),
        endpoint_location=os.getenv("GCP_ENDPOINT_LOCATION", "us"),
        token=args.token,
        default_mode=args.mode,
        verbose=not args.quiet
    )

    try:
        if args.command == "list":
            res = client.list_recently_viewed()
            notebooks = res.get("notebooks", [])
            
            print("\n" + "="*70)
            print(f"📋 \033[1;92mRecently Viewed Notebooks ({len(notebooks)})\033[0m")
            print("="*70)
            for nb in notebooks:
                nb_id = nb.get("notebookId")
                web_url = client.get_web_ui_url(nb_id)
                print(f"  📓 \033[1;93m{nb.get('title')}\033[0m")
                print(f"     ID:        \033[96m{nb_id}\033[0m")
                print(f"     Link:      \033[4;94m{web_url}\033[0m")
                print("-" * 50)
            print("="*70 + "\n")
            
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "create":
            res = client.create_notebook(title=args.title)
            notebook_id = res.get("notebookId")
            target_notebook_id = notebook_id
            web_url = client.get_web_ui_url(notebook_id)
            
            print("\n" + "="*70)
            print("✨ \033[1;92mNotebook Created Successfully!\033[0m")
            print("="*70)
            print(f"  \033[1mTitle\033[0m:        {res.get('title')}")
            print(f"  \033[1mID\033[0m:           \033[96m{notebook_id}\033[0m")
            print(f"  \033[1mWeb UI Link\033[0m:  \033[4;94m{web_url}\033[0m")
            print(f"  \033[1mResource\033[0m:     {res.get('name')}")
            print("="*70 + "\n")
            
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "get":
            res = client.get_notebook(notebook_id=args.id)
            notebook_id = res.get("notebookId")
            target_notebook_id = args.id
            web_url = client.get_web_ui_url(notebook_id)
            
            print("\n" + "="*70)
            print("🔍 \033[1;92mNotebook Details Retrieved!\033[0m")
            print("="*70)
            print(f"  \033[1mTitle\033[0m:        {res.get('title')}")
            print(f"  \033[1mID\033[0m:           \033[96m{notebook_id}\033[0m")
            print(f"  \033[1mWeb UI Link\033[0m:  \033[4;94m{web_url}\033[0m")
            print(f"  \033[1mResource\033[0m:     {res.get('name')}")
            if "sources" in res:
                print(f"  \033[1mSources ({len(res['sources'])})\033[0m:")
                for src in res["sources"]:
                    print(f"    - \033[93m{src.get('title')}\033[0m ({src.get('sourceId', {}).get('id')})")
            print("="*70 + "\n")
            
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "delete":
            client.delete_notebook(notebook_id=args.id)
            target_notebook_id = args.id
            print(f"Notebook ID {args.id} deletion requested successfully.")
            
        elif args.command == "share":
            roles = [{"email": args.email, "role": args.role}]
            client.share_notebook(notebook_id=args.id, accounts_and_roles=roles)
            target_notebook_id = args.id
            print(f"Notebook sharing role for {args.email} set to {args.role}.")
            
        elif args.command == "add-source":
            if args.type == "text":
                src = {"textContent": {"sourceName": args.title, "content": args.content}}
            else:
                src = {"webContent": {"url": args.content, "sourceName": args.title}}
                
            res = client.batch_create_sources(notebook_id=args.id, sources_list=[src])
            target_notebook_id = args.id
            if args.quiet:
                print(json.dumps(res, indent=2))
                
        elif args.command == "upload-file":
            res = client.upload_source_file(
                notebook_id=args.id,
                file_path=args.path,
                display_name=args.title,
                content_type=args.content_type
            )
            target_notebook_id = args.id
            if args.quiet:
                print(json.dumps(res, indent=2))

        elif args.command == "clone":
            res = client.clone_notebook(notebook_id=args.id, new_title=args.title)
            new_id = res.get("new_notebook_id")
            target_notebook_id = new_id
            
            print("\n" + "="*70)
            print("👯 \033[1;92mNotebook Cloned Successfully!\033[0m")
            print("="*70)
            print(f"  \033[1mNew Title\033[0m:        {res.get('new_notebook_title')}")
            print(f"  \033[1mNew ID\033[0m:           \033[96m{new_id}\033[0m")
            print(f"  \033[1mWeb UI Link\033[0m:      \033[4;94m{res.get('web_ui_url')}\033[0m")
            print(f"  \033[1mCloned Sources\033[0m:   {res.get('cloned_sources_count')} webpage sources programmatically replicated.")
            
            non_replicable = res.get("non_replicable_sources", [])
            if non_replicable:
                print("\n⚠️ \033[1;33mManual Re-upload Required for the following sources:\033[0m")
                for src in non_replicable:
                    print(f"    - [{src['type']}] \033[1m{src['title']}\033[0m")
                print("\n  \033[3mNote: Ingestion-only REST APIs do not permit downloading raw file/text payloads.\033[0m")
            print("="*70 + "\n")
            
            if args.quiet:
                print(json.dumps(res, indent=2))

        # Always print the notebook GUID as the last item in the output for easy copy-paste
        if 'target_notebook_id' in locals() and target_notebook_id:
            print(f"\033[1;35mNotebook ID for copy-paste:\033[0m {target_notebook_id}")

    except Exception as e:
        print(f"\033[91mError executing command '{args.command}': {e}\033[0m", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
