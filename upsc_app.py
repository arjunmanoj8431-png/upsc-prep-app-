import streamlit as st
import json
import google.generativeai as genai

# ---------------------------------------------------------
# 1. Page Configuration & Mobile-Friendly CSS
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro", layout="centered", page_icon="🚀")

st.markdown("""
    <style>
    /* Gradient Buttons for Mobile Touch Targets */
    .stButton>button { 
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); 
        color: white !important; 
        border-radius: 15px; 
        border: none; 
        font-weight: bold; 
        width: 100%; /* Full width for easy tapping on Android */
    }
    /* Vibrant Headings */
    h1, h2, h3 { 
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 800; 
    }
    /* Fix Input Box Visibility in Dark Mode */
    .stTextInput div[data-baseweb="base-input"] { 
        background-color: #ffffff !important; 
        border: 2px solid #26D0CE !important; 
        border-radius: 8px !important; 
    }
    .stTextInput input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        caret-color: #000000 !important; 
        font-weight: 600 !important; 
    }
    .stTextInput input::placeholder { color: #666666 !important; -webkit-text-fill-color: #666666 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API Setup
# ---------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ---------------------------------------------------------
# 3. AI Generation Engines
# ---------------------------------------------------------
def fetch_dashboard_data(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an elite UPSC tutor. Generate a study dashboard for: "{topic}".
    
    STRICT RULES FOR JSON STABILITY & VOLUME:
    1. NO NEWLINES: DO NOT use literal newline characters (Enter key) inside strings. Write everything on a single horizontal line if possible.
    2. QUOTES: DO NOT use double quotes (") inside any string values. Use single quotes (') instead.
    3. FLOWCHARTS: Generate 5 Graphviz DOT codes (rankdir=TB). Keep them extremely simple. Do not use backslashes (\).
    4. QUOTAS: You MUST generate EXACTLY 15 distinct MCQ dictionary objects in "pyq_prelims" and EXACTLY 10 distinct strings in "pyq_mains". Do not stop at 1.
    
    Structure exactly like this:
    {{
        "title": "Topic Title",
        "explanation": "A 3-paragraph conceptual overview...",
        "important_topics": ["T1", "T2", "T3"],
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
            {{"q": "Q1...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A) ...", "explanation": "..."}},
            {{"q": "Q2...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A) ...", "explanation": "..."}},
            {{"q": "Q3...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A) ...", "explanation": "..."}}
        ],
        "pyq_mains": [
            "1. Q1 string...",
            "2. Q2 string...",
            "3. Q3 string..."
        ]
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            # FIXED: Added max_output_tokens back in so the AI has room to write 25 questions
            generation_config={"max_output_tokens": 8192, "temperature": 0.2, "response_mime_type": "application/json"}
        )
        return json.loads(response.text, strict=False)
    except Exception as e:
        st.error(f"Failed to generate valid data. Error: {e}")
        return None

def evaluate_answer(question, user_answer):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Grade this UPSC Mains answer out of 15 marks. 
    Question: {question}
    Answer: {user_answer}
    
    Format output exactly as JSON without line breaks inside strings:
    {{
        "marks": "X/15",
        "intro": "...",
        "body": "...",
        "conclusion": "...",
        "strengths": ["...", "..."],
        "improvements": ["...", "..."],
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
        st.error(f"Evaluation failed. Error: {e}")
        return None

# ---------------------------------------------------------
# 4. Mobile-Responsive UI & Routing
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)

search_query = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., Space Technology")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Forging dashboard (This takes ~10 seconds)..."):
            fresh_data = fetch_dashboard_data(search_query)
            if fresh_data:
                st.session_state.current_data = fresh_data
                if 'eval_result' in st.session_state:
                    del st.session_state.eval_result
                st.toast("Success!", icon="✅")
    else:
        st.sidebar.warning("Please enter a topic.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📂 Navigation",
    ["📖 Explanation", "⚡ Cheat Sheet", "🎨 Flowcharts", "📰 Current Affairs", "🎯 Prelims (15)", "✍️ Mains (10)"]
)

# ---------------------------------------------------------
# 5. Main Content Views (Stacking for Android)
# ---------------------------------------------------------
if 'current_data' not in st.session_state or not st.session_state.current_data:
    st.markdown("<h2 style='text-align: center; margin-top: 5vh;'>Welcome to UPSC AI 🚀</h2>", unsafe_allow_html=True)
    st.info("👈 Enter a topic in the sidebar and tap Launch.")
else:
    data = st.session_state.current_data
    st.header(f"📌 {data.get('title', 'Dashboard')}")
    st.markdown("---")
    
    # --- EXPLANATION ---
    if page == "📖 Explanation":
        st.markdown(data.get('explanation', ''))
        st.warning("🔥 **Core Targets**")
        for t in data.get('important_topics', []): 
            st.markdown(f"- {t}")

    # --- CHEAT SHEET ---
    elif page == "⚡ Cheat Sheet":
        st.subheader("High-Density Revision")
        for k, v in data.get('one_pager', {}).items():
            st.info(f"### {k.replace('_', ' ')}\n\n{v}")

    # --- FLOWCHARTS ---
    elif page == "🎨 Flowcharts":
        st.subheader("Process Maps")
        st.caption("If an image fails to load on your device, use the Raw Code dropdown below it.")
        
        for i, fc in enumerate(data.get('flowcharts', [])):
            st.markdown(f"### {fc.get('title', f'Map {i+1}')}")
            code = fc.get('code', '')
            
            try:
                if code:
                    # THE FIX: Flip the AI's single quotes into Graphviz-safe double quotes
                    valid_code = code.replace("'", '"')
                    st.graphviz_chart(valid_code)
                else:
                    st.warning("No data generated for this map.")
            except Exception:
                st.error("Graphviz engine rendering error on this device.")
            
            with st.expander("🛠️ View/Copy Raw Code"):
                st.code(code, language="dot")
            st.markdown("---")

    # --- CURRENT AFFAIRS ---
    elif page == "📰 Current Affairs":
        st.subheader("Recent Developments")
        for item in data.get('current_affairs', []):
            with st.expander(f"📌 {item.get('headline')} | {item.get('gs_paper')}", expanded=True):
                st.write(f"**Relevance:** {item.get('relevance')}")
                st.write(f"**Impact:** {item.get('impact')}")

    # --- PRELIMS ---
    elif page == "🎯 Prelims (15)":
        st.subheader("Active Recall Simulator")
        for i, q in enumerate(data.get('pyq_prelims', [])):
            st.markdown(f"**Q{i+1}: {q.get('q')}**")
            ans = q.get('answer', '')
            choice = st.radio("Options:", q.get('options', []), key=f"r_{i}", index=None, label_visibility="collapsed")
            
            if st.button("Check Answer", key=f"b_{i}"):
                if choice == ans: 
                    st.success(f"🎯 CORRECT! {ans}")
                elif choice is None: 
                    st.warning("Select an option first.")
                else: 
                    st.error(f"❌ INCORRECT. Answer is: {ans}")
                if q.get('explanation'): 
                    st.info(f"**Analysis:** {q.get('explanation')}")
            st.markdown("---")

    # --- MAINS EVALUATION ---
    elif page == "✍️ Mains (10)":
        st.subheader("AI Evaluation Lab")
        qs = data.get('pyq_mains', [])
        if qs:
            sel_q = st.selectbox("Select question to practice:", qs)
            
            # Reset workspace if question changes
            if 'eval_q_track' not in st.session_state or st.session_state.eval_q_track != sel_q:
                st.session_state.eval_q_track = sel_q
                st.session_state.mains_text = ""
                st.session_state.pop('eval_result', None)

            st.write(f"**Prompt:** *{sel_q}*")
            ans_text = st.text_area("Draft your answer here:", height=250, key="mains_text")
            words = len(ans_text.split())
            st.caption(f"Word Count: {words}")
            
            def clear_workspace():
                st.session_state.mains_text = ""
                st.session_state.pop('eval_result', None)

            if st.button("Submit for AI Evaluation"):
                if words < 30: 
                    st.error("Draft is too brief for a proper UPSC evaluation.")
                else:
                    with st.spinner("Reviewing your answer..."):
                        res = evaluate_answer(sel_q, ans_text)
                        if res: 
                            st.session_state.eval_result = res

            st.button("Clear Workspace", on_click=clear_workspace)

            # Display Evaluation
            if 'eval_result' in st.session_state:
                e = st.session_state.eval_result
                st.markdown("---")
                st.metric("Indicative Score", e.get('marks', 'N/A'))
                
                st.info(f"**Intro:** {e.get('intro')}\n\n**Body:** {e.get('body')}\n\n**Conclusion:** {e.get('conclusion')}")
                
                st.success("**Strengths:**\n" + "\n".join([f"- {s}" for s in e.get('strengths', [])]))
                st.warning("**Improvements Needed:**\n" + "\n".join([f"- {i}" for i in e.get('improvements', [])]))
                
                with st.expander("📘 Read Model Approach"):
                    st.write(e.get('model_approach'))
    
