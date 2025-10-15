import fitz
import os
import re
import random
from collections import Counter

def detect_watermark(doc, sample_ratio=0.1, threshold=0.7):
    total_pages = len(doc)
    sample_count = max(3, int(total_pages * sample_ratio))
    sampled_pages = sorted(random.sample(range(total_pages), sample_count))

    image_sets = []
    text_counts = Counter()

    for i in sampled_pages:
        page = doc[i]
        image_sets.append({img[0] for img in page.get_images(full=True)})
        text = page.get_text("text")
        words = re.findall(r'\b\w+\b', text)
        text_counts.update(set(words))

    common_images = set.intersection(*image_sets) if image_sets else set()
    common_texts = [w for w, c in text_counts.items() if c / sample_count >= threshold]

    if common_images:
        return "image", list(common_images)[0]
    elif common_texts:
        return "text", common_texts
    else:
        return None, None


def remove_image_watermark(doc, wm_xref):
    wm_names = {img[7] for page in doc for img in page.get_images(full=True) if img[0] == wm_xref}
    removed_pages = 0

    for page in doc:
        for c in page.get_contents():
            cont = doc.xref_stream(c)
            new_cont = cont
            for name in wm_names:
                pattern = re.compile(rb"/" + name.encode() + rb"\s+Do")
                new_cont = pattern.sub(b"", new_cont)
            if new_cont != cont:
                doc.update_stream(c, new_cont)
                removed_pages += 1
    return removed_pages


def remove_text_watermark(doc, watermark_words):
    removed_pages = 0
    if not watermark_words:
        return 0

    pattern = re.compile("|".join(re.escape(w) for w in watermark_words))
    for page in doc:
        text = page.get_text("text")
        if any(w in text for w in watermark_words):
            new_text = pattern.sub("", text)
            rect = page.rect
            page.clean_contents()
            page.insert_textbox(rect, new_text)
            removed_pages += 1
    return removed_pages


def process_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    wm_type, wm_data = detect_watermark(doc)

    if wm_type == "image":
        print(f"[{input_pdf}] Image watermark detected (xref={wm_data})")
        modified = remove_image_watermark(doc, wm_data)
    elif wm_type == "text":
        print(f"[{input_pdf}] Text watermark detected: {wm_data[:5]}...")
        modified = remove_text_watermark(doc, wm_data)
    else:
        print(f"[{input_pdf}] No watermark detected → skipped")
        return

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc.save(output_pdf)
    print(f" → {output_pdf} ({modified} pages modified)")


if __name__ == "__main__":
    input_folder = "."
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    for fname in os.listdir(input_folder):
        if fname.lower().endswith(".pdf"):
            inp = os.path.join(input_folder, fname)
            outp = os.path.join(output_folder, fname)
            process_pdf(inp, outp)
