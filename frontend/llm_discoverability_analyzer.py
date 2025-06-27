
import streamlit as st
import requests
import asyncio
import websockets
import json

# --- Page Setup ---
st.set_page_config(page_title="LLM Discoverability Analyzer", layout="wide")
st.title("🔍 LLM Discoverability Analyzer")
st.markdown("See exactly how ChatGPT talks about your brand when customers ask questions")

@st.cache_data
def fetch_categories():
    try:
        response = requests.get("http://127.0.0.1:8000/question-repository/categories")
        if response.status_code == 200:
            return response.json().get("unique_categories", [])
        else:
            return []
    except:
        return []

# --- Sidebar ---
with st.sidebar:
    st.header("Experiment Setup")
    st.subheader("Your Brand")

    brand_name = st.text_input("Brand Name", placeholder="e.g., Clay")
    categories = fetch_categories()
    category = st.selectbox("Industry/Category", options=[""] + categories + ["Other"])

    custom_category = ""
    if category == "Other" or category == "":
        custom_category = st.text_input("Custom Category", placeholder="e.g., Sales Intelligence")

    final_category = custom_category if category in ["Other", ""] else category

    competitors = st.text_area("Key Competitors", placeholder="One per line:\nZoomInfo\nClearbit\nApollo.io")

    # Load Smart Templates
    st.subheader("Questions to Test")
    st.caption("What are your potential customers asking ChatGPT?")

    all_required = all([brand_name.strip(), final_category.strip(), competitors.strip()])
    if st.button("📄 Load Smart Templates", disabled=not all_required):
        try:
            res = requests.get("http://127.0.0.1:8000/question-repository").json()
            competitors_list = [c.strip() for c in competitors.splitlines() if c.strip()]
            comp_str = ", ".join(competitors_list)
            matching = [q["question"] for q in res["questions"] if q["category"].lower() == final_category.lower()]
            personalized = [q.replace("[brand]", brand_name).replace("[competitor]", comp_str) for q in matching]

            if personalized:
                st.session_state.questions = personalized
            else:
                st.warning("No matching questions found.")
        except Exception as e:
            st.error(f"Failed to load: {str(e)}")

    if "questions" not in st.session_state:
        st.session_state.questions = []

    new_q = st.text_input("➕ Add Custom Question", max_chars=200)
    if st.button("Add Question") and new_q.strip():
        st.session_state.questions.append(new_q.strip())

    st.markdown("**Current Questions:**")
    st.markdown("**Select the questions you'd like to keep:**")

    selected_flags = []
    for i, q in enumerate(st.session_state.questions):
        is_selected = st.checkbox(q, key=f"select_{i}")
        selected_flags.append(is_selected)

    st.session_state.final_selected_questions = [
        q for q, selected in zip(st.session_state.questions, selected_flags) if selected
    ]

    st.caption("Minimum 5 questions recommended for meaningful insights")

    st.subheader("Select AI to Test")
    st.checkbox("ChatGPT (GPT-4)", value=True)
    st.checkbox("Perplexity (Coming Soon)", value=False, disabled=True)
    st.checkbox("Claude (Coming Soon)", value=False, disabled=True)
    st.checkbox("Gemini (Coming Soon)", value=False, disabled=True)

# --- Function: WebSocket Call ---
async def fetch_answers_ws(questions):
    uri = "ws://localhost:8000/ws/bulk-answer"
    total = len(questions)
    results = []
    progress_bar = st.progress(0, text="⏳ Waiting for responses...")

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"questions": questions}))
        received = 0

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data["type"] == "progress":
                received += 1
                percent = int((received / total) * 100)
                progress_bar.progress(percent, text=f"✅ Received {received}/{total} responses")

            elif data["type"] == "complete":
                results = data["results"]
                progress_bar.progress(100, text="🎉 All responses received!")
                break

    return results

# --- Main Area ---
st.subheader("🧠 Summary")
st.markdown("---")

if st.button("🔵 Test Brand Visibility"):
    if not st.session_state.final_selected_questions:
        st.warning("⚠️ Please select at least one question.")
    else:
        with st.spinner("Running analysis..."):
            # Get ChatGPT answers via WebSocket
            answers = asyncio.run(fetch_answers_ws(st.session_state.final_selected_questions))
            st.session_state.answers = answers

            # Call analysis API
            try:
                competitors_list = [c.strip() for c in competitors.splitlines() if c.strip()]
                payload = {
                    "brand": brand_name,
                    "category": final_category,
                    "competitors": competitors_list,
                    "questions_and_responses": [
                        {"question": item["question"], "answer": item["answer"]} for item in answers
                    ]
                }
                res = requests.post("http://127.0.0.1:8000/generate-analysis", json=payload)
                if res.status_code == 200:
                    st.session_state.analysis = res.json()
                else:
                    st.session_state.analysis = {"analysis": "Failed to generate analysis.", "total_tokens": 0, "total_cost": 0.0}
            except Exception as e:
                st.session_state.analysis = {"analysis": f"Error: {e}", "total_tokens": 0, "total_cost": 0.0}

# Show Results if Available
if "answers" in st.session_state and "analysis" in st.session_state:
    tab1, tab2, tab3, tab4 = st.tabs([
    "🗒️ Questions & Answers", 
    "📊 AI-Generated Analysis", 
    "📋 Raw Analysis Data", 
    "📁 Export"
])

    with tab1:
        for idx, item in enumerate(st.session_state.answers, start=1):
            st.markdown(f"### Q{idx}: {item['question']}")
            st.markdown("**ChatGPT's Response:**")
            st.code(item["answer"], language="markdown")

            brand_mentioned = "Yes" if brand_name.lower() in item["answer"].lower() else "No"
            mentioned_comps = [
                c for c in competitors.splitlines() if c.lower() in item["answer"].lower()
            ]
            word_count = len(item["answer"].split())
            cost = round(item["total_cost"], 5)
            tokens = item["total_tokens"]

            st.markdown(f"""
**Quick Facts:**
- Your brand mentioned: **{brand_mentioned}**
- Competitors mentioned: **{', '.join(mentioned_comps) if mentioned_comps else 'None'}**
- Response length: **{word_count} words**
- Total tokens: **{tokens}**
- Total cost: **${cost}**
""")
            st.markdown("---")

    with tab2:
        st.markdown("## 📊 AI-Generated Analysis")
        st.info("This section shows ChatGPT's analysis of all the responses.")
        st.markdown("### 🔍 Summary Insights")
        st.markdown(st.session_state.analysis["analysis"])
        st.markdown("---")
        st.markdown("### 📈 Basic Statistics")
        st.markdown(f"""
- Total questions asked: **{len(st.session_state.answers)}**
- Responses mentioning your brand: **{sum(1 for a in st.session_state.answers if brand_name.lower() in a["answer"].lower())}**
- Responses mentioning competitors: **{sum(1 for a in st.session_state.answers if any(c.lower() in a["answer"].lower() for c in competitors.splitlines()))}**
- Total tokens used: **{st.session_state.analysis.get("total_tokens", 0)}**
- Total cost: **${round(st.session_state.analysis.get("total_cost", 0.0), 5)}**
""")
    
    import pandas as pd

    with tab3:
        st.markdown("## 📑 Raw Mention Tracking")

        questions = [item["question"] for item in st.session_state.answers]
        answers = [item["answer"] for item in st.session_state.answers]
        competitors_list = [c.strip() for c in competitors.splitlines() if c.strip()]
        all_entities = [brand_name] + competitors_list

        # Create mention matrix
        mention_data = []
        for q, a in zip(questions, answers):
            row = {"Question": q}
            for entity in all_entities:
                row[entity] = "Yes" if entity.lower() in a.lower() else "No"
            mention_data.append(row)

        df = pd.DataFrame(mention_data)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Export Mention Table as CSV", csv, file_name="mention_tracking.csv", mime="text/csv")

    # -----------------------
    # Tab 4: Export
    # -----------------------
    import io

    with tab4:
        st.markdown("## 📤 Export Options")

        # Download Raw JSON
        export_data = {
            "brand": brand_name,
            "category": final_category,
            "competitors": competitors_list,
            "questions_and_responses": st.session_state.answers,
            "analysis": st.session_state.analysis
        }
        json_bytes = json.dumps(export_data, indent=2).encode("utf-8")
        st.download_button("📊 Download Raw Data (JSON)", data=json_bytes, file_name="llm_analysis_raw.json", mime="application/json")

        