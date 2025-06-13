import streamlit as st
import os

st.set_page_config(
    page_title="DocBot 💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType
import re

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 25px;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(99, 102, 241, 0.2);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        margin-left: 2rem;
    }
    
    .chat-message.bot {
        background: white;
        color: #1f2937;
        margin-right: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .chat-message .message {
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #dcfce7;
        color: #166534;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    /* Spinner styling */
    .stSpinner {
        text-align: center;
        padding: 2rem;
    }
    
    /* Help text styling */
    .stMarkdown p {
        color: #6b7280;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

def strip_markdown(text):
    text = re.sub(r"```(?:\w+)?", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Please set the GOOGLE_API_KEY environment variable")
    st.stop()

# Header
st.markdown("""
<div class="header">
    <h1>📄 DocBot — Your Documentation Assistant</h1>
    <p>Ask questions about any documentation and get instant answers</p>
</div>
""", unsafe_allow_html=True)

# URL input with custom styling
user_url = st.text_input(
    "Enter the documentation URL",
    placeholder="https://example.com/docs",
    help="Paste the URL of the documentation you want to chat with"
)

if "agent" not in st.session_state:
    st.session_state.agent = None
    st.session_state.history = []

# Load documentation button
if st.button("🔄 Load & Index Documentation", use_container_width=True) and user_url:
    with st.spinner("Loading and indexing documentation..."):
        knowledge = UrlKnowledge(
            urls=[user_url],
            vector_db=LanceDb(
                uri="tmp/lancedb",
                table_name="dynamic_docs",
                search_type=SearchType.hybrid,
                embedder=GeminiEmbedder(
                    id="embedding-001",
                    api_key=api_key,
                )
            ),
        )
        storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/agent.db")

        st.session_state.agent = Agent(
            model=Gemini(
                id="gemini-2.0-flash",
                api_key=api_key,
            ),
            tools=[],
            instructions=[
                "Search the loaded documentation before answering.",
                "Do not hallucinate. Only answer from the provided document.",
            ],
            knowledge=knowledge,
            storage=storage,
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            markdown=True,
        )
        st.session_state.agent.knowledge.load(recreate=True)
    st.success("✅ Documentation loaded successfully. You can start asking questions!")

# Chat interface
if st.session_state.agent:
    # Display chat history
    for q, a in st.session_state.history:
        st.markdown(f"""
        <div class="chat-message user">
            <div class="message"><strong>You:</strong> {q}</div>
        </div>
        <div class="chat-message bot">
            <div class="message"><strong>Bot:</strong> {a}</div>
        </div>
        """, unsafe_allow_html=True)

    # Input area
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("❓ Ask a question", key="user_question", label_visibility="collapsed")
    with col2:
        send_button = st.button("💬 Send", use_container_width=True)

    if (send_button or user_input) and user_input:
        with st.spinner("Thinking..."):
            answer = st.session_state.agent.run(user_input)
            response_text = answer.content if hasattr(answer, "content") else str(answer)
            cleaned_response = strip_markdown(response_text)

            st.session_state.history.append((user_input, cleaned_response))
            
            # Display new messages
            st.markdown(f"""
            <div class="chat-message user">
                <div class="message"><strong>You:</strong> {user_input}</div>
            </div>
            <div class="chat-message bot">
                <div class="message"><strong>Bot:</strong> {cleaned_response}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Clear the input
            st.session_state.user_question = ""

