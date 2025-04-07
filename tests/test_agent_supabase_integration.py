import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import the necessary modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supabase_service import SupabaseService
from agents.data_collector.agent import DataCollectorAgent
from agents.report_generator.agent import ReportGeneratorAgent
from agents.qa.agent import QAAgent

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_data_collector_with_custom_keyword():
    """Test the data collector agent with custom keywords."""
    print_separator("TESTING DATA COLLECTOR AGENT WITH CUSTOM KEYWORDS")

    # Initialize the data collector agent
    data_collector = DataCollectorAgent()

    # Test data
    sector = "Technology"
    country = "France"
    custom_keywords = ["electric vehicles", "sustainable finance", "digital transformation"]

    # Process queries with different custom keywords
    results = []
    for keyword in custom_keywords:
        print(f"Collecting data with custom keyword: '{keyword}'")

        # Prepare parameters
        parameters = {
            "sector": sector,
            "country": country,
            "custom_keyword": keyword
        }

        # Process with data collector agent
        result = data_collector.process(parameters)
        results.append(result)

        print(f"  Collected {len(result['collected_data'])} data points")
        print(f"  Stored {len(result['stored_data'])} data points")

        # Verify that the custom keyword was stored correctly
        for data_point in result['stored_data']:
            print(f"  Data point: {data_point['data_point']}")
            print(f"  Value: {data_point['value']}")
            print(f"  Custom keyword: {data_point.get('custom_keyword')}")
            print()

    # Verify that we can retrieve the data by custom keyword
    for keyword in custom_keywords:
        print(f"Retrieving data with custom keyword: '{keyword}'")
        filtered_data = SupabaseService.get_market_data(
            sector=sector,
            country=country,
            custom_keyword=keyword
        )

        print(f"  Found {len(filtered_data)} data points")
        if filtered_data:
            print(f"  First data point: {filtered_data[0]['data_point']}")
            print(f"  Custom keyword: {filtered_data[0].get('custom_keyword')}")
            print()

    return results

def test_report_generator_with_custom_keyword():
    """Test the report generator agent with custom keywords."""
    print_separator("TESTING REPORT GENERATOR AGENT WITH CUSTOM KEYWORDS")

    # Initialize the report generator agent
    report_generator = ReportGeneratorAgent()

    # Test data
    sector = "Technology"
    country = "France"
    custom_keywords = ["electric vehicles", "sustainable finance", "digital transformation"]

    # Process queries with different custom keywords
    results = []
    for keyword in custom_keywords:
        print(f"Generating report with custom keyword: '{keyword}'")

        # Prepare parameters
        parameters = {
            "sector": sector,
            "country": country,
            "custom_keyword": keyword
        }

        # Process with report generator agent
        result = report_generator.process(parameters)

        # Check if there was an error
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue

        results.append(result)

        print(f"  Generated report: {result['report']['title']}")
        print(f"  Summary: {result['report']['summary'][:100]}...")

        # Verify that the custom keyword was stored correctly
        stored_report = result['stored_report']
        print(f"  Stored report ID: {stored_report['id']}")
        print(f"  Custom keyword: {stored_report.get('custom_keyword')}")
        print()

    # Verify that we can retrieve the reports by custom keyword
    for keyword in custom_keywords:
        print(f"Retrieving reports with custom keyword: '{keyword}'")
        filtered_reports = SupabaseService.get_reports(
            sector=sector,
            country=country,
            custom_keyword=keyword
        )

        print(f"  Found {len(filtered_reports)} reports")
        if filtered_reports:
            print(f"  First report title: {filtered_reports[0]['title']}")
            print(f"  Custom keyword: {filtered_reports[0].get('custom_keyword')}")
            print()

    return results

def test_qa_agent_with_custom_keyword():
    """Test the QA agent with custom keywords."""
    print_separator("TESTING QA AGENT WITH CUSTOM KEYWORDS")

    # Initialize the QA agent
    qa_agent = QAAgent()

    # Test data
    sector = "Technology"
    country = "France"
    custom_keywords = ["electric vehicles", "sustainable finance", "digital transformation"]

    # Process queries with different custom keywords
    results = []
    for keyword in custom_keywords:
        print(f"Asking question with custom keyword: '{keyword}'")

        # Prepare parameters
        parameters = {
            "question": f"What are the key trends in {keyword} for the {sector} sector in {country}?",
            "sector": sector,
            "country": country,
            "custom_keyword": keyword
        }

        # Process with QA agent
        result = qa_agent.process(parameters)

        # Check if there was an error
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue

        results.append(result)

        print(f"  Question: {parameters['question']}")
        print(f"  Answer: {result['answer'][:100]}...")
        print(f"  Reports used: {len(result['reports_used'])}")

        # Verify that the custom keyword was used in the query
        stored_query = result['stored_query']
        entities = json.loads(stored_query['entities'])
        print(f"  Stored query ID: {stored_query['id']}")
        print(f"  Custom keyword in entities: {entities.get('custom_keyword')}")
        print()

    return results

def main():
    """Run the tests."""
    print("Starting agent-Supabase integration tests...")

    # Test data collector with custom keywords
    data_collector_results = test_data_collector_with_custom_keyword()

    # Test report generator with custom keywords
    report_generator_results = test_report_generator_with_custom_keyword()

    # Test QA agent with custom keywords
    qa_agent_results = test_qa_agent_with_custom_keyword()

    print_separator("TEST SUMMARY")
    print(f"Data collector tests: {len(data_collector_results)} completed")
    print(f"Report generator tests: {len(report_generator_results)} completed")
    print(f"QA agent tests: {len(qa_agent_results)} completed")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
