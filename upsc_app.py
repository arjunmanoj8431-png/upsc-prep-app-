import streamlit as st
import google.generativeai as genai
import json
from typing import List, TypedDict

# ==============================================================================
# 1. PAGE SETUP & MOBILE-FIRST CSS
# ==============================================================================
st.set_page_config(page_title="UPSC AI Pro", layout="centered", page_icon="🏛️")

st.markdown("""
    <style>
    /* Gradient Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); 
        color: white !important; 
        border-radius: 10px; 
        font-weight: 800; 
        width: 100%; 
        padding: 0.6rem;
    }
    .stButton>button:hover { transform: scale(1.02); }
    
    /* Theme-Agnostic Search Box */
    div[data-baseweb="input"] { 
        background-color: #ffffff !important; 
        border: 2px solid #26D0CE !important; 
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold; 
    }
    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }
    
    /* Vibrant Headings */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 900; 
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. STRICT TYPED SCHEMAS (GUARANTEES PERFECT JSON)
# ==============================================================================
class CheatSheetSchema(TypedDict):
    constitutional_legal_basis: str
    statistics_reports: str
    keywords: str
    current_affairs_context: str
    challenges_solutions: str

class FlowchartSchema(TypedDict):
    title: str
    dot_code: str

class CurrentAffairsSchema(TypedDict):
    gs_paper: str
    headline: str
    relevance: str

class MCQSchema(TypedDict):
    question: str
    options: List[str]
    correct_answer: str
    short_explanation: str

class DashboardSchema(TypedDict):
    topic_title: str
    core_explanation: str
    important_subtopics: List[str]
    cheat_sheet: CheatSheetSchema
    flowcharts: List[FlowchartSchema]
    recent_news: List[CurrentAffairsSchema]
    prelims_mcqs: List[MCQSchema]
    mains_questions: List[str]

class GradingSchema(TypedDict):
    marks_out_of_15: str
    introduction_feedback: str
    body_feedback: str
    conclusion_feedback: str
    strengths: List[str]
    improvements: List[str]
    ideal_framework: str

# ==============================================================================
# 3. API CONFIGURATION
# ==============================================================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ==============================================================================
# 4. GENERATION ENGINES (GEMINI 2.5 FLASH)
# ==============================================================================
def forge_dashboard(topic: str):
    """Generates the main dashboard using strict JSON Schema enforcement and massive data prompts."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC professor. Create a MASSIVE, highly detailed study dashboard for: "{topic}".
    
    You are constrained to a strict JSON schema. To satisfy the requirements, you MUST follow these volume constraints. DO NOT BE LAZY:
    
    1. 'core_explanation': Write a comprehensive 3-to-4 paragraph deep-dive. DO NOT be brief.
    2. 'flowcharts': You MUST generate EXACTLY 5 distinct flowcharts. Do not stop at 1.
       - Map 1: Core Mechanism / Concept
       - Map 2: Historical Context / Background
       - Map 3: Institutional / Legal Setup
       - Map 4: Impacts & Challenges
       - Map 5: Strategic Way Forward
    3. 'prelims_mcqs': You MUST generate EXACTLY 15 high-difficulty MCQs.
    4. 'mains_questions': You MUST generate EXACTLY 10 analytical questions.
    5. 'important_subtopics': Provide 5 to 7 high-yield subtopics.
    6. 'recent_news': Provide exactly 3 current affairs developments.
    7. 'cheat_sheet': Fill out every single key with a dense, detailed paragraph of information.
    
    For Graphviz DOT codes inside the flowcharts, use standard double quotes for your labels (e.g., node [label="Supreme Court"]). The JSON engine will automatically escape them.
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.25,
                response_mime_type="application/json",
                response_schema=DashboardSchema
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Generation Engine Error: {e}")
        return None

def grade_answer(question: str, answer: str):
    """Grades the mains answer using strict JSON Schema enforcement."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a strict UPSC examiner. Grade this out of 15 marks. Provide detailed feedback.
    Question: {question}
    Answer: {answer}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=GradingSchema
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Grading Engine Error: {e}")
        return None

# ==============================================================================
# 5. UI ROUTING & STATE CONTROLS
# ==============================================================================
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)

user_topic = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., Monetary Policy")

if st.sidebar.button("🚀 Launch AI Engine"):
    if user_topic:
        with st.spinner("⚡ Forging massive dataset via Gemini 2.5 Flash (Takes ~10-15 seconds)..."):
            new_data = forge_dashboard(user_topic)
            if new_data:
                st.session_state.app_data = new_data
                st.session_state.pop('mains_grade', None) # Clear old grades
                st.toast("Dashboard Ready!", icon="✅")
    else:
        st.sidebar.warning("Please enter a topic.")

st.sidebar.markdown("---")
view = st.sidebar.radio(
    "📂 Modules",
    ["📖 Core Concepts", "⚡ 5-Pillar Cheat Sheet", "🎨 Flowcharts", "📰 Current Affairs", "🎯 Prelims (15 Qs)", "✍️ Mains Lab (10 Qs)"]
)

# ==============================================================================
# 6. MAIN CONTENT RENDERING
# ==============================================================================
if 'app_data' not in st.session_state or not st.session_state.app_data:
    st.markdown("<h2 style='text-align: center; margin-top: 10vh;'>System Ready. 🚀</h2>", unsafe_allow_html=True)
    st.info("👈 Enter a topic in the sidebar and launch the engine. The AI will output deep, structured data without crashing.")
else:
    db = st.session_state.app_data
    st.header(f"📌 {db.get('topic_title', 'Dashboard')}")
    st.markdown("---")

    # --- CORE CONCEPTS ---
    if view == "📖 Core Concepts":
        st.markdown(db.get('core_explanation', 'No explanation provided.'))
        st.warning("🔥 **High-Yield Targets**")
        for topic in db.get('important_subtopics', []):
            st.markdown(f"- {topic}")

    # --- CHEAT SHEET ---
    elif view == "⚡ 5-Pillar Cheat Sheet":
        st.subheader("Strategic Overview")
        for key, val in db.get('cheat_sheet', {}).items():
            clean_title = key.replace('_', ' ').title()
            st.info(f"### {clean_title}\n\n{val}")

    # --- FLOWCHARTS ---
    elif view == "🎨 Flowcharts":
        st.subheader("Process & Structure Maps")
        st.caption("If rendering fails on mobile, use the Raw Code expander.")
        
        flowcharts = db.get('flowcharts', [])
        if not flowcharts:
            st.info("No flowcharts generated.")
            
        for i, chart in enumerate(flowcharts):
            st.markdown(f"### {chart.get('title', f'Map {i+1}')}")
            raw_code = chart.get('dot_code', '')
            
            if raw_code:
                # Security pass to ensure Graphviz handles quotes properly
                safe_code = raw_code.replace("'", '"')
                try:
                    st.graphviz_chart(safe_code)
                except Exception:
                    st.error("Graphviz rendering failed. See raw code below.")
            
            with st.expander("🛠️ View Raw DOT Code"):
                st.code(raw_code, language="dot")
            st.markdown("---")

    # --- CURRENT AFFAIRS ---
    elif view == "📰 Current Affairs":
        st.subheader("Syllabus Linkages")
        for news in db.get('recent_news', []):
            with st.expander(f"📌 {news.get('headline')} | {news.get('gs_paper')}", expanded=True):
                st.write(f"**Relevance:** {news.get('relevance')}")

    # --- PRELIMS SIMULATOR ---
    elif view == "🎯 Prelims (15 Qs)":
        st.subheader("Active Recall Assessment")
        mcqs = db.get('prelims_mcqs', [])
        st.caption(f"Loaded {len(mcqs)} Targets")
        
        for i, mcq in enumerate(mcqs):
            st.markdown(f"**Q{i+1}: {mcq.get('question')}**")
            correct = mcq.get('correct_answer', '')
            choice = st.radio("Select:", mcq.get('options', []), key=f"q_{i}", index=None, label_visibility="collapsed")
            
            if st.button("Check Answer", key=f"btn_{i}"):
                if choice == correct:
                    st.success(f"🎯 CORRECT! {correct}")
                elif not choice:
                    st.warning("Please make a selection.")
                else:
                    st.error(f"❌ INCORRECT. Answer: {correct}")
                st.info(f"**Analysis:** {mcq.get('short_explanation')}")
            st.markdown("---")

    # --- MAINS LAB ---
    elif view == "✍️ Mains Lab (10 Qs)":
        st.subheader("AI-Assisted Drafting")
        questions = db.get('mains_questions', [])
        st.caption(f"Loaded {len(questions)} Analytical Prompts")
        
        if questions:
            active_q = st.selectbox("Select Prompt:", questions)
            
            # Reset workspace on question change
            if 'last_q' not in st.session_state or st.session_state.last_q != active_q:
                st.session_state.last_q = active_q
                st.session_state.draft_text = ""
                st.session_state.pop('mains_grade', None)

            st.write(f"**Mission:** {active_q}")
            draft = st.text_area("Workspace:", height=250, key="draft_text")
            
            def clear_memory():
                st.session_state.draft_text = ""
                st.session_state.pop('mains_grade', None)

            c1, c2 = st.columns([1, 1])
            with c1: 
                submit = st.button("Grade via 2.5-Flash")
            with c2: 
                st.button("Clear Workspace", on_click=clear_memory)

            if submit:
                if len(draft.split()) < 30:
                    st.error("Draft is too short for formal assessment.")
                else:
                    with st.spinner("Analyzing parameters..."):
                        grade_report = grade_answer(active_q, draft)
                        if grade_report:
                            st.session_state.mains_grade = grade_report

            if 'mains_grade' in st.session_state:
                gr = st.session_state.mains_grade
                st.markdown("---")
                st.metric("Indicative Score", gr.get('marks_out_of_15', 'N/A'))
                
                st.info(f"**Intro:** {gr.get('introduction_feedback')}\n\n**Body:** {gr.get('body_feedback')}\n\n**Conclusion:** {gr.get('conclusion_feedback')}")
                st.success("**Strengths:**\n" + "\n".join([f"- {s}" for s in gr.get('strengths', [])]))
                st.warning("**Improvements:**\n" + "\n".join([f"- {i}" for i in gr.get('improvements', [])]))
                
                with st.expander("📘 Read Model Framework"):
                    st.write(gr.get('ideal_framework'))
