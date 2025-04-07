import os
import json
import sys
from dotenv import load_dotenv
from ..base_agent import BaseAgent
from supabase_service import SupabaseService
from openai import OpenAI

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

class ReportGeneratorAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive reports based on Market data stored in Supabase.
    """

    def __init__(self, openai_client: OpenAI = None):
        """
        Initializes the ReportGeneratorAgent.

        Args:
            openai_client (OpenAI, optional): An initialized OpenAI client instance.
        """
        super().__init__(
            name="Report Generator Agent",
            description="Generates comprehensive Market reports by synthesizing data retrieved from the database.",
            openai_client=openai_client
        )
        # Store the desired model for this agent
        self.model = "gpt-4o" # Or choose a suitable model for report generation

    def _get_system_prompt(self):
        """
        Get the system prompt for the Report Generator Agent.

        Returns:
            str: The system prompt
        """
        return """
        You are an expert financial analyst specializing in equipment financing markets for Market.
        Your task is to generate comprehensive, well-structured Market reports based on the data provided.

        Your reports should include:
        1. Executive Summary: A concise overview of the key findings
        2. Market Overview: Size, growth rate, and key trends
        3. Competitive Landscape: Key players and their Market positions
        4. Regulatory Environment: Relevant regulations and their impact
        5. Economic Factors: Economic indicators affecting the Market
        6. Opportunities and Challenges: Potential opportunities and challenges in the Market
        7. Recommendations: Strategic recommendations for Market

        For each section, cite the specific data points used and their sources.
        Use a professional, analytical tone throughout the report.
        Format the report in a clear, structured manner with headings and subheadings.
        """ + " Structure the report clearly with sections like Executive Summary, Market Overview, Key Trends, Competitive Landscape, and Conclusion."

    def process(self, query):
        """
        Process a report generation query and store the results in Supabase.

        Args:
            query (dict): A dictionary containing the query parameters:
                - sector (str): The Market sector
                - country (str): The country
                - financial_product (str, optional): The financial product

        Returns:
            dict: The generated report
        """
        # Get parameters safely
        sector = query.get('sector')
        country = query.get('country') # Use .get() for country
        financial_product = query.get('financial_product')
        custom_keyword = query.get('custom_keyword')

        if not sector:
            return {"error": "Sector is required for report generation."}
        # Removed check requiring country

        # Retrieve Market data from Supabase - Attempt 1 (with custom_keyword)
        print(f"Attempting to retrieve data for Sector: {sector}, Country: {country}, Keyword: {custom_keyword}")
        market_data = SupabaseService.get_market_data(
            sector=sector,
            country=country, # Pass country (can be None)
            custom_keyword=custom_keyword # Pass custom_keyword (can be None)
        )

        # Attempt 2 (fallback without custom_keyword if Attempt 1 failed and keyword was present)
        if not market_data and custom_keyword:
            print(f"⚠️ No data found with keyword '{custom_keyword}'. Trying fallback without keyword.")
            market_data = SupabaseService.get_market_data(
                sector=sector,
                country=country, # Pass country (can be None)
                custom_keyword=None # Fallback retrieval
            )

        # Final check if data exists
        if not market_data:
            # Ensure the error is nested under 'result' for consistent handling
            return {
                "query": query,
                "result": {
                     "error": "No Market data found for the specified parameters, even after fallback."
                }
            }

        # Format the data for the model
        formatted_data = self._format_data_for_model(market_data)

        # Format the query for the model
        report_title = f"Market Report: {sector} Sector"
        if country:
            report_title += f" in {country}"
        if financial_product:
            report_title += f" - {financial_product} Products"
        if custom_keyword:
            report_title += f" ({custom_keyword})"

        formatted_query = f"Generate a comprehensive Market report for the {sector} sector"
        if country:
            formatted_query += f" in {country}"
        if financial_product:
            formatted_query += f", focusing on {financial_product} products"
        if custom_keyword:
            formatted_query += f", with specific emphasis on {custom_keyword}"

        # Prepare messages for main report generation
        report_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{formatted_query}\n\nHere is the Market data to use:\n\n{formatted_data}"}
        ]

        # Get response using the inherited helper method
        try:
            report_content = self._call_openai_api(messages=report_messages, model=self.model, temperature=0.7)
        except Exception as e:
            print(f"Error calling OpenAI API for report content: {e}")
            # Nest the error under 'result' for consistent UI handling
            return {
                "query": query,
                "result": {
                    "error": f"Failed to generate report content: {e}"
                }
            }

        # Prepare messages for summary generation
        summary_messages = [
            {"role": "system", "content": "You are an expert at summarizing financial reports. Create a concise executive summary of the following Market report, highlighting the key findings and recommendations."},
            {"role": "user", "content": report_content}
        ]

        # Generate a summary using the helper method
        try:
            # Using a smaller model for the summary
            report_summary = self._call_openai_api(messages=summary_messages, model="gpt-4o-mini", temperature=0.5)
        except Exception as e:
            print(f"Error calling OpenAI API for report summary: {e}")
            # Proceed without summary or return error?
            report_summary = "Error generating summary."

        # Prepare metadata
        metadata = {"data_points": len(market_data)}
        if custom_keyword:
            metadata['custom_keyword'] = custom_keyword

        # Store the report in Supabase
        financial_product_to_store = financial_product if financial_product else 'General'
        try:
            stored_report = SupabaseService.store_report(
                title=report_title,
                sector=sector, # sector is required
                country=country, # Pass country (can be None)
                financial_product=financial_product_to_store,
                content=report_content,
                summary=report_summary,
                metadata=metadata,
                custom_keyword=custom_keyword # Pass custom_keyword (can be None)
            )
        except Exception as e:
            print(f"Error storing report: {e}")
            stored_report = {"error": f"Failed to store report: {e}"}

        # Return results nested under 'result' key for consistency
        return {
            "query": query,
            "result": { # Nest the report details here
                "report": {
                    "title": report_title,
                    "content": report_content,
                    "summary": report_summary
                },
                "stored_report": stored_report # Include storage status/info
            }
        }

    def _format_data_for_model(self, market_data):
        """
        Format Market data for the model.

        Args:
            market_data (list): List of Market data records

        Returns:
            str: Formatted Market data
        """
        formatted_data = ""

        # Group data by data_point
        data_by_point = {}
        for item in market_data:
            data_point = item['data_point']
            if data_point not in data_by_point:
                data_by_point[data_point] = []
            data_by_point[data_point].append(item)

        # Format each data point
        for data_point, items in data_by_point.items():
            formatted_data += f"## {data_point.replace('_', ' ').title()}\n\n"

            for item in items:
                formatted_data += f"- Value: {item['value']}\n"
                formatted_data += f"  Source: {item['source']}\n"
                formatted_data += f"  Date: {item['date']}\n\n"

        return formatted_data
