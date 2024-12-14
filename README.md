# E-book Companion with Grok Vision

This application helps you analyze and recall plot points from your e-books using xAI's vision model. Upload pages from your books and ask questions about the content!

## Features

- Upload PDF pages or images from your books
- Ask questions about the content
- Get AI-powered analysis of scenes and plot points
- Support for both PDF and image formats

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your xAI API key:
```
XAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Launch the application using the command above
2. Upload a page from your book (PDF or image format)
3. Enter your question about the content
4. Click "Analyze" to get insights from the AI

## Notes

- For PDFs, currently only the first page will be analyzed
- Make sure your images are clear and readable
- The more specific your questions, the better the analysis will be

## Requirements

- Python 3.7+
- xAI API key
- See requirements.txt for full list of dependencies
