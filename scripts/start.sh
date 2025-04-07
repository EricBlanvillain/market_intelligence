#!/bin/bash

# Start the Market Intelligence Platform
echo "Starting Market Intelligence Platform..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Get the project root directory (parent of the script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"
echo "Working directory: $(pwd)"

# Check if .env file exists in the project root
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    # Source the .env file if it exists (for bash)
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Using existing environment variables."
    # Check if .env.example exists in the project root and offer to copy it
    if [ -f .env.example ]; then
        read -p "Would you like to create a .env file from .env.example? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo "Created .env file from .env.example. Please edit it with your API keys."
            exit 1
        fi
    fi
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set it in your .env file or export it in your shell."
    exit 1
fi

# Check if Supabase credentials are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "Warning: Supabase credentials are not set. The application will use mock data."
fi

# Determine which Python to use
PYTHON_CMD=$(which python3 || which python)
echo "Using Python: $PYTHON_CMD"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Not running in a virtual environment. Using system Python."
else
    echo "Running in virtual environment: $VIRTUAL_ENV"
fi

# Install required packages from the project root
echo "Installing required packages..."
$PYTHON_CMD -m pip install -r requirements.txt

# Install specific version of Supabase
echo "Installing compatible version of Supabase..."
$PYTHON_CMD -m pip install 'supabase==0.7.1' --no-deps
$PYTHON_CMD -m pip install 'httpx<0.24.0,>=0.23.0' 'gotrue<0.6.0,>=0.5.0' 'postgrest-py<0.11.0,>=0.10.2' 'realtime<0.0.6,>=0.0.5' 'storage3<0.4.0,>=0.3.5' 'supafunc<0.3.0,>=0.2.2' 'websockets<11.0,>=10.3' 'python-dateutil<3.0.0,>=2.8.1' 'pydantic<2.0.0,>=1.9.1'

# Run the Supabase setup script from the project root
echo "Running Supabase setup..."
$PYTHON_CMD scripts/setup_supabase.py

# Specifically check for openai package
if ! $PYTHON_CMD -c "import openai" &> /dev/null; then
    echo "OpenAI package not found. Installing it specifically..."
    $PYTHON_CMD -m pip install openai

    # Check if installation was successful
    if ! $PYTHON_CMD -c "import openai" &> /dev/null; then
        echo "Error: Failed to install OpenAI package. Please install it manually:"
        echo "pip install openai"
        exit 1
    fi
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit is not installed. Installing it specifically..."
    $PYTHON_CMD -m pip install streamlit

    # Check if installation was successful
    if ! command -v streamlit &> /dev/null; then
        echo "Error: Failed to install Streamlit. Please install it manually:"
        echo "pip install streamlit"
        exit 1
    fi
fi

# Run the Streamlit app from the project root
echo "Starting Streamlit server..."
streamlit run src/market_intelligence_app/multi_agent_app.py

# Check if Streamlit started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Streamlit server."
    echo "Please check the error messages above."
    exit 1
fi
