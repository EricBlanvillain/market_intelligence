import os
import json
import sys
from dotenv import load_dotenv
from ..base_agent import BaseAgent
from supabase_service import SupabaseService
from openai import OpenAI
from datetime import datetime

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting Market data and storing it in Supabase.
    Uses the gpt-4o-search-preview model to search the web for up-to-date information.
    """

    def __init__(self, openai_client: OpenAI = None):
        """
        Initializes the DataCollectorAgent.

        Args:
            openai_client (OpenAI, optional): An initialized OpenAI client instance.
        """
        super().__init__(
            name="Data Collector",
            description="Collects Market data from the web and stores it in Supabase",
            openai_client=openai_client
        )
        # Store the desired model for this agent if needed for API calls
        self.model = "gpt-4o" # Or whichever model this agent should use

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
        """ + " Focus on finding quantifiable data points or key qualitative insights."

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
        # Get parameters safely
        sector = query.get('sector')
        country = query.get('country') # Use .get() for country
        financial_product = query.get('financial_product')
        custom_keyword = query.get('custom_keyword')

        if not sector:
            return {"error": "Sector is required for data collection."}
        # Removed check requiring country

        # Format query for the model with strict JSON instructions
        formatted_query = f"""
Collect key Market data points (e.g., market_size, growth_rate, key_players, market_trends) for the {sector} sector{f' in {country}' if country else ''}{f', focusing on {financial_product} products' if financial_product else ''}{f', specifically regarding {custom_keyword}' if custom_keyword else ''}.

Your response MUST be ONLY a valid JSON list of objects. Each object should represent a data point and have the following keys: "name" (string, e.g., "market_size"), "value" (string), "source" (string, cite your source), and "date" (string, YYYY-MM-DD or year).

DO NOT include any introductory text, explanations, apologies, or markdown formatting like ```json. ONLY output the raw JSON list starting with [ and ending with ].

Example of the exact expected format:
[
  {{
    "name": "market_size",
    "value": "€5.2 billion",
    "source": "Example Report 2024",
    "date": "2024"
  }},
  {{
    "name": "growth_rate",
    "value": "4.7% CAGR",
    "source": "Market Analysis Inc.",
    "date": "2024-01-15"
  }}
]
"""

        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": formatted_query}
            ]

            # Get response using the inherited helper method
            response_text = self._call_openai_api(messages=messages, model=self.model, temperature=0.1) # Lower temperature might help consistency

            # Attempt to find JSON within potential markdown fences (common LLM mistake)
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("```"):
                 response_text = response_text.strip()[3:-3].strip()

            # Check if the response is empty
            if not response_text:
                print("⚠️ No content in response, using mock data")
                raise ValueError("Received empty response from LLM")

            print(f"Cleaned response from OpenAI: {response_text[:500]}...")

            # Parse the response to extract structured data
            try:
                structured_data = json.loads(response_text)
                if not isinstance(structured_data, list): # Ensure it's a list as requested
                    print("⚠️ LLM response was valid JSON but not a list. Attempting recovery or using mock data.")
                    # Handle non-list JSON if possible, or raise error
                    raise ValueError("LLM returned valid JSON but not the expected list format.")
            except json.JSONDecodeError as json_err:
                print(f"Error parsing response: {json_err}")
                print(f"Invalid JSON received: {response_text}")
                return {"error": f"Error parsing response from LLM. Invalid JSON received.", "raw_response": response_text}
            except ValueError as val_err:
                 # Handle the non-list JSON case
                 return {"error": str(val_err), "raw_response": response_text}

        except Exception as e:
            print(f"Error calling OpenAI API or processing response: {e}")
            # Create mock data for development/testing
            current_year = datetime.now().year
            response_text = json.dumps([
                {
                    "name": "market_size",
                    "value": f"€5.2 billion for {sector} in {country}",
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
            return {"error": f"API call or initial processing failed: {e}", "raw_response": response_text}

        # Store the collected data in Supabase
        stored_data = []
        for data_point in structured_data:
            # Ensure required fields are present
            if 'name' in data_point and 'value' in data_point:
                try:
                    stored_item = SupabaseService.store_market_data(
                        sector=sector, # sector is required
                        country=country, # Pass country (can be None)
                        data_point=data_point['name'],
                        value=data_point['value'],
                        source=data_point.get('source', 'LLM Response'),
                        date=data_point.get('date', datetime.now().strftime("%Y-%m-%d")),
                        custom_keyword=custom_keyword # Pass custom_keyword (can be None)
                    )
                    stored_data.append(stored_item)
                except Exception as e:
                    print(f"Error storing data point {data_point.get('name')}: {e}")
                    # Optionally add error info to results

        return {
            "query": query,
            "collected_data": stored_data # Return the successfully stored items
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
