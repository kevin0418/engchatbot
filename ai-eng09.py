#
#  문제 만들기 앱 - 영어 버전
#
import streamlit as st
import pdfplumber
import openai
import os
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import tempfile
import PyPDF2
import docx
import requests
from io import BytesIO

# Streamlit page configuration
st.set_page_config(
    page_title="Test Question Generator",
    page_icon="❓",
    layout="wide"
)

# Title
st.title("📚 Test Generator by Kevin")
st.markdown("Automatically generate questions from PDF, Word, or text files.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    
    # API key input
    openai_api_key = st.secrets["api_keys"]["my_api_key"]

    # Number of questions setting
    num_questions = st.slider(
        "Number of questions  (1-10)",
        min_value=1,
        max_value=10,
        value=5
    )
    
    # Question type selection
    #["Multiple Choice", "Short Answer", "Mixed"]
    question_type = st.selectbox(
        "Question type",
        ["Multiple Choice", "Fill-in-the-Blank", "Mixed"]
    )
    
    # Difficulty level
    difficulty = st.selectbox(
        "Difficulty level",
        ["Easy", "Medium", "Hard", "Adaptive"]
    )

# File upload section
st.header("1. Upload File")
uploaded_file = st.file_uploader(
    "Choose a file",
    type=['pdf', 'txt', 'docx'],
    help="Supported formats: PDF, TXT, DOCX"
)

# Direct text input option
text_input = st.text_area(
    "Or paste your text directly",
    height=150,
    placeholder="Paste the text you want to generate questions from here..."
)

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_txt(file):
    """Read content from text file"""
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading text file: {e}")
        return None

def extract_text_from_docx(file):
    """Extract text from Word document"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return None

def preprocess_text(text):
    """Preprocess text"""
    if not text:
        return None
    
    # Sentence tokenization
    try:
        sentences = sent_tokenize(text)
        st.info(f"Extracted {len(sentences)} sentences from the text.")
        return text
    except Exception as e:
        st.warning(f"Error in sentence tokenization: {e}. Using original text.")
        return text

def generate_questions_openai(text, num_questions, question_type, difficulty):
    """Generate questions using OpenAI"""
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
        return None
    
    openai.api_key = openai_api_key
       
    question_type_map = {
        "Multiple Choice": "multiple choice questions with 4 options each",
        "Fill-in-the-Blank": "Fill-in-the-Blank questions",
        "Mixed": "mixed questions (both multiple choice and sFill-in-the-Blank)"
    }
    
    prompt = f"""
    Generate {num_questions} {question_type_map[question_type]} from the following text.
    
    Requirements:
    1. Create clear and well-structured questions for Year 6-12 students
    2. For multiple choice questions, include 4 distinct options
    3. Include correct answers with brief explanations
    4. Questions should be appropriate for {difficulty.lower()} difficulty level
    5. Base questions only on the provided text content
    
    Text: {text[:4000]}  # Considering token limits
    
    Format for each question:
    Q1. [Question content]
    A. [Option A]
    B. [Option B]
    C. [Option C]
    D. [Option D]
    Answer: [Correct answer]
    Explanation: [Brief explanation]
    
    For Fill-in-the-Blank questions:
    Q1. [Question content]
    Answer: [Expected answer]
    Explanation: [Brief explanation]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional educator. You specialize in creating good quiz questions from given texts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None
 
# Main processing logic
def main():
    extracted_text = None
    
    # Process file or text input
    if uploaded_file is not None:
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            extracted_text = extract_text_from_txt(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_text = extract_text_from_docx(uploaded_file)
    
    elif text_input.strip():
        extracted_text = text_input
        st.success("Text input received.")
    
    # Text preprocessing and preview
    if extracted_text:
        processed_text = preprocess_text(extracted_text)
        
        # Text preview
        with st.expander("Extracted Text Preview"):
            st.text_area("Text content", processed_text[:1000] + "..." if len(processed_text) > 1000 else processed_text, height=200)
        
        st.header("2. Generate Questions")
        
        # Generate questions button
        if st.button("Generate Questions", type="primary"):
            with st.spinner("Generating questions..."):
                                
                questions = generate_questions_openai(processed_text, num_questions, question_type, difficulty)
                
                # Display results
                if questions:
                    st.header("3. Generated Questions")
                    st.markdown("---")
                    
                    # Format the output better
                    st.write(questions)
                    
                    # Download button
                    st.download_button(
                        label="Download Questions as Text",
                        data=questions,
                        file_name="generated_questions.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to generate questions.")

    else:
        st.info("Please upload a file or enter text to get started.")

# Check for NLTK data
try:
    sent_tokenize("test")
except LookupError:
    st.warning("Downloading NLTK data...")
    import nltk
    nltk.download('punkt')

if __name__ == "__main__":
    main()

