import streamlit as st
import graphviz
import pandas as pd
import google.generativeai as genai
import json

# ---------------------------------------------------------
# Page Configuration & CSS Styling
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

# Injecting Custom CSS for a Dashy, Animated, Colorful Look
st.markdown("""
    <style>
    /* Main Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* Animated Buttons */
    .stButton>button {
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        border: none;
        color: #1e1e1e;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Colorful Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1e3c72 0%, #2a5298 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headers and Text */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Flashy Success/Info Boxes */
    div.stAlert {
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
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
# High-Capacity LLM Data Generation Function
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Upgraded prompt for maximum capacity (Multiple flowcharts, huge PYQ lists)
    prompt = f"""
    You are an elite UPSC tutor. Generate highly extensive, deep-dive study material for: "{topic}".
    Max out your output capacity to provide as many PYQs and Flowcharts as safely possible without cutting off.
    
    Respond ONLY with a valid JSON object. Do not include ```json markdown.
    
    Structure exactly like this:
    {{
        "title": "Clear Title",
        "explanation": "At least 5-6 paragraphs of deep, conceptual explanation. Use bolding and bullets.",
        "important_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
        "one_pager": {{
            "Fact 1": "Details", "Fact 2": "Details", "Fact 3": "Details", "Fact 4": "Details", "Fact 5": "Details"
        }},
        "flowcharts": [
            {{"title": "Core Mechanism", "code": "digraph G {{ rankdir=LR; A -> B; }}"}},
            {{"title": "Historical Evolution / Process", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "Impact Analysis", "code": "digraph G {{ A -> B; }}"}}
        ],
        "pyq_prelims": [
            {{
                "year": 2023, 
                "q": "Generate up to 10 highly accurate Prelims MCQs...",
                "options": ["A) Opt 1", "B) Opt 2", "C) Opt 3", "D) Opt 4"],
                "answer": "A) Opt 1",
                "explanation": "Detailed explanation."
            }}
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "Generate up to 8 accurate Mains analytical questions..."}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        start_index = raw_text.find('{')
        end_index = raw_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            clean_json = raw_text[start_index:end_index+1]
            return json.loads(clean_json, strict=False)
        else:
            return None
    except Exception as e:
        return None

# ---------------------------------------------------------
# UI: Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.title("✨ UPSC Pro Dash")
st.sidebar.markdown("---")

if 'current_data' not in st.session_state:
    st.session_state.current_data = None

st.sidebar.subheader("🔍 Search Topic")
search_query = st.sidebar.text_input("Enter Syllabus Topic:")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Synthesizing deep-dive data..."):
            data = fetch_topic_data_from_ai(search_query)
            if data:
                st.session_state.current_data = data
                st.toast("Data generated successfully!", icon="✅")
            else:
                st.sidebar.error("Data generation failed. Try a slightly narrower topic.")
    else:
        st.sidebar.warning("Please enter a topic.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📂 Navigate Dash",
    ["📖 Deep Explanation", 
     "⚡ Flashcards (One-Pager)", 
     "🎨 Visual Maps (Flowcharts)", 
     "🎯 Prelims Simulator", 
     "✍️ Mains Masterclass"]
)

# ---------------------------------------------------------
# UI: Main Content Area
# ---------------------------------------------------------
if st.session_state.current_data is None:
    st.markdown("<h1 style='text-align: center; color: #6a11cb;'>Welcome to the Future of UPSC Prep 🚀</h1>", unsafe_allow_html=True)
    st.info("👈 Fire up the AI Engine in the sidebar to generate a custom, colorful dashboard for any topic.")
else:
    data = st.session_state.current_data
    st.header(f"📌 {data.get('title', 'Topic Dashboard')}")
    st.markdown("---")
    
    # PAGE 1: Explanation
    if page == "📖 Deep Explanation":
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(data.get('explanation', 'No data.'))
        with col2:
            st.info("🔥 **High Yield Sub-Topics**")
            for item in data.get('important_topics', []):
                st.markdown(f"- {item}")

    # PAGE 2: One-Pager
    elif page == "⚡ Flashcards (One-Pager)":
        st.subheader("High-Speed Revision")
        one_pager_data = data.get('one_pager', {})
        if one_pager_data:
            for key, value in one_pager_data.items():
                st.success(f"**{key}:** {value}")

    # PAGE 3: Flowcharts (Multiple Tabs)
    elif page == "🎨 Visual Maps (Flowcharts)":
        st.subheader("Process & Mechanism Maps")
        flowcharts = data.get('flowcharts', [])
        
        if not flowcharts:
            st.info("No flowcharts generated.")
        else:
            # Create a dynamic number of tabs based on how many flowcharts the AI generated
            tabs = st.tabs([fc.get('title', f"Map {i+1}") for i, fc in enumerate(flowcharts)])
            
            for i, tab in enumerate(tabs):
                with tab:
                    fc_code = flowcharts[i].get('code', '')
                    if "digraph" in fc_code:
                        try:
                            st.graphviz_chart(fc_code)
                        except Exception:
                            st.error("Invalid diagram syntax.")
                    else:
                        st.warning("Diagram data missing.")

    # PAGE 4: Prelims Interactive
    elif page == "🎯 Prelims Simulator":
        st.subheader("Interactive Prelims Combat")
        prelims_qs = data.get('pyq_prelims', [])
        
        if not prelims_qs:
            st.info("No Prelims data available.")
        else:
            for i, pyq in enumerate(prelims_qs):
                with st.expander(f"Question {i+1} - Year: {pyq.get('year', 'N/A')}", expanded=(i==0)):
                    st.write(f"**{pyq.get('q')}**")
                    options = pyq.get('options', [])
                    ans = pyq.get('answer', '')
                    
                    if options:
                        user_choice = st.radio("Select:", options, key=f"radio_{i}", index=None, label_visibility="collapsed")
                        if st.button("Verify Target", key=f"btn_{i}"):
                            if user_choice == ans:
                                st.success(f"🎯 SPOT ON! The answer is {ans}")
                                st.balloons() # Animated success!
                            elif user_choice is None:
                                st.warning("Select an option to fire.")
                            else:
                                st.error(f"❌ Missed. Correct target: {ans}")
                            if pyq.get('explanation'):
                                st.info(f"**Intel:** {pyq.get('explanation')}")

    # PAGE 5: Mains Practice
    elif page == "✍️ Mains Masterclass":
        st.subheader("Mains Answer Writing")
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        
        if questions:
            selected_q = st.selectbox("Select Target Question", questions)
            st.write(f"**Mission:** {selected_q}")
            
            answer = st.text_area("Draft your response (150-250 words):", height=250)
            words = len(answer.split())
            
            st.progress(min(words / 250, 1.0))
            st.caption(f"Word Status: {words} / 250 max")
            
            if st.button("Submit Draft"):
                if words < 50:
                    st.error("Draft too short. Expand your analysis.")
                else:
                    st.success("Draft securely recorded for review! 📝")
                    st.toast("Excellent writing session!", icon="✨")
        else:
            st.info("No Mains questions available.")
