import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")

# Function to execute SQL commands
def execute_sql(sql_command):
    """Execute a SQL command using the Supabase REST API."""
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Endpoint for executing SQL
    endpoint = f"{supabase_url}/rest/v1/rpc/exec_sql"

    # Payload with the SQL command
    payload = {
        "query": sql_command
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"✅ SQL command executed successfully.")
            return True
        else:
            print(f"❌ Error executing SQL command: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception executing SQL command: {e}")
        return False

# Read the SQL file
def read_sql_file(file_path):
    """Read SQL commands from a file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        return None

# Split SQL commands
def split_sql_commands(sql_content):
    """Split SQL content into individual commands."""
    # Split by semicolon, but ignore semicolons inside quotes
    commands = []
    current_command = ""
    in_quotes = False
    quote_char = None

    for char in sql_content:
        if char in ["'", '"'] and (not in_quotes or quote_char == char):
            in_quotes = not in_quotes
            if in_quotes:
                quote_char = char
            else:
                quote_char = None

        current_command += char

        if char == ";" and not in_quotes:
            commands.append(current_command.strip())
            current_command = ""

    # Add the last command if it doesn't end with a semicolon
    if current_command.strip():
        commands.append(current_command.strip())

    return commands

# Main function
def main():
    """Main function to execute SQL setup."""
    print("Starting SQL setup...")

    # Read the SQL file
    sql_content = read_sql_file("create_tables.sql")
    if not sql_content:
        return

    # Split into commands
    commands = split_sql_commands(sql_content)
    print(f"Found {len(commands)} SQL commands to execute.")

    # Execute each command
    success_count = 0
    for i, command in enumerate(commands):
        if command and not command.startswith("--"):  # Skip comments
            print(f"\nExecuting command {i+1}/{len(commands)}:")
            print(f"{command[:100]}..." if len(command) > 100 else command)

            if execute_sql(command):
                success_count += 1

    print(f"\nSQL setup completed. {success_count}/{len(commands)} commands executed successfully.")
    print("Now run setup_supabase.py to populate the tables with sample data.")

if __name__ == "__main__":
    main()
