import streamlit as st
import graphviz
import pandas as pd
import google.generativeai as genai
import json
import os

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="UPSC AI Master", layout="wide", page_icon="📚")

# ---------------------------------------------------------
# API Configuration
# ---------------------------------------------------------
# Setup your Gemini API Key. 
# Best practice: create a folder named '.streamlit', inside it create 'secrets.toml'
# and add GEMINI_API_KEY = "your_key_here" to it.
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # Fallback: Replace the string below with your actual API key for testing
    # WARNING: Do not publish your app publicly with the API key hardcoded here.
    genai.configure(api_key="YOUR_API_KEY_HERE") 

# ---------------------------------------------------------
# LLM Data Generation Function
# ---------------------------------------------------------
@st.cache_data(show_spinner=False) # Caches the data so we don't call the API repeatedly for the same topic
def fetch_topic_data_from_ai(topic):
    """
    Calls the Gemini API, forces a JSON response, and returns the parsed dictionary.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # We use a highly detailed prompt to ensure the output exactly matches our app's structure
    prompt = f"""
    You are an expert UPSC (Union Public Service Commission of India) tutor.
    Generate highly accurate, in-depth study material for the topic: "{topic}".
    
    Respond ONLY with a valid JSON object. Do not include markdown formatting like ```json.
    
    The JSON must follow this exact structure:
    {{
        "title": "Clear Title of the Topic",
        "explanation": "A highly detailed, 3-4 paragraph explanation covering the geographical, historical, or constitutional basics. Use markdown (bolding, bullet points).",
        "important_topics": ["Crucial Sub-topic 1", "Crucial Sub-topic 2", "Crucial Sub-topic 3", "Crucial Sub-topic 4", "Crucial Sub-topic 5"],
        "one_pager": {{
            "Key Fact 1": "Details",
            "Key Fact 2": "Details",
            "Key Fact 3": "Details",
            "Key Fact 4": "Details",
            "Key Fact 5": "Details"
        }},
        "flowchart": "A valid Graphviz DOT language string representing a process flowchart or mind map for this topic. Example: 'digraph G {{ A -> B; B -> C; }}'. Ensure syntax is perfect.",
        "pyq_prelims": [
            {{"year": 2021, "q": "A highly relevant mock or actual UPSC Prelims question regarding this topic."}},
            {{"year": 2018, "q": "Another relevant Prelims question."}}
        ],
        "pyq_mains": [
            {{"year": 2022, "q": "A highly relevant mock or actual UPSC Mains analytical question regarding this topic."}},
            {{"year": 2019, "q": "Another relevant Mains question."}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response in case the LLM wrapped it in markdown code blocks
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        data = json.loads(raw_text.strip())
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
search_query = st.sidebar.text_input("Enter a topic (e.g., 'Anti-Defection Law', 'Buddhism')")

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
    st.info("👈 Enter any topic in the syllabus in the sidebar, and the AI will generate a complete dashboard for it.")
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
        st.write("Memorize these key facts for Prelims and to enrich Mains introductions/conclusions.")
        
        one_pager_data = data.get('one_pager', {})
        if one_pager_data:
            df = pd.DataFrame(list(one_pager_data.items()), columns=['Parameter', 'Fact / Details'])
            st.table(df)
        else:
            st.write("No one-pager facts generated.")

    # PAGE 3: Flow Charts
    elif page == "3. Flow Charts":
        st.header("Process Flow / Mechanism")
        st.write("Use this structure to save time and space in your GS papers.")
        
        flowchart_code = data.get('flowchart', "")
        if flowchart_code and "digraph" in flowchart_code:
            try:
                st.graphviz_chart(flowchart_code)
            except Exception as e:
                st.error("The AI generated an invalid flowchart format.")
                st.code(flowchart_code)
        else:
            st.info("No flowchart could be generated for this topic.")

    # PAGE 4: PYQs
    elif page == "4. Previous Year Questions":
        st.warning("⚠️ **Note:** The AI generates highly relevant practice questions, but you should verify this data against official UPSC question papers to ensure the exact year and wording are accurate.")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prelims Practice")
            for pyq in data.get('pyq_prelims', []):
                with st.expander(f"Question ({pyq.get('year', 'N/A')})"):
                    st.write(pyq.get('q', ''))
                    
        with col2:
            st.subheader("Mains Practice")
            for pyq in data.get('pyq_mains', []):
                with st.expander(f"Question ({pyq.get('year', 'N/A')})"):
                    st.write(pyq.get('q', ''))

    # PAGE 5: Mains Answer Writing
    elif page == "5. Mains Answer Writing":
        st.header("Mains Practice Simulator")
        
        questions = [q['q'] for q in data.get('pyq_mains', []) if 'q' in q]
        if questions:
            selected_q = st.selectbox("Select Question to practice", questions)
            st.markdown(f"**Attempt:** {selected_q}")
            
            with st.expander("Show Recommended Structure Hint"):
                st.markdown("""
                * **Introduction:** Define the core concept. Provide a brief context or data point.
                * **Body Paragraph 1:** Address the first part of the question.
                * **Body Paragraph 2:** Address the second part/challenges/impact. Use a micro-diagram.
                * **Conclusion:** Way forward, SDG linkage, or policy recommendation.
                """)
            
            answer = st.text_area("Type your answer here (Aim for 150-250 words):", height=300)
            word_count = len(answer.split())
            st.caption(f"Current Word Count: {word_count} words")
            
            if st.button("Submit Answer"):
                if word_count < 50:
                    st.warning("Your answer is too short. Try to elaborate on the body paragraphs.")
                else:
                    st.success("Answer recorded!")
        else:
            st.info("No Mains questions generated for this topic.")
