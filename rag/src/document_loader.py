import pymupdf as fitz
import pytesseract
from PIL import Image
import os

# Explicit Tesseract configuration
# Path to Tesseract executable
# Tesseract executable
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Tesseract language data directory
def extract_text_with_ocr(page):
    """
    Convert PDF page to image and extract text using OCR.
    """

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image = Image.frombytes(
        "RGB",
        (pix.width, pix.height),
        pix.samples
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return text.strip()


def load_pdf(file_path):
    """
    Extract text from a PDF.
    Uses normal text extraction first.
    Falls back to OCR if the page has no extractable text.
    """

    print("Extracting text from PDF...")

    pdf = fitz.open(file_path)

    documents = []

    for page_number, page in enumerate(pdf, start=1):

        # Try normal PDF text extraction
        text = page.get_text().strip()

        # If no text exists, use OCR
        if not text:
            print(f"Page {page_number}: No text found. Using OCR...")

            text = extract_text_with_ocr(page)
            print(f"OCR TEXT FROM PAGE {page_number}:")
            print(text[:500])

        else:
            print(f"Page {page_number}: Text extracted normally.")

        # Store only pages with extracted text
        if text:
            documents.append({
                "text": text,
                "page": page_number
            })

    pdf.close()

    print(f"Extracted text from {len(documents)} pages.")

    return documents