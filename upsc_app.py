import streamlit as st
import graphviz
import json
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration & Bulletproof Adaptive CSS
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Animated Gradient Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        color: white !important;
        border-radius: 25px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
        transition: all 0.3s ease;
        font-weight: 700;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(255, 75, 43, 0.6);
    }
    
    /* Vibrant Headings that adapt to any background */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    
    /* Card-like Info Boxes */
    div.stAlert {
        border-radius: 15px !important;
        border-left: 5px solid #26D0CE !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* --- SIDEBAR & DARK MODE FIXES --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #141E30, #243B55) !important;
    }
    
    /* Make static sidebar text white */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2 { 
        color: #ffffff !important; 
    }
    
    /* The absolute fix for the search input in Dark Mode */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #26D0CE !important;
        border-radius: 8px !important;
    }
    
    /* Override Streamlit's stubborn Webkit Dark Mode text colors and the blinking cursor */
    div[data-baseweb="input"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        background-color: transparent !important;
        font-weight: 600;
    }
    
    /* Ensure placeholder text is visible but distinct */
    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# API Configuration
# ---------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ---------------------------------------------------------
# AI Data Generation (Strictly No Caching)
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate a massive, deep-dive study dashboard for: "{topic}".
    
    CRITICAL INSTRUCTIONS TO AVOID ERRORS:
    1. EXPLANATION: 6+ detailed paragraphs.
    2. ONE-PAGER: Must be a 5-pillar strategic summary using the exact keys below.
    3. FLOWCHARTS: Generate EXACTLY 5 Graphviz DOT flowcharts covering different angles (Mechanism, History, Setup, Impact, Solutions).
    4. PRELIMS: Generate EXACTLY 15 high-difficulty MCQs.
    5. MAINS: Generate EXACTLY 15 analytical Mains questions.
    
    Respond ONLY with a valid JSON object. Do not include markdown code blocks like ```json.
    
    Structure exactly like this:
    {{
        "title": "Clear Topic Title",
        "explanation": "Deep, conceptual explanation here...",
        "important_topics": ["Subtopic 1", "Subtopic 2", "Subtopic 3", "Subtopic 4", "Subtopic 5"],
        "one_pager": {{
            "Constitutional_and_Legal_Basis": "Detailed facts...",
            "High_Yield_Statistics_and_Reports": "Detailed facts...",
            "Core_Conceptual_Keywords": "Detailed facts...",
            "Current_Affairs_Context": "Detailed facts...",
            "Critical_Challenges_and_Solutions": "Detailed facts..."
        }},
        "flowcharts": [
            {{"title": "1. Core Mechanism", "code": "digraph G {{ rankdir=LR; node [style=filled, fillcolor=lightblue]; A -> B; }}"}},
            {{"title": "2. Historical Evolution", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "3. Institutional Setup", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "4. Impact Analysis", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "5. Way Forward Strategy", "code": "digraph G {{ A -> B; }}"}}
        ],
        "pyq_prelims": [
            {{
                "year": 2023, 
                "q": "Question text...", 
                "options": ["A) Opt 1", "B) Opt 2", "C) Opt 3", "D) Opt 4"],
