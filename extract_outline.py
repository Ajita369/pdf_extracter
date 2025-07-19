import fitz  # PyMuPDF
import json
import glob
import re
from collections import Counter

# 1. Extract all text spans from every page

def extract_spans(doc):
    spans = []
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        spans.append({
                            "text": text,
                            "size": round(span["size"], 1),
                            "flags": span["flags"],
                            "page": pno + 1
                        })
    return spans

# 2. Infer heading font sizes

def infer_heading_sizes(spans):
    sizes = [s["size"] for s in spans]
    freq = Counter(sizes)
    body, _ = freq.most_common(1)[0]
    larger = sorted([sz for sz in freq if sz > body], reverse=True)
    return larger[:3], body

# 3. Numbered heading detection

numbered_re = re.compile(r"^(\d+(?:\.\d+){0,2})\s+(.+)$")

def classify_numbered(text):
    m = numbered_re.match(text)
    if not m:
        return None, None
    depth = m.group(1).count('.') + 1
    return f"H{min(depth,3)}", m.group(2).strip()

# 4. Build title + outline

def build_outline(spans):
    heading_sizes, _ = infer_heading_sizes(spans)
    title = None
    outline = []

    for s in spans:
        # Title: largest font on page 1
        if s["page"] == 1 and s["size"] == heading_sizes[0] and not title:
            title = s["text"]
            continue
        # Numbered headings
        lvl, txt = classify_numbered(s["text"])
        if lvl:
            outline.append({"level": lvl, "text": txt, "page": s["page"]})
            continue
        # Size-based headings
        if s["size"] in heading_sizes:
            idx = heading_sizes.index(s["size"])
            outline.append({"level": f"H{idx+1}", "text": s["text"], "page": s["page"]})
    return title or "", outline

# 5. Main: process all PDFs

if __name__ == '__main__':
    for pdf in glob.glob('/app/input/*.pdf'):
        doc = fitz.open(pdf)
        spans = extract_spans(doc)
        title, outline = build_outline(spans)
        out = {'title': title, 'outline': outline}
        out_path = '/app/output/' + pdf.split('/')[-1].replace('.pdf', '.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)