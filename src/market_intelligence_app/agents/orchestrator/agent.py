import os
import json
import sys
from dotenv import load_dotenv
import openai

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

    def __init__(self):
        """Initialize the Orchestrator Agent."""
        super().__init__(
            name="Orchestrator",
            description="Orchestrates the workflow between specialized agents",
            model="gpt-4o-mini"  # Using a smaller model for orchestration decisions
        )

        # Initialize specialized agents
        self.data_collector = DataCollectorAgent()
        self.report_generator = ReportGeneratorAgent()
        self.qa_agent = QAAgent()

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

    def process(self, query_text):
        """
        Process a user query and route it to the appropriate specialized agent.

        Args:
            query_text (str): The user's query text

        Returns:
            dict: The result from the appropriate specialized agent
        """
        # Analyze the query to determine intent and extract parameters
        analysis = self._analyze_query(query_text)

        # Route the query to the appropriate agent based on the intent
        if analysis['intent'] == 'data_collection':
            result = self.data_collector.process(analysis['parameters'])
            return {
                "agent": "data_collector",
                "intent": analysis['intent'],
                "parameters": analysis['parameters'],
                "result": result
            }

        elif analysis['intent'] == 'report_generation':
            result = self.report_generator.process(analysis['parameters'])
            return {
                "agent": "report_generator",
                "intent": analysis['intent'],
                "parameters": analysis['parameters'],
                "result": result
            }

        elif analysis['intent'] == 'question_answering':
            result = self.qa_agent.process(analysis['parameters'])
            return {
                "agent": "qa_agent",
                "intent": analysis['intent'],
                "parameters": analysis['parameters'],
                "result": result
            }

        else:
            # If the intent is not recognized, provide a helpful error message
            return {
                "error": "Unable to determine the appropriate agent for this query",
                "query": query_text,
                "analysis": analysis
            }

    def _analyze_query(self, query_text):
        """
        Analyze a user query to determine intent and extract parameters.

        Args:
            query_text (str): The user's query text

        Returns:
            dict: The analysis result with intent and parameters
        """
        # Use OpenAI to analyze the query
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """
                You are an expert at analyzing user queries about financial Market intelligence.
                Your task is to determine the intent of the query and extract relevant parameters.

                Possible intents:
                1. data_collection: The user wants to collect Market data
                2. report_generation: The user wants to generate a Market report
                3. question_answering: The user wants to ask a question about Market reports

                Parameters to extract:
                - sector: The Market sector (e.g., Healthcare, Technology, Transportation)
                - country: The country (e.g., France, Germany, UK)
                - financial_product: The financial product (e.g., Leasing, SALB, Loan)
                - custom_keyword: Any specific keyword or focus area mentioned (e.g., Electric Car, Software, Medical Equipment, Crane)
                - question: The specific question (for question_answering intent)

                IMPORTANT: For custom_keyword, extract ANY specific product, technology, or focus area mentioned in the query.
                Examples of custom keywords: Electric Car, Software, Medical Equipment, Crane, Construction Equipment, etc.

                If the user explicitly mentions they're looking for data about a specific keyword like 'Crane',
                make sure to extract 'Crane' as the custom_keyword.

                Format your response as a JSON object with 'intent' and 'parameters' fields.
                """},
                {"role": "user", "content": query_text}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        # Parse the response
        try:
            analysis = json.loads(response.choices[0].message.content)
            print(f"Query analysis: {analysis}")

            # Ensure the analysis has the required fields
            if 'intent' not in analysis:
                analysis['intent'] = 'unknown'
            if 'parameters' not in analysis:
                analysis['parameters'] = {}

            # For question_answering intent, ensure the question parameter is set
            if analysis['intent'] == 'question_answering' and 'question' not in analysis['parameters']:
                analysis['parameters']['question'] = query_text

            # Check for direct mentions of custom keywords in the query
            # This is a fallback in case the model doesn't extract them properly
            lower_query = query_text.lower()
            common_keywords = ["crane", "electric car", "software", "medical equipment", "airlines", "automation", "renewable"]

            for keyword in common_keywords:
                if keyword in lower_query and ('custom_keyword' not in analysis['parameters'] or not analysis['parameters']['custom_keyword']):
                    print(f"Directly detected custom keyword: {keyword}")
                    analysis['parameters']['custom_keyword'] = keyword.title()

            return analysis

        except json.JSONDecodeError:
            # If the response is not valid JSON, return a default analysis
            return {
                "intent": "unknown",
                "parameters": {}
            }

    def execute_workflow(self, workflow):
        """
        Execute a multi-step workflow involving multiple agents.

        Args:
            workflow (dict): A dictionary describing the workflow:
                - steps (list): A list of workflow steps, each with:
                    - agent (str): The agent to use ('data_collector', 'report_generator', or 'qa_agent')
                    - parameters (dict): The parameters for the agent
                - context (dict, optional): Shared context for the workflow

        Returns:
            dict: The results of the workflow
        """
        results = []
        context = workflow.get('context', {})

        for step in workflow['steps']:
            # Update step parameters with context if needed
            parameters = step['parameters'].copy()
            for key, value in context.items():
                if key not in parameters:
                    parameters[key] = value

            # Execute the step with the appropriate agent
            if step['agent'] == 'data_collector':
                result = self.data_collector.process(parameters)
            elif step['agent'] == 'report_generator':
                result = self.report_generator.process(parameters)
            elif step['agent'] == 'qa_agent':
                result = self.qa_agent.process(parameters)
            else:
                result = {"error": f"Unknown agent: {step['agent']}"}

            # Store the result
            step_result = {
                "agent": step['agent'],
                "parameters": parameters,
                "result": result
            }
            results.append(step_result)

            # Update the context with the result if needed
            if 'update_context' in step and step['update_context']:
                for key in step['update_context']:
                    if key == 'sector' and 'sector' in parameters:
                        context['sector'] = parameters['sector']
                    elif key == 'country' and 'country' in parameters:
                        context['country'] = parameters['country']
                    elif key == 'financial_product' and 'financial_product' in parameters:
                        context['financial_product'] = parameters['financial_product']
                    elif key == 'custom_keyword' and 'custom_keyword' in parameters:
                        context['custom_keyword'] = parameters['custom_keyword']
                    # Add more context updates as needed

        return {
            "workflow": workflow,
            "results": results,
            "final_context": context
        }
