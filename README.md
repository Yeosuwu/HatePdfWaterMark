# PDF Watermark Remover

This script automatically detects and removes both **image** and **text** watermarks from PDF files using [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/).

It’s optimized for documents where the same watermark (image or text) appears repeatedly on many or all pages.

---

## How it works

1. The script analyzes a **small random sample (≈ 10%)** of the pages.  
   - It compares all image objects across those sampled pages to find any identical image → **image watermark**.  
   - It also compares the text content across the same pages to find repeated words → **text watermark**.

2. Based on what it detects:  
   - **Image watermark:** removes every reference to the detected image object across the entire file.  
   - **Text watermark:** removes recurring text patterns that appear on most sampled pages.

3. The cleaned PDF is saved to an `output` folder with the same filename.

---

## Usage

1. Install dependencies:
   pip install pymupdf

2. Place your PDF files in the same folder as the script.

3. Run the script:
   python HatePdfWaterMark.py

4. Cleaned PDFs will be saved in an `output` folder.

---

## When it works best

✅ Works best when:
- The watermark (image or text) is **identical** on most or all pages.  
- The watermark appears consistently from the beginning or throughout the document.  
- The watermark is embedded as a separate image object or text layer.

⚠️ May not work if:
- Each page has a slightly different watermark.  
- The watermark is part of the background image or scanned text.  
- The watermark appears only on a few pages with unique positioning.

---

## Notes

- The script automatically detects whether the watermark is image-based or text-based — no manual configuration needed.  
- Sampling only about 10% of pages makes it **fast**, even for large PDFs.  
- The detection threshold and sample ratio can be adjusted inside the code (`sample_ratio`, `threshold`).  
- Outputs are saved in the `output` directory with the same filenames.

---

Save hours of manual cleanup.  
Remove image **and** text watermarks from PDFs in seconds.
