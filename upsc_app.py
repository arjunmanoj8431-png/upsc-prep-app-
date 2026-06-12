import streamlit as st
import graphviz
import json
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration & Modern CSS Styling
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Animated Gradient Backgrounds & Buttons */
    .stApp { background: #f8f9fa; }
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
    /* Vibrant Headings */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #1A2980, #26D0CE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    /* Card-like Info Boxes */
    div.stAlert {
        border-radius: 15px;
        border-left: 5px solid #26D0CE;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        background-color: white;
    }
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #141E30, #243B55);
    }
    [data-testid="stSidebar"] * { color: white !important; }
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
            {{"title": "1. Core Mechanism", "code": "digraph G {{ rankdir=LR; A -> B; }}"}},
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
                "answer": "A) Opt 1", 
                "explanation": "Explanation here..."
            }}
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "Mains question text..."}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Bulletproof JSON extractor
        start_index = raw_text.find('{')
        end_index = raw_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            clean_json = raw_text[start_index:end_index+1]
            return json.loads(clean_json, strict=False)
        return None
    except Exception as e:
        return None

# ---------------------------------------------------------
# UI: Sidebar Navigation & App State
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: white;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("🔍 Enter Syllabus Topic:")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Forging deep-dive dashboard (Generating 30+ Qs & 5 Maps)..."):
            fresh_data = fetch_topic_data_from_ai(search_query)
            if fresh_data:
                st.session_state.current_data = fresh_data
                st.toast("Dashboard successfully generated!", icon="✅")
            else:
                st.sidebar.error("Data generation failed due to size limits. Try again.")
    else:
        st.sidebar.warning("Please enter a topic first.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📂 Navigation Menu",
    ["📖 In-Depth Explanation", 
     "⚡ 5-Pillar Cheat Sheet", 
     "🎨 Visual Maps (5 Flowcharts)", 
     "🎯 Prelims Combat (15 MCQs)", 
     "✍️ Mains Masterclass (15 Qs)"]
)

# ---------------------------------------------------------
# UI: Main Content Area
# ---------------------------------------------------------
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>Welcome to the Future of UPSC Prep 🚀</h1>", unsafe_allow_html=True)
    st.info("👈 Type a topic into the sidebar and launch the AI to generate a completely fresh, un-cached dashboard.")
else:
    data = st.session_state.current_data
    st.header(f"📌 {data.get('title', 'Target Dashboard')}")
    st.markdown("---")
    
    # --- PAGE 1: EXPLANATION ---
    if page == "📖 In-Depth Explanation":
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(data.get('explanation', 'No explanation data found.'))
        with col2:
            st.warning("🔥 **Core Targets**")
            for item in data.get('important_topics', []):
                st.markdown(f"- {item}")

    # --- PAGE 2: 5-PILLAR CHEAT SHEET ---
    elif page == "⚡ 5-Pillar Cheat Sheet":
        st.subheader("High-Density Strategic Revision")
        one_pager = data.get('one_pager', {})
        if one_pager:
            cols = st.columns(2)
            for i, (key, value) in enumerate(one_pager.items()):
                # Distribute the 5 pillars beautifully across the two columns
                with cols[i % 2]:
                    formatted_title = key.replace('_', ' ')
                    st.info(f"### {formatted_title}\n\n{value}")
        else:
            st.write("No cheat sheet data generated.")

    # --- PAGE 3: 5 FLOWCHARTS ---
    elif page == "🎨 Visual Maps (5 Flowcharts)":
        st.subheader("Process, Mechanism & Impact Maps")
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
                            st.error("The AI generated invalid Graphviz syntax for this map.")
                    else:
                        st.warning("Diagram code missing.")

    # --- PAGE 4: 15 PRELIMS MCQS ---
    elif page == "🎯 Prelims Combat (15 MCQs)":
        st.subheader("Interactive Active Recall Simulator")
        prelims_qs = data.get('pyq_prelims', [])
        
        if not prelims_qs:
            st.info("No Prelims data available.")
        else:
            st.caption(f"Loaded {len(prelims_qs)} targets for this session.")
            for i, pyq in enumerate(prelims_qs):
                with st.container():
                    st.markdown(f"**Q{i+1} ({pyq.get('year', 'Simulated')}): {pyq.get('q')}**")
                    options = pyq.get('options', [])
                    ans = pyq.get('answer', '')
                    
                    if options:
                        user_choice = st.radio("Select:", options, key=f"radio_{i}", index=None, label_visibility="collapsed")
                        
                        if st.button("Check Answer", key=f"btn_{i}"):
                            if user_choice == ans:
                                st.success(f"🎯 CORRECT! The answer is {ans}")
                                st.balloons()
                            elif user_choice is None:
                                st.warning("Please select an option before checking.")
                            else:
                                st.error(f"❌ INCORRECT. The valid target is: {ans}")
                            if pyq.get('explanation'):
                                st.info(f"**Analysis:** {pyq.get('explanation')}")
                    st.markdown("---")

    # --- PAGE 5: 15 MAINS QUESTIONS ---
    elif page == "✍️ Mains Masterclass (15 Qs)":
        st.subheader("Mains Answer Draft Simulator")
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        
        if questions:
            st.caption(f"Loaded {len(questions)} analytical questions.")
            selected_q = st.selectbox("Select your target question:", questions)
            st.write(f"**Your Mission:** {selected_q}")
            
            answer = st.text_area("Draft your response below (Aim for 150 - 250 words):", height=300)
            words = len(answer.split())
            
            # Interactive Progress Bar for Word Count
            st.progress(min(words / 250, 1.0))
            st.caption(f"Current Word Count: {words} / 250")
            
            if st.button("Submit Draft for Review"):
                if words < 50:
                    st.error("Draft is too brief. Expand on the core concepts and impacts.")
                else:
                    st.success("Draft successfully locked in! 📝")
        else:
            st.info("No Mains questions available.")
