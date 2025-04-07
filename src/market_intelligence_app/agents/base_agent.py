import os
import json
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from openai import OpenAI # Import the OpenAI class

# Remove old global configuration
# load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """

    def __init__(self, name: str, description: str, openai_client: OpenAI = None):
        """
        Initializes the BaseAgent.

        Args:
            name (str): The name of the agent.
            description (str): A brief description of the agent's purpose.
            openai_client (OpenAI, optional): An initialized OpenAI client instance. Defaults to None.
        """
        self.name = name
        self.description = description
        self.client = openai_client # Store the passed client
        self.system_prompt = self._get_system_prompt()
        self.context = []

    def _get_system_prompt(self):
        """
        Returns the system prompt for the agent.
        Can be overridden by subclasses.
        """
        return f"You are {self.name}, {self.description}."

    def add_context(self, role, content):
        """
        Adds a message to the agent's context.
        """
        self.context.append({"role": role, "content": content})
        # Optional: Limit context size
        # MAX_CONTEXT_SIZE = 10
        # self.context = self.context[-MAX_CONTEXT_SIZE:]

    def query(self, query, temperature=0.7, model="gpt-4o-mini"):
        """
        Sends a query to the OpenAI API using the agent's context.
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(self.context)
        messages.append({"role": "user", "content": query})

        # Use the helper method to make the API call
        response_text = self._call_openai_api(messages, model=model, temperature=temperature)
        self.add_context("assistant", response_text)

        return response_text

    @abstractmethod
    def process(self, parameters: dict) -> dict:
        """
        Processes the given parameters and returns a result.
        This method MUST be implemented by subclasses.
        """
        pass

    def _call_openai_api(self, messages: list, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
        """
        Calls the OpenAI Chat Completions API using the provided client.
        """
        if not self.client:
            print("!!! WARNING: OpenAI client not explicitly provided to agent. Creating default client.")
            try:
                fallback_key = os.getenv("OPENAI_API_KEY")
                print(f"!!! Fallback using key from os.getenv ending in: ...{fallback_key[-4:] if fallback_key else 'None'}")
                if not fallback_key:
                     raise ValueError("OPENAI_API_KEY environment variable not found for fallback.")
                self.client = OpenAI(api_key=fallback_key)
            except Exception as e:
                 print(f"!!! Fallback client initialization failed: {e}")
                 raise Exception(f"Failed to initialize default OpenAI client: {e}")

        try:
            current_key = self.client.api_key
            print(f"--- Making API call via BaseAgent for {self.name}. Key ending in: ...{current_key[-4:] if current_key else 'None'}")
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log the error and re-raise or return an error message
            key_used_at_error = self.client.api_key if self.client else 'No Client'
            print(f"!!! OpenAI API call FAILED for {self.name}. Error: {e}. Key ending in: ...{key_used_at_error[-4:] if isinstance(key_used_at_error, str) else key_used_at_error}")
            raise Exception(f"OpenAI API call failed: {e}")
