# Market Intelligence Platform Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Agent System](#agent-system)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [User Guide](#user-guide)
7. [Development Guide](#development-guide)
8. [Troubleshooting](#troubleshooting)

## Introduction

The Market Intelligence Platform is a multi-agent system designed to collect, analyze, and report on Market data for the equipment financing sector. The platform leverages AI agents to gather Market intelligence, generate comprehensive reports, and answer questions about various sectors and financial products.

## Architecture

The platform is built on a multi-agent architecture where specialized agents work together to provide valuable insights. The system consists of the following components:

1. **Streamlit Web Application**: The user interface for interacting with the system
2. **Agent System**: A collection of specialized AI agents for different tasks
3. **Supabase Database**: Storage for Market data, reports, and queries
4. **OpenAI API**: Powers the AI capabilities of the agents

### System Flow

1. User submits a request through the Streamlit interface
2. The orchestrator agent analyzes the request and routes it to the appropriate specialized agent
3. The specialized agent processes the request and returns results
4. Results are stored in the Supabase database and displayed to the user

## Agent System

The platform uses a multi-agent system with specialized roles:

### Orchestrator Agent

The orchestrator agent is responsible for:
- Analyzing user queries to determine intent
- Routing queries to the appropriate specialized agent
- Managing the execution of multi-step workflows
- Coordinating communication between agents

**Implementation**: `agents/orchestrator/agent.py`

### Data Collector Agent

The data collector agent is responsible for:
- Gathering Market data from the web
- Structuring the collected data
- Storing the data in the Supabase database

**Implementation**: `agents/data_collector/agent.py`

### Report Generator Agent

The report generator agent is responsible for:
- Retrieving Market data from the database
- Analyzing the data to identify trends and insights
- Generating comprehensive reports with executive summaries
- Storing the reports in the database

**Implementation**: `agents/report_generator/agent.py`

### QA Agent

The QA agent is responsible for:
- Retrieving reports from the database
- Analyzing reports to answer user questions
- Providing detailed, accurate answers with citations

**Implementation**: `agents/qa/agent.py`

## Database Schema

The platform uses Supabase as its database. The database schema consists of the following tables:

### Market Data Table

Stores collected Market data.

**Table Name**: `market_data`

**Columns**:
- `id`: UUID (primary key)
- `sector`: String
- `country`: String
- `financial_product`: String (optional)
- `name`: String (e.g., "market_size", "growth_rate")
- `value`: String
- `source`: String
- `date`: Date
- `created_at`: Timestamp

### Reports Table

Stores generated reports.

**Table Name**: `reports`

**Columns**:
- `id`: UUID (primary key)
- `title`: String
- `sector`: String
- `country`: String
- `financial_product`: String (optional)
- `summary`: Text
- `content`: Text
- `created_at`: Timestamp

### Queries Table

Stores user queries and responses.

**Table Name**: `queries`

**Columns**:
- `id`: UUID (primary key)
- `question`: Text
- `answer`: Text
- `sector`: String (optional)
- `country`: String (optional)
- `financial_product`: String (optional)
- `reports_used`: Array of UUIDs
- `created_at`: Timestamp

### Workflows Table

Stores multi-step workflows.

**Table Name**: `workflows`

**Columns**:
- `id`: UUID (primary key)
- `name`: String
- `steps`: JSON
- `results`: JSON
- `created_at`: Timestamp

## API Reference

### Supabase Service

The `supabase_service.py` file provides a wrapper around the Supabase API for interacting with the database.

#### Methods

- `get_market_data(sector=None, country=None, data_point=None)`: Retrieve Market data with optional filters
- `insert_market_data(data)`: Insert new Market data
- `get_reports(sector=None, country=None, financial_product=None)`: Retrieve reports with optional filters
- `insert_report(report)`: Insert a new report
- `get_queries(question=None, sector=None, country=None)`: Retrieve queries with optional filters
- `insert_query(query)`: Insert a new query
- `get_workflows(name=None)`: Retrieve workflows with optional filters
- `insert_workflow(workflow)`: Insert a new workflow

## User Guide

### Chat Interface

The Chat Interface allows you to interact with the orchestrator agent to automatically route your queries to the appropriate specialized agent.

1. Enter your message in the text area
2. Click "Send"
3. The orchestrator will analyze your query and route it to the appropriate agent
4. The response will be displayed in the chat history

### Data Collection

The Data Collection page allows you to collect Market data for specific sectors and countries.

1. Select a sector from the dropdown
2. Select a country from the dropdown
3. Optionally select a financial product
4. Click "Collect Data"
5. The data collector agent will gather Market data and store it in the database
6. The collected data will be displayed on the page

### Report Generation

The Report Generation page allows you to generate comprehensive reports based on collected data.

1. Select a sector from the dropdown
2. Select a country from the dropdown
3. Optionally select a financial product
4. Click "Generate Report"
5. The report generator agent will analyze the data and generate a report
6. The report will be displayed on the page

### Question Answering

The Question Answering page allows you to ask specific questions about markets and get detailed answers.

1. Enter your question in the text area
2. Optionally filter by sector, country, or financial product
3. Click "Ask Question"
4. The QA agent will analyze reports to answer your question
5. The answer will be displayed on the page

### Workflow Builder

The Workflow Builder page allows you to create and execute multi-step workflows involving multiple agents.

1. Add steps to your workflow by selecting agent types and parameters
2. Click "Execute Workflow" to run the entire workflow
3. The results of each step will be displayed on the page

### Data Explorer

The Data Explorer page allows you to browse and search through collected data and generated reports.

1. Select the "Market Data" tab to view collected Market data
2. Select the "Reports" tab to view generated reports
3. Select the "Queries" tab to view past queries and answers
4. Select the "Bulk Data Collection" tab to collect data for multiple sectors and countries at once

## Development Guide

### Adding a New Agent

To add a new agent to the system:

1. Create a new directory in the `agents` directory (e.g., `agents/new_agent`)
2. Create an `__init__.py` file in the new directory
3. Create an `agent.py` file in the new directory that implements the agent
4. Update the orchestrator agent to route queries to the new agent

### Modifying the Database Schema

To modify the database schema:

1. Update the `setup_supabase.py` file to include the new tables or columns
2. Run the setup script to apply the changes to the database
3. Update the `supabase_service.py` file to include methods for interacting with the new tables or columns

### Adding a New Feature to the UI

To add a new feature to the UI:

1. Update the `multi_agent_app.py` file to include the new feature
2. Add a new page or tab to the UI if necessary
3. Update the documentation to include the new feature

## Troubleshooting

### Database Connection Issues

If you encounter issues connecting to Supabase:

1. Verify your Supabase URL and key in `.env`
2. Check that your Supabase project is active
3. Verify that the required tables exist

### Agent Issues

If you encounter issues with the agents:

1. Check the agent logs for errors
2. Verify that the OpenAI API key is valid
3. Check that the agent parameters are correctly configured

### UI Issues

If you encounter issues with the UI:

1. Check the Streamlit logs for errors
2. Verify that the required packages are installed
3. Check that the session state is correctly initialized
