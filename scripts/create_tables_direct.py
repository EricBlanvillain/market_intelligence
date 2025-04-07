import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import time
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Successfully connected to Supabase.")
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")
    raise

def create_market_data_table():
    """Create the market_data table using the Supabase client."""
    print("Creating market_data table...")

    # First, check if the table exists
    try:
        supabase.table("market_data").select("id").limit(1).execute()
        print("market_data table already exists.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            # Table doesn't exist, create it
            try:
                # Create a sample record with all required fields to create the table
                sample_data = {
                    "id": str(uuid.uuid4()),
                    "sector": "Sample",
                    "country": "Sample",
                    "data_point": "Sample",
                    "value": "Sample",
                    "source": "Sample",
                    "date": "2023-01-01",
                    "custom_keyword": "Sample",
                    "metadata": json.dumps({}),
                    "created_at": datetime.now().isoformat()
                }

                supabase.table("market_data").insert(sample_data).execute()
                print("✅ market_data table created successfully.")
                return True
            except Exception as e:
                print(f"❌ Error creating market_data table: {e}")
                return False
        else:
            print(f"❌ Error checking market_data table: {e}")
            return False

def create_reports_table():
    """Create the reports table using the Supabase client."""
    print("Creating reports table...")

    # First, check if the table exists
    try:
        supabase.table("reports").select("id").limit(1).execute()
        print("reports table already exists.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            # Table doesn't exist, create it
            try:
                # Create a sample record with all required fields to create the table
                sample_data = {
                    "id": str(uuid.uuid4()),
                    "title": "Sample Report",
                    "sector": "Sample",
                    "country": "Sample",
                    "financial_product": "Sample",
                    "content": "Sample content",
                    "summary": "Sample summary",
                    "custom_keyword": "Sample",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "metadata": json.dumps({})
                }

                supabase.table("reports").insert(sample_data).execute()
                print("✅ reports table created successfully.")
                return True
            except Exception as e:
                print(f"❌ Error creating reports table: {e}")
                return False
        else:
            print(f"❌ Error checking reports table: {e}")
            return False

def create_queries_table():
    """Create the queries table using the Supabase client."""
    print("Creating queries table...")

    # First, check if the table exists
    try:
        supabase.table("queries").select("id").limit(1).execute()
        print("queries table already exists.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            # Table doesn't exist, create it
            try:
                # Create a sample record with all required fields to create the table
                sample_data = {
                    "id": str(uuid.uuid4()),
                    "query_text": "Sample query",
                    "query": "Sample query",
                    "entities": json.dumps({}),
                    "intent": "Sample intent",
                    "response": "Sample response",
                    "result": "Sample result",
                    "agent_type": "Sample agent",
                    "custom_keyword": "Sample",
                    "timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "metadata": json.dumps({})
                }

                supabase.table("queries").insert(sample_data).execute()
                print("✅ queries table created successfully.")
                return True
            except Exception as e:
                print(f"❌ Error creating queries table: {e}")
                return False
        else:
            print(f"❌ Error checking queries table: {e}")
            return False

def create_workflows_table():
    """Create the workflows table using the Supabase client."""
    print("Creating workflows table...")

    # First, check if the table exists
    try:
        supabase.table("workflows").select("id").limit(1).execute()
        print("workflows table already exists.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            # Table doesn't exist, create it
            try:
                # Create a sample record with all required fields to create the table
                sample_data = {
                    "id": str(uuid.uuid4()),
                    "name": "Sample Workflow",
                    "description": "Sample description",
                    "steps": json.dumps([]),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "status": "completed",
                    "metadata": json.dumps({})
                }

                supabase.table("workflows").insert(sample_data).execute()
                print("✅ workflows table created successfully.")
                return True
            except Exception as e:
                print(f"❌ Error creating workflows table: {e}")
                return False
        else:
            print(f"❌ Error checking workflows table: {e}")
            return False

def main():
    """Main function to create all tables."""
    print("Starting table creation...")

    # Create tables
    market_data_success = create_market_data_table()
    reports_success = create_reports_table()
    queries_success = create_queries_table()
    workflows_success = create_workflows_table()

    # Summary
    print("\nTable creation summary:")
    print(f"market_data: {'✅ Success' if market_data_success else '❌ Failed'}")
    print(f"reports: {'✅ Success' if reports_success else '❌ Failed'}")
    print(f"queries: {'✅ Success' if queries_success else '❌ Failed'}")
    print(f"workflows: {'✅ Success' if workflows_success else '❌ Failed'}")

    if market_data_success and reports_success and queries_success and workflows_success:
        print("\n✅ All tables created successfully.")
        print("Now run setup_supabase.py to populate the tables with sample data.")
    else:
        print("\n⚠️ Some tables could not be created.")
        print("Please check the error messages above and try again.")
        print("You may need to create the tables manually in the Supabase dashboard.")

if __name__ == "__main__":
    main()
