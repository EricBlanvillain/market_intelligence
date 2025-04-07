import os
import json
import sys
from dotenv import load_dotenv
from ..base_agent import BaseAgent
from supabase_service import SupabaseService
from openai import OpenAI

# Add parent directory to path to import base_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent
from supabase_service import SupabaseService

# Import specialized agents
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_collector"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report_generator"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qa"))

from agents.data_collector.agent import DataCollectorAgent
from agents.report_generator.agent import ReportGeneratorAgent
from agents.qa.agent import QAAgent

# Load environment variables
load_dotenv()

class OrchestratorAgent(BaseAgent):
    """
    Agent responsible for orchestrating the workflow between specialized agents.
    """

    def __init__(self, openai_client: OpenAI = None):
        """
        Initializes the OrchestratorAgent.

        Args:
            openai_client (OpenAI, optional): An initialized OpenAI client instance.
        """
        super().__init__(
            name="Orchestrator Agent",
            description="Routes user queries to the appropriate specialized agent (Data Collector, Report Generator, QA Agent) based on intent.",
            openai_client=openai_client
        )

        # Initialize specialized agents, passing the client
        self.data_collector = DataCollectorAgent(openai_client=self.client)
        self.report_generator = ReportGeneratorAgent(openai_client=self.client)
        self.qa_agent = QAAgent(openai_client=self.client)

    def _get_system_prompt(self):
        """
        Get the system prompt for the Orchestrator Agent.

        Returns:
            str: The system prompt
        """
        return """
        You are an expert orchestrator for a multi-agent system specializing in financial Market intelligence.
        Your task is to analyze user queries and determine which specialized agent should handle them.

        You have access to the following specialized agents:
        1. Data Collector Agent: Collects Market data from the web and stores it in the database
        2. Report Generator Agent: Generates comprehensive reports based on stored Market data
        3. QA Agent: Answers questions about Market reports

        When analyzing a query:
        1. Identify the user's intent (data collection, report generation, or question answering)
        2. Extract relevant parameters (sector, country, financial product, etc.)
        3. Determine which agent should handle the query
        4. Format the query appropriately for the selected agent

        Always maintain a helpful, professional tone and ensure the user's query is routed to the most appropriate agent.
        """

    def process(self, query_text: str) -> dict:
        """
        Processes a user query, determines the intent, and routes to the correct agent.
        """
        try:
            # Analyze the query to determine intent and parameters
            analysis = self._analyze_query(query_text)

            intent = analysis.get("intent")
            parameters = analysis.get("parameters", {})

            agent_to_call = None
            agent_name_str = ""

            if intent == "data_collection":
                agent_to_call = self.data_collector
                agent_name_str = "data_collector"
            elif intent == "report_generation":
                agent_to_call = self.report_generator
                agent_name_str = "report_generator"
            elif intent == "question_answering":
                agent_to_call = self.qa_agent
                agent_name_str = "qa_agent"
                # Ensure the question is passed correctly if not extracted
                if "question" not in parameters:
                    parameters["question"] = query_text
            else:
                # Default or fallback behavior (e.g., use QA agent for general queries)
                print(f"Orchestrator: Unclear intent '{intent}'. Defaulting to QA.")
                agent_to_call = self.qa_agent
                agent_name_str = "qa_agent"
                parameters["question"] = query_text

            # Call the selected agent
            if agent_to_call:
                raw_result_dict = agent_to_call.process(parameters)
                # Extract the relevant part (the inner 'result' dict or the error dict)
                final_result_data = raw_result_dict.get("result", raw_result_dict) # Use inner result if exists, else the whole dict (for direct errors)
                return {
                    "agent": agent_name_str,
                    "parameters": parameters,
                    "result": final_result_data # Return the extracted inner result/error
                }
            else:
                # Should not happen with the default case, but handle anyway
                return {"error": "Could not determine which agent to call."}

        except Exception as e:
            print(f"Error in Orchestrator process: {e}")
            # import traceback
            # traceback.print_exc() # Print stack trace for detailed debugging
            return {"error": str(e)}

    def _analyze_query(self, query_text: str) -> dict:
        """
        Uses the LLM to analyze the user query and extract intent and parameters.
        """
        prompt = f"""
Analyze the following user query for a Market intelligence system. Determine the user's intent and extract relevant parameters.

User Query: "{query_text}"

Possible Intents:
- data_collection: User wants to find, research, or collect new/up-to-date data, facts, or outlooks about a Market (e.g., 'Find data on...', 'Research the outlook for...', 'What is the latest market size for...?', 'Collect information about...'). This is for getting *new* information.
- report_generation: User wants a structured summary or generated report based on *existing, previously collected* data (e.g., 'Generate a report on...', 'Summarize the data for...', 'Create an overview of...'). This uses data already in the system.
- question_answering: User is asking a specific question about existing data or reports (e.g., 'What was the growth rate last year?', 'Who are the key players listed in the report?').

Parameters to Extract:
- sector (e.g., Technology, Healthcare, Video Game)
- country (e.g., France, US) - Optional
- financial_product (e.g., Leasing, Loan) - Optional
- custom_keyword (any specific term like 'market outlook 2025', 'electric vehicles', 'sustainability') - Optional
- question (if intent is question_answering)

Output ONLY a JSON object with 'intent' and 'parameters' keys. Examples:
{{"intent": "report_generation", "parameters": {{"sector": "Technology", "country": "Germany"}}}} # Generate report from existing data
{{"intent": "question_answering", "parameters": {{"question": "What is the growth rate for leasing in the French healthcare sector?"}}}} # Ask about existing data
{{"intent": "data_collection", "parameters": {{"sector": "Video Game", "custom_keyword": "market outlook 2025"}}}} # Research new info
{{"intent": "data_collection", "parameters": {{"sector": "Transportation", "country": "UK"}}}} # Collect new data
"""

        messages = [
            {"role": "system", "content": "You are an expert query analyzer for a Market intelligence system. Your task is to determine intent (data_collection, report_generation, question_answering) and extract parameters from user queries. Output only JSON."},
            {"role": "user", "content": prompt}
        ]

        # Use the _call_openai_api helper method inherited from BaseAgent
        try:
            response_text = self._call_openai_api(messages, model="gpt-4o-mini", temperature=0.1)
            # print(f"_analyze_query response: {response_text}") # Debugging
            analysis = json.loads(response_text)
            return analysis
        except json.JSONDecodeError:
            print(f"Error decoding JSON from LLM analysis: {response_text}")
            # Fallback: Treat as a general question if analysis fails
            return {"intent": "question_answering", "parameters": {"question": query_text}}
        except Exception as e:
            print(f"Error during query analysis: {e}")
            # Fallback: Treat as a general question on error
            return {"intent": "question_answering", "parameters": {"question": query_text}}

    def execute_workflow(self, workflow: dict) -> dict:
        """
        Executes a predefined workflow consisting of multiple steps.
        (Implementation similar to previous examples, ensuring client is passed)
        """
        results = []
        context = workflow.get("context", {})

        for step in workflow.get("steps", []):
            agent_type = step.get("agent")
            parameters = step.get("parameters", {})

            # Update parameters from context if needed
            # ... (context update logic)

            agent = None
            if agent_type == "data_collector":
                agent = self.data_collector
            elif agent_type == "report_generator":
                agent = self.report_generator
            elif agent_type == "qa_agent":
                agent = self.qa_agent

            if agent:
                try:
                    result = agent.process(parameters)
                    step_result = {"agent": agent_type, "parameters": parameters, "result": result}
                    results.append(step_result)

                    # Update context if needed
                    # ... (context update logic)

                except Exception as e:
                    results.append({"agent": agent_type, "parameters": parameters, "error": str(e)})
                    # Optionally break workflow on error
                    # break
            else:
                results.append({"agent": agent_type, "error": f"Unknown agent type: {agent_type}"})

        return {"results": results, "final_context": context}
