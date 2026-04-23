# 📚 AI Study Assistant

An AI-powered Study Assistant that helps students learn smarter by generating quizzes, flashcards, and audio summaries from notes or uploaded files.

---

## 🚀 Features

* Quiz Generator (MCQ & True/False)
* Difficulty Levels (Easy, Medium, Hard)
* Flashcards with interactive navigation
* AI Audio Summary using Text-to-Speech
* PDF, TXT, DOCX Upload Support
* Study Progress Dashboard with performance tracking

---

## 🛠️ Tech Stack

* Python
* Streamlit
* LangChain
* Groq API
* SQLite
* PyPDF
* gTTS

---

## ⚙️ How It Works

1. Upload or paste study material
2. Extract text from documents
3. Generate:

   * Quiz questions
   * Flashcards
   * Audio summaries
4. Track performance using database

---

## 📦 Installation

```bash id="clone1"
git clone https://github.com/MedhaReddyKakarla/AI-Study-Assistant.git
cd AI-Study-Assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

Run:

```bash id="run1"
streamlit run app.py
```

---

## 🤖 AI Capabilities

* Natural Language Processing
* Content Understanding using LLM
* Automated Quiz & Flashcard Generation
* Educational Content Transformation

---

## 📈 Future Improvements

* Fill-in-the-blank questions
* Smarter flashcards
* Advanced analytics dashboard
* Multi-document support


---

