import streamlit as st
import google.generativeai as genai
import json
import re

# ==============================================================================
# 1. INTERFACE CONFIGURATION & RESPONSIVE UI STYLING
# ==============================================================================
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="centered", page_icon="🏛️")

st.markdown("""
    <style>
    /* Gradient Action Controls */
    .stButton>button { 
        background: linear-gradient(135deg, #00B4DB 0%, #0083B0 100%); 
        color: white !important; 
        border-radius: 10px; 
        font-weight: 700; 
        width: 100%; 
        border: none;
        padding: 0.5rem;
    }
    .stButton>button:active { transform: scale(0.99); }
    
    /* High-Contrast Search Input */
    div[data-baseweb="input"] { 
        background-color: #ffffff !important; 
        border: 2px solid #00B4DB !important; 
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: 600 !important; 
    }
    
    /* Typography Typography Styling */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(45deg, #FF416C, #FF4B2B); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 800; 
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CORE ENGINE INITIALIZATION
# ==============================================================================
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE")

# ==============================================================================
# 3. JSON STREAM REPAIR ENGINE (ANTI-CRASH LAYER)
# ==============================================================================
def repair_and_load_json(raw_text: str):
    """Sanitizes raw LLM string text to guarantee standard JSON compliance."""
    # Clean out any accidental markdown code fence syntax
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    # Fix unescaped control characters and newlines inside string parameters
    def replace_newlines(match):
        return match.group(0).replace('\n', '\\n').replace('\t', '\\t')
    
    # Locate all content enclosed within valid string quotes
    string_pattern = re.compile(r'"([^"\\]|\\.)*"')
    clean_text = string_pattern.sub(replace_newlines, clean_text)
    
    return json.loads(clean_text, strict=False)

# ==============================================================================
# 4. DATA GENERATION PIPELINE (GEMINI 2.5 FLASH)
# ==============================================================================
def execute_dashboard_generation(topic: str):
    """Compiles whole core dashboard via structured JSON formatting configuration."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert UPSC Civil Services exam curator. Produce an exhaustive learning architecture for: "{topic}".
    
    CRITICAL SYNTAX INSTRUCTIONS:
    - You must return a single, highly structured JSON object.
    - All text values must use escaped standard text line breaks ("\\n") instead of literal unescaped newlines.
    
    CRITICAL STRUCTURE INSTRUCTIONS:
    - Provide EXACTLY 15 multiple-choice questions (MCQs) for Prelims.
    - Provide EXACTLY 10 long-form analytical questions for Mains.
    - For flowcharts, use simple Graphviz DOT syntax using standard double quotes for node definitions.
    
    Strict JSON Target Schema Layout:
    {{
        "title": "Syllabus Module Title",
        "brief_overview": "Comprehensive thematic explanation...",
        "core_anchors": ["Anchor Point 1", "Anchor Point 2"],
        "pillars": {{
            "legal_constitutional": "Data context...",
            "statistical_indices": "Data context...",
            "conceptual_keywords": "Data context...",
            "contemporary_context": "Data context...",
            "bottlenecks_remedies": "Data context..."
        }},
        "diagrams": [
            {{"title": "Flow Diagram 1", "dot": "digraph G {{ rankdir=TB; node [shape=box]; \\"A\\" -> \\"B\\"; }}"}}
        ],
        "current_linkages": [
            {{"paper": "GS Paper X", "event": "Analysis detail..."}}
        ],
        "prelims_dataset": [
            {{"question": "Q...", "choices": ["A", "B", "C", "D"], "correct": "A", "rationale": "..."}}
        ],
        "mains_dataset": [
            "Mains Question 1...",
            "Mains Question 2..."
        ]
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.15,
                "response_mime_type": "application/json"
            }
        )
        return repair_and_load_json(response.text)
    except Exception as e:
        st.error(f"Critical System Exception: {e}")
        return None

def execute_evaluation(mains_q: str, student_answer: str):
    """Evaluates a handwritten mains transcript against a fixed criteria schema."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Evaluate the following UPSC response out of 15 marks.
    Question: {mains_q}
    Student Answer: {student_answer}
    
    Return a structured JSON file conforming to:
    {{
        "score": "X/15",
        "segment_analysis": "Detailed structure review...",
        "positives": ["Point 1"],
        "gaps": ["Point 1"],
        "benchmark_blueprint": "Ideal solution framework..."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return repair_and_load_json(response.text)
    except Exception as e:
        st.error(f"Evaluation Module Error: {e}")
        return None

# ==============================================================================
# 5. DESKTOP/MOBILE ROUTING AND APPLICATION CONTROLS
# ==============================================================================
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)

target_topic = st.sidebar.text_input("🔍 Input Target Syllabus Topic:", placeholder="e.g., Left Wing Extremism")

if st.sidebar.button("🚀 Execute Analytical Build"):
    if target_topic:
        with st.spinner("⚡ Synthesizing via Gemini 2.5 Flash Engine..."):
            payload = execute_dashboard_generation(target_topic)
            if payload:
                st.session_state.active_payload = payload
                st.session_state.pop('active_grading', None)
                st.toast("Data Matrix Assembled Successfully!", icon="✅")
    else:
        st.sidebar.warning("A specific syllabus parameter must be defined.")

st.sidebar.markdown("---")
selected_view = st.sidebar.radio(
    "📂 Active Terminal Layout",
    ["📖 Knowledge Matrix", "⚡ 5-Pillar Matrix", "🎨 Graphviz Flowcharts", "📰 GS Linkages", "🎯 Prelims Simulator (15)", "✍️ Mains Lab (10)"]
)

# ==============================================================================
# 6. STRUCTURAL INTERFACE CONTENT GENERATION
# ==============================================================================
if 'active_payload' not in st.session_state or not st.session_state.active_payload:
    st.markdown("<h2 style='text-align: center; margin-top: 15vh;'>System Ready. 🚀</h2>", unsafe_allow_html=True)
    st.info("👈 Please define an educational vector in the control panel to engage the 2.5-Flash pipeline.")
else:
    core_data = st.session_state.active_payload
    st.header(f"📌 Module: {core_data.get('title', 'Active Workspace')}")
    st.markdown("---")

    # --- TERMINAL 1: KNOWLEDGE MATRIX ---
    if selected_view == "📖 Knowledge Matrix":
        st.markdown(core_data.get('brief_overview', 'Information unavailable.'))
        st.warning("🔥 **High-Priority Analytical Concepts**")
        for anchor in core_data.get('core_anchors', []):
            st.markdown(f"- {anchor}")

    # --- TERMINAL 2: 5-PILLAR MATRIX ---
    elif selected_view == "⚡ 5-Pillar Matrix":
        st.subheader("Structural Pillar Analysis")
        pillars_dict = core_data.get('pillars', {})
        for label, descriptive_text in pillars_dict.items():
            normalized_heading = label.replace('_', ' ').title()
            st.info(f"### {normalized_heading}\n\n{descriptive_text}")

    # --- TERMINAL 3: FLOWCHARTS ---
    elif selected_view == "🎨 Graphviz Flowcharts":
        st.subheader("Process Engineering Diagrams")
        diagram_list = core_data.get('diagrams', [])
        
        for index, item in enumerate(diagram_list):
            st.markdown(f"### {item.get('title', f'Diagram System {index+1}')}")
            dot_string = item.get('dot', '')
            
            if dot_string:
                try:
                    st.graphviz_chart(dot_string.replace("'", '"'))
                except Exception:
                    st.error("Visualization pipeline failed to interpret current code configuration.")
            
            with st.expander("🛠️ View Source DOT Code"):
                st.code(dot_string, language="dot")
            st.markdown("---")

    # --- TERMINAL 4: GS LINKAGES ---
    elif selected_view == "📰 GS Linkages":
        st.subheader("Syllabus Intersection Points")
        for link in core_data.get('current_linkages', []):
            with st.expander(f"📌 Linkage Domain: {link.get('paper', 'General Studies')}", expanded=True):
                st.write(link.get('event', 'No metrics recorded.'))

    # --- TERMINAL 5: PRELIMS SIMULATOR ---
    elif selected_view == "🎯 Prelims Simulator (15)":
        st.subheader("Active Retrieval Optimization")
        mcq_pool = core_data.get('prelims_dataset', [])
        
        for target_idx, question_node in enumerate(mcq_pool):
            st.markdown(f"**Q{target_idx+1}: {question_node.get('question')}**")
            valid_target = question_node.get('correct', '')
            
            user_input = st.radio(
                "Options:", 
                question_node.get('choices', []), 
                key=f"prelim_q_{target_idx}", 
                index=None, 
                label_visibility="collapsed"
            )
            
            if st.button("Evaluate Assessment", key=f"eval_trigger_{target_idx}"):
                if user_input == valid_target:
                    st.success(f"🎯 CORRECT. Selected value matches standard: {valid_target}")
                elif not user_input:
                    st.warning("An evaluation selection must be registered.")
                else:
                    st.error(f"❌ DEFICIT. Authorized standard value: {valid_target}")
                st.info(f"**Rationale:** {question_node.get('rationale')}")
            st.markdown("---")

    # --- TERMINAL 6: MAINS LAB ---
    elif selected_view == "✍️ Mains Lab (10)":
        st.subheader("Mains Examination Laboratory")
        mains_pool = core_data.get('mains_dataset', [])
        
        if mains_pool:
            selected_prompt = st.selectbox("Select Target Question Vector:", mains_pool)
            
            if 'current_target_q' not in st.session_state or st.session_state.current_target_q != selected_prompt:
                st.session_state.current_target_q = selected_prompt
                st.session_state.response_draft = ""
                st.session_state.pop('active_grading', None)

            st.write(f"**Analytical Prompt:** {selected_prompt}")
            written_input = st.text_area("Draft Matrix Workspace:", height=250, key="response_draft")
            calculated_words = len(written_input.split())
            st.caption(f"Word Registration Count: **{calculated_words}**")

            def reset_workspace_memory():
                st.session_state.response_draft = ""
                st.session_state.pop('active_grading', None)

            left_split, right_split = st.columns(2)
            with left_split:
                execute_grading = st.button("Initialize Grading Analysis")
            with right_split:
                st.button("Purge Current Workspace", on_click=reset_workspace_memory)

            if execute_grading:
                if calculated_words < 30:
                    st.error("Insufficent text density to extract a structural pattern profile.")
                else:
                    with st.spinner("Processing framework telemetry..."):
                        grading_result = execute_evaluation(selected_prompt, written_input)
                        if grading_result:
                            st.session_state.active_grading = grading_result

            if 'active_grading' in st.session_state:
                report_node = st.session_state.active_grading
                st.markdown("---")
                st.metric("Indicative Score Rating", report_node.get('score', 'N/A'))
                
                st.info(f"### Structural Evaluation Breakdown\n\n{report_node.get('segment_analysis')}")
                
                st.success("**Validated Strengths:**\n" + "\n".join([f"- {pos}" for pos in report_node.get('positives', [])]))
                st.warning("**Structural Gaps Identified:**\n" + "\n".join([f"- {gap}" for gap in report_node.get('gaps', [])]))
                
                with st.expander("📘 Review Target Benchmark Blueprint"):
                    st.write(report_node.get('benchmark_blueprint'))
