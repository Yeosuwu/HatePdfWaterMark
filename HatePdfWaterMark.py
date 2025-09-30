import fitz
import os
import re

def find_watermark_xref(doc):
    if len(doc) < 2:
        return None
    xrefs1 = {img[0] for img in doc[0].get_images(full=True)}
    xrefs2 = {img[0] for img in doc[1].get_images(full=True)}
    common = xrefs1 & xrefs2
    return list(common)[0] if common else None

def remove_watermark(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    wm_xref = find_watermark_xref(doc)

    if not wm_xref:
        print(f"[{input_pdf}] No common image found → skipped")
        return

    wm_names = {img[7] for page in doc for img in page.get_images(full=True) if img[0] == wm_xref}

    if not wm_names:
        print(f"[{input_pdf}] Could not find watermark name → skipped")
        return

    print(f"[{input_pdf}] Watermark xref={wm_xref}, names={wm_names}")

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

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc.save(output_pdf)
    print(f" → {output_pdf} ({removed_pages} pages modified)")


if __name__ == "__main__":
    input_folder = "."
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    for fname in os.listdir(input_folder):
        if fname.lower().endswith(".pdf"):
            inp = os.path.join(input_folder, fname)
            outp = os.path.join(output_folder, fname)
            remove_watermark(inp, outp)
