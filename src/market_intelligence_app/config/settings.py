"""
Configuration settings for the Market Intelligence Platform.
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Application settings
APP_NAME = "Market Intelligence Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Agent settings
AGENT_SETTINGS = {
    "orchestrator": {
        "model": os.getenv("ORCHESTRATOR_MODEL", "gpt-4o-mini"),
        "temperature": float(os.getenv("ORCHESTRATOR_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("ORCHESTRATOR_MAX_TOKENS", "1000"))
    },
    "data_collector": {
        "model": os.getenv("DATA_COLLECTOR_MODEL", "gpt-4o"),
        "temperature": float(os.getenv("DATA_COLLECTOR_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("DATA_COLLECTOR_MAX_TOKENS", "2000"))
    },
    "report_generator": {
        "model": os.getenv("REPORT_GENERATOR_MODEL", "gpt-4o"),
        "temperature": float(os.getenv("REPORT_GENERATOR_TEMPERATURE", "0.5")),
        "max_tokens": int(os.getenv("REPORT_GENERATOR_MAX_TOKENS", "4000"))
    },
    "qa_agent": {
        "model": os.getenv("QA_AGENT_MODEL", "gpt-4o"),
        "temperature": float(os.getenv("QA_AGENT_TEMPERATURE", "0.3")),
        "max_tokens": int(os.getenv("QA_AGENT_MAX_TOKENS", "2000"))
    }
}

# Data settings
SECTORS = [
    "Healthcare",
    "Technology",
    "Transportation",
    "Industrial Equipment",
    "Energy",
    "Construction",
    "Agriculture",
    "Retail",
    "Financial Services",
    "Manufacturing"
]

COUNTRIES = [
    "France",
    "Germany",
    "UK",
    "US",
    "China",
    "Japan",
    "Italy",
    "Spain",
    "Brazil",
    "India"
]

FINANCIAL_PRODUCTS = [
    "Leasing",
    "SALB (Sale and Lease Back)",
    "Loan",
    "Rental",
    "Asset Finance"
]

# Database table names
MARKET_DATA_TABLE = "market_data"
REPORTS_TABLE = "reports"
QUERIES_TABLE = "queries"
WORKFLOWS_TABLE = "workflows"
