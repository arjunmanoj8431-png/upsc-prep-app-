import streamlit as st
import json
import google.generativeai as genai
import typing

# =====================================================================
# 1. PAGE CONFIGURATION & RESPONSIVE CSS
# =====================================================================
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="centered", page_icon="🚀")

st.markdown("""
    <style>
    /* Mobile-Optimized Gradient Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); 
        color: white !important; 
        border-radius: 12px; 
        border: none; 
        font-weight: 800; 
        width: 100%; 
        padding: 0.6rem;
        transition: transform 0.2s ease;
    }
    .stButton>button:active { transform: scale(0.98); }
    
    /* Dynamic Headings */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 900; 
    }
    
    /* Bulletproof Dark-Mode Search Box */
    .stTextInput div[data-baseweb="base-input"] { 
        background-color: #ffffff !important; 
        border: 2px solid #26D0CE !important; 
        border-radius: 8px !important; 
    }
    .stTextInput input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        caret-color: #000000 !important; 
        font-weight: bold !important; 
    }
    .stTextInput input::placeholder { 
        color: #777777 !important; 
        -webkit-text-fill-color: #777777 !important; 
    }
    
    /* Clean Expanders and Info Boxes */
    div.stAlert { border-radius: 10px !important; }
    .streamlit-expanderHeader { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. SCHEMA DEFINITIONS (ENFORCES PERFECT JSON SYNTAX)
# =====================================================================
class CheatSheet(typing.TypedDict):
    Constitutional_and_Legal_Basis: str
    Statistics_and_Reports: str
    Conceptual_Keywords: str
    Current_Affairs_Context: str
    Challenges_and_Solutions: str

class Flowchart(typing.TypedDict):
    title: str
    code: str

class CurrentAffair(typing.TypedDict):
    gs_paper: str
    headline: str
    relevance: str
    impact: str

class MCQ(typing.TypedDict):
    q: str
    options: typing.List[str]
    answer: str
    explanation: str

class DashboardSchema(typing.TypedDict):
    title: str
    explanation: str
    core_targets: typing.List[str]
    cheat_sheet: CheatSheet
    flowcharts: typing.List[Flowchart]
    current_affairs: typing.List[CurrentAffair]
    prelims: typing.List[MCQ]
    mains: typing.List[str]

class EvaluationSchema(typing.TypedDict):
    marks_awarded: str
    intro_feedback: str
    body_feedback: str
    conclusion_feedback: str
    strengths: typing.List[str]
    improvements: typing.List[str]
    model_framework: str

# =====================================================================
# 3. API INITIALIZATION
# =====================================================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# =====================================================================
# 4. AI GENERATION ENGINES (GEMINI 2.5 FLASH)
# =====================================================================
def generate_dashboard(topic):
    """Generates the dashboard mathematically constrained to the DashboardSchema."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC exam strategist. Generate a comprehensive study dashboard for the topic: "{topic}".
    
    CRITICAL INSTRUCTIONS:
    - You must output EXACTLY 15 highly distinct MCQs for Prelims.
    - You must output EXACTLY 10 distinct questions for Mains.
    - For Graphviz DOT codes, use standard formatting (rankdir=TB). The backend will automatically handle quote escaping.
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192, 
                temperature=0.2, 
                response_mime_type="application/json",
                response_schema=DashboardSchema
            )
        )
        return json.loads(response.text, strict=False)
    except Exception as e:
        st.error(f"Engine Failure: {e}")
        return None

def grade_mains_answer(question, user_answer):
    """Evaluates a student's answer constrained to the EvaluationSchema."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a strict UPSC examiner. Grade this answer out of 15 marks.
    Question: {question}
    Answer: {user_answer}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1, 
                response_mime_type="application/json",
                response_schema=EvaluationSchema
            )
        )
        return json.loads(response.text, strict=False)
    except Exception as e:
        st.error(f"Grading Failure: {e}")
        return None

# =====================================================================
# 5. SIDEBAR NAVIGATION & STATE MANAGEMENT
# =====================================================================
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)

query = st.sidebar.text_input("🔍 Search Syllabus Topic:", placeholder="e.g., Cyber Security")

if st.sidebar.button("🚀 Launch AI Engine"):
    if query:
        with st.spinner("⚡ Processing via Gemini 2.5 Flash Schema..."):
            result = generate_dashboard(query)
            if result:
                st.session_state.dashboard_data = result
                # Purge old evaluation data if it exists
                st.session_state.pop('evaluation_data', None)
                st.toast("Dashboard successfully compiled!", icon="✅")
    else:
        st.sidebar.warning("Input required.")

st.sidebar.markdown("---")
active_tab = st.sidebar.radio(
    "📂 Interface Modules",
    ["📖 Deep Dive Explanation", 
     "⚡ Strategic Cheat Sheet", 
     "🎨 Analytical Flowcharts", 
     "📰 GS Current Affairs", 
     "🎯 Prelims Simulator (15)", 
     "✍️ Mains Evaluation Lab (10)"]
)

# =====================================================================
# 6. MAIN CONTENT RENDERING
# =====================================================================
if 'dashboard_data' not in st.session_state or not st.session_state.dashboard_data:
    st.markdown("<h2 style='text-align: center; margin-top: 10vh;'>System Ready. 🚀</h2>", unsafe_allow_html=True)
    st.info("👈 Enter a target topic in the sidebar to initialize the 2.5-Flash engine.")
else:
    data = st.session_state.dashboard_data
    st.header(f"📌 {data.get('title', 'Module Active')}")
    st.markdown("---")
    
    # ----------------- MODULE 1: EXPLANATION -----------------
    if active_tab == "📖 Deep Dive Explanation":
        st.markdown(data.get('explanation', 'No explanation provided.'))
        st.warning("🔥 **Core Targets & Keywords**")
        for target in data.get('core_targets', []):
            st.markdown(f"- {target}")

    # ----------------- MODULE 2: CHEAT SHEET -----------------
    elif active_tab == "⚡ Strategic Cheat Sheet":
        st.subheader("5-Pillar Overview")
        for key, value in data.get('cheat_sheet', {}).items():
            formatted_title = key.replace('_', ' ')
            st.info(f"### {formatted_title}\n\n{value}")

    # ----------------- MODULE 3: FLOWCHARTS -----------------
    elif active_tab == "🎨 Analytical Flowcharts":
        st.subheader("Process & Structure Mapping")
        st.caption("Graphviz renders automatically. Raw code is provided below each map as a failsafe.")
        
        flowcharts = data.get('flowcharts', [])
        for i, chart in enumerate(flowcharts):
            st.markdown(f"### {chart.get('title', f'Map {i+1}')}")
            dot_code = chart.get('code', '')
            
            if dot_code:
                try:
                    st.graphviz_chart(dot_code)
                except Exception:
                    st.error("Graphviz encountered an unsupported character sequence.")
            else:
                st.warning("No rendering code generated.")
                
            with st.expander("🛠️ View DOT Code"):
                st.code(dot_code, language="dot")
            st.markdown("---")

    # ----------------- MODULE 4: CURRENT AFFAIRS -----------------
    elif active_tab == "📰 GS Current Affairs":
        st.subheader("Dynamic Syllabus Linkages")
        for news in data.get('current_affairs', []):
            with st.expander(f"📌 {news.get('headline')} | {news.get('gs_paper')}", expanded=True):
                st.markdown(f"**Relevance:** {news.get('relevance')}")
                st.markdown(f"**Impact:** {news.get('impact')}")

    # ----------------- MODULE 5: PRELIMS -----------------
    elif active_tab == "🎯 Prelims Simulator (15)":
        st.subheader("Active Recall Assessment")
        for i, q_data in enumerate(data.get('prelims', [])):
            st.markdown(f"**Q{i+1}: {q_data.get('q')}**")
            correct_ans = q_data.get('answer', '')
            user_choice = st.radio("Select an option:", q_data.get('options', []), key=f"mcq_{i}", index=None, label_visibility="collapsed")
            
            if st.button("Submit Answer", key=f"btn_{i}"):
                if user_choice == correct_ans:
                    st.success(f"🎯 CORRECT! {correct_ans}")
                elif user_choice is None:
                    st.warning("Please make a selection.")
                else:
                    st.error(f"❌ INCORRECT. The valid answer is: {correct_ans}")
                
                if q_data.get('explanation'):
                    st.info(f"**Analysis:** {q_data.get('explanation')}")
            st.markdown("---")

    # ----------------- MODULE 6: MAINS EVALUATION -----------------
    elif active_tab == "✍️ Mains Evaluation Lab (10)":
        st.subheader("AI-Assisted Answer Writing")
        mains_qs = data.get('mains', [])
        
        if mains_qs:
            target_q = st.selectbox("Select a prompt to draft:", mains_qs)
            
            # Reset the text area and evaluation if the user changes the question
            if 'active_question' not in st.session_state or st.session_state.active_question != target_q:
                st.session_state.active_question = target_q
                st.session_state.mains_draft = ""
                st.session_state.pop('evaluation_data', None)

            st.write(f"**Mission:** {target_q}")
            draft_text = st.text_area("Draft workspace:", height=250, key="mains_draft")
            word_count = len(draft_text.split())
            st.caption(f"Current Word Count: **{word_count}**")

            # Native Streamlit callback ensures memory is wiped cleanly without throwing exceptions
            def wipe_workspace():
                st.session_state.mains_draft = ""
                st.session_state.pop('evaluation_data', None)

            col1, col2 = st.columns(2)
            with col1:
                trigger_eval = st.button("Grade via 2.5-Flash")
            with col2:
                st.button("Clear Workspace", on_click=wipe_workspace)

            if trigger_eval:
                if word_count < 30:
                    st.error("Draft is too brief for a structural assessment. Expand your points.")
                else:
                    with st.spinner("Analyzing parameters and formatting..."):
                        eval_report = grade_mains_answer(target_q, draft_text)
                        if eval_report:
                            st.session_state.evaluation_data = eval_report

            # Display the grading report if it exists
            if 'evaluation_data' in st.session_state:
                e_report = st.session_state.evaluation_data
                st.markdown("---")
                st.metric(label="Indicative Score", value=e_report.get('marks_awarded', 'N/A'))
                
                st.info(f"**Intro Dynamics:** {e_report.get('intro_feedback')}\n\n"
                        f"**Body Structure:** {e_report.get('body_feedback')}\n\n"
                        f"**Conclusion Alignment:** {e_report.get('conclusion_feedback')}")
                
                st.success("**Core Strengths:**\n" + "\n".join([f"- {s}" for s in e_report.get('strengths', [])]))
                st.warning("**Critical Improvements:**\n" + "\n".join([f"- {i}" for i in e_report.get('improvements', [])]))
                
                with st.expander("📘 View Optimal Model Framework"):
                    st.write(e_report.get('model_framework'))
    
