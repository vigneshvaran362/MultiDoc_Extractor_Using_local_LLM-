import streamlit as st
import ollama
import pytesseract
from PIL import Image
import json
import fitz  # PyMuPDF
import docx  # python-docx
from pdf2image import convert_from_bytes
import io 

# --- CONFIGURATION ---

# 1. Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 2. Poppler Path (Your specific path)
POPPLER_PATH = r"E:\Personal project\Release-25.07.0-0\poppler-25.07.0\Library\bin"

# --- 1. OCR FUNCTION (Renamed) ---
def ocr_image(image):
    """Extracts text from a single PIL Image object using Tesseract."""
    st.write("Running OCR on image...")
    try:
        text = pytesseract.image_to_string(image)
        if not text.strip():
            st.warning("OCR returned no text for this image.")
            return ""
        st.success("OCR completed for 1 page.")
        return text
    except Exception as e:
        st.error(f"An error occurred during OCR: {e}")
        return ""

# --- 2. Word Doc Processor ---
def process_docx(file_bytes):
    """Extracts text from a .docx file."""
    st.write("Reading Word document...")
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = [para.text for para in doc.paragraphs]
        st.success("Word document processed.")
        return "\n".join(full_text)
    except Exception as e:
        st.error(f"Error reading .docx file: {e}")
        return None

# --- 3. PDF Processor (Hybrid) ---
def process_pdf(file_bytes):
    """
    Hybrid PDF processor.
    1. Tries to extract text directly (native PDF).
    2. If it fails (scanned PDF), it falls back to OCR.
    """
    st.write("Processing PDF...")
    full_text = ""
    
    # --- Part A: Try native text extraction (fast) ---
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text()
    except Exception as e:
        st.error(f"PyMuPDF error: {e}")
        return None

    # --- Part B: If native text is empty, fall back to OCR (slow) ---
    if not full_text.strip():
        st.warning("No native text found. Falling back to OCR. This may take a while...")
        full_text = ""
        try:
            # Convert PDF pages to images
            images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
            st.info(f"Found {len(images)} pages to OCR.")
            
            # Run OCR on each image
            for i, img in enumerate(images):
                st.write(f"Running OCR on page {i+1}...")
                page_text = ocr_image(img)
                full_text += f"\n\n--- Page {i+1} ---\n{page_text}"
            st.success("All PDF pages processed via OCR.")
        except Exception as e:
            st.error(f"PDF-to-Image conversion failed. Is Poppler installed and the path correct? Error: {e}")
            return None
    else:
        st.success("Native PDF text extracted.")
        
    return full_text

# --- 4. LLM JSON EXTRACTION FUNCTION ---
def extract_structured_data(text_content, user_prompt):
    """Uses a local LLM via Ollama to extract structured data."""
    
    system_prompt = """
    You are an expert AI assistant for a document processing pipeline.
    Your sole task is to analyze the user-provided text and extract the
    information requested in the user's prompt.

    You MUST return the extracted data in a single, valid JSON object.
    Do not provide any explanation, preamble, or text before or after the JSON.
    If a value is not found, return "null" for that field.
    """
    
    user_message = f"""
    DOCUMENT TEXT:
    ---
    {text_content}
    ---
    
    USER PROMPT:
    "{user_prompt}"
    
    Extract the information requested in the USER PROMPT from the DOCUMENT TEXT.
    Return ONLY the valid JSON object.
    """

    try:
        st.write("Sending text and prompt to local LLM (phi3:mini)...")
        response = ollama.chat(
            model='phi3:mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            format='json'
        )
        
        st.success("LLM processing complete.")
        return response['message']['content']
        
    except Exception as e:
        st.error(f"Error calling Ollama: {e}")
        st.info("Is the Ollama server running? (It should be running automatically)")
        return None

# --- 5. STREAMLIT UI ---
st.set_page_config(layout="wide")
st.title("📄 MultiDoc Extractor")
st.markdown("Upload an Image, PDF, or Word document and ask the AI to extract any information you need.")

# Custom Prompt Field
default_prompt = "Extract the all details."
user_prompt = st.text_area(
    "Enter your prompt (what you want to extract):", 
    value=default_prompt,
    height=100
)

# Updated File Uploader
uploaded_file = st.file_uploader(
    "Choose a document (PNG, JPG, PDF, DOCX)", 
    type=["png", "jpg", "jpeg", "pdf", "docx"]
)

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    # --- THIS 'with col1:' BLOCK IS THE FIXED PART ---
    with col1:
        # Create a placeholder to fix the "stuck" error message
        preview_placeholder = st.empty()

        # Logic to display different file types
        if uploaded_file.type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            preview_placeholder.image(image, caption="Uploaded Image", use_column_width=True)
        
        elif uploaded_file.type == "application/pdf":
            preview_placeholder.info("Uploaded PDF. Displaying first page as image.")
            try:
                # Show a preview of the PDF
                preview_images = convert_from_bytes(uploaded_file.getvalue(), poppler_path=POPPLER_PATH, first_page=1, last_page=1)
                if preview_images:
                    # Use the placeholder to display the image
                    preview_placeholder.image(preview_images[0], caption="PDF First Page Preview", use_column_width=True)
            except Exception as e:
                # Display the error INSIDE the placeholder
                preview_placeholder.warning(f"Could not render PDF preview: {e}")
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            preview_placeholder.info("Uploaded Word Document. Preview not available.")

    # --- This 'with col2:' block is for the results ---
    with col2:
        st.info("Processing & Results")
        with st.spinner("Processing document..."):
            
            raw_text = None
            file_bytes = uploaded_file.getvalue()

            # Main routing logic
            if uploaded_file.type in ["image/png", "image/jpeg"]:
                image = Image.open(io.BytesIO(file_bytes))
                raw_text = ocr_image(image)
            elif uploaded_file.type == "application/pdf":
                raw_text = process_pdf(file_bytes)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                raw_text = process_docx(file_bytes)
            
            if raw_text and user_prompt:
                # Step 2: Run LLM Extraction
                json_string = extract_structured_data(raw_text, user_prompt)
                
                if json_string:
                    st.subheader("Extracted JSON Data")
                    try:
                        json_data = json.loads(json_string)
                        st.json(json_data)
                    except json.JSONDecodeError:
                        st.warning("LLM did not return perfect JSON. Displaying raw output:")
                        st.code(json_string, language="json")
                        
                st.subheader("Raw Text from Document")
                st.text_area("Extracted Text", raw_text, height=300)