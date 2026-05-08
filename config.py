import os
try:
    import streamlit as st
    GEMINI_API_KEY   = st.secrets["GEMINI_API_KEY"]
    GROQ_API_KEY     = st.secrets["GROQ_API_KEY"]
    TAVILY_API_KEY   = st.secrets["TAVILY_API_KEY"]
    PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
    MY_PASSWORD      = st.secrets["MY_PASSWORD"]
    ENCRYPTION_KEY   = st.secrets["ENCRYPTION_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY   = os.getenv("TAVILY_API_KEY", "")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    MY_PASSWORD      = os.getenv("MY_PASSWORD", "admin123")
    ENCRYPTION_KEY   = os.getenv("ENCRYPTION_KEY", "")
