# PDF Watermark Remover

This script removes repeated image watermarks from PDF files using [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/).

It is designed for scanned PDFs where the same watermark image is inserted on every page (for example, class notes, books, or distributed materials).

---

## How it works

1. The script compares the images on **page 1 and page 2**.  
   - Regular content images are different on each page.  
   - The repeated image found on both pages is assumed to be the watermark.

2. Once the watermark image is identified, the script scans the whole document.  
   - It finds all references to the same image.  
   - It removes those references from every page.

3. A cleaned PDF is saved without the watermark.

---

## Usage

1. Install requirements:
   ```bash
   pip install pymupdf
   ```

2. Place your PDF files in the same folder as the script.

3. Run the script:
   ```bash
   python start.py
   ```

4. Cleaned PDFs will be saved in an `output` folder with the same filename.

---

## When it works

- Works best when:
  - The watermark is **the same image** on all pages.
  - The watermark appears in **page 1 and page 2**.
- Does not work if:
  - The watermark is text, not an image.
  - Each page uses a slightly different watermark image.

---

## Notes

- The script is optimized for repeated image watermarks only.  
- For text-based watermarks, you need a different approach.  
- Tested with educational PDFs and scanned documents.
