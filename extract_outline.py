import fitz       # PyMuPDF
import json
import glob
import os
import re
import langid
from collections import Counter

# 1) Numbered‑heading regex (e.g. "1.", "1.2.", "1.2.3")
numbered_re = re.compile(r"^(\d+(?:\.\d+){0,2})\s+(.+)$")
def classify_numbered(text):
    m = numbered_re.match(text)
    if not m:
        return None, None
    depth = m.group(1).count('.') + 1
    return f"H{min(depth, 3)}", m.group(2).strip()

# 2) Extract all text spans (with font sizes) from every page
def extract_spans(doc):
    spans = []
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        for blk in page.get_text("dict")["blocks"]:
            if blk["type"] != 0:  # ignore non-text blocks
                continue
            for line in blk["lines"]:
                for sp in line["spans"]:
                    txt = sp["text"].strip()
                    if not txt:
                        continue
                    spans.append({
                        "text": txt,
                        "size": round(sp["size"], 1),
                        "page": pno  # zero‑indexed pages
                    })
    return spans

# 3) Infer heading font sizes by frequency clustering
def infer_heading_sizes(spans):
    freq = Counter(s["size"] for s in spans)
    if not freq:
        return [], None
    # Most common size = body text
    body_size, _ = freq.most_common(1)[0]
    # Any larger sizes are potential headings
    larger = sorted((sz for sz in freq if sz > body_size), reverse=True)
    # Up to three tiers (H1, H2, H3)
    return larger[:3], body_size

# 4) Build the outline with title‑fallback and deferred langid
def build_outline(spans):
    heading_sizes, _ = infer_heading_sizes(spans)
    title = None
    seen_title = set()
    temp = []

    # 4.1 Classification pass (no langid calls here)
    for s in spans:
        txt, pg, sz = s["text"], s["page"], s["size"]

        # Title: first span on page 0 with the largest heading-size
        if pg == 0 and heading_sizes and sz == heading_sizes[0] and title is None:
            title = txt
            seen_title.add(txt)
            continue

        # Numbered headings override (1., 1.2., 1.2.3)
        lvl, core = classify_numbered(txt)
        if lvl:
            temp.append((lvl, core, pg))
            continue

        # Size‑based headings (font size tiers)
        if sz in heading_sizes and txt not in seen_title:
            idx = heading_sizes.index(sz)
            temp.append((f"H{idx+1}", txt, pg))

    # 4.2 Title‑fallback if not set above
    if not title:
        page0_spans = [s for s in spans if s["page"] == 0]
        if page0_spans:
            # Choose the span with the maximum font size
            fallback = max(page0_spans, key=lambda x: x["size"])
            title = fallback["text"]

    # 4.3 Attach language tag to each heading (deferred langid)
    outline = []
    for lvl, txt, pg in temp:
        lang, _ = langid.classify(txt)
        outline.append({
            "level": lvl,
            "text": txt,
            "page": pg,
            "lang": lang or None
        })

    return title or "", outline

# 5) Main: process all PDFs in app/input → app/output
if __name__ == "__main__":
    INPUT_DIR  = os.path.join("app", "input")
    OUTPUT_DIR = os.path.join("app", "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for pdf_path in glob.glob(os.path.join(INPUT_DIR, "*.pdf")):
        print(f"📄 Processing {pdf_path} …")
        try:
            doc = fitz.open(pdf_path)
            spans = extract_spans(doc)
            title, outline = build_outline(spans)

            result = {
                "title":   title,
                "outline": outline
            }

            base = os.path.splitext(os.path.basename(pdf_path))[0]
            out_path = os.path.join(OUTPUT_DIR, f"{base}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved to {out_path}")
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")

