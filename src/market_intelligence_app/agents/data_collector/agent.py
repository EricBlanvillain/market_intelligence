import os
import json
import sys
from dotenv import load_dotenv
import openai
from datetime import datetime

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent
from supabase_service import SupabaseService

# Load environment variables
load_dotenv()

class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting Market data and storing it in Supabase.
    Uses the gpt-4o-search-preview model to search the web for up-to-date information.
    """

    def __init__(self):
        """Initialize the Data Collector Agent."""
        super().__init__(
            name="Data Collector",
            description="Collects Market data from the web and stores it in Supabase",
            model="gpt-4o"  # Using a standard model since web search is not working correctly
        )

    def _get_system_prompt(self):
        """
        Get the system prompt for the Data Collector Agent.

        Returns:
            str: The system prompt
        """
        return """
        You are an expert financial analyst specializing in equipment financing markets for Market.
        Your task is to collect accurate and up-to-date Market data.

        When collecting data, focus on the following key data points:
        1. Market size (in EUR or USD)
        2. Growth rate (annual percentage)
        3. Key players (top companies in the Market)
        4. Market trends (emerging trends in the sector)
        5. Regulatory factors (relevant regulations affecting the Market)
        6. Economic indicators (relevant economic factors)

        For each data point, provide:
        - The specific value or information
        - The source of the information
        - The date of the information

        Format your response as structured data that can be easily parsed and stored in a database.

        IMPORTANT: Your response MUST be in JSON format with an array of data points. Each data point should have 'name', 'value', 'source', and 'date' fields.
        Example format:
        [
            {
                "name": "market_size",
                "value": "€5.2 billion",
                "source": "Source Name",
                "date": "2023"
            },
            {
                "name": "growth_rate",
                "value": "4.7% annual growth",
                "source": "Source Name",
                "date": "2023"
            }
        ]
        """

    def process(self, query):
        """
        Process a data collection query and store the results in Supabase.

        Args:
            query (dict): A dictionary containing the query parameters:
                - sector (str): The Market sector
                - country (str): The country
                - financial_product (str, optional): The financial product
                - custom_keyword (str, optional): Custom keyword for more specific data

        Returns:
            dict: The collected data
        """
        # Format the query for the model
        formatted_query = f"Collect Market data for the {query['sector']} sector in {query['country']}"
        if 'financial_product' in query and query['financial_product']:
            formatted_query += f", focusing on {query['financial_product']} products"
        if 'custom_keyword' in query and query['custom_keyword']:
            formatted_query += f", with specific emphasis on {query['custom_keyword']}"
            print(f"Including custom keyword in query: {query['custom_keyword']}")

        try:
            # Get response from the model without web search for now
            # Web search functionality requires additional setup
            print(f"Sending query to OpenAI: {formatted_query}")
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": formatted_query}
                ],
                temperature=0.7
            )

            # For development/testing, create mock data if the API call fails
            if not hasattr(response.choices[0].message, 'content') or not response.choices[0].message.content:
                print("⚠️ No content in response, using mock data")
                current_year = datetime.now().year
                response_text = json.dumps([
                    {
                        "name": "market_size",
                        "value": f"€5.2 billion for {query['sector']} in {query['country']}",
                        "source": "Mock Data Source",
                        "date": f"{current_year}"
                    },
                    {
                        "name": "growth_rate",
                        "value": "4.7% annual growth",
                        "source": "Mock Data Source",
                        "date": f"{current_year}"
                    }
                ])
            else:
                response_text = response.choices[0].message.content
                print(f"Response from OpenAI: {response_text[:500]}...")

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Create mock data for development/testing
            current_year = datetime.now().year
            response_text = json.dumps([
                {
                    "name": "market_size",
                    "value": f"€5.2 billion for {query['sector']} in {query['country']}",
                    "source": "Mock Data Source",
                    "date": f"{current_year}"
                },
                {
                    "name": "growth_rate",
                    "value": "4.7% annual growth",
                    "source": "Mock Data Source",
                    "date": f"{current_year}"
                }
            ])

        # Parse the response to extract structured data
        print(f"Parsing response...")
        data_points = self._parse_response(response_text, query['sector'], query['country'])
        print(f"Parsed {len(data_points)} data points")

        # Prepare metadata with custom keyword if available
        metadata = {}
        if 'custom_keyword' in query and query['custom_keyword']:
            metadata['custom_keyword'] = query['custom_keyword']
            print(f"Adding custom_keyword to metadata: {query['custom_keyword']}")

        # Store the data points in Supabase
        stored_data = []
        for data_point in data_points:
            # Merge metadata with any existing metadata in the data point
            data_point_metadata = data_point.get('metadata', {})
            data_point_metadata.update(metadata)

            # Debug print to verify metadata
            if 'custom_keyword' in data_point_metadata:
                print(f"Storing data point with custom_keyword in metadata: {data_point_metadata['custom_keyword']}")

            # Ensure custom_keyword is passed directly as well for redundancy
            custom_keyword = query.get('custom_keyword', None)
            if not custom_keyword and 'custom_keyword' in data_point_metadata:
                custom_keyword = data_point_metadata['custom_keyword']

            result = SupabaseService.store_market_data(
                sector=query['sector'],
                country=query['country'],
                data_point=data_point['name'],
                value=data_point['value'],
                source=data_point['source'],
                date=data_point.get('date'),
                metadata=data_point_metadata,
                custom_keyword=custom_keyword  # Pass custom_keyword directly
            )
            if result:
                stored_data.append(result)

        return {
            "query": query,
            "collected_data": data_points,
            "stored_data": stored_data
        }

    def _parse_response(self, response_text, sector, country):
        """
        Parse the response from the model to extract structured data points.

        Args:
            response_text (str): The response from the model
            sector (str): The Market sector
            country (str): The country

        Returns:
            list: A list of data points
        """
        # First, try to parse as JSON if the response is already structured
        try:
            data = json.loads(response_text)
            if isinstance(data, list):
                # Ensure each data point has proper date formatting
                for item in data:
                    if 'date' in item:
                        item['date'] = self._format_date(item['date'])
                return data
            elif isinstance(data, dict) and 'data_points' in data:
                # Ensure each data point has proper date formatting
                for item in data['data_points']:
                    if 'date' in item:
                        item['date'] = self._format_date(item['date'])
                return data['data_points']
        except json.JSONDecodeError:
            pass

        # If not JSON, try to extract structured data from the text
        # This is a very simplified approach - you would want more robust parsing
        data_points = []

        # Look for common data point patterns
        patterns = [
            "Market size", "Growth rate", "Key players",
            "Market trends", "Regulatory factors", "Economic indicators"
        ]

        lines = response_text.split('\n')
        current_data_point = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line starts a new data point
            for pattern in patterns:
                if line.startswith(pattern) or pattern in line[:30]:
                    if current_data_point:
                        data_points.append(current_data_point)

                    current_data_point = {
                        "name": pattern.lower().replace(" ", "_"),
                        "value": line.split(":", 1)[1].strip() if ":" in line else "",
                        "source": "",
                        "date": "",
                        "metadata": {}
                    }
                    break

            # If we're in a data point and this line contains a source
            if current_data_point and ("source:" in line.lower() or "http" in line.lower()):
                current_data_point["source"] = line.split(":", 1)[1].strip() if ":" in line else line

            # If we're in a data point and this line contains a date
            if current_data_point and ("date:" in line.lower() or "20" in line):
                # Extract date with better handling for year-only values
                date_value = line.split(":", 1)[1].strip() if ":" in line else line
                current_data_point["date"] = self._format_date(date_value)

        # Add the last data point if there is one
        if current_data_point:
            data_points.append(current_data_point)

        return data_points

    def _format_date(self, date_value):
        """
        Format a date value to ensure it's in a consistent format.

        Args:
            date_value (str): The date value to format

        Returns:
            str: The formatted date
        """
        if not date_value:
            return datetime.now().isoformat()

        # If it's just a year (e.g., "2023"), format it properly
        if str(date_value).strip().isdigit() and len(str(date_value).strip()) == 4:
            return f"{date_value.strip()}-01-01"

        # Try to extract year from strings like "2023" or "in 2023"
        import re
        year_match = re.search(r'\b(20\d{2})\b', str(date_value))
        if year_match:
            return f"{year_match.group(1)}-01-01"

        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value.isoformat()

        # Try to parse various date formats
        try:
            from dateutil import parser
            parsed_date = parser.parse(str(date_value), fuzzy=True)
            return parsed_date.isoformat()
        except:
            # If all parsing fails, use current date
            return datetime.now().isoformat()
