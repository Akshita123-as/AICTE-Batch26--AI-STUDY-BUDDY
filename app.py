import os
import streamlit as st  # type: ignore
import google.generativeai as genai  # type: ignore

try:
    from pdf2image import convert_from_bytes  # type: ignore
except ImportError:
    convert_from_bytes = None

try:
    import pytesseract  # type: ignore
except ImportError:
    pytesseract = None

API_KEY="add your Gemini API key here"  # Replace with your actual Gemini API key or set it as an environment variable
genai.configure(api_key=API_KEY)  # Replace with your actual Gemini API key or set it as an environment variable

try:
    for model in genai.list_models():
        print(model.name)
except Exception as e:
        print("ERROR:",e) 
        models_available = True
try:
    # Try importing from pypdf (preferred, newer package).
    # Use importlib to avoid static-analysis import warnings in some editors.
    import importlib

    pypdf = importlib.import_module("pypdf")
    PdfReader = getattr(pypdf, "PdfReader")
except Exception:
    try:
        # Fallback to PyPDF2 (older package)
        import importlib

        PyPDF2 = importlib.import_module("PyPDF2")
        PdfReader = getattr(PyPDF2, "PdfReader")
    except Exception:
        PdfReader = None


def call_model(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Model call failed: {e}"


def main():
    st.set_page_config(page_title="AI Study Buddy")
    st.title("📚 AI Powered Study Buddy")

    # Prefer API key from environment, but allow user input in the UI (safer than hardcoding).
    model_available = genai is not None

    uploaded_file = st.file_uploader("Upload your study notes (PDF)", type="pdf")
    pdf_text = ""

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            pdf_text += page_text + "\n"

        if pdf_text.strip():
            st.success("PDF uploaded successfully")
        else:
            st.warning("Uploaded PDF contains no extractable text.")

    st.sidebar.title("📚 AI Study Buddy")

    option = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📖 Summary",
            "❓ Ask Questions",
            "📝 Quiz",
            "🗂 Flashcards"
        ]
    )

    if option == "📖 Summary":
        if st.button("Generate Summary"):
            if not pdf_text.strip():
                st.warning("Please upload a PDF with text before generating a summary.")
            else:
                prompt = f"""Act as an expert teacher.

Read the notes and create a concise study summary.

Rules:
1. Use bullet points.
2. Each point should be only 1-2 lines.
3. Do not copy the original text.
4. Explain in simple student-friendly language.
5. Include only important concepts.
6. Maximum 10 points.

Notes:
{pdf_text}
"""
                result = call_model(prompt)
                st.subheader("Summary")
                st.write(result)

    elif option == "❓ Ask Questions":
        question = st.text_input("Ask a Question")
        if st.button("Get Answer"):
            if not pdf_text.strip():
                st.warning("Please upload a PDF with text before asking questions.")
            elif not question.strip():
                st.warning("Please enter a question.")
            else:
                prompt = f"""
You are an AI Study Buddy and friendly teacher.

Study Notes:
{pdf_text}

Student Question:
{question}

Instructions:
1. First check whether the answer is available in the study notes.
2. If the answer exists in the notes, answer based on the notes and mention important points from them.
3. If the answer is not present in the notes, answer using your own knowledge.
4. Explain in simple student-friendly language.
5. If the topic is difficult, provide a small example.
6. Keep the answer clear and concise.
7. If the answer is not in the notes, start with:
   "This topic is not covered in the uploaded notes, but here's an explanation:"
"""
                result = call_model(prompt)
                st.subheader("Answer")
                st.write(result)

    elif option == "📝 Quiz":
        if st.button("Generate MCQs"):
            if not pdf_text.strip():
                st.warning("Please upload a PDF with text before generating a quiz.")
            else:
                prompt = f"""
Create 10 MCQ questions from the notes.

Rules:
- Generate 10 multiple-choice questions.
- Each question should have exactly 4 options.
- Display options vertically, one per line.
- Mention the correct answer after each question.
- Questions should test understanding.
- Easy to Medium difficulty.

Format:

Q1. Question text?  question and options should not be in the same line

A. Option 1
B. Option 2
C. Option 3
D. Option 4

Correct Answer: B

Q2. Question text?

A. Option 1
B. Option 2
C. Option 3
D. Option 4

Correct Answer: D

Notes:
{pdf_text}
"""
                result = call_model(prompt)
                st.subheader("Quiz")
                st.write(result)

    elif option == "🗂 Flashcards":
        if st.button("Generate Flashcards"):
            if not pdf_text.strip():
                st.warning("Please upload a PDF with text before generating flashcards.")
            else:
                prompt = f"""
Create flashcards from the notes.

Format: question and answer should be one by one

Q: what is DBMS?

A: Software to store, manage, and retrieve data.

Q: What does DBMS stand for?

A: Database Management System

Keep answers short and easy to remember.

Notes:
{pdf_text}
"""
                result = call_model(prompt)
                st.subheader("Flashcards")
                st.write(result)
                st.markdown(result)

    else:
        st.write("Select a section from the sidebar to get started.")


if __name__ == "__main__":
    main()