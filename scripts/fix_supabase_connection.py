import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import subprocess
import pkg_resources

def check_supabase_version():
    """
    Check the installed version of the supabase-py library and update if needed.
    """
    try:
        # Get the installed version of supabase-py
        supabase_version = pkg_resources.get_distribution("supabase").version
        print(f"Current supabase-py version: {supabase_version}")

        # Check if the version is compatible
        # The proxy parameter issue typically occurs in newer versions
        if supabase_version.startswith("0."):
            print("You have an older version of supabase-py which may be more compatible.")
            return True

        # Ask if the user wants to downgrade to a compatible version
        print("\nThe current version of supabase-py may have compatibility issues.")
        print("Would you like to install a compatible version? (y/n)")
        choice = input().lower()

        if choice == 'y':
            print("Installing a compatible version of supabase-py...")
            # Install a specific version known to work
            subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase==0.7.1"])
            print("✅ Installed supabase-py version 0.7.1")
            print("Please restart your application for the changes to take effect.")
            return True
        else:
            print("Continuing with the current version.")
            return True
    except Exception as e:
        print(f"Error checking supabase version: {e}")
        return False

def check_and_fix_supabase_connection():
    """
    Check and fix the Supabase connection by ensuring the environment variables
    are properly loaded and the Supabase client is initialized correctly.
    """
    print("Checking Supabase connection...")

    # Load environment variables
    load_dotenv()

    # Check if Supabase credentials are available
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials. Please check your .env file.")
        print(f"SUPABASE_URL: {'✅ Found' if supabase_url else '❌ Missing'}")
        print(f"SUPABASE_KEY: {'✅ Found' if supabase_key else '❌ Missing'}")
        return False

    # Try to connect to Supabase
    try:
        # Try to create the client with standard parameters
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            print("✅ Successfully connected to Supabase.")
        except TypeError as e:
            # Check if the error is about the 'proxy' argument
            if "unexpected keyword argument 'proxy'" in str(e):
                print("⚠️ Detected older version of Supabase library, adjusting connection parameters...")
                # Try creating the client without the proxy parameter
                import inspect
                valid_params = inspect.signature(create_client).parameters
                kwargs = {"supabase_url": supabase_url, "supabase_key": supabase_key}
                # Only include parameters that are valid for this version
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
                supabase = create_client(**filtered_kwargs)
                print("✅ Successfully connected to Supabase with adjusted parameters.")
            else:
                # If it's a different TypeError, re-raise it
                raise

        # Test connection by querying tables
        tables = ["market_data", "reports", "queries", "workflows"]
        for table in tables:
            try:
                response = supabase.table(table).select("id").limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible.")
            except Exception as e:
                print(f"❌ Error accessing table '{table}': {e}")
                print(f"You may need to run setup_supabase.py to create the table.")
                return False

        print("\n✅ Supabase connection is working correctly.")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        # Check if it's a version compatibility issue
        if "unexpected keyword argument" in str(e):
            print("\n⚠️ This appears to be a version compatibility issue with the supabase-py library.")
            check_supabase_version()
        return False

def main():
    """Main function to run the script."""
    success = check_and_fix_supabase_connection()
    if not success:
        # If the connection check failed, check the supabase version
        print("\nChecking supabase-py library version...")
        check_supabase_version()
        print("\nPlease fix the Supabase connection issues before running the application.")
        print("You may need to:")
        print("1. Check your .env file for correct Supabase credentials")
        print("2. Run setup_supabase.py to create the necessary tables")
        print("3. Ensure your Supabase instance is running and accessible")
        print("4. Install a compatible version of supabase-py: pip install supabase==0.7.1")
    else:
        print("\nYou can now run the application with:")
        print("streamlit run multi_agent_app.py")

if __name__ == "__main__":
    main()
