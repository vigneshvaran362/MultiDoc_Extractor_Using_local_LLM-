📄 MultiDoc Extractor
MultiDoc Extractor is a high-performance, privacy-first document analysis tool. It runs 100% locally, using a hybrid retrieval system (Tesseract, PyMuPDF) and a local LLM (Ollama) to extract custom, structured data from various document types, including images, scanned PDFs, native PDFs, and Word documents.

🚀 Live Demo



https://github.com/user-attachments/assets/e4aafa90-33cc-4402-81fe-b4f859fb3061


💡 The "Why" (The Problem)
In a world of cloud APIs, processing sensitive documents (like invoices, medical reports, or legal contracts) is a risk. Data is sent to third-party servers, incurring API costs and creating a data privacy blindspot.

This project solves that problem. MultiDoc Extractor provides a powerful, query-based extraction tool that runs entirely on your own machine. It's:

Privacy-First: No data ever leaves your computer.

Cost-Free: No API bills, no matter how many documents you process.

Flexible: It's not limited to fixed fields. You can ask for any information in plain English (e.g., "Extract the line items and their quantities").

⚙️ Architecture
The application uses a hybrid, multi-modal retrieval pipeline. The right tool is selected for each file type to extract raw text, which is then fed to the LLM for analysis.

File Upload (.pdf, .docx, .png, .jpg)     ↓ Hybrid Retrieval Pipeline

Scanned PDF/Image: → Poppler (Converts to Image) → Tesseract OCR (Extracts Text)

Native PDF: → PyMuPDF (Extracts Text Directly)

Word DOCX: → python-docx (Extracts Text Directly)     ↓ Text & Custom Prompt     ↓ Local LLM (Ollama + phi3:mini)     ↓ Structured JSON Output

✨ Key Features
Multi-Modal Input: Handles .pdf (scanned or native), .docx, .png, and .jpg files.

Hybrid PDF Processing: Intelligently chooses between fast native text extraction (PyMuPDF) and robust OCR (Tesseract) for scanned PDFs.

Custom Querying: Uses a local LLM to extract any data you ask for via a text prompt.

100% Local: All processing, from OCR to LLM inference, happens on your machine.

Simple UI: A clean Streamlit interface for file uploads, custom prompts, and results.

💻 Tech Stack
Backend & UI: Python, Streamlit

LLM Serving: Ollama

LLM Model: phi3:mini (or any Ollama model like llama3:8b)

OCR Engine: Tesseract

Document Parsing:

PyMuPDF (fitz) - Native PDFs

python-docx - Word Documents

pdf2image - PDF to Image Conversion

Dependencies: Poppler (for pdf2image)

🚀 How to Run It Locally
Prerequisites
You must have the following non-Python dependencies installed first:

Ollama: Download and install from ollama.com. (The server will run automatically in the background).

Tesseract OCR: Download the installer. Crucial: During installation, ensure you check the box to "Add Tesseract to system PATH".

Poppler: Download the latest Windows release (.zip file). Unzip it to a permanent location (e.g., C:\Program Files\poppler).

Setup Instructions
Clone this repository:

Bash

git clone https://your-github-repo-url/MultiDoc-Extractor.git
cd MultiDoc-Extractor
Create and activate a virtual environment:

Bash

python -m venv .venv
.\.venv\Scripts\Activate.ps1
(If you get a script error, run this first: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process)

Install Python libraries:

Bash

pip install -r requirements.txt
(Note: You'll need to create a requirements.txt file with all the libraries we installed: streamlit, ollama, pytesseract, pillow, PyMuPDF, pdf2image, python-docx)

Pull the LLM model:

Bash

ollama pull phi3:mini
Configure Paths in app.py: Open app.py and update the paths at the top of the file to match your Tesseract and Poppler installations.

Python

# 1. Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 2. Poppler Path (Point this to the 'bin' folder)
POPPLER_PATH = r"C:\path\to\your\poppler-xx.xx.x\Library\bin"
Run the app!

Bash

streamlit run app.py
