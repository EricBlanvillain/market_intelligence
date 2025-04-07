import sys
import subprocess
import pkg_resources

def fix_supabase_version():
    """
    Install a compatible version of the supabase-py library to fix the 'proxy' keyword argument error.
    """
    print("Checking current supabase-py version...")

    try:
        # Get the installed version of supabase-py
        try:
            supabase_version = pkg_resources.get_distribution("supabase").version
            print(f"Current supabase-py version: {supabase_version}")
        except pkg_resources.DistributionNotFound:
            print("supabase-py is not installed. Installing compatible version...")
            supabase_version = None

        # Install a compatible version
        print("Installing a compatible version of supabase-py (0.7.1)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase==0.7.1"])

        # Verify the installation
        new_version = pkg_resources.get_distribution("supabase").version
        print(f"✅ Successfully installed supabase-py version {new_version}")
        print("\nPlease restart your application for the changes to take effect.")
        print("You can now run the application with:")
        print("streamlit run multi_agent_app.py")

        return True
    except Exception as e:
        print(f"❌ Error installing supabase-py: {e}")
        print("\nYou can try manually installing the compatible version with:")
        print("pip install supabase==0.7.1")
        return False

if __name__ == "__main__":
    fix_supabase_version()
