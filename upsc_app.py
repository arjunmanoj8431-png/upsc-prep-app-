import streamlit as st
import json
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="UPSC AI Pro", layout="wide")

# CSS
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    .stButton>button { border-radius: 20px; background: #26D0CE; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# API Setup
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def fetch_data(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Force JSON schema to prevent parsing errors
    prompt = f"""
    Create a study guide for '{topic}'. Output ONLY valid JSON:
    {{
        "title": "Topic",
        "explanation": "concise explanation",
        "flowchart": "digraph G {{ rankdir=TB; A -> B; }}",
        "prelims": [{{"q": "...", "opt": ["A", "B", "C", "D"], "ans": "A"}}],
        "mains": ["Q1", "Q2"]
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

# App UI
st.title("🚀 UPSC Pro Dashboard")
topic = st.text_input("Topic:")

if st.button("Launch Engine"):
    with st.spinner("Generating..."):
        st.session_state.data = fetch_data(topic)

if 'data' in st.session_state and st.session_state.data:
    d = st.session_state.data
    st.header(d['title'])
    
    tabs = st.tabs(["Explanation", "Flowchart", "Prelims", "Mains"])
    with tabs[0]: st.write(d['explanation'])
    with tabs[1]: st.graphviz_chart(d['flowchart'])
    with tabs[2]:
        for i, q in enumerate(d['prelims']): st.write(f"{i+1}. {q['q']}")
    with tabs[3]:
        for i, q in enumerate(d['mains']): st.write(f"{i+1}. {q}")
            
