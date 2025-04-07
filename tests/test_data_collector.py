import os
import json
from dotenv import load_dotenv
import openai
from agents.data_collector.agent import DataCollectorAgent

# Load environment variables
load_dotenv()

# Initialize the data collector agent
data_collector = DataCollectorAgent()

# Test parameters
parameters = {
    "sector": "Healthcare",
    "country": "France"
}

print(f"Testing data collection for {parameters['sector']} in {parameters['country']}...")

# Process with data collector agent
try:
    result = data_collector.process(parameters)

    print(f"Result type: {type(result)}")
    print(f"Result keys: {result.keys()}")

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Successfully collected {len(result['collected_data'])} data points!")

        # Display the collected data
        for i, data_point in enumerate(result["collected_data"]):
            print(f"\nData Point {i+1}:")
            print(f"Name: {data_point['name']}")
            print(f"Value: {data_point['value']}")
            print(f"Source: {data_point['source']}")
            print(f"Date: {data_point['date']}")

except Exception as e:
    print(f"Exception occurred: {e}")
