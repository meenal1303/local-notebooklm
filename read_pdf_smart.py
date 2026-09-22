import fitz
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(pdf_path, min_chars_per_page=50):
    """
    Extract text from a PDF.
    - Tries normal text extraction first.
    - Falls back to OCR for pages that look like scans.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_number, page in enumerate(doc, start=1):
        # Try normal text extraction first
        text = page.get_text().strip()

        if len(text) < min_chars_per_page:
            # Looks like a scanned/image page — run OCR
            print(f"  Page {page_number}: text too short ({len(text)} chars), running OCR...")
            
            # Render the page as an image at 2x zoom for better OCR accuracy
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            
            # Run OCR
            text = pytesseract.image_to_string(img).strip()
            print(f"  Page {page_number}: OCR extracted {len(text)} chars")
        else:
            print(f"  Page {page_number}: got {len(text)} chars directly")

        full_text += f"\n--- Page {page_number} ---\n{text}"

    doc.close()
    return full_text


if __name__ == "__main__":
    pdf_file = "Photo.pdf"  # change to "scanned.pdf" to test OCR
    print(f"Reading {pdf_file}...\n")
    result = extract_text_from_pdf(pdf_file)
    print("\n--- First 1000 characters ---")
    print(result[:1000])
    print(f"\n[Total characters: {len(result)}]")
