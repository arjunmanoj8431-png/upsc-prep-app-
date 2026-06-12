import streamlit as st
import google.generativeai as genai
import json
import re

# ==============================================================================
# 1. GLOBAL INTERFACE PROPERTIES & MOBILE-ADAPTIVE CSS
# ==============================================================================
st.set_page_config(page_title="UPSC AI Pro", layout="centered", page_icon="🏛️")

st.markdown("""
    <style>
    /* Full-width touch targets optimized for web and mobile viewports */
    .stButton>button { 
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); 
        color: white !important; 
        border-radius: 10px; 
        font-weight: 800; 
        width: 100%; 
        padding: 0.6rem;
        border: none;
    }
    .stButton>button:hover { transform: scale(1.01); }
    
    /* High-contrast form elements resilient to platform dark mode overrides */
    div[data-baseweb="input"] { 
        background-color: #ffffff !important; 
        border: 2px solid #26D0CE !important; 
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold !important; 
    }
    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
    }
    
    /* Text layout enhancement for long-form reading configuration */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 900; 
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. RUNTIME STREAM REPAIR ENGINE (PARSING INSURANCE POLICY)
# ==============================================================================
def repair_and_load_json(raw_text: str):
    """Isolates core JSON strings from accidental structural anomalies."""
    clean_text = raw_text.strip()
    clean_text = re.sub(r"^```json\s*", "", clean_text)
    clean_text = re.sub(r"^```\s*", "", clean_text)
    clean_text = re.sub(r"\s*```$", "", clean_text)
    return json.loads(clean_text, strict=False)

# ==============================================================================
# 3. CORE SERVICE CLIENT CONFIGURATION
# ==============================================================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ==============================================================================
# 4. DISCRETE PROCESSING ENGINES (GEMINI 2.5 FLASH EXCLUSIVE)
# ==============================================================================
def forge_dashboard(topic: str):
    """Compiles macro-level dashboard datasets mapping strictly to core constraints."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC professor. Create a MASSIVE, highly detailed study dashboard for the topic: "{topic}".
    
    CRITICAL SYNTAX RULES:
    1. Output strictly in valid JSON layout format.
    2. DO NOT use unescaped double quotes inside your string values. If you need quotes inside text, use single quotes (').
    3. DO NOT use literal structural line breaks inside string arguments. Use explicit '\\n' character sequences instead.
    
    VOLUME MAPPING MANDATES (DO NOT TRUNCATE OR OMIT):
    - 'explanation': Write a comprehensive 3-paragraph structural breakdown.
    - 'flowcharts': You MUST generate EXACTLY 5 distinct flowchart nodes. Build structural definitions mapping out core components, timeline evolution, institutional setups, current bottlenecks, and strategic policy solutions.
    - 'prelims': You MUST generate EXACTLY 15 distinct, advanced multiple-choice questions.
    - 'mains': You MUST generate EXACTLY 10 distinct high-level analytical questions.
    - 'important_topics': Highlight 5 to 7 related operational subtopics.
    - 'current_affairs': Map 3 specific contemporary case developments.
    - 'cheat_sheet': Provide rich, data-dense informational strings across all 5 standard keys.
    
    Structure your JSON layout EXACTLY according to this blueprint framework:
    {{
        "title": "Normalized Topic Title",
        "explanation": "...",
        "important_topics": ["Subtopic A", "Subtopic B"],
        "cheat_sheet": {{
            "Constitutional_and_Legal_Basis": "...",
            "Statistics_and_Reports": "...",
            "Conceptual_Keywords": "...",
            "Current_Affairs_Context": "...",
            "Challenges_and_Solutions": "..."
        }},
        "flowcharts": [
            {{"title": "1. Structural Framework Blueprint", "code": "digraph G {{ rankdir=TB; node [shape=box]; A -> B; }}"}}
        ],
        "current_affairs": [
            {{"gs_paper": "GS Paper X", "headline": "...", "relevance": "...", "impact": "..."}}
        ],
        "prelims": [
            {{"q": "Advanced Question Text...", "options": ["A) Opt 1", "B) Opt 2", "C) Opt 3", "D) Opt 4"], "answer": "A) Opt 1", "explanation": "Deep conceptual analysis..."}}
        ],
        "mains": [
            "1. Macro Question Prompt...",
            "2. Macro Question Prompt..."
        ]
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )
        return response.text
    except Exception as e:
        st.error(f"Upstream API Communication Timeout: {e}")
        return None

def grade_answer(question: str, answer: str):
    """Evaluates standalone manuscript compositions across micro-analytical constraints."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a strict Civil Services Examiner evaluation officer. Grade this candidate answer out of a maximum of 15 marks.
    Question: {question}
    Answer: {answer}
    
    Return output strictly matching this clean JSON layout formatting:
    {{
        "marks": "X/15",
        "intro": "Critical opening evaluation...",
        "body": "Analysis of multi-dimensional core arguments...",
        "conclusion": "Policy paradigm recommendation check...",
        "strengths": ["Item 1", "Item 2"],
        "improvements": ["Item 1", "Item 2"],
        "ideal_framework": "Detailed blueprint roadmap for maximum score baseline..."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )
        return response.text
    except Exception as e:
        st.error(f"Upstream API Communication Timeout: {e}")
        return None

# ==============================================================================
# 5. SIDEBAR NAVIGATION & RUNTIME ENVIRONMENT HOOKS
# ==============================================================================
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)

user_topic = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., FinTech Regulation")

if st.sidebar.button("🚀 Launch AI Engine"):
    if user_topic:
        with st.spinner("⚡ Processing structured telemetry via Gemini 2.5 Flash..."):
            raw_response = forge_dashboard(user_topic)
            if raw_response:
                try:
                    parsed_data = repair_and_load_json(raw_response)
                    st.session_state.app_data = parsed_data
                    st.session_state.pop('mains_grade', None)
                    st.toast("Dashboard compiling routine successful!", icon="✅")
                except Exception as parse_error:
                    st.error(f"Intercepted broken structural output sequence: {parse_error}")
                    with st.expander("🛠️ View Raw Recovered Text Matrix", expanded=True):
                        st.code(raw_response, language="json")
    else:
        st.sidebar.warning("Operational target required. Define a syllabus vector.")

st.sidebar.markdown("---")
view = st.sidebar.radio(
    "📂 Active Module Workspace",
    ["📖 Core Concepts", "⚡ 5-Pillar Cheat Sheet", "🎨 Flowcharts", "📰 Current Affairs", "🎯 Prelims (15 Qs)", "✍️ Mains Lab (10 Qs)"]
)

# ==============================================================================
# 6. RUNTIME DATA PRESENTATION PARADIGMS
# ==============================================================================
if 'app_data' not in st.session_state or not st.session_state.app_data:
    st.markdown("<h2 style='text-align: center; margin-top: 10vh;'>System Engine Idle. 🚀</h2>", unsafe_allow_html=True)
    st.info("👈 Enter an academic topic parameter in the master configuration dock to activate runtime modules.")
else:
    db = st.session_state.app_data
    topic_id = db.get('title', 'default_node').replace(" ", "_") # Dynamic key factor to neutralize component bleed
    st.header(f"📌 {db.get('title', 'Active Workspace')}")
    st.markdown("---")

    # --- VIEW 1: CORE CONCEPTS ---
    if view == "📖 Core Concepts":
        st.markdown(db.get('explanation', 'Data index entry missing.'))
        st.warning("🔥 **Syllabus Focus Focal Points**")
        for topic in db.get('important_topics', []):
            st.markdown(f"- {topic}")

    # --- VIEW 2: 5-PILLAR CHEAT SHEET ---
    elif view == "⚡ 5-Pillar Cheat Sheet":
        st.subheader("High-Density Revision Matrix")
        for key, val in db.get('cheat_sheet', {}).items():
            clean_title = key.replace('_', ' ').title()
            st.info(f"### {clean_title}\n\n{val}")

    # --- VIEW 3: FLOWCHARTS ---
    elif view == "🎨 Flowcharts":
        st.subheader("Process Mechanism Blueprints")
        st.caption("Visual assets parse down automatically. Raw DOT scripts are exposed beneath instances as a hardware fallback layer.")
        
        flowcharts = db.get('flowcharts', [])
        for i, chart in enumerate(flowcharts):
            st.markdown(f"### {chart.get('title', f'Diagram Matrix {i+1}')}")
            raw_code = chart.get('code', '')
            
            if raw_code:
                safe_code = raw_code.replace("'", '"')
                try:
                    st.graphviz_chart(safe_code)
                except Exception:
                    st.error("Graphviz abstraction error encountered during engine local parse routine.")
            
            with st.expander("🛠️ View Raw DOT Mapping Script"):
                st.code(raw_code, language="dot")
            st.markdown("---")

    # --- VIEW 4: CURRENT AFFAIRS ---
    elif view == "📰 Current Affairs":
        st.subheader("Dynamic Contemporary Case Integration")
        for news in db.get('current_affairs', []):
            with st.expander(f"📌 {news.get('headline')} | {news.get('gs_paper')}", expanded=True):
                st.write(f"**Relevance Architecture:** {news.get('relevance')}")
                st.write(f"**Operational Real-World Impact:** {news.get('impact', '')}")

    # --- VIEW 5: PRELIMS ASSESSMENT ---
    elif view == "🎯 Prelims (15 Qs)":
        st.subheader("Active Recall Optimization Engine")
        mcqs = db.get('prelims', [])
        st.caption(f"Active Parameter Pool: Verified {len(mcqs)} Operational Problems")
        
        for i, mcq in enumerate(mcqs):
            st.markdown(f"**Q{i+1}: {mcq.get('q')}**")
            correct = mcq.get('answer', '')
            
            # FIXED: Dynamic topic_id string attached to eliminate crossover choice bleed bugs across runtime sessions
            choice = st.radio("Select Target Option Vector:", mcq.get('options', []), key=f"q_{topic_id}_{i}", index=None, label_visibility="collapsed")
            
            if st.button("Submit Choice Matrix Verification", key=f"btn_{topic_id}_{i}"):
                if choice == correct:
                    st.success(f"🎯 ANALYSIS CONFIRMED: Target choice matches system standard: {correct}")
                elif not choice:
                    st.warning("Input parameter verification missing. Select an alternate option.")
                else:
                    st.error(f"❌ COMPLIANCE DEFICIT: Evaluated selection faulty. System baseline: {correct}")
                st.info(f"**Explanatory Framework Trace:** {mcq.get('explanation')}")
            st.markdown("---")

    # --- VIEW 6: MAINS LAB ---
    elif view == "✍️ Mains Lab (10 Qs)":
        st.subheader("Analytical Essay Verification Terminal")
        questions = db.get('mains', [])
        st.caption(f"Active Parameter Pool: Verified {len(questions)} Core Compositions")
        
        if questions:
            active_q = st.selectbox("Select Target Question Prompt Profile:", questions)
            
            if 'last_q' not in st.session_state or st.session_state.last_q != active_q:
                st.session_state.last_q = active_q
                st.session_state.draft_text = ""
                st.session_state.pop('mains_grade', None)

            st.write(f"**Core Prompt Matrix:** {active_q}")
            draft = st.text_area("Input Composition Drafting Board Workspace:", height=250, key="draft_text")
            
            def clear_memory():
                st.session_state.draft_text = ""
                st.session_state.pop('mains_grade', None)

            c1, c2 = st.columns([1, 1])
            with c1: 
                submit = st.button("Initialize Script Verification Parsing")
            with c2: 
                st.button("Clear Input Workspace Space", on_click=clear_memory)

            if submit:
                if len(draft.split()) < 30:
                    st.error("Text content metrics display insufficient density parameters to run profile comparison scans.")
                else:
                    with st.spinner("Extracting stylistic features and structuring core parameters..."):
                        raw_eval = grade_answer(active_q, draft)
                        if raw_eval:
                            try:
                                parsed_eval = repair_and_load_json(raw_eval)
                                st.session_state.mains_grade = parsed_eval
                            except Exception:
                                st.error("Failed to map structure array sequence during analysis run.")

            if 'mains_grade' in st.session_state:
                gr = st.session_state.mains_grade
                st.markdown("---")
                st.metric("Indicative Quality Profile Rating", gr.get('marks', 'N/A'))
                
                st.info(f"**Structural Opening Mechanics:** {gr.get('intro')}\n\n**Body Parameter Balancing:** {gr.get('body')}\n\n**Forward Terminal Optimization:** {gr.get('conclusion')}")
                st.success("**Validated Functional Strengths:**\n" + "\n".join([f"- {s}" for s in gr.get('strengths', [])]))
                st.warning("**Identified Critical Performance Gaps:**\n" + "\n".join([f"- {i}" for i in gr.get('improvements', [])]))
                
                with st.expander("📘 Review Baseline Solution Structural Blueprint Model"):
                    st.write(gr.get('ideal_framework'))
