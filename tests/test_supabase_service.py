import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import the Supabase service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supabase_service import SupabaseService

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_market_data_with_custom_keyword():
    """Test storing and retrieving Market data with custom keywords."""
    print_separator("TESTING MARKET DATA WITH CUSTOM KEYWORDS")

    # Test data
    sector = "Technology"
    country = "France"
    custom_keywords = ["electric vehicles", "sustainable finance", "digital transformation"]

    # Store Market data with different custom keywords
    stored_data_ids = []
    for i, keyword in enumerate(custom_keywords):
        print(f"Storing Market data with custom keyword: '{keyword}'")

        # Create metadata with custom keyword
        metadata = {"custom_keyword": keyword}

        # Store Market data
        data_point = f"market_size_{i+1}"
        value = f"€{(i+1) * 10}.5 billion"
        source = f"Test Source for {keyword}"
        date = datetime.now().isoformat()

        result = SupabaseService.store_market_data(
            sector=sector,
            country=country,
            data_point=data_point,
            value=value,
            source=source,
            date=date,
            metadata=metadata
        )

        stored_data_ids.append(result["id"])
        print(f"  Stored data ID: {result['id']}")
        print(f"  Data point: {result['data_point']}")
        print(f"  Value: {result['value']}")
        print(f"  Custom keyword: {result.get('custom_keyword')}")
        print()

    # Retrieve all Market data
    print("Retrieving all Market data:")
    all_data = SupabaseService.get_market_data(sector=sector, country=country)
    print(f"  Found {len(all_data)} data points")

    # Retrieve Market data filtered by each custom keyword
    for keyword in custom_keywords:
        print(f"Retrieving Market data with custom keyword: '{keyword}'")
        filtered_data = SupabaseService.get_market_data(
            sector=sector,
            country=country,
            custom_keyword=keyword
        )

        print(f"  Found {len(filtered_data)} data points")
        for data in filtered_data:
            print(f"  Data point: {data['data_point']}")
            print(f"  Value: {data['value']}")
            print(f"  Custom keyword: {data.get('custom_keyword')}")
            print()

    return stored_data_ids

def test_reports_with_custom_keyword():
    """Test storing and retrieving reports with custom keywords."""
    print_separator("TESTING REPORTS WITH CUSTOM KEYWORDS")

    # Test data
    sector = "Technology"
    country = "France"
    financial_product = "Leasing"
    custom_keywords = ["electric vehicles", "sustainable finance", "digital transformation"]

    # Store reports with different custom keywords
    stored_report_ids = []
    for i, keyword in enumerate(custom_keywords):
        print(f"Storing report with custom keyword: '{keyword}'")

        # Create metadata with custom keyword
        metadata = {
            "custom_keyword": keyword,
            "data_points": 5
        }

        # Store report
        title = f"Test Report {i+1}: {sector} in {country} - {keyword}"
        content = f"This is a test report about {sector} in {country} focusing on {keyword}."
        summary = f"Summary of {keyword} in {sector} sector in {country}."

        result = SupabaseService.store_report(
            title=title,
            sector=sector,
            country=country,
            financial_product=financial_product,
            content=content,
            summary=summary,
            metadata=metadata
        )

        stored_report_ids.append(result["id"])
        print(f"  Stored report ID: {result['id']}")
        print(f"  Title: {result['title']}")
        print(f"  Custom keyword: {result.get('custom_keyword')}")
        print()

    # Retrieve all reports
    print("Retrieving all reports:")
    all_reports = SupabaseService.get_reports(sector=sector, country=country)
    print(f"  Found {len(all_reports)} reports")

    # Retrieve reports filtered by each custom keyword
    for keyword in custom_keywords:
        print(f"Retrieving reports with custom keyword: '{keyword}'")
        filtered_reports = SupabaseService.get_reports(
            sector=sector,
            country=country,
            custom_keyword=keyword
        )

        print(f"  Found {len(filtered_reports)} reports")
        for report in filtered_reports:
            print(f"  Title: {report['title']}")
            print(f"  Custom keyword: {report.get('custom_keyword')}")
            print()

    return stored_report_ids

def main():
    """Run the tests."""
    print("Starting Supabase service tests...")

    # Test Market data with custom keywords
    market_data_ids = test_market_data_with_custom_keyword()

    # Test reports with custom keywords
    report_ids = test_reports_with_custom_keyword()

    print_separator("TEST SUMMARY")
    print(f"Market data entries created: {len(market_data_ids)}")
    print(f"Report entries created: {len(report_ids)}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
