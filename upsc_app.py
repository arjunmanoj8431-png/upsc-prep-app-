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
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    div.stAlert {
        border-radius: 15px !important;
        border-left: 5px solid #26D0CE !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #141E30, #243B55) !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2 { 
        color: #ffffff !important; 
    }
    .stTextInput div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border: 2px solid #26D0CE !important;
        border-radius: 8px !important;
    }
    .stTextInput input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        font-weight: 600 !important;
    }
    .stTextInput input::placeholder {
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
# AI Generation Engines (Strict JSON Enforcement)
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate a deep-dive study dashboard for: "{topic}".
    
    CRITICAL INSTRUCTIONS:
    1. EXPLANATION: 3 paragraphs max. Be hyper-concise.
    2. ONE-PAGER: 5-pillar summary. Brief bullet points.
    3. FLOWCHARTS: EXACTLY 5 Graphviz DOT flowcharts (rankdir=TB). DO NOT use double quotes inside the DOT code strings. Use single quotes if necessary.
    4. CURRENT AFFAIRS: EXACTLY 3 recent news developments.
    5. PRELIMS: EXACTLY 15 high-difficulty MCQs. (Keep options short. Explanations MUST be under 15 words).
    6. MAINS: EXACTLY 10 analytical Mains questions.
    
    Structure exactly like this:
    {{
        "title": "Clear Topic Title",
        "explanation": "Conceptual explanation here...",
        "important_topics": ["Subtopic 1", "Subtopic 2", "Subtopic 3", "Subtopic 4", "Subtopic 5"],
        "one_pager": {{
            "Constitutional_and_Legal_Basis": "Brief facts...",
            "High_Yield_Statistics_and_Reports": "Brief facts...",
            "Core_Conceptual_Keywords": "Brief facts...",
            "Current_Affairs_Context": "Brief facts...",
            "Critical_Challenges_and_Solutions": "Brief facts..."
        }},
        "flowcharts": [
            {{"title": "1. Core Mechanism", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightblue]; A -> B; }}"}},
            {{"title": "2. Historical Evolution", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightyellow]; A -> B; }}"}},
            {{"title": "3. Institutional Setup", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightgreen]; A -> B; }}"}},
            {{"title": "4. Impact Analysis", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightgrey]; A -> B; }}"}},
            {{"title": "5. Way Forward Strategy", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightpink]; A -> B; }}"}}
        ],
        "current_affairs": [
            {{
                "gs_paper": "GS Paper 3",
                "headline": "Brief Headline...",
                "relevance": "Brief syllabus connection...",
                "impact": "Brief impact..."
            }}
        ],
        "pyq_prelims": [
            {{
                "year": 2023, 
                "q": "Question text...", 
                "options": ["A) Opt 1", "B) Opt 2", "C) Opt 3", "D) Opt 4"], 
                "answer": "A) Opt 1", 
                "explanation": "Brief explanation..."
            }}
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "Mains question text..."}}
        ]
    }}
    """
    
    try:
        # NATIVE JSON ENFORCEMENT ADDED HERE
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192, 
                "temperature": 0.2,
                "response_mime_type": "application/json" 
            }
        )
        # Because we forced application/json, we no longer need clunky string parsing
        return json.loads(response.text)
    except Exception as e:
        # We will print the exact debug error to the screen so we can see if it fails again
        st.error(f"System Debug Error: {e}")
        return None

def evaluate_mains_answer(question, user_answer):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a strict, veteran civil services examiner evaluation board officer grading a UPSC Mains answer sheet.
    
    Question: {question}
    Candidate's Answer: {user_answer}
    
    Critique this response rigorously under exact UPSC standards out of a maximum of 15 marks. Be objective.
    
    Structure exactly:
    {{
        "marks_allocated": "X/15",
        "intro_critique": "Analysis of their opening...",
        "body_critique": "Analysis of arguments, dimensions explored...",
        "conclusion_critique": "Analysis of the way forward...",
        "explicit_strengths": ["Strength 1", "Strength 2"],
        "critical_improvements": ["Improvement 1", "Improvement 2"],
        "model_approach": "A brief overview of a top-scoring approach..."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"System Debug Error: {e}")
        return None

# ---------------------------------------------------------
# UI: Sidebar Navigation & App State
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: white;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., Agricultural Extension")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Forging deep-dive dashboard (Enforcing strict JSON protocol)..."):
            fresh_data = fetch_topic_data_from_ai(search_query)
            if fresh_data:
                st.session_state.current_data = fresh_data
                if 'active_evaluation' in st.session_state:
                    del st.session_state.active_evaluation
                st.toast
    
