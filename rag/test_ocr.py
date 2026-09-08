import fitz
from src.document_loader import extract_text_with_ocr


PDF_PATH = "rag/data/V3+T+ALBUM.pdf"

# Pages where OCR was triggered
OCR_PAGES = [16, 20, 25, 52, 54]


def main():
    pdf = fitz.open(PDF_PATH)

    for page_number in OCR_PAGES:
        print("\n" + "=" * 60)
        print(f"OCR TEST - PAGE {page_number}")
        print("=" * 60)

        # PyMuPDF uses 0-based indexing
        page = pdf[page_number - 1]

        text = extract_text_with_ocr(page)

        if text.strip():
            print(text[:1500])
        else:
            print("No text detected by OCR.")

    pdf.close()


if __name__ == "__main__":
    main()