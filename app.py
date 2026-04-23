import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

import re
from pypdf import PdfReader

import sqlite3
from datetime import datetime

from docx import Document

st.set_page_config(
    page_title="Smart AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
    <style>

    /* Page padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 4rem;
        padding-right: 4rem;
    }

    /* Background */
    body {
        background-color: #f4f6f9;
    }

    .main {
        background-color: #f4f6f9;
    }

    /* Sidebar */
    .stSidebar {
        background-color: #e9edf2;
    }

    /* Headings */
    h1, h2, h3 {
        color: #1f2d3d;
        font-weight: 600;
    }

    /* Buttons */
    .stButton>button {
        background-color: #2f3e4d;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        border: none;
        font-size: 15px;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #3e5368;
    }

    /* Text Area */
    textarea {
        border: 1px solid #dcdfe3 !important;
        border-radius: 14px !important;
        padding: 14px !important;
        font-size: 16px !important;
        background-color: #ffffff !important;
    }

    /* Radio buttons spacing */
    .stRadio > div {
        gap: 0.6rem;
    }

    /* Card style for sections */
    .stMarkdown, .stSubheader {
        background-color: #ffffff;
        padding: 1.3rem;
        border-radius: 14px;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }

    /* Audio player spacing */
    audio {
        margin-top: 1rem;
    }

    /* Smooth overall font feel */
    html, body, [class*="css"]  {
        font-family: "Segoe UI", sans-serif;
    }

    </style>
""", unsafe_allow_html=True)

# Create database connection
conn = sqlite3.connect("study_progress.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER,
    total INTEGER,
    date TEXT
)
""")
conn.commit()

# Load API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant"
)

st.markdown("<h1 style='text-align:center;'>📚 Smart AI Study Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Your AI Study Companion</p>", unsafe_allow_html=True)


menu = st.sidebar.selectbox(
    "Choose Feature",
    ["Quiz", "Flashcards", "Audio Summary", "Progress Dashboard"]
)

# difficulty = st.sidebar.selectbox(
#     "Select Quiz Difficulty",
#     ["Easy", "Medium", "Hard"]
# )

# quiz_type = st.sidebar.selectbox(
#     "Select Quiz Type",
#     ["MCQ", "True/False"]
# )

user_input = st.text_area("Paste your study material here:")

uploaded_file = st.file_uploader(
    "Upload your study file (PDF or TXT or DOCX)",
    type=["pdf", "txt", "docx"]
)
        
if uploaded_file is not None:

    if uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        pdf_text = ""

        for page in pdf_reader.pages:
            pdf_text += page.extract_text()

        user_input = pdf_text[:4000]

    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        user_input = text[:4000]

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        doc_text = ""

        for para in doc.paragraphs:
            doc_text += para.text + "\n"

        user_input = doc_text[:4000]

if menu == "Quiz":
    
    st.markdown("""
    <div style='background:#ffffff; padding:20px; border-radius:12px;
    box-shadow:0 4px 12px rgba(0,0,0,0.06); margin-bottom:20px'>
    <h3>📝 Quiz Settings</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        difficulty = st.selectbox(
            "Select Difficulty",
            ["Easy", "Medium", "Hard"]
        )

    with col2:
        quiz_type = st.selectbox(
            "Select Quiz Type",
            ["MCQ", "True/False"]
        )

    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])

    with col_btn2:
        generate = st.button("🚀 Generate Quiz", use_container_width=True)

    if generate:

        if user_input:
            
            prompt = ChatPromptTemplate.from_template(
                """
                You are an expert educational tutor.

                Generate 5 {difficulty} level {quiz_type} questions from the given text.

                Rules:
                - Questions must be clear and meaningful
                - Avoid repetition
                - Cover different concepts
                - Keep options distinct and not obvious

                Difficulty:
                - Easy → Basic recall
                - Medium → Concept understanding
                - Hard → Analytical thinking

                If quiz type is MCQ:
                Format strictly:

                Q1: Question
                A) Option
                B) Option
                C) Option
                D) Option
                Answer: A

                If quiz type is True/False:
                Format strictly:

                Q1: Statement
                Answer: True or False

                Text:
                {text}
                """
            )

            chain = prompt | llm
            
            response = chain.invoke({
                "text": user_input,
                "difficulty": difficulty,
                "quiz_type": quiz_type
            })

            st.session_state.quiz = response.content

        else:
            st.warning("Please enter study material.")


# Show quiz if generated
if menu == "Quiz" and "quiz" in st.session_state:

    quiz_text = st.session_state.quiz
    questions = quiz_text.split("Q")[1:]

    score = 0
    user_answers = []
    
    st.markdown("## 📝 Generated Quiz")
    st.divider()

    for i, q in enumerate(questions):

        lines = q.strip().split("\n")
        question = lines[0]

        st.markdown(f"""
        <div style='background:#ffffff; padding:15px; border-radius:10px; 
        box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-bottom:10px'>
        <b>Q{i+1}:</b> {question}
        </div>
        """, unsafe_allow_html=True)

        # Detect if MCQ question
        if "A)" in q:

            options = lines[1:5]

            correct_answer = re.search(r"Answer:\s*(\w)", q)
            correct = correct_answer.group(1) if correct_answer else None

            choice = st.radio(
                label="",
                options=options,
                key=f"q{i}",
                index=None
            )

            user_answers.append((choice, correct))


        # True / False question
        else:

            correct_answer = re.search(r"Answer:\s*(True|False)", q)
            correct = correct_answer.group(1) if correct_answer else None

            choice = st.radio(
                label="",
                options=["True", "False"],
                key=f"q{i}",
                index=None
            )

            user_answers.append((choice, correct))


    if st.button("Submit Quiz"):

        for choice, correct in user_answers:

            if choice and correct:

                if choice.startswith(correct) or choice == correct:
                    score += 1

        st.markdown(f"""
        ### 🎯 Your Score: {score} / {len(questions)}
        """)

        # Save to database
        cursor.execute(
            "INSERT INTO quiz_scores (score, total, date) VALUES (?, ?, ?)",
            (score, len(questions), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        

# ---------------- FLASHCARD SECTION ----------------

if menu == "Flashcards":

    st.header("🧠 Flashcards")

    if st.button("Generate Flashcards"):

        if user_input:

            prompt = ChatPromptTemplate.from_template(
                """
                Generate 5 flashcards from this text.

                Format strictly like this:

                Q: Question
                A: Answer

                {text}
                """
            )

            chain = prompt | llm
            response = chain.invoke({"text": user_input})

            flashcards_raw = response.content.split("Q:")

            flashcards = []

            for card in flashcards_raw[1:]:
                parts = card.split("A:")
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    flashcards.append((question, answer))

            st.session_state.flashcards = flashcards
            st.session_state.card_index = 0
            st.session_state.flipped = False

        else:
            st.warning("Please enter study material first.")


    if "flashcards" in st.session_state:

        cards = st.session_state.flashcards
        index = st.session_state.card_index

        question, answer = cards[index]

        st.markdown("""
        <style>
        .flashcard-box {
            width: 280px;
            height: 380px;
            margin: 40px auto;
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            font-size: 18px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        }

        .front {
            background: linear-gradient(135deg, #dbeafe, #e0f2fe);
            color: #1e293b;
        }

        .back {
            background: linear-gradient(135deg, #dcfce7, #bbf7d0);
            color: #065f46;
        }

        .card-title {
            font-size: 14px;
            letter-spacing: 1px;
            margin-bottom: 15px;
            opacity: 0.6;
        }
        </style>
        """, unsafe_allow_html=True)

        if not st.session_state.flipped:

            st.markdown(f"""
            <div class="flashcard-box front">
                <div>
                    <div class="card-title">QUESTION</div>
                    {question}
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div class="flashcard-box back">
                <div>
                    <div class="card-title">ANSWER</div>
                    {answer}
                </div>
            </div>
            """, unsafe_allow_html=True)


        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⬅ Previous"):
                if st.session_state.card_index > 0:
                    st.session_state.card_index -= 1
                    st.session_state.flipped = False

        with col2:
            if st.button("Flip"):
                st.session_state.flipped = not st.session_state.flipped

        with col3:
            if st.button("Next ➡"):
                if st.session_state.card_index < len(cards) - 1:
                    st.session_state.card_index += 1
                    st.session_state.flipped = False
                
# ---------------- AUDIO SUMMARY SECTION ----------------

from gtts import gTTS
import tempfile

if menu == "Audio Summary":

    st.divider()
    st.header("🔊 Generate Audio Summary")

    if st.button("Generate Audio Summary"):

        if user_input:

            prompt = ChatPromptTemplate.from_template(
                "Summarize the following text in 5-6 lines:\n\n{text}"
            )

            chain = prompt | llm
            response = chain.invoke({"text": user_input})
            summary = response.content

            st.subheader("Summary:")
            st.write(summary)

            # Convert to speech
            tts = gTTS(summary)
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_audio.name)

            st.audio(temp_audio.name)

        else:
            st.warning("Please enter study material first.")
        
# ---------------- PROGRESS DASHBOARD ----------------

import pandas as pd

if menu == "Progress Dashboard":

    st.divider()
    st.header("📈 Study Progress Dashboard")

    cursor.execute("SELECT score, total, date FROM quiz_scores")
    records = cursor.fetchall()

    if records:

        df = pd.DataFrame(records, columns=["Score", "Total Questions", "Date"])

        total_attempts = len(df)
        avg_score = df["Score"].mean()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Attempts", total_attempts)

        with col2:
            st.metric("Average Score", round(avg_score, 2))

        st.markdown("### 📋 Previous Attempts")
        st.dataframe(df, use_container_width=True)

        st.markdown("")

        # Reset Button
        if st.button("🔄 Reset Progress"):
            cursor.execute("DELETE FROM quiz_scores")
            conn.commit()
            st.success("Progress reset successfully.")
            st.rerun()

    else:
        st.info("No quiz attempts yet.")