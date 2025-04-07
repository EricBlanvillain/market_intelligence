import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# Global variable for the Supabase client
supabase = None

def initialize_supabase():
    """Initialize or reinitialize the Supabase client."""
    global supabase

    # Get credentials from environment
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("⚠️ Missing Supabase credentials. Using mock data for development.")
        supabase = None
        return None

    try:
        # Try to create the client with standard parameters
        try:
            supabase = create_client(supabase_url, supabase_key)
            print("✅ Successfully connected to Supabase.")
            return supabase
        except TypeError as e:
            # Check if the error is about the 'proxy' argument
            if "unexpected keyword argument 'proxy'" in str(e):
                print("⚠️ Detected older version of Supabase library, adjusting connection parameters...")
                # Try creating the client without the proxy parameter
                # This is a workaround for version compatibility issues
                import inspect
                valid_params = inspect.signature(create_client).parameters
                kwargs = {"supabase_url": supabase_url, "supabase_key": supabase_key}
                # Only include parameters that are valid for this version
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
                supabase = create_client(**filtered_kwargs)
                print("✅ Successfully connected to Supabase with adjusted parameters.")
                return supabase
            else:
                # If it's a different TypeError, re-raise it
                raise
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("⚠️ You may need to update your supabase-py library with: pip install --upgrade supabase")
        supabase = None
        return None

# Initialize on module load
supabase = initialize_supabase()

# In-memory storage for development/testing
mock_db = {
    "market_data": [],
    "reports": [],
    "queries": []
}

class SupabaseService:
    """
    Service for interacting with Supabase to store and retrieve data.
    """

    @staticmethod
    def get_client():
        """
        Get the Supabase client, reinitializing if necessary.

        Returns:
            Client: The Supabase client, or None if not available
        """
        global supabase
        if supabase is None:
            supabase = initialize_supabase()
        return supabase

    @staticmethod
    def store_market_data(sector, country, data_point, value, source, date=None, metadata=None, custom_keyword=None):
        """
        Store Market data in Supabase.

        Args:
            sector (str): The Market sector
            country (str): The country
            data_point (str): The specific data point (e.g., "market_size", "growth_rate")
            value (str): The value of the data point
            source (str): The source of the data
            date (str, optional): The date of the data. Defaults to current date.
            metadata (dict, optional): Additional metadata. Defaults to None.
            custom_keyword (str, optional): Custom keyword for more specific data. Defaults to None.

        Returns:
            dict: The stored data record
        """
        if date is None:
            date = datetime.now().isoformat()
        else:
            # Ensure date is in ISO format
            try:
                # If it's already a datetime object
                if isinstance(date, datetime):
                    date = date.isoformat()
                # If it's just a year (e.g., "2023")
                elif isinstance(date, str) and date.strip().isdigit() and len(date.strip()) == 4:
                    year = int(date.strip())
                    date = datetime(year, 1, 1).isoformat()
                # If it's a string but not in ISO format, try to parse it
                elif isinstance(date, str) and 'T' not in date:
                    date = datetime.fromisoformat(date.replace(' ', 'T')).isoformat()
            except Exception as e:
                # If parsing fails, use current date
                print(f"Warning: Could not parse date '{date}' ({str(e)}), using current date instead.")
                date = datetime.now().isoformat()

        if metadata is None:
            metadata = {}

        # If custom_keyword is provided directly, use it
        if custom_keyword:
            # Also add it to metadata for consistency
            if isinstance(metadata, dict):
                metadata['custom_keyword'] = custom_keyword
        # Otherwise, try to extract custom_keyword from metadata if it exists
        else:
            # Try to extract custom_keyword from metadata in different formats
            if isinstance(metadata, dict):
                custom_keyword = metadata.get('custom_keyword')
            elif isinstance(metadata, str):
                try:
                    metadata_dict = json.loads(metadata)
                    if isinstance(metadata_dict, dict):
                        custom_keyword = metadata_dict.get('custom_keyword')
                except:
                    pass

        # Ensure value is serializable
        if isinstance(value, (list, dict)):
            value = json.dumps(value)

        # Generate a unique ID
        record_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        data = {
            "id": record_id,
            "sector": sector,
            "country": country,
            "data_point": data_point,
            "value": value,
            "source": source,
            "date": date,
            "custom_keyword": custom_keyword,
            "metadata": json.dumps(metadata) if isinstance(metadata, dict) else metadata,
            "created_at": created_at
        }

        # Store in Supabase if available
        supabase_success = False
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print(f"Storing Market data in Supabase: {data_point} for {sector} in {country}")
                if custom_keyword:
                    print(f"With custom keyword: {custom_keyword}")

                response = supabase_client.table("market_data").insert(data).execute()
                if hasattr(response, 'data') and response.data:
                    print(f"✅ Successfully stored data in Supabase with ID: {record_id}")
                    supabase_success = True
                else:
                    print("❌ Failed to store data in Supabase - no data returned")
            except Exception as e:
                print(f"❌ Error storing data in Supabase: {e}")
        else:
            print("⚠️ Supabase client not available")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print(f"Storing Market data in mock database as fallback: {data_point} for {sector} in {country}")
            if custom_keyword:
                print(f"With custom keyword: {custom_keyword}")
            mock_db["market_data"].append(data)

        return data

    @staticmethod
    def get_market_data(sector=None, country=None, data_point=None, custom_keyword=None, limit=100):
        """
        Retrieve Market data from Supabase.

        Args:
            sector (str, optional): Filter by sector. Defaults to None.
            country (str, optional): Filter by country. Defaults to None.
            data_point (str, optional): Filter by data point. Defaults to None.
            custom_keyword (str, optional): Filter by custom keyword. Defaults to None.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list: List of Market data records
        """
        # Get data from both Supabase and mock database
        all_data = []
        supabase_success = False

        # First, try to get data from Supabase if available
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print("Retrieving data from Supabase...")
                # In version 0.7.1, we need to use a different approach for querying
                try:
                    # Start with a basic query
                    query = supabase_client.table("market_data").select("*")

                    # Apply filters - in version 0.7.1, we need to chain these differently
                    if sector:
                        query = query.filter("sector", "eq", sector)
                    if country:
                        query = query.filter("country", "eq", country)
                    if data_point:
                        query = query.filter("data_point", "eq", data_point)
                    if custom_keyword:
                        # For custom keyword, use ilike for case-insensitive partial match
                        # In version 0.7.1, we might need to use a different approach
                        try:
                            query = query.filter("custom_keyword", "ilike", f"%{custom_keyword}%")
                        except Exception as e:
                            print(f"Warning: Could not apply custom_keyword filter: {e}")
                            # Fallback to exact match if ilike is not supported
                            if custom_keyword:
                                query = query.filter("custom_keyword", "eq", custom_keyword)

                    # Execute the query - in version 0.7.1, limit might be handled differently
                    # or might need to be applied after fetching the data
                    response = query.execute()

                    if hasattr(response, 'data') and response.data:
                        # Apply limit manually if the API doesn't support it
                        data = response.data[:limit] if len(response.data) > limit else response.data
                        print(f"✅ Found {len(data)} records in Supabase")
                        all_data.extend(data)
                        supabase_success = True
                    else:
                        print("⚠️ No data found in Supabase")
                except Exception as e:
                    print(f"❌ Error with query builder: {e}")
                    # Try a simpler approach as fallback
                    try:
                        # Just get all data and filter manually
                        response = supabase_client.table("market_data").select("*").execute()
                        if hasattr(response, 'data') and response.data:
                            # Filter manually
                            filtered_data = response.data
                            if sector:
                                filtered_data = [d for d in filtered_data if d.get("sector") == sector]
                            if country:
                                filtered_data = [d for d in filtered_data if d.get("country") == country]
                            if data_point:
                                filtered_data = [d for d in filtered_data if d.get("data_point") == data_point]
                            if custom_keyword:
                                custom_keyword_lower = custom_keyword.lower()
                                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

                            # Apply limit
                            filtered_data = filtered_data[:limit]
                            print(f"✅ Found {len(filtered_data)} records in Supabase (manual filtering)")
                            all_data.extend(filtered_data)
                            supabase_success = True
                        else:
                            print("⚠️ No data found in Supabase")
                    except Exception as inner_e:
                        print(f"❌ Error with fallback query: {inner_e}")
            except Exception as e:
                print(f"❌ Error retrieving data from Supabase: {e}")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print("Retrieving data from mock database as fallback...")
            filtered_data = mock_db["market_data"]

            # Apply filters
            if sector:
                filtered_data = [d for d in filtered_data if d["sector"] == sector]
            if country:
                filtered_data = [d for d in filtered_data if d["country"] == country]
            if data_point:
                filtered_data = [d for d in filtered_data if d["data_point"] == data_point]
            if custom_keyword:
                # Make the custom keyword search case-insensitive
                custom_keyword_lower = custom_keyword.lower()
                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

            print(f"Found {len(filtered_data)} records in mock database")
            all_data.extend(filtered_data)

        # Remove duplicates based on id
        unique_ids = set()
        unique_data = []
        for item in all_data:
            if item['id'] not in unique_ids:
                unique_ids.add(item['id'])
                unique_data.append(item)

        print(f"Total unique records found: {len(unique_data)}")
        return unique_data[:limit]

    @staticmethod
    def store_report(title, sector, country, financial_product, content, summary=None, metadata=None, custom_keyword=None):
        """
        Store a report in Supabase.

        Args:
            title (str): The report title
            sector (str): The Market sector
            country (str): The country
            financial_product (str): The financial product
            content (str): The report content
            summary (str, optional): A summary of the report. Defaults to None.
            metadata (dict, optional): Additional metadata. Defaults to None.
            custom_keyword (str, optional): Custom keyword for more specific categorization. Defaults to None.

        Returns:
            dict: The stored report record
        """
        if metadata is None:
            metadata = {}

        # If custom_keyword is provided directly, use it
        if custom_keyword:
            # Also add it to metadata for consistency
            if isinstance(metadata, dict):
                metadata['custom_keyword'] = custom_keyword
        # Otherwise, try to extract custom_keyword from metadata if it exists
        elif isinstance(metadata, dict) and 'custom_keyword' in metadata:
            custom_keyword = metadata['custom_keyword']

        # Ensure dates are in ISO format
        now = datetime.now().isoformat()

        # Generate a unique ID
        record_id = str(uuid.uuid4())

        data = {
            "id": record_id,
            "title": title,
            "sector": sector,
            "country": country,
            "financial_product": financial_product,
            "content": content,
            "summary": summary,
            "custom_keyword": custom_keyword,
            "created_at": now,
            "updated_at": now,
            "metadata": json.dumps(metadata)
        }

        # Store in Supabase if available
        supabase_success = False
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print(f"Storing report in Supabase: {title}")
                if custom_keyword:
                    print(f"With custom keyword: {custom_keyword}")

                response = supabase_client.table("reports").insert(data).execute()
                if hasattr(response, 'data') and response.data:
                    print(f"✅ Successfully stored report in Supabase with ID: {record_id}")
                    supabase_success = True
                else:
                    print("❌ Failed to store report in Supabase - no data returned")
            except Exception as e:
                print(f"❌ Error storing report in Supabase: {e}")
        else:
            print("⚠️ Supabase client not available")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print(f"Storing report in mock database as fallback: {title}")
            if custom_keyword:
                print(f"With custom keyword: {custom_keyword}")
            mock_db["reports"].append(data)

        return data

    @staticmethod
    def get_reports(sector=None, country=None, financial_product=None, custom_keyword=None, limit=100):
        """
        Retrieve reports from Supabase.

        Args:
            sector (str, optional): Filter by sector. Defaults to None.
            country (str, optional): Filter by country. Defaults to None.
            financial_product (str, optional): Filter by financial product. Defaults to None.
            custom_keyword (str, optional): Filter by custom keyword. Defaults to None.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list: List of report records
        """
        # Get data from both Supabase and mock database
        all_data = []
        supabase_success = False

        # First, try to get data from Supabase if available
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print("Retrieving reports from Supabase...")
                # In version 0.7.1, we need to use a different approach for querying
                try:
                    # Start with a basic query
                    query = supabase_client.table("reports").select("*")

                    # Apply filters - in version 0.7.1, we need to chain these differently
                    if sector:
                        query = query.filter("sector", "eq", sector)
                    if country:
                        query = query.filter("country", "eq", country)
                    if financial_product:
                        query = query.filter("financial_product", "eq", financial_product)
                    if custom_keyword:
                        # For custom keyword, use ilike for case-insensitive partial match
                        # In version 0.7.1, we might need to use a different approach
                        try:
                            query = query.filter("custom_keyword", "ilike", f"%{custom_keyword}%")
                        except Exception as e:
                            print(f"Warning: Could not apply custom_keyword filter: {e}")
                            # Fallback to exact match if ilike is not supported
                            if custom_keyword:
                                query = query.filter("custom_keyword", "eq", custom_keyword)

                    # Execute the query - in version 0.7.1, limit might be handled differently
                    # or might need to be applied after fetching the data
                    response = query.execute()

                    if hasattr(response, 'data') and response.data:
                        # Apply limit manually if the API doesn't support it
                        data = response.data[:limit] if len(response.data) > limit else response.data
                        print(f"✅ Found {len(data)} reports in Supabase")
                        all_data.extend(data)
                        supabase_success = True
                    else:
                        print("⚠️ No reports found in Supabase")
                except Exception as e:
                    print(f"❌ Error with query builder: {e}")
                    # Try a simpler approach as fallback
                    try:
                        # Just get all data and filter manually
                        response = supabase_client.table("reports").select("*").execute()
                        if hasattr(response, 'data') and response.data:
                            # Filter manually
                            filtered_data = response.data
                            if sector:
                                filtered_data = [d for d in filtered_data if d.get("sector") == sector]
                            if country:
                                filtered_data = [d for d in filtered_data if d.get("country") == country]
                            if financial_product:
                                filtered_data = [d for d in filtered_data if d.get("financial_product") == financial_product]
                            if custom_keyword:
                                custom_keyword_lower = custom_keyword.lower()
                                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

                            # Apply limit
                            filtered_data = filtered_data[:limit]
                            print(f"✅ Found {len(filtered_data)} reports in Supabase (manual filtering)")
                            all_data.extend(filtered_data)
                            supabase_success = True
                        else:
                            print("⚠️ No reports found in Supabase")
                    except Exception as inner_e:
                        print(f"❌ Error with fallback query: {inner_e}")
            except Exception as e:
                print(f"❌ Error retrieving reports from Supabase: {e}")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print("Retrieving reports from mock database as fallback...")
            filtered_data = mock_db["reports"]

            # Apply filters
            if sector:
                filtered_data = [d for d in filtered_data if d["sector"] == sector]
            if country:
                filtered_data = [d for d in filtered_data if d["country"] == country]
            if financial_product:
                filtered_data = [d for d in filtered_data if d["financial_product"] == financial_product]
            if custom_keyword:
                # Make the custom keyword search case-insensitive
                custom_keyword_lower = custom_keyword.lower()
                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

            print(f"Found {len(filtered_data)} reports in mock database")
            all_data.extend(filtered_data)

        # Remove duplicates based on id
        unique_ids = set()
        unique_data = []
        for item in all_data:
            if item['id'] not in unique_ids:
                unique_ids.add(item['id'])
                unique_data.append(item)

        print(f"Total unique reports found: {len(unique_data)}")
        return unique_data[:limit]

    @staticmethod
    def store_query(query_text, entities, intent, response=None, metadata=None, agent_type=None):
        """
        Store a user query in Supabase.

        Args:
            query_text (str): The user's query text
            entities (dict): Extracted entities from the query
            intent (str): The detected intent
            response (str, optional): The response to the query. Defaults to None.
            metadata (dict, optional): Additional metadata. Defaults to None.
            agent_type (str, optional): The type of agent used. Defaults to None.

        Returns:
            dict: The stored query record
        """
        if metadata is None:
            metadata = {}

        # Extract custom_keyword from metadata if it exists
        custom_keyword = metadata.get('custom_keyword', None)

        # Also check in entities
        if not custom_keyword and isinstance(entities, dict) and 'custom_keyword' in entities:
            custom_keyword = entities['custom_keyword']

        # Ensure dates are in ISO format
        now = datetime.now().isoformat()

        # Generate a unique ID
        record_id = str(uuid.uuid4())

        data = {
            "id": record_id,
            "query_text": query_text,
            "query": query_text,  # For compatibility with sample data
            "entities": json.dumps(entities) if isinstance(entities, dict) else entities,
            "intent": intent,
            "response": response,
            "result": response,  # For compatibility with sample data
            "agent_type": agent_type,
            "custom_keyword": custom_keyword,
            "timestamp": now,
            "created_at": now,
            "metadata": json.dumps(metadata) if isinstance(metadata, dict) else metadata
        }

        # Store in Supabase if available
        supabase_success = False
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print(f"Storing query in Supabase: {query_text[:50]}...")
                if custom_keyword:
                    print(f"With custom keyword: {custom_keyword}")

                response = supabase_client.table("queries").insert(data).execute()
                if hasattr(response, 'data') and response.data:
                    print(f"✅ Successfully stored query in Supabase with ID: {record_id}")
                    supabase_success = True
                else:
                    print("❌ Failed to store query in Supabase - no data returned")
            except Exception as e:
                print(f"❌ Error storing query in Supabase: {e}")
        else:
            print("⚠️ Supabase client not available")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print(f"Storing query in mock database as fallback: {data['query_text'][:50]}...")
            if custom_keyword:
                print(f"With custom keyword: {custom_keyword}")
            mock_db["queries"].append(data)

        return data

    @staticmethod
    def get_queries(agent_type=None, custom_keyword=None, limit=100):
        """
        Retrieve queries from Supabase.

        Args:
            agent_type (str, optional): Filter by agent type. Defaults to None.
            custom_keyword (str, optional): Filter by custom keyword. Defaults to None.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list: List of query records
        """
        # Get data from both Supabase and mock database
        all_data = []
        supabase_success = False

        # First, try to get data from Supabase if available
        supabase_client = SupabaseService.get_client()
        if supabase_client:
            try:
                print("Retrieving queries from Supabase...")
                # In version 0.7.1, we need to use a different approach for querying
                try:
                    # Start with a basic query
                    query = supabase_client.table("queries").select("*")

                    # Apply filters - in version 0.7.1, we need to chain these differently
                    if agent_type:
                        query = query.filter("agent_type", "eq", agent_type)
                    if custom_keyword:
                        # For custom keyword, use ilike for case-insensitive partial match
                        # In version 0.7.1, we might need to use a different approach
                        try:
                            query = query.filter("custom_keyword", "ilike", f"%{custom_keyword}%")
                        except Exception as e:
                            print(f"Warning: Could not apply custom_keyword filter: {e}")
                            # Fallback to exact match if ilike is not supported
                            if custom_keyword:
                                query = query.filter("custom_keyword", "eq", custom_keyword)

                    # Execute the query - in version 0.7.1, limit might be handled differently
                    # or might need to be applied after fetching the data
                    response = query.execute()

                    if hasattr(response, 'data') and response.data:
                        # Apply limit manually if the API doesn't support it
                        data = response.data[:limit] if len(response.data) > limit else response.data
                        print(f"✅ Found {len(data)} queries in Supabase")
                        all_data.extend(data)
                        supabase_success = True
                    else:
                        print("⚠️ No queries found in Supabase")
                except Exception as e:
                    print(f"❌ Error with query builder: {e}")
                    # Try a simpler approach as fallback
                    try:
                        # Just get all data and filter manually
                        response = supabase_client.table("queries").select("*").execute()
                        if hasattr(response, 'data') and response.data:
                            # Filter manually
                            filtered_data = response.data
                            if agent_type:
                                filtered_data = [d for d in filtered_data if d.get("agent_type") == agent_type]
                            if custom_keyword:
                                custom_keyword_lower = custom_keyword.lower()
                                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

                            # Apply limit
                            filtered_data = filtered_data[:limit]
                            print(f"✅ Found {len(filtered_data)} queries in Supabase (manual filtering)")
                            all_data.extend(filtered_data)
                            supabase_success = True
                        else:
                            print("⚠️ No queries found in Supabase")
                    except Exception as inner_e:
                        print(f"❌ Error with fallback query: {inner_e}")
            except Exception as e:
                print(f"❌ Error retrieving queries from Supabase: {e}")

        # Only use mock database if Supabase failed or is not available
        if not supabase_success:
            print("Retrieving queries from mock database as fallback...")
            filtered_data = mock_db["queries"]

            # Apply filters
            if agent_type:
                filtered_data = [d for d in filtered_data if d.get("agent_type") == agent_type]
            if custom_keyword:
                # Make the custom keyword search case-insensitive
                custom_keyword_lower = custom_keyword.lower()
                filtered_data = [d for d in filtered_data if d.get("custom_keyword") and custom_keyword_lower in d.get("custom_keyword", "").lower()]

            print(f"Found {len(filtered_data)} queries in mock database")
            all_data.extend(filtered_data)

        # Remove duplicates based on id
        unique_ids = set()
        unique_data = []
        for item in all_data:
            if item['id'] not in unique_ids:
                unique_ids.add(item['id'])
                unique_data.append(item)

        print(f"Total unique queries found: {len(unique_data)}")
        return unique_data[:limit]

    @staticmethod
    def populate_sample_data():
        """
        Populate the mock database with sample data for testing purposes.
        This method can be called during development to ensure there's data to display.
        """
        # Only populate if the mock database is empty
        if not mock_db["market_data"] and not mock_db["reports"] and not mock_db["queries"]:
            print("Populating mock database with sample data...")

            # Get current date in ISO format
            current_date = datetime.now().isoformat()
            current_year = datetime.now().year

            # Sample Market data
            market_data_samples = [
                {
                    "sector": "Healthcare",
                    "country": "France",
                    "data_point": "market_size",
                    "value": "€45 billion",
                    "source": "French Healthcare Association",
                    "custom_keyword": "medical equipment",
                    "date": current_date
                },
                {
                    "sector": "Technology",
                    "country": "Germany",
                    "data_point": "growth_rate",
                    "value": "8.5% annually",
                    "source": f"German Tech Report {current_year}",
                    "custom_keyword": "software",
                    "date": current_date
                },
                {
                    "sector": "Transportation",
                    "country": "UK",
                    "data_point": "key_players",
                    "value": "British Airways, EasyJet, Virgin Atlantic",
                    "source": "UK Aviation Authority",
                    "custom_keyword": "airlines",
                    "date": current_date
                },
                {
                    "sector": "Industrial Equipment",
                    "country": "US",
                    "data_point": "market_trends",
                    "value": "Increasing automation and IoT integration",
                    "source": "US Manufacturing Report",
                    "custom_keyword": "automation",
                    "date": current_date
                },
                {
                    "sector": "Energy",
                    "country": "France",
                    "data_point": "regulatory_factors",
                    "value": f"New carbon tax implementation in {current_year}",
                    "source": "French Energy Ministry",
                    "custom_keyword": "renewable",
                    "date": current_date
                }
            ]

            for data in market_data_samples:
                SupabaseService.store_market_data(
                    sector=data["sector"],
                    country=data["country"],
                    data_point=data["data_point"],
                    value=data["value"],
                    source=data["source"],
                    date=data["date"],
                    metadata={"custom_keyword": data["custom_keyword"]}
                )

            # Sample reports
            report_samples = [
                {
                    "title": "Healthcare Equipment Market Analysis",
                    "sector": "Healthcare",
                    "country": "France",
                    "financial_product": "Leasing",
                    "content": "The French healthcare equipment Market has shown significant growth in the past year, with hospitals investing in new diagnostic equipment. Leasing options are becoming more popular due to budget constraints and the rapid pace of technological advancement.",
                    "summary": "Growth in French healthcare equipment leasing Market driven by technological advancements.",
                    "custom_keyword": "medical equipment"
                },
                {
                    "title": "Software Industry Financing Trends",
                    "sector": "Technology",
                    "country": "Germany",
                    "financial_product": "Loan",
                    "content": "German software companies are increasingly turning to specialized loans to fund their expansion. The Market is growing at 8.5% annually, with particular strength in enterprise software and cybersecurity solutions.",
                    "summary": "German software companies prefer specialized loans for expansion financing.",
                    "custom_keyword": "software"
                },
                {
                    "title": "UK Airline Fleet Renewal Strategies",
                    "sector": "Transportation",
                    "country": "UK",
                    "financial_product": "SALB (Sale and Lease Back)",
                    "content": "UK airlines are utilizing Sale and Lease Back arrangements to optimize their balance sheets while upgrading their fleets. This strategy has become particularly important in the post-pandemic recovery phase.",
                    "summary": "UK airlines leverage SALB arrangements for fleet modernization and balance sheet optimization.",
                    "custom_keyword": "airlines"
                }
            ]

            for report in report_samples:
                SupabaseService.store_report(
                    title=report["title"],
                    sector=report["sector"],
                    country=report["country"],
                    financial_product=report["financial_product"],
                    content=report["content"],
                    summary=report["summary"],
                    metadata={"custom_keyword": report["custom_keyword"]}
                )

            # Sample queries
            query_samples = [
                {
                    "query_text": "What is the Market size for medical equipment in France?",
                    "agent_type": "data_collection",
                    "result": "The Market size for medical equipment in France is approximately €45 billion according to the French Healthcare Association.",
                    "custom_keyword": "medical equipment"
                },
                {
                    "query_text": "Generate a report on software financing options in Germany",
                    "agent_type": "report_generation",
                    "result": "Report generated on software financing options in Germany. The Market is growing at 8.5% annually with specialized loans being the preferred financing method.",
                    "custom_keyword": "software"
                },
                {
                    "query_text": "Create a workflow for analyzing airline leasing opportunities in the UK",
                    "agent_type": "workflow_builder",
                    "result": "Workflow created for analyzing airline leasing opportunities in the UK, focusing on SALB arrangements which are popular for fleet modernization.",
                    "custom_keyword": "airlines"
                }
            ]

            for query in query_samples:
                SupabaseService.store_query(
                    query_text=query["query_text"],
                    entities={},
                    intent=query["agent_type"],
                    response=query["result"],
                    agent_type=query["agent_type"],
                    metadata={"custom_keyword": query["custom_keyword"]}
                )

            print(f"Sample data populated: {len(mock_db['market_data'])} Market data entries, {len(mock_db['reports'])} reports, {len(mock_db['queries'])} queries")

        return mock_db
