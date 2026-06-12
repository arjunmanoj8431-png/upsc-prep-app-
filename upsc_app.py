import streamlit as st
import graphviz
import json
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration & Dark-Mode Proof CSS
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stButton>button { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: white !important; border-radius: 25px; border: none; font-weight: bold; }
    h1, h2, h3 { background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    div.stAlert { border-radius: 15px !important; border-left: 5px solid #26D0CE !important; box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important; }
    [data-testid="stSidebar"] { background: linear-gradient(to bottom, #141E30, #243B55) !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 { color: #ffffff !important; }
    
    /* Strict Search Box Visibility Enforcement */
    .stTextInput div[data-baseweb="base-input"] { background-color: #ffffff !important; border: 2px solid #26D0CE !important; border-radius: 8px !important; }
    .stTextInput input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; caret-color: #000000 !important; font-weight: 600 !important; }
    .stTextInput input::placeholder { color: #666666 !important; -webkit-text-fill-color: #666666 !important; }
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
# Native JSON Data Generators
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate a comprehensive JSON study dashboard for: "{topic}".
    
    CRITICAL ANTI-CRASH INSTRUCTIONS:
    1. SINGLE LINE STRINGS: You MUST NOT use literal newlines (Enter key) inside any JSON strings. Write all text, explanations, and code on a single continuous horizontal line. 
    2. FLOWCHARTS: EXACTLY 5 Graphviz DOT codes (rankdir=TB). Write the entire DOT code on ONE line. Do not use double quotes inside the DOT code (use single quotes). 
    3. EXPLANATION: 3 brief paragraphs.
    4. ONE-PAGER: 5 keys mapped below.
    5. CURRENT AFFAIRS: 3 recent developments.
    6. PRELIMS: EXACTLY 15 MCQs.
    7. MAINS: EXACTLY 10 analytical Mains questions.
    
    Respond strictly in this JSON format:
    {{
        "title": "Topic Title",
        "explanation": "Concise overview...",
        "important_topics": ["T1", "T2", "T3", "T4", "T5"],
        "one_pager": {{
            "Constitutional_and_Legal_Basis": "...",
            "High_Yield_Statistics_and_Reports": "...",
            "Core_Conceptual_Keywords": "...",
            "Current_Affairs_Context": "...",
            "Critical_Challenges_and_Solutions": "..."
        }},
        "flowcharts": [
            {{"title": "1. Core Mechanism", "code": "digraph G {{ rankdir=TB; node [shape=box]; A -> B; }}"}}
        ],
        "current_affairs": [
            {{"gs_paper": "GS 3", "headline": "...", "relevance": "...", "impact": "..."}}
        ],
        "pyq_prelims": [
            {{"year": 2023, "q": "...", "options": ["A) Opt1", "B) Opt2", "C) Opt3", "D) Opt4"], "answer": "A) Opt1", "explanation": "..."}}
        ],
        "pyq_mains": [
            {{"year": 2023, "q": "..."}}
        ]
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 8192, "temperature": 0.2, "response_mime_type": "application/json"}
        )
        # Added strict=False to forgive any accidental line breaks the AI still tries to sneak in
        return json.loads(response.text, strict=False)
    except Exception as e:
        st.error(f"Data API Error: {e}")
        return None

def evaluate_mains_answer(question, user_answer):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Grade this UPSC Mains answer out of 15 marks. 
    Question: {question}
    Answer: {user_answer}
    
    CRITICAL: Do NOT use line breaks inside the JSON strings. Keep all values on one line.
    
    Format output exactly as JSON:
    {{
        "marks_allocated": "X/15",
        "intro_critique": "...",
        "body_critique": "...",
        "conclusion_critique": "...",
        "explicit_strengths": ["...", "..."],
        "critical_improvements": ["...", "..."],
        "model_approach": "..."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )
        return json.loads(response.text, strict=False)
    except Exception as e:
        st.error(f"Evaluation API Error: {e}")
        return None

# ---------------------------------------------------------
# UI Logic & Routing
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., Agricultural Extension")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Forging deep-dive dashboard (Enforcing anti-crash JSON rules)..."):
            fresh_data = fetch_topic_data_from_ai(search_query)
            if fresh_data:
                st.session_state.current_data = fresh_data
                if 'active_evaluation' in st.session_state:
                    del st.session_state.active_evaluation
                st.toast("Dashboard generated successfully!", icon="✅")
    else:
        st.sidebar.warning("Please enter a topic.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📂 Navigation Menu",
    ["📖 In-Depth Explanation", "⚡ 5-Pillar Cheat Sheet", "🎨 Visual Maps", "📰 GS Current Affairs", "🎯 Prelims Combat (15)", "✍️ Mains Masterclass (10)"]
)

# ---------------------------------------------------------
# Main Content Views
# ---------------------------------------------------------
if 'current_data' not in st.session_state or not st.session_state.current_data:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>Welcome to the Future of Exam Prep 🚀</h1>", unsafe_allow_html=True)
    st.info("👈 Enter a topic in the sidebar and click Launch. The native JSON engine will build your dashboard.")
else:
    data = st.session_state.current_data
    st.header(f"📌 {data.get('title', 'Dashboard')}")
    st.markdown("---")
    
    if page == "📖 In-Depth Explanation":
        c1, c2 = st.columns([3, 1])
        with c1: st.markdown(data.get('explanation', ''))
        with c2:
            st.warning("🔥 **Core Targets**")
            for t in data.get('important_topics', []): st.markdown(f"- {t}")

    elif page == "⚡ 5-Pillar Cheat Sheet":
        st.subheader("High-Density Strategic Revision")
        cols = st.columns(2)
        for i, (k, v) in enumerate(data.get('one_pager', {}).items()):
            with cols[i % 2]: st.info(f"### {k.replace('_', ' ')}\n\n{v}")

    elif page == "🎨 Visual Maps":
        st.subheader("Process & Impact Flowcharts")
        tabs = st.tabs([fc.get('title', f"Map {i+1}") for i, fc in enumerate(data.get('flowcharts', []))])
        for i, tab in enumerate(tabs):
            with tab:
                code = data['flowcharts'][i].get('code', '')
                try:
                    st.graphviz_chart(code)
                except Exception as e:
                    st.error(f"Graphviz rendering error. Raw code:\n{code}")

    elif page == "📰 GS Current Affairs":
        st.subheader("Recent Developments")
        for item in data.get('current_affairs', []):
            with st.expander(f"📌 **{item.get('headline')}** | {item.get('gs_paper')}", expanded=True):
                st.markdown(f"**Relevance:** {item.get('relevance')}\n\n**Impact:** {item.get('impact')}")

    elif page == "🎯 Prelims Combat (15)":
        st.subheader("Active Recall Simulator")
        for i, q in enumerate(data.get('pyq_prelims', [])):
            with st.container():
                st.markdown(f"**Q{i+1}: {q.get('q')}**")
                ans = q.get('answer', '')
                choice = st.radio("Select:", q.get('options', []), key=f"r_{i}", index=None, label_visibility="collapsed")
                if st.button("Check", key=f"b_{i}"):
                    if choice == ans: st.success(f"🎯 CORRECT! {ans}")
                    elif choice is None: st.warning("Select an option.")
                    else: st.error(f"❌ INCORRECT. Answer is: {ans}")
                    if q.get('explanation'): st.info(f"**Analysis:** {q.get('explanation')}")
                st.markdown("---")

    elif page == "✍️ Mains Masterclass (10)":
        st.subheader("AI Evaluation Lab")
        qs = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        if qs:
            sel_q = st.selectbox("Select question:", qs)
            
            if 'eval_q_track' not in st.session_state or st.session_state.eval_q_track != sel_q:
                st.session_state.eval_q_track = sel_q
                st.session_state.mains_text = ""
                st.session_state.pop('active_evaluation', None)

            st.markdown(f"**Prompt:** *{sel_q}*")
            ans_text = st.text_area("Draft answer:", height=300, key="mains_text")
            words = len(ans_text.split())
            st.progress(min(words / 250, 1.0))
            
            def clear_ws():
                st.session_state.mains_text = ""
                st.session_state.pop('active_evaluation', None)

            c1, c2 = st.columns([1, 4])
            with c1: submit = st.button("Submit for AI Evaluation")
            with c2: st.button("Clear Workspace", on_click=clear_ws)

            if submit:
                if words < 40: st.error("Draft too brief.")
                else:
                    with st.spinner("Reviewing structural elements..."):
                        res = evaluate_mains_answer(sel_q, ans_text)
                        if res: st.session_state.active_evaluation = res

            if 'active_evaluation' in st.session_state:
                e_data = st.session_state.active_evaluation
                st.markdown("---")
                mc, sc = st.columns([1, 3])
                with mc: st.metric("Score", e_data.get('marks_allocated', 'N/A'))
                with sc:
                    st.info(f"**Feedback**\n\n**Intro:** {e_data.get('intro_critique')}\n\n**Body:** {e_data.get('body_critique')}\n\n**Conclusion:** {e_data.get('conclusion_critique')}")
                
                c_left, c_right = st.columns(2)
                with c_left:
                    st.success("### ⭐ Strengths")
                    for s in e_data.get('explicit_strengths', []): st.markdown(f"- {s}")
                with c_right:
                    st.warning("### 📈 Improvements")
                    for i in e_data.get('critical_improvements', []): st.markdown(f"- {i}")
                with st.expander("📘 Model Approach"): st.markdown(e_data.get('model_approach'))
    
