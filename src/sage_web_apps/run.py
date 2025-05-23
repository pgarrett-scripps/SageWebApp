import argparse
import os
import sys
import subprocess

def run_streamlit_app(module_path):
    """Helper function to run a Streamlit app from a module path."""
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct absolute path if relative
    if not os.path.isabs(module_path):
        module_path = os.path.join(current_dir, module_path)
    
    # Run streamlit command
    cmd = [sys.executable, "-m", "streamlit", "run", module_path]
    subprocess.run(cmd)

def run_input_app():

    # arg parse to get local

    parser = argparse.ArgumentParser(description="Run the Sage input app.")
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run the app in server mode (default: False)",
    )

    args = parser.parse_args()
    if args.server:
        os.environ["LOCAL"] = "False"
    else:
        # set env local to true if not set (running cli command)
        os.environ["LOCAL"] = "True"

    """Run the sage_input_app.py streamlit application."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_input_app.py")
    run_streamlit_app(app_path)

def run_sage_app():

    parser = argparse.ArgumentParser(description="Run the Sage app.")
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run the app in server mode (default: False)",
    )

    args = parser.parse_args()
    if args.server:
        os.environ["LOCAL"] = "False"
    else:
        # set env local to true if not set (running cli command)
        os.environ["LOCAL"] = "True"

    """Run the sage_app.py streamlit application."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sage_app.py")
    run_streamlit_app(app_path)

if __name__ == "__main__":
    # If script is run directly, show help
    print("This module provides functions to run Sage Streamlit apps.")
    print("Use 'sage-app' or 'sage-input-app' CLI commands to run the apps.")
