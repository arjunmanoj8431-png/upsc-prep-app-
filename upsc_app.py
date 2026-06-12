import streamlit as st
import graphviz
import pandas as pd
import google.generativeai as genai
import json

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Master", layout="wide", page_icon="📚")

# ---------------------------------------------------------
# API Configuration
# ---------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ---------------------------------------------------------
# LLM Data Generation Function
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_topic_data_from_ai(topic):
    # Using the current, active model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Notice the updated instructions for 'pyq_prelims' below
    prompt = f"""
    You are an expert UPSC (Union Public Service Commission of India) tutor.
    Generate highly accurate, in-depth study material for the topic: "{topic}".
    
    Respond ONLY with a valid JSON object. Do not include markdown formatting like ```json.
    
    The JSON must follow this exact structure:
    {{
        "title": "Clear Title of the Topic",
        "explanation": "A highly detailed, 3-4 paragraph explanation covering the geographical, historical, or constitutional basics. Use markdown (bolding, bullet points).",
        "important_topics": ["Crucial Sub-topic 1", "Crucial Sub-topic 2", "Crucial Sub-topic 3"],
        "one_pager": {{
            "Key Fact 1": "Details",
            "Key Fact 2": "Details",
            "Key Fact 3": "Details"
        }},
        "flowchart": "A valid Graphviz DOT language string representing a process flowchart. Example: 'digraph G {{ A -> B; }}'. Ensure syntax is perfect.",
        "pyq_prelims": [
            {{
                "year": 2021, 
                "q": "A highly relevant mock or actual UPSC Prelims question regarding this topic.",
                "options": ["A) Option One", "B) Option Two", "C) Option Three", "D) Option Four"],
                "answer": "A) Option One",
                "explanation": "A brief explanation of why this option is correct."
            }},
            {{
                "year": 2018, 
                "q": "Another relevant Prelims question.",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "answer": "C) Option 3",
                "explanation": "A brief explanation."
            }}
        ],
        "pyq_mains": [
            {{"year": 2022, "q": "A highly relevant mock or actual UPSC Mains analytical question regarding this topic."}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            data = json.loads(raw_text.strip(), strict=False)
        return data
    except Exception as e:
        st.error(f"Error fetching data from AI: {e}")
        return None

# ---------------------------------------------------------
# Sidebar & State Management
# ---------------------------------------------------------
st.sidebar.title("🏛️ UPSC Target App")
st.sidebar.markdown("---")

if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'topic_name' not in st.session_state:
    st.session_state.topic_name = ""

st.sidebar.subheader("Search Topic")
search_query = st.sidebar.text_input("Enter a topic (e.g., 'Fundamental Rights')")

if st.sidebar.button("Generate Study Material"):
    if search_query:
        with st.spinner(f"AI is compiling data for '{search_query}'..."):
            data = fetch_topic_data_from_ai(search_query)
            if data:
                st.session_state.current_data = data
                st.session_state.topic_name = data['title']
    else:
        st.sidebar.warning("Please enter a topic.")

st.sidebar.markdown("---")
st.sidebar.subheader("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["1. Overview & Explanation", 
     "2. One-Pager Revision", 
     "3. Flow Charts", 
     "4. Previous Year Questions", 
     "5. Mains Answer Writing"]
)

# ---------------------------------------------------------
# Main Content Area
# ---------------------------------------------------------
if st.session_state.current_data is None:
    st.title("Welcome to your AI-Powered UPSC Dashboard")
    st.info("👈 Enter any topic in the syllabus in the sidebar to begin.")
else:
    data = st.session_state.current_data
    st.title(f"Topic: {data.get('title', 'Unknown Topic')}")
    
    # PAGE 1: Overview
    if page == "1. Overview & Explanation":
        st.header("In-Depth Explanation")
        st.markdown(data.get('explanation', 'No explanation provided.'))
        
        st.markdown("---")
        st.header("Crucial Sub-Topics to Master")
        for item in data.get('important_topics', []):
            st.markdown(f"- {item}")

    # PAGE 2: One-Pager
    elif page == "2. One-Pager Revision":
        st.header("One-Pager (Quick Revision)")
        one_pager_data = data.get('one_pager', {})
        if one_pager_data:
            df = pd.DataFrame(list(one_pager_data.items()), columns=['Parameter', 'Fact / Details'])
            st.table(df)
        else:
            st.write("No one-pager facts generated.")

    # PAGE 3: Flow Charts
    elif page == "3. Flow Charts":
        st.header("Process Flow / Mechanism")
        flowchart_code = data.get('flowchart', "")
        if flowchart_code and "digraph" in flowchart_code:
            try:
                st.graphviz_chart(flowchart_code)
            except Exception as e:
                st.error("The AI generated an invalid flowchart format.")
        else:
            st.info("No flowchart could be generated for this topic.")

    # PAGE 4: PYQs (INTERACTIVE)
    elif page == "4. Previous Year Questions":
        st.header("Interactive Practice Simulator")
        st.markdown("---")
        
        st.subheader("📝 Prelims Practice (MCQs)")
        prelims_qs = data.get('pyq_prelims', [])
        
        if not prelims_qs:
            st.info("No Prelims questions generated.")
        else:
            for i, pyq in enumerate(prelims_qs):
                with st.container():
                    st.markdown(f"**Q{i+1} ({pyq.get('year', 'N/A')}): {pyq.get('q')}**")
                    options = pyq.get('options', [])
                    correct_answer = pyq.get('answer', '')
                    explanation = pyq.get('explanation', '')
                    
                    if options:
                        # The index=None parameter ensures no option is selected by default
                        user_choice = st.radio("Select an option:", options, key=f"radio_{i}", index=None)
                        
                        if st.button("Check Answer", key=f"btn_{i}"):
                            if user_choice == correct_answer:
                                st.success(f"Correct! The answer is {correct_answer}")
                            elif user_choice is None:
                                st.warning("Please select an option first.")
                            else:
                                st.error(f"Incorrect. The correct answer is: {correct_answer}")
                            
                            if explanation:
                                st.info(f"**Explanation:** {explanation}")
                    st.markdown("---")

        st.subheader("🖋️ Mains Practice")
        for pyq in data.get('pyq_mains', []):
            with st.expander(f"Mains Question ({pyq.get('year', 'N/A')})"):
                st.write(pyq.get('q', ''))

    # PAGE 5: Mains Answer Writing
    elif page == "5. Mains Answer Writing":
        st.header("Mains Answer Writing Simulator")
        
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        if questions:
            selected_q = st.selectbox("Select Question to practice", questions)
            st.markdown(f"**Attempt:** {selected_q}")
            
            with st.expander("Show Recommended Structure Hint"):
                st.markdown("""
                * **Introduction:** Define the core concept. Provide a brief context or data point.
                * **Body Paragraph 1:** Address the first part of the question.
                * **Body Paragraph 2:** Address the second part/challenges/impact.
                * **Conclusion:** Way forward, SDG linkage, or policy recommendation.
                """)
            
            answer = st.text_area("Type your answer here:", height=300)
            word_count = len(answer.split())
            
            # Interactive word count progress bar
            st.caption(f"Word Count: {word_count} / 250")
            progress = min(word_count / 250, 1.0)
            st.progress(progress)
            
            if st.button("Submit Answer"):
                if word_count < 50:
                    st.warning("Your answer is too short to be evaluated. Try to hit at least 150 words.")
                else:
                    st.success("Excellent attempt! Your word count and structure look solid.")
        else:
            st.info("No Mains questions generated for this topic.")
