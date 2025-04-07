import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent
from supabase_service import SupabaseService

# Load environment variables
load_dotenv()

class QAAgent(BaseAgent):
    """
    Agent responsible for answering questions about Market reports stored in Supabase.
    """

    def __init__(self, openai_client: OpenAI = None):
        """
        Initializes the QAAgent.

        Args:
            openai_client (OpenAI, optional): An initialized OpenAI client instance.
        """
        super().__init__(
            name="QA Agent",
            description="Answers questions about Market reports",
            openai_client=openai_client,
        )
        # Store the desired model for this agent if needed for API calls
        self.model = "gpt-4o" # Or whichever model this agent should use

    def _get_system_prompt(self):
        """
        Get the system prompt for the QA Agent.

        Returns:
            str: The system prompt
        """
        return """
        You are an expert financial analyst specializing in equipment financing markets for Market.
        Your task is to answer questions about Market reports accurately and concisely.

        When answering questions:
        1. Base your answers on the report content provided
        2. Cite specific sections or data points from the report when relevant
        3. If the report doesn't contain information to answer a question, clearly state that
        4. Use a professional, helpful tone
        5. Provide concise but comprehensive answers

        Always maintain the context of equipment financing markets and Market' business focus.
        """ + " Base your answers ONLY on the provided context (reports and data). If the answer is not in the context, state that clearly."

    def process(self, query):
        """
        Process a question about Market reports and provide an answer.

        Args:
            query (dict): A dictionary containing the query parameters:
                - question (str): The user's question
                - sector (str, optional): The Market sector to filter reports
                - country (str, optional): The country to filter reports
                - financial_product (str, optional): The financial product to filter reports
                - custom_keyword (str, optional): Custom keyword to filter reports and data
                - report_id (str, optional): A specific report ID to query

        Returns:
            dict: The answer to the question
        """
        # Get parameters safely
        question = query.get('question')
        sector = query.get('sector') # Use .get() for sector
        country = query.get('country') # Use .get() for country
        financial_product = query.get('financial_product')
        custom_keyword = query.get('custom_keyword')

        if not question:
            return {"error": "Question is required."}

        # Retrieve relevant reports and data from Supabase based on available filters
        reports = SupabaseService.get_reports(
            sector=sector, # Pass potentially None value
            country=country, # Pass potentially None value
            financial_product=financial_product, # Pass potentially None value
            custom_keyword=custom_keyword # Pass potentially None value
        )
        market_data = SupabaseService.get_market_data(
            sector=sector, # Pass potentially None value
            country=country, # Pass potentially None value
            custom_keyword=custom_keyword # Pass potentially None value
        )

        # Debug print to check what data was retrieved
        print(f"Retrieved {len(reports)} reports and {len(market_data)} Market data points")
        if custom_keyword:
            print(f"Using custom keyword: {custom_keyword}")

        # Check if we have any data to work with
        if not reports and not market_data:
            error_message = "No Market data or reports found for the specified parameters"
            if custom_keyword:
                error_message += f" '{custom_keyword}'"
            return {
                "error": error_message,
                "query": query
            }

        # Format the reports for the model
        formatted_reports = self._format_reports_for_model(reports)

        # Format the Market data for the model
        formatted_market_data = self._format_market_data_for_model(market_data)

        # Combine all information for the model
        context = ""
        if formatted_market_data:
            context += f"# Market Data\n\n{formatted_market_data}\n\n"
        if formatted_reports:
            context += f"# Reports\n\n{formatted_reports}"

        if not context:
            error_message = "No Market data or reports found for the specified parameters"
            if custom_keyword:
                error_message += f" '{custom_keyword}'"
            return {
                "error": error_message,
                "query": query
            }

        # Prepare messages for the API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Question: {question}\n\nHere is the relevant Market information:\n\n{context}"}
        ]

        # Get response using the inherited helper method
        try:
            answer = self._call_openai_api(messages=messages, model=self.model, temperature=0.7)
        except Exception as e:
            # Handle API call error
            print(f"Error calling OpenAI API in QAAgent: {e}")
            return {"error": f"Failed to get answer from LLM: {e}", "query": query}

        # Store the query in Supabase
        entities = {
            "sector": sector,
            "country": country,
            "financial_product": financial_product,
            "custom_keyword": custom_keyword,
            "report_id": query.get('report_id')
        }

        stored_query = SupabaseService.store_query(
            query_text=question,
            entities=entities,
            intent="question_answering",
            response=answer,
            metadata={
                "reports_used": [r['id'] for r in reports],
                "market_data_used": [d['id'] for d in market_data]
            }
        )

        return {
            "query": query,
            "answer": answer,
            "reports_used": [{"id": r['id'], "title": r['title']} for r in reports],
            "market_data_used": len(market_data),
            "stored_query": stored_query
        }

    def _format_reports_for_model(self, reports):
        """
        Format reports for the model.

        Args:
            reports (list): List of report records

        Returns:
            str: Formatted reports
        """
        if not reports:
            return ""

        formatted_reports = ""

        for i, report in enumerate(reports):
            formatted_reports += f"## Report {i+1}: {report['title']}\n\n"

            # Add summary if available
            if 'summary' in report and report['summary']:
                formatted_reports += f"### Summary\n{report['summary']}\n\n"

            # Add content
            formatted_reports += f"### Content\n{report['content']}\n\n"

            # Add separator between reports
            if i < len(reports) - 1:
                formatted_reports += "---\n\n"

        return formatted_reports

    def _format_market_data_for_model(self, market_data):
        """
        Format Market data for the model.

        Args:
            market_data (list): List of Market data records

        Returns:
            str: Formatted Market data
        """
        if not market_data:
            return ""

        # Group data by sector and country
        grouped_data = {}
        for data in market_data:
            key = f"{data['sector']}_{data['country']}"
            if key not in grouped_data:
                grouped_data[key] = {
                    "sector": data['sector'],
                    "country": data['country'],
                    "custom_keyword": data.get('custom_keyword'),
                    "data_points": {}
                }

            # Add the data point
            grouped_data[key]["data_points"][data['data_point']] = {
                "value": data['value'],
                "source": data['source'],
                "date": data['date']
            }

        # Format the grouped data
        formatted_data = ""
        for key, group in grouped_data.items():
            title = f"{group['sector']} in {group['country']}"
            if group.get('custom_keyword'):
                title += f" - {group['custom_keyword']}"

            formatted_data += f"## {title}\n\n"

            for data_point, details in group['data_points'].items():
                formatted_data += f"### {data_point.replace('_', ' ').title()}\n"
                formatted_data += f"Value: {details['value']}\n"
                formatted_data += f"Source: {details['source']}\n"
                formatted_data += f"Date: {details['date']}\n\n"

            formatted_data += "---\n\n"

        return formatted_data
