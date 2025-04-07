import os
import json
import sys
from dotenv import load_dotenv
import openai

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent
from supabase_service import SupabaseService

# Load environment variables
load_dotenv()

class ReportGeneratorAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive reports based on Market data stored in Supabase.
    """

    def __init__(self):
        """Initialize the Report Generator Agent."""
        super().__init__(
            name="Report Generator",
            description="Generates comprehensive Market reports based on stored data",
            model="gpt-4o"  # Using a more powerful model for report generation
        )

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
        """

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
        # Retrieve Market data from Supabase
        market_data = SupabaseService.get_market_data(
            sector=query['sector'],
            country=query['country'],
            custom_keyword=query.get('custom_keyword')
        )

        if not market_data:
            return {
                "error": "No Market data found for the specified parameters",
                "query": query
            }

        # Format the data for the model
        formatted_data = self._format_data_for_model(market_data)

        # Format the query for the model
        report_title = f"Market Report: {query['sector']} Sector in {query['country']}"
        if 'financial_product' in query and query['financial_product']:
            report_title += f" - {query['financial_product']} Products"
        if 'custom_keyword' in query and query['custom_keyword']:
            report_title += f" ({query['custom_keyword']})"

        formatted_query = f"Generate a comprehensive Market report for the {query['sector']} sector in {query['country']}"
        if 'financial_product' in query and query['financial_product']:
            formatted_query += f", focusing on {query['financial_product']} products"
        if 'custom_keyword' in query and query['custom_keyword']:
            formatted_query += f", with specific emphasis on {query['custom_keyword']}"

        # Get response from the model
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"{formatted_query}\n\nHere is the Market data to use:\n\n{formatted_data}"}
            ],
            temperature=0.7
        )

        report_content = response.choices[0].message.content

        # Generate a summary of the report
        summary_response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using a smaller model for the summary
            messages=[
                {"role": "system", "content": "You are an expert at summarizing financial reports. Create a concise executive summary of the following Market report, highlighting the key findings and recommendations."},
                {"role": "user", "content": report_content}
            ],
            temperature=0.5,
            max_tokens=300
        )

        report_summary = summary_response.choices[0].message.content

        # Prepare metadata
        metadata = {"data_points": len(market_data)}
        if 'custom_keyword' in query and query['custom_keyword']:
            metadata['custom_keyword'] = query['custom_keyword']

        # Store the report in Supabase
        financial_product = query.get('financial_product', 'General')
        stored_report = SupabaseService.store_report(
            title=report_title,
            sector=query['sector'],
            country=query['country'],
            financial_product=financial_product,
            content=report_content,
            summary=report_summary,
            metadata=metadata
        )

        return {
            "query": query,
            "report": {
                "title": report_title,
                "content": report_content,
                "summary": report_summary
            },
            "stored_report": stored_report
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
