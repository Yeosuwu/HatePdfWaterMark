import fitz
import os
import re
import random
import logging
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="Watermark_Results.log",
    filemode="w"
)

def detect_watermark(doc, sample_ratio=0.1, threshold=0.7):
    total_pages = len(doc)

    if total_pages > 1000:
        sample_ratio = 0.02
    elif total_pages > 300:
        sample_ratio = 0.05

    sample_count = min(max(3, int(total_pages * sample_ratio)), 100)
    sampled_pages = sorted(random.sample(range(total_pages), sample_count))

    image_sets = []
    text_counts = Counter()

    for idx, i in enumerate(sampled_pages, 1):
        try:
            print(f"  → Sampling page {i+1}/{total_pages} ({idx}/{sample_count})", end="\r")
            page = doc[i]
            image_sets.append({img[0] for img in page.get_images(full=False)})

            blocks = page.get_text("blocks")
            text = " ".join(block[4] for block in blocks if len(block) > 4)
            words = re.findall(r'\b\w+\b', text)
            text_counts.update(set(words))
        except Exception as e:
            logging.warning(f"Skipped page {i} due to error: {e}")
            continue

    print() 
    common_images = set.intersection(*image_sets) if image_sets else set()
    common_texts = [w for w, c in text_counts.items() if c / sample_count >= threshold]

    if common_images:
        return "image", list(common_images)[0]
    elif common_texts:
        return "text", common_texts
    else:
        return None, None


def remove_image_watermark(doc, wm_xref):
    removed_pages = 0
    try:
        wm_names = {img[7] for page in doc for img in page.get_images(full=True) if img[0] == wm_xref}
    except Exception as e:
        logging.error(f"Failed to gather watermark names: {e}")
        return removed_pages

    total_pages = len(doc)
    for i, page in enumerate(doc, 1):
        print(f"  → Removing image watermark... ({i}/{total_pages})", end="\r")
        try:
            for c in page.get_contents():
                cont = doc.xref_stream(c)
                new_cont = cont
                for name in wm_names:
                    pattern = re.compile(rb"/" + name.encode() + rb"\s+Do")
                    new_cont = pattern.sub(b"", new_cont)
                if new_cont != cont:
                    doc.update_stream(c, new_cont)
                    removed_pages += 1
        except Exception as e:
            logging.warning(f"Failed to process page {i}: {e}")
            continue

    print()
    return removed_pages


def remove_text_watermark(doc, watermark_words):
    removed_pages = 0
    if not watermark_words:
        return 0

    pattern = re.compile("|".join(re.escape(w) for w in watermark_words))
    total_pages = len(doc)
    for i, page in enumerate(doc, 1):
        print(f"  → Removing text watermark... ({i}/{total_pages})", end="\r")
        try:
            blocks = page.get_text("blocks")
            text = " ".join(block[4] for block in blocks if len(block) > 4)
            if any(w in text for w in watermark_words):
                new_text = pattern.sub("", text)
                rect = page.rect
                page.clean_contents()
                page.insert_textbox(rect, new_text)
                removed_pages += 1
        except Exception as e:
            logging.warning(f"Failed to clean text on page {i}: {e}")
            continue

    print()
    return removed_pages


def process_pdf(input_pdf, output_pdf):
    doc = None
    try:
        doc = fitz.open(input_pdf)
        logging.info(f"Opened {input_pdf}")
        print(f"\nProcessing {input_pdf} ({len(doc)} pages)")
    except Exception as e:
        logging.error(f"Failed to open {input_pdf}: {e}")
        print(f"[ERROR] Cannot open {input_pdf}")
        return

    try:
        wm_type, wm_data = detect_watermark(doc)
    except Exception as e:
        logging.error(f"Failed to detect watermark in {input_pdf}: {e}")
        print(f"[ERROR] Detection failed for {input_pdf}")
        return

    try:
        if wm_type == "image":
            print("→ Detected image watermark")
            modified = remove_image_watermark(doc, wm_data)
        elif wm_type == "text":
            print(f"→ Detected text watermark ({wm_data[:3]}...)")
            modified = remove_text_watermark(doc, wm_data)
        else:
            print("→ No watermark detected — skipped.")
            return

        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        doc.save(output_pdf)
        logging.info(f"Saved modified PDF to {output_pdf} ({modified} pages modified)")
        print(f"✅ Saved to {output_pdf} ({modified} pages modified)\n")

    except Exception as e:
        logging.error(f"Processing failed for {input_pdf}: {e}")
        print(f"[ERROR] Processing failed: {e}")

    finally:
        if doc:
            doc.close()
            logging.info(f"Closed {input_pdf}")


if __name__ == "__main__":
    input_folder = "."
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    print("=== PDF Watermark Remover ===\n")

    for fname in os.listdir(input_folder):
        if fname.lower().endswith(".pdf"):
            inp = os.path.join(input_folder, fname)
            outp = os.path.join(output_folder, fname)
            process_pdf(inp, outp)

    print("All PDFs processed.\n")
