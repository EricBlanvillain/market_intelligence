# Market Intelligence Platform

A multi-agent system for collecting, analyzing, and reporting on Market data for Market.

## Overview

The Market Intelligence Platform is a comprehensive solution that leverages AI agents to gather Market intelligence, generate reports, and answer questions about various sectors and financial products. The platform uses a multi-agent architecture where specialized agents work together to provide valuable insights.

## Features

- **Data Collection**: Automatically gather Market data from various sources
- **Report Generation**: Create comprehensive Market reports based on collected data
- **Question Answering**: Get answers to specific questions about markets and financial products
- **Chat Interface**: Interact with the system through a natural language interface
- **Workflow Builder**: Create custom workflows combining multiple agents
- **Data Explorer**: Browse and search through collected data and generated reports

## Repository Structure

```
bpce-intelligence/
├── agents/                  # Agent implementations
│   ├── orchestrator/        # Orchestrator agent
│   ├── data_collector/      # Data collection agent
│   ├── report_generator/    # Report generation agent
│   ├── qa/                  # Question answering agent
│   ├── base_agent.py        # Base agent class
│   └── __init__.py          # Package initialization
├── config/                  # Configuration files
├── utils/                   # Utility functions
├── multi_agent_app.py       # Main Streamlit application
├── supabase_service.py      # Supabase database service
├── setup_supabase.py        # Supabase setup script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── start.sh                 # Start script
├── README.md                # This file
└── DOCUMENTATION.md         # Detailed documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- Streamlit
- Supabase account
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/bpce-intelligence.git
   cd bpce-intelligence
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

4. Run the setup script to initialize the Supabase database:
   ```
   python setup_supabase.py
   ```

5. Start the application:
   ```
   ./start.sh
   ```
   or
   ```
   streamlit run multi_agent_app.py
   ```

## Usage

Once the application is running, you can access it through your web browser at `http://localhost:8501`.

The platform offers several interfaces:

1. **Chat Interface**: Ask questions and get responses from the appropriate agent
2. **Data Collection**: Collect Market data for specific sectors and countries
3. **Report Generation**: Generate reports based on collected data
4. **Question Answering**: Ask specific questions about markets and get detailed answers
5. **Workflow Builder**: Create custom workflows combining multiple agents
6. **Data Explorer**: Browse and search through collected data and generated reports

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).
