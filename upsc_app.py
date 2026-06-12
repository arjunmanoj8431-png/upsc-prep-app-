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
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 20px;
        border: none;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.6);
    }
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    div.stAlert {
        border-radius: 12px;
        border: 1px solid rgba(0, 180, 219, 0.3);
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
# High-Capacity LLM Data Generation Function (No Caching)
# ---------------------------------------------------------
# Note: @st.cache_data has been removed. Every search is a fresh generation.
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate highly extensive, deep-dive study material for: "{topic}".
    
    CRITICAL INSTRUCTIONS: 
    1. You MUST generate exactly 5 flowcharts.
    2. You MUST generate exactly 15 Prelims MCQs.
    3. You MUST generate exactly 15 Mains analytical questions.
    Do not stop early. Do not skip any items.
    
    Respond ONLY with a valid JSON object. Do not include ```json markdown.
    
    Structure exactly like this:
    {{
        "title": "Clear Title",
        "explanation": "At least 5 paragraphs of deep, conceptual explanation. Use bolding and bullets.",
        "important_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
        "one_pager": {{
            "Fact 1": "Details", "Fact 2": "Details", "Fact 3": "Details", "Fact 4": "Details", "Fact 5": "Details"
        }},
        "flowcharts": [
            {{"title": "1. Core Mechanism & Concept", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightblue]; A -> B; }}"}},
            {{"title": "2. Historical Evolution / Timeline", "code": "digraph G {{ rankdir=LR; node [shape=box]; A -> B; }}"}},
            {{"title": "3. Institutional / Administrative Setup", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "4. Causes, Effects & Impact Analysis", "code": "digraph G {{ A -> B; }}"}},
            {{"title": "5. Challenges & Way Forward", "code": "digraph G {{ A -> B; }}"}}
        ],
        "pyq_prelims": [
            {{
                "year": 2023, 
                "q": "Question 1 text...",
                "options": ["A) Opt 1", "B) Opt 2", "C) Opt 3", "D) Opt 4"],
                "answer": "A) Opt 1",
                "explanation": "Detailed explanation."
            }}
            // MUST REPEAT THIS EXACT BLOCK 15 TIMES
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "Question 1 text..."}}
            // MUST REPEAT THIS EXACT BLOCK 15 TIMES
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
        with st.spinner("⚡ Synthesizing deep-dive data (This may take longer due to 15-question quotas)..."):
            data = fetch_topic_data_from_ai(search_query)
            if data:
                # Overwrites old data completely
                st.session_state.current_data = data
                st.toast("Data generated successfully!", icon="✅")
            else:
                st.sidebar.error("Data generation failed or JSON was truncated. Try again.")
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
    st.markdown("<h1 style='text-align: center;'>Welcome to the Future of UPSC Prep 🚀</h1>", unsafe_allow_html=True)
    st.info("👈 Fire up the AI Engine in the sidebar to generate a custom dashboard for any topic.")
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

    # PAGE 3: Flowcharts
    elif page == "🎨 Visual Maps (Flowcharts)":
        st.subheader("Process & Mechanism Maps")
        flowcharts = data.get('flowcharts', [])
        
        if not flowcharts:
            st.info("No flowcharts generated.")
        else:
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
        st.subheader("Interactive Prelims Combat (Goal: 15 Questions)")
        prelims_qs = data.get('pyq_prelims', [])
        
        if not prelims_qs:
            st.info("No Prelims data available.")
        else:
            st.caption(f"Generated {len(prelims_qs)} questions for this session.")
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
                                st.balloons()
                            elif user_choice is None:
                                st.warning("Select an option to fire.")
                            else:
                                st.error(f"❌ Missed. Correct target: {ans}")
                            if pyq.get('explanation'):
                                st.info(f"**Intel:** {pyq.get('explanation')}")

    # PAGE 5: Mains Practice
    elif page == "✍️ Mains Masterclass":
        st.subheader("Mains Answer Writing (Goal: 15 Questions)")
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        
        if questions:
            st.caption(f"Generated {len(questions)} questions for this session.")
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
