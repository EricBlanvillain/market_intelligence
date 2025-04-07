import os
import json
from dotenv import load_dotenv
import openai
from abc import ABC, abstractmethod

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    """

    def __init__(self, name, description, model="gpt-4o-mini"):
        """
        Initialize the base agent.

        Args:
            name (str): The name of the agent
            description (str): A description of the agent's purpose
            model (str, optional): The OpenAI model to use. Defaults to "gpt-4o-mini".
        """
        self.name = name
        self.description = description
        self.model = model
        self.system_prompt = self._get_system_prompt()
        self.context = []

    @abstractmethod
    def _get_system_prompt(self):
        """
        Get the system prompt for the agent.

        Returns:
            str: The system prompt
        """
        pass

    def add_context(self, role, content):
        """
        Add a message to the agent's context.

        Args:
            role (str): The role of the message sender (system, user, assistant)
            content (str): The message content
        """
        self.context.append({"role": role, "content": content})

    def clear_context(self):
        """Clear the agent's context."""
        self.context = []

    def get_response(self, query, temperature=0.7):
        """
        Get a response from the agent.

        Args:
            query (str): The query to send to the agent
            temperature (float, optional): The temperature for response generation. Defaults to 0.7.

        Returns:
            str: The agent's response
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.context)
        messages.append({"role": "user", "content": query})

        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )

        response_text = response.choices[0].message.content
        self.add_context("assistant", response_text)

        return response_text

    @abstractmethod
    def process(self, input_data):
        """
        Process input data and return a result.

        Args:
            input_data: The input data to process

        Returns:
            The processed result
        """
        pass
