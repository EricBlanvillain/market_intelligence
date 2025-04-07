#!/usr/bin/env python3
"""
Setup script for creating Supabase tables for Market Intelligence platform.
This script creates the necessary tables in Supabase if they don't exist.
"""

import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

def create_supabase_client() -> Client:
    """Create and return a Supabase client."""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Successfully connected to Supabase at {SUPABASE_URL}")
        return client
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        sys.exit(1)

def create_table_if_not_exists(client, table_name, schema):
    """Create a table if it doesn't exist."""
    try:
        # Check if table exists by trying to select from it
        try:
            response = client.table(table_name).select("*").limit(1).execute()
            print(f"✅ Table '{table_name}' already exists")
            return True
        except Exception:
            # Table doesn't exist, create it
            print(f"Creating table '{table_name}'...")

            # For version 0.7.1, we need to use SQL to create tables
            # This is a simplified approach - in a production environment,
            # you would use migrations or a more robust schema management system

            # Convert schema to SQL
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")

            sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            );
            """

            # Execute SQL
            response = client.rpc("exec_sql", {"query": sql}).execute()
            print(f"✅ Table '{table_name}' created successfully")
            return True

    except Exception as e:
        print(f"❌ Error creating table '{table_name}': {e}")
        return False

def main():
    """Main function to set up Supabase tables."""
    client = create_supabase_client()

    # Define table schemas
    schemas = {
        "market_data": {
            "id": "text PRIMARY KEY",
            "sector": "text",
            "country": "text",
            "data_point": "text",
            "custom_keyword": "text",
            "content": "text",
            "date": "timestamp with time zone",
            "metadata": "jsonb",
            "created_at": "timestamp with time zone DEFAULT now()"
        },
        "reports": {
            "id": "text PRIMARY KEY",
            "sector": "text",
            "country": "text",
            "financial_product": "text",
            "custom_keyword": "text",
            "title": "text",
            "content": "text",
            "date": "timestamp with time zone",
            "metadata": "jsonb",
            "created_at": "timestamp with time zone DEFAULT now()"
        },
        "queries": {
            "id": "text PRIMARY KEY",
            "query_text": "text",
            "response": "text",
            "entities": "jsonb",
            "intent": "text",
            "agent_type": "text",
            "custom_keyword": "text",
            "timestamp": "timestamp with time zone",
            "created_at": "timestamp with time zone DEFAULT now()"
        }
    }

    # Create tables
    success_count = 0
    for table_name, schema in schemas.items():
        if create_table_if_not_exists(client, table_name, schema):
            success_count += 1

    print(f"\nSetup complete: {success_count}/{len(schemas)} tables created or verified.")

    # Insert test data if needed
    if "--with-test-data" in sys.argv:
        print("\nInserting test data...")
        # Add code to insert test data here
        pass

if __name__ == "__main__":
    main()
