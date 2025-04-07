import os
import json
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Import our agent orchestrator
from agents.orchestrator.agent import OrchestratorAgent
from supabase_service import SupabaseService, mock_db

# Load environment variables
load_dotenv()

# Initialize the orchestrator agent
orchestrator = OrchestratorAgent()

# Populate sample data for development/testing
SupabaseService.populate_sample_data()

# Set page configuration
st.set_page_config(
    page_title="Market Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide default Streamlit navigation menu */
    header {
        visibility: hidden;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    /* Hide top navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        display: none;
    }

    /* Global styles */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Market Color Variables */
    :root {
        --bpce-green: #00965E;
        --bpce-blue: #0082C3;
        --bpce-orange: #FF5F00;
        --bpce-green-light: rgba(0, 150, 94, 0.1);
        --bpce-blue-light: rgba(0, 130, 195, 0.1);
        --bpce-orange-light: rgba(255, 95, 0, 0.1);
    }

    /* Header styles with decorative bar */
    .main-header {
        font-size: 2.5rem;
        color: var(--bpce-green);
        margin-bottom: 0.5rem;
        font-weight: 700;
        position: relative;
        padding-bottom: 0.5rem;
    }
    .main-header::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        height: 4px;
        width: 100px;
        background: linear-gradient(90deg, var(--bpce-green), var(--bpce-blue));
        border-radius: 2px;
    }

    .sub-header {
        font-size: 1.5rem;
        color: var(--bpce-blue);
        margin-bottom: 0.5rem;
        font-weight: 600;
        position: relative;
        padding-bottom: 0.5rem;
    }
    .sub-header::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        height: 3px;
        width: 70px;
        background: linear-gradient(90deg, var(--bpce-blue), rgba(0, 130, 195, 0.5));
        border-radius: 2px;
    }

    /* Section divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, var(--bpce-green-light), var(--bpce-blue-light), rgba(0, 0, 0, 0));
        margin: 1.5rem 0;
        border: none;
    }

    /* Card styles with subtle shadow */
    .card {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--bpce-blue);
        color: #111827;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transform: translateY(-2px);
    }

    /* Ensure all elements inside card have dark color */
    .card * {
        color: #111827 !important;
    }

    .info-text {
        color: #4B5563;
        font-size: 0.9rem;
    }

    .highlight {
        background-color: var(--bpce-green-light);
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: 500;
        color: var(--bpce-green) !important;
    }

    /* Agent tag with improved styling */
    .agent-tag {
        background-color: var(--bpce-blue-light);
        color: var(--bpce-blue) !important;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
        border: 1px solid rgba(0, 130, 195, 0.3);
    }

    /* Report container with improved styling */
    .report-container {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-top: 1rem;
        color: #111827;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    /* Ensure all elements inside report-container have dark color */
    .report-container * {
        color: #111827 !important;
    }

    /* Additional styling for specific elements in reports */
    .report-container h3, .report-container h4 {
        color: var(--bpce-green) !important;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        position: relative;
        padding-bottom: 0.3rem;
    }
    .report-container h3::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        height: 2px;
        width: 50px;
        background: linear-gradient(90deg, var(--bpce-green), rgba(0, 150, 94, 0.5));
        border-radius: 1px;
    }

    .report-container p, .report-container li, .report-container div {
        color: #111827 !important;
        line-height: 1.6;
    }

    .report-container ul, .report-container ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Specific styling for report content */
    .report-content {
        color: #111827 !important;
    }
    .report-content * {
        color: #111827 !important;
    }

    .answer-text {
        color: #111827;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* Ensure all elements inside answer-text have dark color */
    .answer-text * {
        color: #111827 !important;
    }

    /* Ensure progress text is dark */
    .progress-text {
        color: #111827;
        font-weight: 500;
    }

    /* Button styling */
    .stButton > button {
        background-color: var(--bpce-green);
        color: white;
        border-radius: 0.375rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #007a4d; /* Darker Market green */
    }

    /* Success message styling */
    .element-container div[data-testid="stAlert"] {
        border-radius: 0.375rem;
        border-left-color: var(--bpce-green) !important;
    }

    /* Warning message styling */
    .element-container div[data-testid="stAlert"][data-baseweb="notification"] {
        border-left-color: var(--bpce-orange) !important;
    }

    /* Form styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        border-radius: 0.375rem;
        border: 1px solid #D1D5DB;
    }

    /* Checkbox styling */
    .stCheckbox > div[data-testid="stMarkdownContainer"] > label > div[role="checkbox"] {
        border-color: var(--bpce-blue);
    }
    .stCheckbox > div[data-testid="stMarkdownContainer"] > label > div[role="checkbox"][data-checked="true"] {
        background-color: var(--bpce-blue);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--bpce-green);
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] .main-header {
        color: white;
    }
    [data-testid="stSidebar"] .main-header::after {
        background: linear-gradient(90deg, white, rgba(255, 255, 255, 0.5));
    }
    [data-testid="stSidebar"] h3 {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        padding-left: 1rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: white;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: var(--bpce-blue);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--bpce-green);
        border-bottom-color: var(--bpce-green) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1rem 0;
    }

    /* Fix for white text on white background */
    .stTabs [data-baseweb="tab-list"] button p {
        color: var(--bpce-blue) !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
        color: var(--bpce-green) !important;
    }

    /* Ensure all text in the main content area has proper contrast */
    [data-testid="stAppViewContainer"] {
        color: #111827;
    }
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] div {
        color: #111827;
    }

    /* Ensure text in markdown is visible */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6 {
        color: #111827 !important;
    }

    /* Fix for text in the sidebar */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div {
        color: white !important;
    }

    /* Fix for text in the sidebar radio buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label div p {
        color: white !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        color: var(--bpce-blue) !important;
        font-weight: 500;
    }
    .streamlit-expanderHeader:hover {
        color: var(--bpce-green) !important;
    }

    /* Fix for text in expanders */
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent span {
        color: #111827 !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .stDataFrame [data-testid="stTable"] {
        border-radius: 0.5rem;
    }
    .stDataFrame thead tr th {
        background-color: var(--bpce-green-light);
        color: var(--bpce-green) !important;
    }

    /* Fix for text in dataframes */
    .stDataFrame tbody tr td {
        color: #111827 !important;
    }

    /* Fix for text in selectboxes */
    .stSelectbox label p {
        color: #111827 !important;
    }

    /* Fix for selectbox selected value (the card) */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border-color: #2D3748 !important;
    }

    div[data-baseweb="select"] > div > div {
        color: white !important;
    }

    div[data-baseweb="select"] > div > div > div > div {
        color: white !important;
    }

    div[data-baseweb="select"] > div > div > div > div > div {
        color: white !important;
    }

    /* Fix for all text inside selectbox cards */
    div[data-baseweb="select"] * {
        color: white !important;
    }

    /* Fix for selectbox label */
    div[data-baseweb="select"] + div {
        color: #111827 !important;
    }

    /* Fix for dropdown/selectbox options with dark background */
    div[data-baseweb="select"] ul {
        background-color: #1E293B !important;
    }

    div[data-baseweb="select"] ul li {
        color: white !important;
    }

    div[data-baseweb="select"] ul li:hover,
    div[data-baseweb="select"] ul li[aria-selected="true"] {
        background-color: #2D3748 !important;
    }

    div[data-baseweb="select"] ul li[aria-selected="true"] div {
        color: white !important;
    }

    div[data-baseweb="select"] ul li div {
        color: white !important;
    }

    /* Global input styling - white background with dark text */
    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #D1D5DB !important;
    }

    div[data-baseweb="select"] > div > div {
        color: #111827 !important;
    }

    div[data-baseweb="select"] > div > div > div > div {
        color: #111827 !important;
    }

    div[data-baseweb="select"] > div > div > div > div > div {
        color: #111827 !important;
    }

    /* Fix for all text inside selectbox cards */
    div[data-baseweb="select"] * {
        color: #111827 !important;
    }

    /* Fix for text in checkboxes */
    .stCheckbox label span {
        color: #111827 !important;
    }

    /* Fix for text in text inputs */
    .stTextInput label p {
        color: #111827 !important;
    }

    /* Fix for text in text areas */
    .stTextArea label p {
        color: #111827 !important;
    }

    /* Fix for text in buttons */
    .stButton button p {
        color: white !important;
    }

    /* Fix for text in tabs */
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] div,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] label {
        color: #111827 !important;
    }

    /* Fix specifically for the Market Data tab */
    .stTabs [data-baseweb="tab-panel"] [data-testid="stMarkdownContainer"] p strong,
    .stTabs [data-baseweb="tab-panel"] [data-testid="stMarkdownContainer"] p b {
        color: #111827 !important;
    }

    /* Fix for text in the green background sections */
    [style*="background-color: rgb(0, 150, 94)"] p,
    [style*="background-color: rgb(0, 150, 94)"] div,
    [style*="background-color: rgb(0, 150, 94)"] span {
        color: white !important;
    }

    /* Fix for text in the green background sections */
    [style*="background-color: rgb(0, 150, 94)"] * {
        color: white !important;
    }

    /* Fix for text in the tab content */
    .stTabs [data-baseweb="tab-panel"] [data-testid="element-container"] p {
        color: #111827 !important;
    }

    /* Fix for text in the tab content */
    .stTabs [data-baseweb="tab-panel"] [data-testid="element-container"] div {
        color: #111827 !important;
    }

    /* Fix for Data Explorer tab filter dropdowns */
    .stSelectbox label {
        color: #111827 !important;
    }

    /* Ensure text in Data Explorer filter dropdowns is visible */
    .stSelectbox [data-baseweb="select"] div[role="button"] {
        background-color: #FFFFFF !important;
    }

    .stSelectbox [data-baseweb="select"] div[role="button"] div {
        color: #111827 !important;
    }

    /* Fix for selected text in selectbox cards */
    div[data-baseweb="select"] div[role="button"] span {
        color: #111827 !important;
    }

    div[data-baseweb="select"] div[role="button"] span span {
        color: #111827 !important;
    }

    /* Fix for selected value text */
    div[data-baseweb="select"] div[role="button"] div[data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }

    /* Ensure all text elements inside selectbox are dark */
    div[data-baseweb="select"] div[role="button"] * {
        color: #111827 !important;
    }

    /* Fix for text in Data Explorer expanders */
    .streamlit-expanderContent p strong,
    .streamlit-expanderContent div strong,
    .streamlit-expanderContent span strong,
    .streamlit-expanderContent p b,
    .streamlit-expanderContent div b,
    .streamlit-expanderContent span b {
        color: #111827 !important;
    }

    /* Fix for text in Data Explorer dataframes */
    .stDataFrame [data-testid="stTable"] td {
        color: #111827 !important;
    }

    /* Fix for text in Data Explorer text inputs */
    .stTextInput input {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }

    /* Fix for text in Data Explorer text areas */
    .stTextArea textarea {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }

    /* Fix for custom keyword filter text input */
    input[aria-label*="Filter by Custom Keyword"],
    input[aria-label*="Custom Keyword"] {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }

    /* Fix for question answering text area */
    textarea[aria-label*="Your Question"],
    textarea[aria-label*="question"] {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }

    /* Fix for text in Data Explorer checkboxes */
    .stCheckbox label span p {
        color: #111827 !important;
    }

    /* Fix for text in Data Explorer buttons */
    .stButton button {
        color: white !important;
    }

    /* Fix for text in Data Explorer expander headers */
    .streamlit-expanderHeader p {
        color: var(--bpce-blue) !important;
    }

    /* Fix for text in Data Explorer cards */
    .card p strong,
    .card p b {
        color: #111827 !important;
    }

    /* Fix for text in Data Explorer info text */
    .info-text {
        color: #4B5563 !important;
    }

    /* Fix for text in Data Explorer progress text */
    .progress-text {
        color: #111827 !important;
    }

    /* Additional fixes for selectbox text in all tabs */
    /* Target the actual text node inside the selectbox */
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {
        color: #111827 !important;
    }

    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        color: #111827 !important;
    }

    /* Force all text inside selectbox to be dark */
    div[data-baseweb="select"] div {
        color: #111827 !important;
    }

    div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Specific fix for Question Answering tab */
    form[data-testid="stForm"] div[data-baseweb="select"] div {
        color: #111827 !important;
    }

    form[data-testid="stForm"] div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Specific fix for Data Explorer tab */
    [data-testid="stVerticalBlock"] div[data-baseweb="select"] div {
        color: #111827 !important;
    }

    [data-testid="stVerticalBlock"] div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* Preserve dropdown menu styling with dark background and white text */
    div[data-baseweb="popover"] div[data-baseweb="menu"] {
        background-color: #1E293B !important;
    }

    div[data-baseweb="popover"] div[data-baseweb="menu"] * {
        color: white !important;
    }

    div[data-baseweb="popover"] div[role="listbox"] {
        background-color: #1E293B !important;
    }

    div[data-baseweb="popover"] div[role="listbox"] * {
        color: white !important;
    }

    div[data-baseweb="popover"] div[role="option"] {
        color: white !important;
    }

    div[data-baseweb="popover"] div[role="option"]:hover {
        background-color: #2D3748 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<div class='main-header'>Market Intelligence</div>", unsafe_allow_html=True)
st.sidebar.markdown("### Multi-Agent System")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_workflow' not in st.session_state:
    st.session_state.current_workflow = None
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Chat Interface", "Data Collection", "Report Generation", "Question Answering", "Workflow Builder", "Data Explorer"])

# Main content
if page == "Chat Interface":
    st.markdown("<div class='main-header'>Chat Interface</div>", unsafe_allow_html=True)
    st.markdown("Interact with the orchestrator agent to automatically route your queries to the appropriate specialized agent.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Chat interface
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div class='card' style='border-left: 4px solid #4B5563;'><b>You:</b> {message['content']}</div>", unsafe_allow_html=True)
        else:
            agent_tag = f"<span class='agent-tag'>{message['agent']}</span>" if 'agent' in message else ""
            st.markdown(f"<div class='card'>{agent_tag}<b>Assistant:</b> {message['content']}</div>", unsafe_allow_html=True)

    # Input for new message
    user_input = st.text_area("Your message:", height=100)
    if st.button("Send"):
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Process the query with the orchestrator
            result = orchestrator.process(user_input)

            # Format the response
            if "error" in result:
                response_content = f"Error: {result['error']}"
                agent_name = "Orchestrator"
            else:
                agent_name = result["agent"].replace("_", " ").title()

                if result["agent"] == "data_collector":
                    if "error" in result["result"]:
                        response_content = f"Error: {result['result']['error']}"
                    else:
                        data_points = len(result["result"]["collected_data"])
                        response_content = f"I've collected {data_points} data points about the {result['parameters']['sector']} sector in {result['parameters']['country']}."

                        # Add custom keyword information if available
                        if 'custom_keyword' in result['parameters'] and result['parameters']['custom_keyword']:
                            response_content += f" The data focuses on '{result['parameters']['custom_keyword']}'."

                        response_content += " The data has been stored in the database."

                elif result["agent"] == "report_generator":
                    if "error" in result["result"]:
                        response_content = f"Error: {result['result']['error']}"
                    else:
                        report_title = result["result"]["report"]["title"]
                        report_summary = result["result"]["report"]["summary"]
                        response_content = f"I've generated a report titled '{report_title}'."

                        # Add custom keyword information if available
                        if 'custom_keyword' in result['parameters'] and result['parameters']['custom_keyword']:
                            response_content += f" The report focuses on '{result['parameters']['custom_keyword']}'."

                        response_content += f"\n\n**Summary:**\n{report_summary}\n\nThe full report has been stored in the database."

                elif result["agent"] == "qa_agent":
                    if "error" in result["result"]:
                        response_content = f"Error: {result['result']['error']}"
                    else:
                        response_content = result["result"]["answer"]

                        # Add information about the data used
                        if 'reports_used' in result["result"] and result["result"]["reports_used"]:
                            num_reports = len(result["result"]["reports_used"])
                            response_content += f"\n\n_Based on {num_reports} report(s)"

                            # Add custom keyword information if available
                            if 'custom_keyword' in result['parameters'] and result['parameters']['custom_keyword']:
                                response_content += f" about '{result['parameters']['custom_keyword']}'"

                            response_content += "._"

                        # Add information about Market data used
                        elif 'market_data_used' in result["result"] and result["result"]["market_data_used"] > 0:
                            num_data_points = result["result"]["market_data_used"]
                            response_content += f"\n\n_Based on {num_data_points} Market data point(s)"

                            # Add custom keyword information if available
                            if 'custom_keyword' in result['parameters'] and result['parameters']['custom_keyword']:
                                response_content += f" about '{result['parameters']['custom_keyword']}'"

                            response_content += "._"

                else:
                    response_content = "I'm not sure how to process this request."

                # Store query in Supabase
                entities = {}
                if "parameters" in result:
                    if "sector" in result["parameters"]:
                        entities["sector"] = result["parameters"]["sector"]
                    if "country" in result["parameters"]:
                        entities["country"] = result["parameters"]["country"]
                    if "financial_product" in result["parameters"]:
                        entities["financial_product"] = result["parameters"]["financial_product"]

                    # Extract custom_keyword if it exists
                    custom_keyword = result["parameters"].get("custom_keyword", None)
                else:
                    custom_keyword = None

                SupabaseService.store_query(
                    query_text=user_input,
                    entities=entities,
                    intent="chat",
                    response=response_content,
                    agent_type=result["agent"],
                    metadata={
                        "custom_keyword": custom_keyword
                    }
                )

            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_content,
                "agent": agent_name
            })

            # Rerun to update the UI
            st.rerun()

elif page == "Data Collection":
    st.markdown("<div class='main-header'>Data Collection</div>", unsafe_allow_html=True)
    st.markdown("Use the Data Collector Agent to gather Market data from the web and store it in the database.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Form for data collection
    with st.form("data_collection_form"):
        sector = st.selectbox("Sector", [
            "Healthcare", "Technology", "Transportation", "Industrial Equipment",
            "Energy", "Construction", "Agriculture", "Retail",
            "Financial Services", "Manufacturing"
        ])
        country = st.selectbox("Country", [
            "France", "Germany", "UK", "US", "China", "Japan",
            "Italy", "Spain", "Brazil", "India"
        ])
        financial_product = st.selectbox("Financial Product (Optional)", [
            "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
        ])

        # Add custom keyword input
        custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                      help="Enter any additional keyword to refine your search (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

        submitted = st.form_submit_button("Collect Data")

        if submitted:
            # Show spinner while collecting data
            with st.spinner("Collecting data from the web..."):
                # Prepare parameters
                parameters = {
                    "sector": sector,
                    "country": country
                }
                if financial_product:
                    parameters["financial_product"] = financial_product
                if custom_keyword:
                    parameters["custom_keyword"] = custom_keyword

                # Process with data collector agent
                result = orchestrator.data_collector.process(parameters)

                # Display results
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Successfully collected {len(result['collected_data'])} data points!")

                    # Store query in Supabase
                    entities = {
                        "sector": sector,
                        "country": country,
                        "financial_product": financial_product if financial_product else None
                    }

                    query_text = f"Collect data for {sector} sector in {country}"
                    if financial_product:
                        query_text += f" for {financial_product}"
                    if custom_keyword:
                        query_text += f" related to {custom_keyword}"

                    SupabaseService.store_query(
                        query_text=query_text,
                        entities=entities,
                        intent="data_collection",
                        response=f"Collected {len(result['collected_data'])} data points",
                        agent_type="data_collector",
                        metadata={
                            "data_points": len(result['collected_data']),
                            "custom_keyword": custom_keyword if custom_keyword else None
                        }
                    )

                    # Display the collected data
                    st.markdown("<div class='sub-header'>Collected Data</div>", unsafe_allow_html=True)
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    for i, data_point in enumerate(result["collected_data"]):
                        st.markdown(f"""
                        <div class='card'>
                            <h4>{data_point['name'].replace('_', ' ').title()}</h4>
                            <p><b>Value:</b> {data_point['value']}</p>
                            <p><b>Source:</b> {data_point['source']}</p>
                            <p><b>Date:</b> {data_point['date']}</p>
                        </div>
                        """, unsafe_allow_html=True)

elif page == "Report Generation":
    st.markdown("<div class='main-header'>Report Generation</div>", unsafe_allow_html=True)
    st.markdown("Generate comprehensive Market reports based on the data stored in the database.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Form for report generation
    with st.form("report_generation_form"):
        sector = st.selectbox("Sector", [
            "Healthcare", "Technology", "Transportation", "Industrial Equipment",
            "Energy", "Construction", "Agriculture", "Retail",
            "Financial Services", "Manufacturing"
        ])
        country = st.selectbox("Country", [
            "France", "Germany", "UK", "US", "China", "Japan",
            "Italy", "Spain", "Brazil", "India"
        ])
        financial_product = st.selectbox("Financial Product (Optional)", [
            "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
        ])

        # Add custom keyword input
        custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                      help="Enter any additional keyword to refine your report (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

        submitted = st.form_submit_button("Generate Report")

        if submitted:
            # Show spinner while generating report
            with st.spinner("Generating report..."):
                # Prepare parameters
                parameters = {
                    "sector": sector,
                    "country": country
                }
                if financial_product:
                    parameters["financial_product"] = financial_product
                if custom_keyword:
                    parameters["custom_keyword"] = custom_keyword

                # Process with report generator agent
                result = orchestrator.report_generator.process(parameters)

                # Display results
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"Successfully generated report: {result['report']['title']}")

                    # Store query in Supabase
                    entities = {
                        "sector": sector,
                        "country": country,
                        "financial_product": financial_product if financial_product else None
                    }

                    query_text = f"Generate report for {sector} sector in {country}"
                    if financial_product:
                        query_text += f" for {financial_product}"
                    if custom_keyword:
                        query_text += f" related to {custom_keyword}"

                    SupabaseService.store_query(
                        query_text=query_text,
                        entities=entities,
                        intent="report_generation",
                        response=f"Generated report: {result['report']['title']}",
                        agent_type="report_generator",
                        metadata={
                            "report_title": result['report']['title'],
                            "custom_keyword": custom_keyword if custom_keyword else None
                        }
                    )

                    # Display the report
                    st.markdown("<div class='sub-header'>Report</div>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='report-container'>
                        <h3>{result['report']['title']}</h3>
                        <h4>Executive Summary</h4>
                        <p>{result['report']['summary']}</p>
                        <h4>Full Report</h4>
                        <div class="report-content">{result['report']['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

elif page == "Question Answering":
    st.markdown("<div class='main-header'>Question Answering</div>", unsafe_allow_html=True)
    st.markdown("Ask questions about the Market reports stored in the database.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Form for question answering
    with st.form("qa_form"):
        question = st.text_area("Your Question:", height=100)

        # Optional filters
        st.markdown("### Optional Filters")

        # Always show filters instead of hiding behind checkbox
        col1, col2 = st.columns(2)
        with col1:
            sector = st.selectbox("Sector", [
                "", "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                "Energy", "Construction", "Agriculture", "Retail",
                "Financial Services", "Manufacturing"
            ])
        with col2:
            country = st.selectbox("Country", [
                "", "France", "Germany", "UK", "US", "China", "Japan",
                "Italy", "Spain", "Brazil", "India"
            ])

        col3, col4 = st.columns(2)
        with col3:
            financial_product = st.selectbox("Financial Product", [
                "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
            ])
        with col4:
            # Add custom keyword input
            custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                        help="Enter any additional keyword to refine your search (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

        submitted = st.form_submit_button("Ask Question")

        if submitted and question:
            # Show spinner while processing question
            with st.spinner("Processing your question..."):
                # Prepare parameters
                parameters = {
                    "question": question
                }
                if sector:
                    parameters["sector"] = sector
                if country:
                    parameters["country"] = country
                if financial_product:
                    parameters["financial_product"] = financial_product
                if custom_keyword:
                    parameters["custom_keyword"] = custom_keyword

                # Process with QA agent
                result = orchestrator.qa_agent.process(parameters)

                # Display results
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("Question answered!")

                    # Store query in Supabase
                    entities = {
                        "sector": sector if sector else "All",
                        "country": country if country else "All",
                        "financial_product": financial_product if financial_product else "All"
                    }

                    SupabaseService.store_query(
                        query_text=question,
                        entities=entities,
                        intent="question_answering",
                        response=result['answer'],
                        agent_type="qa_agent",
                        metadata={
                            "reports_used": len(result['reports_used']),
                            "custom_keyword": custom_keyword if custom_keyword else None
                        }
                    )

                    # Add to session state query history for backward compatibility
                    query_record = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "question": question,
                        "answer": result['answer'],
                        "reports_used": len(result['reports_used']),
                        "sector": sector if sector else "All",
                        "country": country if country else "All",
                        "financial_product": financial_product if financial_product else "All",
                        "custom_keyword": custom_keyword if custom_keyword else "None"
                    }
                    st.session_state.query_history.append(query_record)

                    # Display the answer
                    st.markdown("<div class='sub-header'>Answer</div>", unsafe_allow_html=True)
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='card'>
                        <div class='answer-text'>{result['answer']}</div>
                        <p class='info-text'>Based on {len(result['reports_used'])} reports</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display the reports used
                    if result['reports_used']:
                        st.markdown("<div class='sub-header'>Reports Used</div>", unsafe_allow_html=True)
                        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                        for report in result['reports_used']:
                            st.markdown(f"- {report['title']}")

elif page == "Workflow Builder":
    st.markdown("<div class='main-header'>Workflow Builder</div>", unsafe_allow_html=True)
    st.markdown("Create and execute multi-step workflows involving multiple agents.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Workflow builder interface
    if st.session_state.current_workflow is None:
        st.session_state.current_workflow = {
            "steps": [],
            "context": {}
        }

    # Display current workflow
    if st.session_state.current_workflow["steps"]:
        st.markdown("<div class='sub-header'>Current Workflow</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        for i, step in enumerate(st.session_state.current_workflow["steps"]):
            agent_name = step["agent"].replace("_", " ").title()
            st.markdown(f"""
            <div class='card'>
                <span class='agent-tag'>{agent_name}</span>
                <b>Step {i+1}</b>
                <p>{json.dumps(step['parameters'], indent=2)}</p>
            </div>
            """, unsafe_allow_html=True)

    # Add step to workflow
    st.markdown("<div class='sub-header'>Add Step to Workflow</div>", unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    with st.form("add_step_form"):
        agent_type = st.selectbox("Agent Type", [
            "data_collector", "report_generator", "qa_agent"
        ])

        # Parameters based on agent type
        if agent_type == "data_collector":
            sector = st.selectbox("Sector", [
                "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                "Energy", "Construction", "Agriculture", "Retail",
                "Financial Services", "Manufacturing"
            ])
            country = st.selectbox("Country", [
                "France", "Germany", "UK", "US", "China", "Japan",
                "Italy", "Spain", "Brazil", "India"
            ])
            financial_product = st.selectbox("Financial Product (Optional)", [
                "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
            ])

            # Add custom keyword input
            custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                          help="Enter any additional keyword to refine your search (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

            parameters = {
                "sector": sector,
                "country": country
            }
            if financial_product:
                parameters["financial_product"] = financial_product
            if custom_keyword:
                parameters["custom_keyword"] = custom_keyword

        elif agent_type == "report_generator":
            use_context = st.checkbox("Use context from previous steps")

            if use_context:
                parameters = {}
            else:
                sector = st.selectbox("Sector", [
                    "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                    "Energy", "Construction", "Agriculture", "Retail",
                    "Financial Services", "Manufacturing"
                ])
                country = st.selectbox("Country", [
                    "France", "Germany", "UK", "US", "China", "Japan",
                    "Italy", "Spain", "Brazil", "India"
                ])
                financial_product = st.selectbox("Financial Product (Optional)", [
                    "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
                ])

                # Add custom keyword input
                custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                              help="Enter any additional keyword to refine your report (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

                parameters = {
                    "sector": sector,
                    "country": country
                }
                if financial_product:
                    parameters["financial_product"] = financial_product
                if custom_keyword:
                    parameters["custom_keyword"] = custom_keyword

        elif agent_type == "qa_agent":
            question = st.text_area("Question:", height=100)
            use_context = st.checkbox("Use context from previous steps")

            parameters = {
                "question": question
            }

            if not use_context:
                sector = st.selectbox("Sector (Optional)", [
                    "", "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                    "Energy", "Construction", "Agriculture", "Retail",
                    "Financial Services", "Manufacturing"
                ])
                country = st.selectbox("Country (Optional)", [
                    "", "France", "Germany", "UK", "US", "China", "Japan",
                    "Italy", "Spain", "Brazil", "India"
                ])
                financial_product = st.selectbox("Financial Product (Optional)", [
                    "", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"
                ])

                # Add custom keyword input
                custom_keyword = st.text_input("Custom Keyword (Optional)", "",
                                              help="Enter any additional keyword to refine your search (e.g., 'electric vehicles', 'sustainable finance', 'digital transformation')")

                if sector:
                    parameters["sector"] = sector
                if country:
                    parameters["country"] = country
                if financial_product:
                    parameters["financial_product"] = financial_product
                if custom_keyword:
                    parameters["custom_keyword"] = custom_keyword

        update_context = st.checkbox("Update workflow context with results")

        submitted = st.form_submit_button("Add Step")

        if submitted:
            # Add step to workflow
            step = {
                "agent": agent_type,
                "parameters": parameters
            }

            if update_context:
                step["update_context"] = ["sector", "country", "financial_product", "custom_keyword"]

            st.session_state.current_workflow["steps"].append(step)
            st.rerun()

    # Execute workflow
    if st.session_state.current_workflow["steps"]:
        if st.button("Execute Workflow"):
            with st.spinner("Executing workflow..."):
                # Execute the workflow
                results = orchestrator.execute_workflow(st.session_state.current_workflow)
                st.session_state.workflow_results = results

                # Store workflow execution in Supabase
                workflow_steps = [step["agent"] for step in st.session_state.current_workflow["steps"]]
                workflow_summary = f"Executed workflow with {len(workflow_steps)} steps: {', '.join(workflow_steps)}"

                # Extract parameters from the first step for metadata
                entities = {}
                metadata = {"workflow_steps": workflow_steps}

                if st.session_state.current_workflow["steps"]:
                    first_step = st.session_state.current_workflow["steps"][0]
                    if "parameters" in first_step:
                        if "sector" in first_step["parameters"]:
                            entities["sector"] = first_step["parameters"]["sector"]
                        if "country" in first_step["parameters"]:
                            entities["country"] = first_step["parameters"]["country"]
                        if "financial_product" in first_step["parameters"]:
                            entities["financial_product"] = first_step["parameters"]["financial_product"]

                        # Extract custom_keyword if it exists
                        custom_keyword = first_step["parameters"].get("custom_keyword", None)
                        if custom_keyword:
                            metadata["custom_keyword"] = custom_keyword

                SupabaseService.store_query(
                    query_text=workflow_summary,
                    entities=entities,
                    intent="workflow_execution",
                    response=f"Workflow executed with {len(results['results'])} results",
                    agent_type="workflow_builder",
                    metadata=metadata
                )

                st.rerun()

    # Reset workflow
    if st.session_state.current_workflow["steps"]:
        if st.button("Reset Workflow"):
            st.session_state.current_workflow = {
                "steps": [],
                "context": {}
            }
            st.session_state.workflow_results = None
            st.rerun()

    # Display workflow results
    if st.session_state.workflow_results:
        st.markdown("<div class='sub-header'>Workflow Results</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        for i, result in enumerate(st.session_state.workflow_results["results"]):
            agent_name = result["agent"].replace("_", " ").title()
            st.markdown(f"""
            <div class='card'>
                <span class='agent-tag'>{agent_name}</span>
                <b>Step {i+1} Results</b>
            </div>
            """, unsafe_allow_html=True)

            # Display appropriate results based on agent type
            if result["agent"] == "data_collector":
                if "error" in result["result"]:
                    st.error(f"Error: {result['result']['error']}")
                else:
                    st.success(f"Collected {len(result['result']['collected_data'])} data points")
                    st.json(result["result"]["collected_data"])

            elif result["agent"] == "report_generator":
                if "error" in result["result"]:
                    st.error(f"Error: {result['result']['error']}")
                else:
                    st.success(f"Generated report: {result['result']['report']['title']}")
                    st.markdown(f"### Summary\n{result['result']['report']['summary']}")
                    with st.expander("View Full Report"):
                        st.markdown(f"""
                        <div class='report-container'>
                            <div class='report-content'>{result['result']['report']['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            elif result["agent"] == "qa_agent":
                if "error" in result["result"]:
                    st.error(f"Error: {result['result']['error']}")
                else:
                    st.markdown(f"### Answer\n{result['result']['answer']}")
                    st.markdown(f"Based on {len(result['result']['reports_used'])} reports")

elif page == "Data Explorer":
    st.markdown("<div class='main-header'>Data Explorer</div>", unsafe_allow_html=True)
    st.markdown("Explore the data stored in the database.")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Initialize auto_refresh in session state if it doesn't exist
    if 'auto_refresh_data' not in st.session_state:
        st.session_state.auto_refresh_data = True

    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh data when tab is opened", value=st.session_state.auto_refresh_data)
    st.session_state.auto_refresh_data = auto_refresh

    # Reset loaded flags when changing auto-refresh setting
    if 'prev_auto_refresh' not in st.session_state or st.session_state.prev_auto_refresh != auto_refresh:
        if 'market_data_loaded' in st.session_state:
            del st.session_state.market_data_loaded
        if 'reports_loaded' in st.session_state:
            del st.session_state.reports_loaded
        if 'queries_loaded' in st.session_state:
            del st.session_state.queries_loaded
        st.session_state.prev_auto_refresh = auto_refresh

    # Tabs for different data types
    tab1, tab2, tab3, tab4 = st.tabs(["Market Data", "Reports", "Queries", "Bulk Data Collection"])

    with tab1:
        st.markdown("<div class='sub-header'>Market Data</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Display total count of Market data entries
        total_market_data = len(SupabaseService.get_market_data())
        st.markdown(f"<p style='color: #111827;'><strong style='color: #111827;'>Total Market data entries:</strong> {total_market_data}</p>", unsafe_allow_html=True)

        if total_market_data == 0:
            st.warning("No Market data found in the database. Use the Data Collection tab to collect data first.")

        # Filters for Market data
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sector_filter = st.selectbox("Filter by Sector", ["All", "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                "Energy", "Construction", "Agriculture", "Retail",
                "Financial Services", "Manufacturing"])
        with col2:
            country_filter = st.selectbox("Filter by Country", ["All", "France", "Germany", "UK", "US", "China", "Japan",
                "Italy", "Spain", "Brazil", "India"])
        with col3:
            data_point_filter = st.selectbox("Filter by Data Point", ["All", "market_size", "growth_rate", "key_players",
                "market_trends", "regulatory_factors", "economic_indicators"])
        with col4:
            keyword_filter = st.text_input("Filter by Custom Keyword", "",
                                          help="Enter a keyword like 'electric car' to filter data")

        # Add a clear filters button
        if st.button("Clear Filters"):
            sector_filter = "All"
            country_filter = "All"
            data_point_filter = "All"
            keyword_filter = ""
            # Force refresh
            if 'market_data_loaded' in st.session_state:
                del st.session_state.market_data_loaded
            st.rerun()

        # Get Market data
        refresh_button = st.button("Refresh Market Data")

        # Auto-refresh or manual refresh
        if refresh_button or (st.session_state.auto_refresh_data and 'market_data_loaded' not in st.session_state):
            with st.spinner("Loading Market data..."):
                # Apply filters
                sector = None if sector_filter == "All" else sector_filter
                country = None if country_filter == "All" else country_filter
                data_point = None if data_point_filter == "All" else data_point_filter
                custom_keyword = None if not keyword_filter else keyword_filter

                market_data = SupabaseService.get_market_data(sector=sector, country=country, data_point=data_point, custom_keyword=custom_keyword)

                # Mark as loaded
                st.session_state.market_data_loaded = True

                if not market_data:
                    st.info("No Market data found with the specified filters.")
                else:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(market_data)

                    # Ensure all columns are serializable to Arrow format
                    for col in df.columns:
                        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

                    # Format dates with error handling
                    if 'date' in df.columns:
                        try:
                            # Try to convert dates with flexible parsing
                            df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
                            # Replace NaT values with original strings
                            mask = df['date'].isna()
                            if mask.any():
                                df.loc[mask, 'date'] = [str(d)[:10] if d else 'N/A' for d in df.loc[mask, 'date'].index.map(lambda i: market_data[i].get('date'))]
                        except Exception as e:
                            st.warning(f"Could not format some dates properly: {str(e)}")
                            # Keep original date strings
                            df['date'] = df['date'].astype(str).apply(lambda x: x[:10] if len(x) > 10 else x)

                    if 'created_at' in df.columns:
                        try:
                            df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                            # Replace NaT values with original strings
                            mask = df['created_at'].isna()
                            if mask.any():
                                df.loc[mask, 'created_at'] = [str(d)[:16] if d else 'N/A' for d in df.loc[mask, 'created_at'].index.map(lambda i: market_data[i].get('created_at'))]
                        except Exception as e:
                            st.warning(f"Could not format some timestamps properly: {str(e)}")
                            # Keep original timestamp strings
                            df['created_at'] = df['created_at'].astype(str).apply(lambda x: x[:16] if len(x) > 16 else x)

                    # Display data
                    st.markdown(f"**Found {len(market_data)} data points matching your filters:**")
                    st.dataframe(df)

                    # Display data in a more readable format
                    st.markdown("<div class='sub-header'>Data Points Details</div>", unsafe_allow_html=True)
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    for i, data in enumerate(market_data):
                        with st.expander(f"{data['sector']} - {data['country']} - {data['data_point']}"):
                            st.markdown(f"""
                            <div class='card'>
                                <h4>{data['data_point'].replace('_', ' ').title()}</h4>
                                <p><b>Value:</b> {data['value']}</p>
                                <p><b>Source:</b> {data['source']}</p>
                                <p><b>Date:</b> {data['date'][:10] if data['date'] else 'N/A'}</p>
                                {f"<p><b>Custom Keyword:</b> {data['custom_keyword']}</p>" if data.get('custom_keyword') else ""}
                                <p><b>Created At:</b> {data['created_at'][:16] if data['created_at'] else 'N/A'}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # Add debug section
                    with st.expander("Debug Information"):
                        st.markdown("### Raw Data in Memory")
                        st.markdown("This section shows the raw data stored in the in-memory database, which can help diagnose issues with data storage and retrieval.")
                        st.markdown(f"**Total records in mock_db['market_data']:** {len(mock_db['market_data'])}")

                        # Show all custom keywords in the database
                        all_keywords = set()
                        for item in mock_db["market_data"]:
                            if item.get("custom_keyword"):
                                all_keywords.add(item.get("custom_keyword"))
                            # Also check metadata
                            if isinstance(item.get("metadata"), dict) and item.get("metadata").get("custom_keyword"):
                                all_keywords.add(item.get("metadata").get("custom_keyword"))
                            elif isinstance(item.get("metadata"), str):
                                try:
                                    metadata_dict = json.loads(item.get("metadata"))
                                    if metadata_dict.get("custom_keyword"):
                                        all_keywords.add(metadata_dict.get("custom_keyword"))
                                except:
                                    pass

                        st.markdown(f"**All custom keywords in database:** {', '.join(all_keywords) if all_keywords else 'None'}")

                        # Show raw data for debugging
                        if st.checkbox("Show Raw Data"):
                            st.json(mock_db["market_data"])

    with tab2:
        st.markdown("<div class='sub-header'>Reports</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Display total count of reports
        total_reports = len(SupabaseService.get_reports())
        st.markdown(f"**Total reports:** {total_reports}")

        if total_reports == 0:
            st.warning("No reports found in the database. Use the Report Generation tab to generate reports first.")

        # Filters for reports
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sector_filter = st.selectbox("Filter Reports by Sector", ["All", "Healthcare", "Technology", "Transportation", "Industrial Equipment",
                "Energy", "Construction", "Agriculture", "Retail",
                "Financial Services", "Manufacturing"])
        with col2:
            country_filter = st.selectbox("Filter Reports by Country", ["All", "France", "Germany", "UK", "US", "China", "Japan",
                "Italy", "Spain", "Brazil", "India"])
        with col3:
            product_filter = st.selectbox("Filter Reports by Product", ["All", "Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"])
        with col4:
            keyword_filter = st.text_input("Filter Reports by Keyword", "")

        # Get reports
        refresh_button = st.button("Refresh Reports")

        # Auto-refresh or manual refresh
        if refresh_button or (st.session_state.auto_refresh_data and 'reports_loaded' not in st.session_state):
            with st.spinner("Loading reports..."):
                # Apply filters
                sector = None if sector_filter == "All" else sector_filter
                country = None if country_filter == "All" else country_filter
                financial_product = None if product_filter == "All" else product_filter
                custom_keyword = None if not keyword_filter else keyword_filter

                reports = SupabaseService.get_reports(sector=sector, country=country, financial_product=financial_product, custom_keyword=custom_keyword)

                # Mark as loaded
                st.session_state.reports_loaded = True

                if not reports:
                    st.info("No reports found with the specified filters.")
                else:
                    # Convert to DataFrame for display if needed
                    df = pd.DataFrame(reports)

                    # Ensure all columns are serializable to Arrow format
                    for col in df.columns:
                        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

                    # Format dates with error handling if needed
                    if 'created_at' in df.columns:
                        try:
                            df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                            # Replace NaT values with original strings
                            mask = df['created_at'].isna()
                            if mask.any():
                                df.loc[mask, 'created_at'] = [str(d)[:16] if d else 'N/A' for d in df.loc[mask, 'created_at'].index.map(lambda i: reports[i].get('created_at'))]
                        except Exception as e:
                            st.warning(f"Could not format some timestamps properly: {str(e)}")
                            # Keep original timestamp strings
                            df['created_at'] = df['created_at'].astype(str).apply(lambda x: x[:16] if len(x) > 16 else x)

                    if 'updated_at' in df.columns:
                        try:
                            df['updated_at'] = pd.to_datetime(df['updated_at'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                            # Replace NaT values with original strings
                            mask = df['updated_at'].isna()
                            if mask.any():
                                df.loc[mask, 'updated_at'] = [str(d)[:16] if d else 'N/A' for d in df.loc[mask, 'updated_at'].index.map(lambda i: reports[i].get('updated_at'))]
                        except Exception as e:
                            # Keep original timestamp strings
                            df['updated_at'] = df['updated_at'].astype(str).apply(lambda x: x[:16] if len(x) > 16 else x)

                    # Display summary of reports
                    st.markdown(f"**Found {len(reports)} reports matching your filters:**")
                    st.markdown("<div class='sub-header'>Report Details</div>", unsafe_allow_html=True)
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

                    # Display reports as expandable cards
                    for report in reports:
                        # Format the date for display with error handling
                        created_at_display = "N/A"
                        if report.get('created_at'):
                            try:
                                if isinstance(report['created_at'], str) and 'T' in report['created_at']:
                                    created_at_display = report['created_at'].split('T')[0]
                                else:
                                    created_at_display = str(report['created_at'])[:10]
                            except:
                                created_at_display = str(report['created_at'])[:10]

                        with st.expander(f"{report['title']} ({created_at_display})"):
                            st.markdown(f"### Summary\n{report['summary']}")

                            # Display metadata
                            st.markdown("### Metadata")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**Sector:** {report['sector']}")
                            with col2:
                                st.markdown(f"**Country:** {report['country']}")
                            with col3:
                                st.markdown(f"**Financial Product:** {report['financial_product']}")

                            if report.get('custom_keyword'):
                                st.markdown(f"**Custom Keyword:** {report['custom_keyword']}")

                            st.markdown("### Full Report")
                            st.markdown(f"""
                            <div class='report-container'>
                                <div class='report-content'>{report['content']}</div>
                            </div>
                            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='sub-header'>Query History</div>", unsafe_allow_html=True)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Get all queries from the database
        all_queries = SupabaseService.get_queries()

        # Auto-refresh or manual refresh
        refresh_button = st.button("Refresh Queries")

        if refresh_button or (st.session_state.auto_refresh_data and 'queries_loaded' not in st.session_state):
            with st.spinner("Loading queries..."):
                # Get all queries from the database
                all_queries = SupabaseService.get_queries()

                # Mark as loaded
                st.session_state.queries_loaded = True

        if not all_queries:
            st.info("No queries have been made yet. Use the Question Answering section to ask questions about Market reports.")
        else:
            # Add search/filter functionality
            search_term = st.text_input("Search in questions or answers:", "")

            # Filter options
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                date_filter = st.date_input("Filter by date:", None)
            with filter_col2:
                agent_filter = st.selectbox("Filter by Agent Type:", ["All"] + list(set([q.get("agent_type", "Unknown") for q in all_queries if q.get("agent_type")])))
            with filter_col3:
                keyword_filter = st.selectbox("Filter by Keyword:", ["All"] + list(set([q.get("custom_keyword", "None") for q in all_queries if q.get("custom_keyword")])))

            # Apply filters
            filtered_queries = all_queries.copy()

            if search_term:
                filtered_queries = [q for q in filtered_queries if
                                   search_term.lower() in q.get("query", "").lower() or
                                   search_term.lower() in q.get("query_text", "").lower() or
                                   search_term.lower() in q.get("result", "").lower() or
                                   search_term.lower() in q.get("response", "").lower()]

            if date_filter:
                date_str = date_filter.strftime("%Y-%m-%d")
                filtered_queries = [q for q in filtered_queries if
                                   q.get("created_at", "").startswith(date_str) or
                                   q.get("timestamp", "").startswith(date_str)]

            if agent_filter != "All":
                filtered_queries = [q for q in filtered_queries if q.get("agent_type") == agent_filter]

            if keyword_filter != "All":
                filtered_queries = [q for q in filtered_queries if q.get("custom_keyword") == keyword_filter]

            # Display query history
            st.markdown(f"### Showing {len(filtered_queries)} of {len(all_queries)} queries")
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

            # Option to export query history
            if st.button("Export Query History to CSV"):
                # Convert to DataFrame
                query_df = pd.DataFrame(filtered_queries)

                # Ensure all columns are serializable
                for col in query_df.columns:
                    if query_df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        query_df[col] = query_df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

                # Convert to CSV
                csv = query_df.to_csv(index=False)

                # Create download button
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"query_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            # Display queries in reverse chronological order (newest first)
            for i, query in enumerate(reversed(filtered_queries)):
                # Get the query text and result
                query_text = query.get("query_text", query.get("query", "Unknown query"))
                result = query.get("response", query.get("result", "No result available"))

                # Format the timestamp for display with error handling
                timestamp_display = "Unknown date"
                timestamp = query.get("timestamp", query.get("created_at", ""))
                if timestamp:
                    try:
                        if isinstance(timestamp, str) and 'T' in timestamp:
                            timestamp_display = timestamp.split('T')[0] + " " + timestamp.split('T')[1][:5]
                        else:
                            timestamp_display = str(timestamp)[:16]
                    except:
                        timestamp_display = str(timestamp)[:16]

                with st.expander(f"{timestamp_display} - {query_text[:50]}{'...' if len(query_text) > 50 else ''}"):
                    st.markdown(f"**Question:**")
                    st.markdown(f"<div class='card'>{query_text}</div>", unsafe_allow_html=True)

                    st.markdown(f"**Answer:**")
                    st.markdown(f"<div class='card'><div class='answer-text'>{result}</div></div>", unsafe_allow_html=True)

                    # Metadata
                    st.markdown("**Metadata:**")
                    meta_col1, meta_col2 = st.columns(2)
                    with meta_col1:
                        st.markdown(f"**Agent Type:** {query.get('agent_type', 'Unknown')}")
                    with meta_col2:
                        if query.get('custom_keyword'):
                            st.markdown(f"**Custom Keyword:** {query.get('custom_keyword')}")

                    # Option to rerun this query
                    if st.button(f"Rerun this query", key=f"rerun_{i}"):
                        st.session_state.rerun_query = {
                            "question": query_text,
                            "agent_type": query.get("agent_type", "data_collection"),
                            "custom_keyword": query.get("custom_keyword")
                        }
                        st.session_state.page = "Question Answering"
                        st.rerun()

    with tab4:
        st.markdown("<div class='sub-header'>Bulk Data Collection</div>", unsafe_allow_html=True)
        st.markdown("Collect Market data for multiple sectors and countries and store it in the database.")
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # Form for bulk data collection
        with st.form("bulk_data_collection_form"):
            # Select sectors
            st.markdown("### Select Sectors")
            sectors_options = ["Healthcare", "Technology", "Transportation", "Industrial Equipment",
                "Energy", "Construction", "Agriculture", "Retail",
                "Financial Services", "Manufacturing"]

            sectors_cols = st.columns(2)
            selected_sectors = []

            for i, sector in enumerate(sectors_options):
                col_idx = i % 2
                with sectors_cols[col_idx]:
                    if st.checkbox(sector, value=True):
                        selected_sectors.append(sector)

            # Select countries
            st.markdown("### Select Countries")
            countries_options = ["France", "Germany", "UK", "US", "China", "Japan",
                "Italy", "Spain", "Brazil", "India"]

            countries_cols = st.columns(2)
            selected_countries = []

            for i, country in enumerate(countries_options):
                col_idx = i % 2
                with countries_cols[col_idx]:
                    if st.checkbox(country, value=True):
                        selected_countries.append(country)

            # Select financial products (optional)
            st.markdown("### Select Financial Products (Optional)")
            products_options = ["Leasing", "SALB (Sale and Lease Back)", "Loan", "Rental", "Asset Finance"]

            products_cols = st.columns(2)
            selected_products = []

            for i, product in enumerate(products_options):
                col_idx = i % 2
                with products_cols[col_idx]:
                    if st.checkbox(product):
                        selected_products.append(product)

            # Custom keywords (optional)
            st.markdown("### Custom Keywords (Optional)")
            st.markdown("Enter custom keywords to refine your search, one per line:")
            custom_keywords_text = st.text_area(
                label="Custom Keywords",
                value="",
                height=100,
                help="Enter keywords like 'electric vehicles', 'sustainable finance', 'digital transformation', etc. One keyword per line.",
                label_visibility="collapsed"
            )

            # Parse custom keywords
            custom_keywords = []
            if custom_keywords_text:
                custom_keywords = [kw.strip() for kw in custom_keywords_text.split('\n') if kw.strip()]

            # Submit button
            submitted = st.form_submit_button("Start Data Collection")

            if submitted:
                if not selected_sectors:
                    st.error("Please select at least one sector.")
                elif not selected_countries:
                    st.error("Please select at least one country.")
                else:
                    # Create a progress container
                    progress_container = st.empty()
                    progress_container.markdown("<div class='card'><p class='progress-text'>Starting data collection...</p></div>", unsafe_allow_html=True)

                    # Create a results container
                    results_container = st.empty()

                    # Track progress
                    total_combinations = len(selected_sectors) * len(selected_countries)
                    if selected_products:
                        total_combinations *= len(selected_products)
                    if custom_keywords:
                        total_combinations *= len(custom_keywords)
                    if not selected_products and not custom_keywords:
                        total_combinations = len(selected_sectors) * len(selected_countries)

                    completed = 0
                    successful = 0
                    failed = 0

                    # Store results for display
                    collection_results = []

                    # Collect data for each sector-country combination
                    for sector in selected_sectors:
                        for country in selected_countries:
                            # Process with different combinations
                            if selected_products and custom_keywords:
                                # Both products and keywords
                                for product in selected_products:
                                    for keyword in custom_keywords:
                                        completed += 1
                                        progress_container.markdown(
                                            f"<div class='card'><p class='progress-text'>Processing {completed}/{total_combinations}: {sector} in {country}, {product}, keyword: {keyword}</p></div>",
                                            unsafe_allow_html=True
                                        )

                                        # Prepare parameters
                                        parameters = {
                                            "sector": sector,
                                            "country": country,
                                            "financial_product": product,
                                            "custom_keyword": keyword
                                        }

                                        # Process with data collector agent
                                        try:
                                            result = orchestrator.data_collector.process(parameters)

                                            if "error" in result:
                                                failed += 1
                                                collection_results.append({
                                                    "sector": sector,
                                                    "country": country,
                                                    "financial_product": product,
                                                    "custom_keyword": keyword,
                                                    "status": "Failed",
                                                    "message": result["error"]
                                                })
                                            else:
                                                successful += 1
                                                data_points = len(result["collected_data"])
                                                collection_results.append({
                                                    "sector": sector,
                                                    "country": country,
                                                    "financial_product": product,
                                                    "custom_keyword": keyword,
                                                    "status": "Success",
                                                    "message": f"Collected {data_points} data points"
                                                })
                                        except Exception as e:
                                            failed += 1
                                            collection_results.append({
                                                "sector": sector,
                                                "country": country,
                                                "financial_product": product,
                                                "custom_keyword": keyword,
                                                "status": "Error",
                                                "message": str(e)
                                            })
                            elif selected_products:
                                # Only products, no keywords
                                for product in selected_products:
                                    completed += 1
                                    progress_container.markdown(
                                        f"<div class='card'><p class='progress-text'>Processing {completed}/{total_combinations}: {sector} in {country}, {product}</p></div>",
                                        unsafe_allow_html=True
                                    )

                                    # Prepare parameters
                                    parameters = {
                                        "sector": sector,
                                        "country": country,
                                        "financial_product": product
                                    }

                                    # Process with data collector agent
                                    try:
                                        result = orchestrator.data_collector.process(parameters)

                                        if "error" in result:
                                            failed += 1
                                            collection_results.append({
                                                "sector": sector,
                                                "country": country,
                                                "financial_product": product,
                                                "status": "Failed",
                                                "message": result["error"]
                                            })
                                        else:
                                            successful += 1
                                            data_points = len(result["collected_data"])
                                            collection_results.append({
                                                "sector": sector,
                                                "country": country,
                                                "financial_product": product,
                                                "status": "Success",
                                                "message": f"Collected {data_points} data points"
                                            })
                                    except Exception as e:
                                        failed += 1
                                        collection_results.append({
                                            "sector": sector,
                                            "country": country,
                                            "financial_product": product,
                                            "status": "Error",
                                            "message": str(e)
                                        })
                            elif custom_keywords:
                                # Only keywords, no products
                                for keyword in custom_keywords:
                                    completed += 1
                                    progress_container.markdown(
                                        f"<div class='card'><p class='progress-text'>Processing {completed}/{total_combinations}: {sector} in {country}, keyword: {keyword}</p></div>",
                                        unsafe_allow_html=True
                                    )

                                    # Prepare parameters
                                    parameters = {
                                        "sector": sector,
                                        "country": country,
                                        "custom_keyword": keyword
                                    }

                                    # Process with data collector agent
                                    try:
                                        result = orchestrator.data_collector.process(parameters)

                                        if "error" in result:
                                            failed += 1
                                            collection_results.append({
                                                "sector": sector,
                                                "country": country,
                                                "custom_keyword": keyword,
                                                "status": "Failed",
                                                "message": result["error"]
                                            })
                                        else:
                                            successful += 1
                                            data_points = len(result["collected_data"])
                                            collection_results.append({
                                                "sector": sector,
                                                "country": country,
                                                "custom_keyword": keyword,
                                                "status": "Success",
                                                "message": f"Collected {data_points} data points"
                                            })
                                    except Exception as e:
                                        failed += 1
                                        collection_results.append({
                                            "sector": sector,
                                            "country": country,
                                            "custom_keyword": keyword,
                                            "status": "Error",
                                            "message": str(e)
                                        })
                            else:
                                # No products or keywords
                                completed += 1
                                progress_container.markdown(
                                    f"<div class='card'><p class='progress-text'>Processing {completed}/{total_combinations}: {sector} in {country}</p></div>",
                                    unsafe_allow_html=True
                                )

                                # Prepare parameters
                                parameters = {
                                    "sector": sector,
                                    "country": country
                                }

                                # Process with data collector agent
                                try:
                                    result = orchestrator.data_collector.process(parameters)

                                    if "error" in result:
                                        failed += 1
                                        collection_results.append({
                                            "sector": sector,
                                            "country": country,
                                            "status": "Failed",
                                            "message": result["error"]
                                        })
                                    else:
                                        successful += 1
                                        data_points = len(result["collected_data"])
                                        collection_results.append({
                                            "sector": sector,
                                            "country": country,
                                            "status": "Success",
                                            "message": f"Collected {data_points} data points"
                                        })
                                except Exception as e:
                                    failed += 1
                                    collection_results.append({
                                        "sector": sector,
                                        "country": country,
                                        "status": "Error",
                                        "message": str(e)
                                    })

                    # Update final progress
                    progress_container.markdown(
                        f"<div class='card'><p class='progress-text'>Data collection completed: {successful} successful, {failed} failed</p></div>",
                        unsafe_allow_html=True
                    )

                    # Display results
                    results_df = pd.DataFrame(collection_results)
                    results_container.dataframe(results_df)

                    # Option to generate reports based on collected data
                    if successful > 0:
                        if st.button("Generate Reports from Collected Data"):
                            st.info("This will generate reports for all successfully collected data. This may take some time.")
                            # Implementation for report generation would go here

# Footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown(f"<div class='card' style='text-align: center; border-left: none; border-top: 4px solid #00965E;'><p class='info-text'> © {datetime.now().year} Market Intelligence Platform | Powered by Agentic MCP</p></div>", unsafe_allow_html=True)
