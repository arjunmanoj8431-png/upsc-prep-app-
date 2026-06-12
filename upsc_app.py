import streamlit as st
import graphviz
import pandas as pd
import google.generativeai as genai
import json

# ---------------------------------------------------------
# Page Configuration & CSS Styling
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; border-radius: 20px; border: none; }
    h1, h2, h3 { background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .css-1r6slbo { background-color: rgba(0,0,0,0.05); }
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
# Generation Function
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate extensive, deep-dive study material for: "{topic}".
    
    CRITICAL: 
    - ONE-PAGER must be a 5-pillar strategic summary (A: Legal/Constitutional, B: High-Yield Stats/Committees, C: Key Concepts, D: Current Context, E: Challenges vs Solutions).
    - Provide EXACTLY 5 flowcharts (DOT format).
    - Provide EXACTLY 15 Prelims MCQs and 15 Mains questions.
    
    Respond ONLY with valid JSON. Structure:
    {{
        "title": "Topic Name",
        "explanation": "6+ paragraphs of deep analysis.",
        "important_topics": ["T1", "T2", "T3", "T4", "T5"],
        "one_pager": {{
            "Constitutional_Legal_Basis": "...",
            "High_Yield_Facts_Stats": "...",
            "Conceptual_Keywords": "...",
            "Current_Context": "...",
            "Challenges_and_Solutions": "..."
        }},
        "flowcharts": [
            {{"title": "Mechanism", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "Evolution", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "Institutional", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "Impact", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "Strategy", "code": "digraph G {{ A -> B; }}"}}
        ],
        "pyq_prelims": [
            {{"year": 2023, "q": "...", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."}}
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "..."}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(raw_text[start:end+1], strict=False)
        return None
    except:
        return None

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("✨ UPSC Pro Dash")
search_query = st.sidebar.text_input("Enter Syllabus Topic:")
if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Fetching deep-dive data..."):
            st.session_state.current_data = fetch_topic_data_from_ai(search_query)

# ---------------------------------------------------------
# Main UI
# ---------------------------------------------------------
if 'current_data' in st.session_state and st.session_state.current_data:
    data = st.session_state.current_data
    page = st.sidebar.radio("Navigate", ["Explanation", "One-Pager", "Flowcharts", "Prelims", "Mains"])
    
    if page == "Explanation":
        st.header(data['title'])
        st.markdown(data['explanation'])
        
    elif page == "One-Pager":
        st.subheader("Strategic Cheat Sheet")
        one_pager = data.get('one_pager', {})
        cols = st.columns(2)
        for i, (key, value) in enumerate(one_pager.items()):
            with cols[i % 2]:
                st.info(f"### {key.replace('_', ' ')}\n{value}")
                
    elif page == "Flowcharts":
        for fc in data.get('flowcharts', []):
            with st.expander(fc['title'], expanded=True):
                st.graphviz_chart(fc['code'])
                
    elif page == "Prelims":
        for i, q in enumerate(data.get('pyq_prelims', [])):
            with st.expander(f"Q{i+1}: {q['q']}"):
                choice = st.radio("Options", q['options'], key=f"p_{i}", index=None)
                if st.button("Check", key=f"b_{i}"):
                    st.write(f"Correct: {q['answer']}\n\nExplanation: {q['explanation']}")
                    
    elif page == "Mains":
        for q in data.get('pyq_mains', []):
            st.warning(f"**Mains Question:** {q['q']}")
            st.text_area("Your Answer:", key=q['q'][:10])

else:
    st.markdown("# UPSC Pro Dash")
    st.info("Enter a topic to generate your deep-dive dashboard.")
