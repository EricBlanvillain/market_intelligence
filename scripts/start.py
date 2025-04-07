#!/usr/bin/env python3
"""
Start script for Market Intelligence Platform.
This script ensures all dependencies are installed and environment variables are set
before starting the Streamlit application.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed and install them if needed."""
    print("Checking dependencies...")

    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Error: pip is not available. Please install pip first.")
        return False

    # Install required packages
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Error: Failed to install required packages.")
        return False

    # Specifically check for openai
    try:
        import importlib.util
        if importlib.util.find_spec("openai") is None:
            print("OpenAI package not found. Installing it specifically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    except (ImportError, subprocess.CalledProcessError):
        print("Error: Failed to install OpenAI package.")
        return False

    # Check for streamlit
    streamlit_path = shutil.which("streamlit")
    if not streamlit_path:
        print("Streamlit not found. Installing it specifically...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        except subprocess.CalledProcessError:
            print("Error: Failed to install Streamlit.")
            return False

    return True

def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found.")
        env_example = Path(".env.example")
        if env_example.exists():
            response = input("Would you like to create a .env file from .env.example? (y/n): ")
            if response.lower() == 'y':
                with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                    dst.write(src.read())
                print("Created .env file from .env.example. Please edit it with your API keys.")
                return False

    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        # Try to load from .env file if it exists
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == "OPENAI_API_KEY":
                            openai_key = value
                            os.environ["OPENAI_API_KEY"] = value

    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return False

    # Check for Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        print("Warning: Supabase credentials are not set. The application will use mock data.")

    return True

def start_application():
    """Start the Streamlit application."""
    print("Starting Streamlit server...")

    try:
        # Use subprocess.run instead of check_call to capture output
        result = subprocess.run(["streamlit", "run", "multi_agent_app.py"],
                               check=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to start Streamlit server.")
        return False

def main():
    """Main function to start the Market Intelligence Platform."""
    print("Starting Market Intelligence Platform...")

    # Change to the script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")

    # Print Python and system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")

    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"Running in virtual environment: {sys.prefix}")
    else:
        print("Not running in a virtual environment. Using system Python.")

    # Check dependencies and environment
    if not check_dependencies():
        print("Failed to install required dependencies. Exiting.")
        sys.exit(1)

    if not check_environment():
        print("Environment setup incomplete. Exiting.")
        sys.exit(1)

    # Start the application
    if not start_application():
        print("Application failed to start. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
