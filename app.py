import streamlit as st
import os
from openai import OpenAI
import base64
from PIL import Image
from pdf2image import convert_from_path
import io
import tempfile
import glob
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="📚 GROKFLIX",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Netflix-like theme
st.markdown("""
    <style>
    /* Main theme colors and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@400;700&display=swap');
    
    :root {
        --netflix-red: #E50914;
        --netflix-black: #141414;
        --netflix-dark-gray: #181818;
        --netflix-light-gray: #2F2F2F;
    }

    /* Global styles */
    .stApp {
        background-color: var(--netflix-black);
        color: white;
        font-family: 'Netflix Sans', sans-serif;
    }

    .main {
        background-color: var(--netflix-black);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--netflix-dark-gray);
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Netflix Sans', sans-serif;
        font-weight: bold;
        color: white;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: var(--netflix-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-family: 'Netflix Sans', sans-serif !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background-color: #f40612 !important;
        transform: scale(1.02);
    }

    /* File uploader */
    .upload-box {
        background-color: var(--netflix-dark-gray);
        border: 2px solid var(--netflix-light-gray);
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        transition: all 0.3s ease;
    }

    .upload-box:hover {
        border-color: var(--netflix-red);
        box-shadow: 0 0 10px rgba(229, 9, 20, 0.3);
    }

    /* Text areas and inputs */
    .stTextArea>div>div>textarea {
        background-color: var(--netflix-dark-gray);
        color: white;
        border: 1px solid var(--netflix-light-gray);
        border-radius: 4px;
        padding: 12px;
    }

    .stTextArea>div>div>textarea:focus {
        border-color: var(--netflix-red);
        box-shadow: 0 0 10px rgba(229, 9, 20, 0.3);
    }

    /* Cards */
    .netflix-card {
        background-color: var(--netflix-dark-gray);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .netflix-card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }

    /* Spinner */
    .stSpinner {
        border-top-color: var(--netflix-red) !important;
    }

    /* Alerts and messages */
    .stAlert {
        background-color: var(--netflix-dark-gray);
        color: white;
        border: 1px solid var(--netflix-red);
    }

    /* Dividers */
    hr {
        border-color: var(--netflix-light-gray);
    }

    /* Images */
    .stImage {
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stImage:hover {
        transform: scale(1.02);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--netflix-black);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--netflix-light-gray);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--netflix-red);
    }

    /* Carousel styles */
    .book-row {
        display: flex;
        overflow-x: auto;
        padding: 20px 0;
        scroll-behavior: smooth;
    }
    
    .book-card {
        background-color: var(--netflix-dark-gray);
        border-radius: 4px;
        margin: 0 10px;
        min-width: 200px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .book-card:hover {
        transform: scale(1.1);
        z-index: 1;
    }
    
    .book-card img {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 4px;
    }
    
    .book-title {
        padding: 10px;
        color: white;
        font-weight: bold;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: var(--netflix-black);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
        background-color: var(--netflix-black);
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--netflix-red);
        border-bottom: 2px solid var(--netflix-red);
    }
    </style>
    """, unsafe_allow_html=True)

def init_client():
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        st.error("❌ Please set your XAI API key in the .env file")
        return None
    return OpenAI(
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
    )

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def process_uploaded_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file.flush()
                try:
                    images = convert_from_path(tmp_file.name)
                    os.unlink(tmp_file.name)
                    return images[0] if images else None
                except Exception as e:
                    st.error("❌ Error processing PDF: Please make sure poppler is installed.")
                    st.info("💡 On Mac, you can install poppler using: brew install poppler")
                    return None
        else:
            return Image.open(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        return None

def analyze_image(client, image, query):
    if not client:
        return "Error: XAI client not initialized"
    
    with st.spinner("🎬 Analyzing your book..."):
        try:
            base64_image = encode_image(image)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": query,
                        },
                    ],
                },
            ]

            response = client.chat.completions.create(
                model="grok-vision-beta",
                messages=messages,
                stream=False,
                temperature=0.01,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error analyzing image: {str(e)}"

def load_sample_books():
    """Load sample books from the sample_books directory"""
    sample_books = []
    sample_books_path = os.path.join(os.path.dirname(__file__), 'sample_books')
    for pdf_file in glob.glob(os.path.join(sample_books_path, '*.pdf')):
        try:
            # Convert first page to image for preview
            images = convert_from_path(pdf_file, first_page=1, last_page=1)
            if images:
                preview = images[0]
                sample_books.append({
                    'path': pdf_file,
                    'name': Path(pdf_file).stem.replace('_', ' ').title(),
                    'preview': preview
                })
        except Exception as e:
            st.error(f"Error loading {pdf_file}: {str(e)}")
    return sample_books

def show_book_carousel(books, title):
    """Display a Netflix-style book carousel"""
    st.markdown(f"### {title}")
    
    # Create a row of books
    cols = st.columns(4)
    for i, book in enumerate(books):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class='book-card' onclick='select_book("{book['path']}")'>
                    <img src='data:image/jpeg;base64,{encode_image(book["preview"])}' />
                    <div class='book-title'>{book['name']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def main():
    # Header with Netflix-style logo
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #E50914; font-size: 3.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
                📚 GROKFLIX
            </h1>
            <p style='color: #ffffff; font-size: 1.2em;'>Your AI Book Companion</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize client
    client = init_client()

    # Tabs for Browse and My Books
    tab1, tab2 = st.tabs(["📚 Browse Books", "📖 My Books"])

    with tab1:
        # Load and display sample books
        sample_books = load_sample_books()
        
        # Show different categories
        st.markdown("## Popular Books")
        show_book_carousel(sample_books[:4], "Trending Now")
        
        st.markdown("## Classic Literature")
        show_book_carousel(sample_books[4:8] if len(sample_books) > 4 else sample_books, "Timeless Classics")
        
        st.markdown("## Science Fiction")
        show_book_carousel(sample_books[8:12] if len(sample_books) > 8 else sample_books, "Explore New Worlds")

    with tab2:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown("<div class='netflix-card'>", unsafe_allow_html=True)
            st.markdown("### 📚 Upload Your Book")
            uploaded_file = st.file_uploader(
                "Choose a book (PDF) or page (Image)",
                type=["pdf", "png", "jpg", "jpeg"],
                help="Supported formats: PDF, PNG, JPG, JPEG"
            )
            
            if uploaded_file:
                image = process_uploaded_file(uploaded_file)
                if image:
                    st.image(image, caption="", use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='netflix-card'>", unsafe_allow_html=True)
            st.markdown("### 🎬 Ask About Your Book")
            
            # Sample questions
            st.markdown("#### 💡 Popular Questions")
            questions = [
                "What are the main events in this scene?",
                "Who are the key characters involved?",
                "What's the significance of this moment?",
                "How does this connect to the plot?"
            ]
            
            cols = st.columns(2)
            for i, q in enumerate(questions):
                with cols[i % 2]:
                    if st.button(q, key=f"q_{i}"):
                        st.session_state.query = q

            st.markdown("#### 🎭 Your Question")
            query = st.text_area(
                "",
                value=st.session_state.get("query", ""),
                placeholder="Type your question about the book...",
                height=100
            )

            if st.button("🎬 Analyze", key="analyze_button"):
                if uploaded_file and query:
                    response = analyze_image(client, image, query)
                    st.markdown("#### 🎯 Analysis")
                    st.markdown(f"<div class='netflix-card'>{response}</div>", unsafe_allow_html=True)
                elif not uploaded_file:
                    st.warning("🎬 Please upload a book page first!")
                else:
                    st.warning("🎬 Please enter your question!")
            st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style='text-align: center; padding: 20px; color: #666666;'>
            <p>Made with 🎬 by GROKFLIX | Powered by xAI's Grok Vision</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    if 'query' not in st.session_state:
        st.session_state.query = ""
    main()
