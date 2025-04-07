import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import the necessary modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supabase_service import SupabaseService
from agents.orchestrator.agent import OrchestratorAgent

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_workflow_with_custom_keyword():
    """Test a workflow with custom keywords."""
    print_separator("TESTING WORKFLOW WITH CUSTOM KEYWORDS")

    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent()

    # Test data
    sector = "Technology"
    country = "France"
    custom_keyword = "electric vehicles"

    # Create a workflow that:
    # 1. Collects data with a custom keyword
    # 2. Generates a report using that data
    # 3. Answers a question about the report
    workflow = {
        "steps": [
            {
                "agent": "data_collector",
                "parameters": {
                    "sector": sector,
                    "country": country,
                    "custom_keyword": custom_keyword
                },
                "update_context": ["sector", "country", "custom_keyword"]
            },
            {
                "agent": "report_generator",
                "parameters": {
                    # Use context from previous step
                },
                "update_context": ["sector", "country", "custom_keyword"]
            },
            {
                "agent": "qa_agent",
                "parameters": {
                    "question": f"What are the key trends in {custom_keyword} for the {sector} sector in {country}?"
                    # Use context from previous steps
                }
            }
        ],
        "context": {}
    }

    print("Executing workflow...")
    results = orchestrator.execute_workflow(workflow)

    # Verify the results
    print("\nWorkflow results:")

    # Check the final context
    final_context = results["final_context"]
    print(f"Final context: {json.dumps(final_context, indent=2)}")

    # Check each step
    for i, step_result in enumerate(results["results"]):
        agent = step_result["agent"]
        parameters = step_result["parameters"]
        result = step_result["result"]

        print(f"\nStep {i+1} ({agent}):")
        print(f"  Parameters: {json.dumps(parameters, indent=2)}")

        # Check if custom_keyword was passed correctly
        if "custom_keyword" in parameters:
            print(f"  Custom keyword in parameters: {parameters['custom_keyword']}")

        # Check specific results based on agent type
        if agent == "data_collector":
            if "error" in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Collected {len(result['collected_data'])} data points")
                print(f"  Stored {len(result['stored_data'])} data points")

                # Check if custom_keyword was stored correctly
                for data_point in result['stored_data'][:1]:  # Just check the first one
                    print(f"  Sample data point: {data_point['data_point']}")
                    print(f"  Custom keyword in data: {data_point.get('custom_keyword')}")

        elif agent == "report_generator":
            if "error" in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Generated report: {result['report']['title']}")

                # Check if custom_keyword was stored correctly
                stored_report = result['stored_report']
                print(f"  Custom keyword in report: {stored_report.get('custom_keyword')}")

        elif agent == "qa_agent":
            if "error" in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Question: {parameters['question']}")
                print(f"  Answer: {result['answer'][:100]}...")
                print(f"  Reports used: {len(result['reports_used'])}")

                # Check if custom_keyword was used in the query
                stored_query = result['stored_query']
                entities = json.loads(stored_query['entities'])
                print(f"  Custom keyword in entities: {entities.get('custom_keyword')}")

    return results

def main():
    """Run the tests."""
    print("Starting workflow tests with custom keywords...")

    # Test workflow with custom keywords
    workflow_results = test_workflow_with_custom_keyword()

    print_separator("TEST SUMMARY")
    print(f"Workflow steps completed: {len(workflow_results['results'])}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
