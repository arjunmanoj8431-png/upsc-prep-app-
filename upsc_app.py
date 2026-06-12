import streamlit as st
import graphviz
import json
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration & Bulletproof Adaptive CSS
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Pro Dashboard", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Animated Gradient Buttons */
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
    
    /* Vibrant Headings that adapt to any background */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #00b4db, #0083b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    
    /* Card-like Info Boxes */
    div.stAlert {
        border-radius: 15px !important;
        border-left: 5px solid #26D0CE !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* --- SIDEBAR FIXES --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #141E30, #243B55) !important;
    }
    
    /* Make static sidebar text white */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2 { 
        color: #ffffff !important; 
    }
    
    /* --- THE ULTIMATE SEARCH BOX FIX --- */
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
    
    .stTextInput input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
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
# AI Evaluation & Generation Engines
# ---------------------------------------------------------
def fetch_topic_data_from_ai(topic):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # We added instructions to be DENSE and CONCISE to fit the 15-question quota into the token limit
    prompt = f"""
    You are an elite UPSC tutor. Generate a massive, deep-dive study dashboard for: "{topic}".
    
    CRITICAL INSTRUCTIONS TO AVOID TRUNCATION LIMITS:
    1. EXPLANATION: 4-5 dense paragraphs. Keep it strictly conceptual.
    2. ONE-PAGER: 5-pillar strategic summary using bullet points to save tokens.
    3. FLOWCHARTS: EXACTLY 5 Graphviz DOT flowcharts (rankdir=TB). Keep node labels brief.
    4. CURRENT AFFAIRS: 3 recent news developments mapped to GS Papers.
    5. PRELIMS: EXACTLY 15 high-difficulty MCQs. Keep explanations to 1 strict sentence.
    6. MAINS: EXACTLY 15 analytical Mains questions.
    
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
            {{"title": "1. Core Mechanism", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightblue]; A -> B; }}"}},
            {{"title": "2. Historical Evolution", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightyellow]; A -> B; }}"}},
            {{"title": "3. Institutional Setup", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightgreen]; A -> B; }}"}},
            {{"title": "4. Impact Analysis", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightgrey]; A -> B; }}"}},
            {{"title": "5. Way Forward Strategy", "code": "digraph G {{ rankdir=TB; node [shape=box, style=filled, fillcolor=lightpink]; A -> B; }}"}}
        ],
        "current_affairs": [
            {{
                "gs_paper": "GS Paper 3",
                "headline": "Recent Headline related to topic...",
                "relevance": "How this connects to the static syllabus...",
                "impact": "The real-world implications or recent updates..."
            }}
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
        # FORCING THE MAXIMUM TOKEN LIMIT
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 8192, "temperature": 0.2}
        )
        raw_text = response.text.strip()
        start_index = raw_text.find('{')
        end_index = raw_text.rfind('}')
        if start_index != -1 and end_index != -1:
            clean_json = raw_text[start_index:end_index+1]
            return json.loads(clean_json, strict=False)
        return None
    except Exception as e:
        return None

def evaluate_mains_answer(question, user_answer):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a strict, veteran civil services examiner evaluation board officer grading a UPSC Mains answer sheet.
    
    Question: {question}
    Candidate's Answer: {user_answer}
    
    Critique this response rigorously under exact UPSC standards out of a maximum of 15 marks. Be objective. Real examiners rarely award above 9/15 unless the answer is masterfully multi-dimensional.
    
    Respond ONLY with a valid JSON object matching this structure exactly:
    {{
        "marks_allocated": "X/15",
        "intro_critique": "Analysis of their opening, conceptual framework, definitions, or context...",
        "body_critique": "Analysis of arguments, dimensions explored, facts integration, structural coherence...",
        "conclusion_critique": "Analysis of the way forward, balance, optimism, and alignment with policy frameworks...",
        "explicit_strengths": ["Strength 1", "Strength 2"],
        "critical_improvements": ["What to add to score 2 more marks", "Missing parameters or data links"],
        "model_approach": "A brief overview or bullet points of what a top-scoring baseline approach would feature..."
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1}
        )
        raw_text = response.text.strip()
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(raw_text[start:end+1], strict=False)
        return None
    except Exception as e:
        return None

# ---------------------------------------------------------
# UI: Sidebar Navigation & App State
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: white;'>✨ UPSC Pro Dash</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

search_query = st.sidebar.text_input("🔍 Enter Syllabus Topic:", placeholder="e.g., Agricultural Entomology")

if st.sidebar.button("🚀 Launch AI Engine"):
    if search_query:
        with st.spinner("⚡ Forging deep-dive dashboard (Generating 30+ Qs & Maps)..."):
            fresh_data = fetch_topic_data_from_ai(search_query)
            if fresh_data:
                st.session_state.current_data = fresh_data
                if 'active_evaluation' in st.session_state:
                    del st.session_state.active_evaluation
                st.toast("Dashboard successfully generated!", icon="✅")
            else:
                st.sidebar.error("Data generation failed due to size limits. Try again or search a slightly narrower topic.")
    else:
        st.sidebar.warning("Please enter a topic first.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📂 Navigation Menu",
    ["📖 In-Depth Explanation", 
     "⚡ 5-Pillar Cheat Sheet", 
     "🎨 Visual Maps (5 Flowcharts)", 
     "📰 GS Current Affairs",
     "🎯 Prelims Combat (15 MCQs)", 
     "✍️ Mains Masterclass (15 Qs)"]
)

# ---------------------------------------------------------
# UI: Main Content Area
# ---------------------------------------------------------
if 'current_data' not in st.session_state or st.session_state.current_data is None:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh;'>Welcome to the Future of Exam Prep 🚀</h1>", unsafe_allow_html=True)
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
                        
    # --- PAGE 4: CURRENT AFFAIRS ---
    elif page == "📰 GS Current Affairs":
        st.subheader("Recent Developments & GS Paper Linkages")
        ca_data = data.get('current_affairs', [])
        
        if not ca_data:
            st.info("No current affairs linkages generated for this topic.")
        else:
            for item in ca_data:
                with st.expander(f"📌 **{item.get('headline', 'Headline')}** | {item.get('gs_paper', 'GS Paper')}", expanded=True):
                    st.markdown(f"**Relevance to Syllabus:** {item.get('relevance', '')}")
                    st.markdown(f"**Recent Impact / Context:** {item.get('impact', '')}")

    # --- PAGE 5: 15 PRELIMS MCQS ---
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

    # --- PAGE 6: 15 MAINS QUESTIONS WITH ACTIVE AI GRADING ---
    elif page == "✍️ Mains Masterclass (15 Qs)":
        st.subheader("Mains Answer Writing & AI Evaluation Lab")
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        
        if questions:
            st.caption(f"Loaded {len(questions)} analytical questions.")
            selected_q = st.selectbox("Select your target question to attempt:", questions)
            
            if 'eval_question_track' not in st.session_state or st.session_state.eval_question_track != selected_q:
                st.session_state.eval_question_track = selected_q
                st.session_state.mains_text_input_area = ""
                if 'active_evaluation' in st.session_state:
                    del st.session_state.active_evaluation

            st.markdown(f"**Mission Prompt:** *{selected_q}*")
            
            answer_text = st.text_area(
                "Write or refine your draft answer below (Aim for 150 - 250 words):", 
                height=300, 
                placeholder="Begin structuring your response with a strong introduction...",
                key="mains_text_input_area"
            )
            
            word_count = len(answer_text.split())
            st.progress(min(word_count / 250, 1.0))
            st.caption(f"Current Word Count: **{word_count}** / 250 maximum benchmark")
            
            def clear_workspace():
                st.session_state.mains_text_input_area = ""
                if 'active_evaluation' in st.session_state:
                    del st.session_state.active_evaluation

            col_actions_1, col_actions_2 = st.columns([1, 4])
            with col_actions_1:
                submit_clicked = st.button("Submit for AI Evaluation")
            with col_actions_2:
                st.button("Clear Answer Workspace", on_click=clear_workspace)

            if submit_clicked:
                if word_count < 40:
                    st.error("Your draft is too brief to undergo standard civil services criteria evaluation. Expand your structural framework.")
                else:
                    with st.spinner("🔍 Reviewing structural paradigms, facts coverage, and assigning marks..."):
                        evaluation_result = evaluate_mains_answer(selected_q, answer_text)
                        if evaluation_result:
                            st.session_state.active_evaluation = evaluation_result
                        else:
                            st.error("Evaluation engine timeout or formatting collision. Please re-trigger the verification.")

            if 'active_evaluation' in st.session_state and st.session_state.active_evaluation:
                eval_data = st.session_state.active_evaluation
                st.markdown("---")
                st.subheader("🎯 Evaluation Dashboard Results")
                
                metric_col, structural_col = st.columns([1, 3])
                with metric_col:
                    st.metric(label="Indicative Score Allocated", value=eval_data.get('marks_allocated', 'N/A'))
                    st.caption("⚠️ *AI scores are strictly indicative evaluation guidelines. Always verify crucial data points and official case laws against primary reference sources.*")
                    
                with structural_col:
                    st.info(f"**Structural Blueprint Feedback**")
                    st.markdown(f"**1. Introduction Contextualization:**\n{eval_data.get('intro_critique', '')}")
                    st.markdown(f"**2. Body Analysis & Multi-Dimensional Data Coverage:**\n{eval_data.get('body_critique', '')}")
                    st.markdown(f"**3. Conclusion & Forward-Looking Policy Framework Alignment:**\n{eval_data.get('conclusion_critique', '')}")
                
                st.markdown("---")
                st_col_left, st_col_right = st.columns(2)
                with st_col_left:
                    st.success("### ⭐ Structural Strengths Captured")
                    for strength in eval_data.get('explicit_strengths', []):
                        st.markdown(f"- {strength}")
                with st_col_right:
                    st.warning("### 📈 Core Actions to Earn +2 Marks")
                    for improvement in eval_data.get('critical_improvements', []):
                        st.markdown(f"- {improvement}")
                
                st.markdown("---")
                with st.expander("📘 Review Optimal Model Baseline Framework"):
                    st.markdown(eval_data.get('model_approach', 'Model blueprint text not generated.'))
                    
                st.success("📝 **Feedback Processed.** You can edit your text in the workspace box above right now to adjust parameters and hit 'Submit for AI Evaluation' again to track your adjusted score timeline!")
        else:
            st.info("No Mains structural questions available.")
