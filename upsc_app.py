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
    .stButton>button { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: white !important; border-radius: 25px; border: none; }
    h1, h2, h3 { background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    [data-testid="stSidebar"] { background: linear-gradient(to bottom, #141E30, #243B55) !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 { color: #ffffff !important; }
    .stTextInput div[data-baseweb="base-input"] { background-color: #ffffff !important; border-radius: 8px !important; }
    .stTextInput input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; caret-color: #000000 !important; }
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
# AI Generation Engine
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # NEW STRATEGY: Explicitly telling AI to avoid all backslashes in DOT code
    prompt = f"""
    Generate a JSON study dashboard for: "{topic}".
    
    STRICT RULES:
    1. FLOWCHARTS: Generate 5 Graphviz DOT codes (rankdir=TB). 
       DO NOT use backslashes (\). If you need line breaks, use <br/> tags.
       Use single quotes inside DOT strings to avoid JSON conflict.
    2. JSON: Must be perfect.
    
    Structure:
    {{
        "title": "Topic",
        "explanation": "3 paras.",
        "important_topics": ["T1", "T2"],
        "one_pager": {{"Basis": "...", "Stats": "...", "Keywords": "...", "Context": "...", "Challenges": "..."}},
        "flowcharts": [
            {{"title": "Title", "code": "digraph G {{ rankdir=TB; node [shape=box]; A -> B; }}"}}
        ],
        "current_affairs": [{{"gs_paper": "GS 3", "headline": "...", "relevance": "...", "impact": "..."}}],
        "pyq_prelims": [{{"year": 2023, "q": "...", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."}}],
        "pyq_mains": [{{"year": 2023, "q": "..."}}]
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Generation Error: {e}")
        return None

# ---------------------------------------------------------
# UI Logic
# ---------------------------------------------------------
st.sidebar.markdown("## ✨ UPSC Pro Dash")
search_query = st.sidebar.text_input("Enter Topic:")
if st.sidebar.button("🚀 Launch"):
    if search_query:
        with st.spinner("Forging dashboard..."):
            st.session_state.current_data = fetch_topic_data_from_ai(search_query)
            st.rerun()

if 'current_data' in st.session_state and st.session_state.current_data:
    data = st.session_state.current_data
    page = st.sidebar.radio("Navigate", ["Explanation", "Cheat Sheet", "Maps", "Current Affairs", "Prelims", "Mains"])
    
    if page == "Explanation":
        st.header(data['title'])
        st.markdown(data['explanation'])
    elif page == "Cheat Sheet":
        for k, v in data['one_pager'].items(): st.info(f"**{k}**: {v}")
    elif page == "Maps":
        for fc in data['flowcharts']:
            with st.expander(fc['title']): st.graphviz_chart(fc['code'])
    # ... (Add remaining pages as structured in previous code)
    
