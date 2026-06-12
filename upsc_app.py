import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(layout="wide")

# API Setup
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_ai_data(topic):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Generate a study guide for '{topic}'. Output ONLY valid JSON with these keys: 
    "title", "explanation" (max 3 paragraphs), "one_pager" (object with 5 keys), 
    "flowcharts" (list of 5 dicts with title/code), "prelims" (list of 15 dicts), 
    "mains" (list of 10 strings). Use single quotes inside flowcharts."""
    
    response = model.generate_content(prompt)
    text = response.text.replace('```json', '').replace('```', '')
    return json.loads(text)

st.title("🚀 UPSC Pro Dashboard")
topic = st.text_input("Enter Topic")

if st.button("Generate"):
    try:
        data = get_ai_data(topic)
        st.session_state.data = data
    except Exception as e:
        st.error(f"Error: {e}")

if 'data' in st.session_state:
    d = st.session_state.data
    st.header(d['title'])
    tab1, tab2, tab3 = st.tabs(["Explanation", "Prelims", "Mains"])
    with tab1: st.write(d['explanation'])
    with tab2:
        for i, q in enumerate(d['prelims']): st.write(f"{i+1}. {q['q']}")
    with tab3:
        for i, q in enumerate(d['mains']): st.write(f"{i+1}. {q}")
            
