
# import fitz  # PyMuPDF
# import json
# import glob
# import re
# import os
# from collections import Counter

# # 1. Extract all text spans from every page
# def extract_spans(doc):
#     spans = []
#     for pno in range(doc.page_count):
#         page = doc.load_page(pno)
#         for b in page.get_text("dict")["blocks"]:
#             if b["type"] != 0:
#                 continue
#             for line in b["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"].strip()
#                     if text:
#                         spans.append({
#                             "text": text,
#                             "size": round(span["size"], 1),
#                             "flags": span["flags"],
#                             "page": pno  # ✅ Page numbers start from 0
#                         })
#     return spans

# # 2. Infer heading font sizes
# def infer_heading_sizes(spans):
#     sizes = [s["size"] for s in spans]
#     freq = Counter(sizes)
#     body, _ = freq.most_common(1)[0]
#     larger = sorted([sz for sz in freq if sz > body], reverse=True)
#     return larger[:3], body

# # 3. Numbered heading detection
# numbered_re = re.compile(r"^(\d+(?:\.\d+){0,2})\s+(.+)$")

# def classify_numbered(text):
#     m = numbered_re.match(text)
#     if not m:
#         return None, None
#     depth = m.group(1).count('.') + 1
#     return f"H{min(depth, 3)}", m.group(2).strip()

# # 4. Build title + outline
# def build_outline(spans):
#     heading_sizes, _ = infer_heading_sizes(spans)

#     # ✅ Pick first span with largest heading size on page 0
#     title = ""
#     title_candidates = [s for s in spans if s["page"] == 0 and s["size"] == heading_sizes[0]]
#     title_span = None
#     if title_candidates:
#         title_span = title_candidates[0]
#         title = title_span["text"]

#     outline = []
#     for s in spans:
#         # ✅ Skip span used as title
#         if title_span and s["text"] == title and s["page"] == title_span["page"] and s["size"] == title_span["size"]:
#             continue

#         # Numbered headings
#         lvl, txt = classify_numbered(s["text"])
#         if lvl:
#             outline.append({"level": lvl, "text": txt, "page": s["page"]})
#             continue

#         # Size-based headings
#         if s["size"] in heading_sizes:
#             idx = heading_sizes.index(s["size"])
#             outline.append({"level": f"H{idx+1}", "text": s["text"], "page": s["page"]})

#     return title, outline

# # 5. Main: process all PDFs
# if __name__ == '__main__':
#     input_dir = os.path.join("app", "input")
#     output_dir = os.path.join("app", "output")

#     for pdf in glob.glob(os.path.join(input_dir, "*.pdf")):
#         print(f"Processing: {pdf}")
#         doc = fitz.open(pdf)
#         spans = extract_spans(doc)
#         title, outline = build_outline(spans)
#         out = {'title': title, 'outline': outline}
#         filename = os.path.basename(pdf).replace(".pdf", ".json")
#         out_path = os.path.join(output_dir, filename)
#         with open(out_path, 'w', encoding='utf-8') as f:
#             json.dump(out, f, indent=2, ensure_ascii=False)
#         print(f"Saved to: {out_path}")








import fitz  # PyMuPDF
import json
import glob
import re
import os
from collections import Counter
import langid

# 1. Extract spans from each page
def extract_spans(doc):
    spans = []
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        spans.append({
                            "text": text,
                            "size": round(span["size"], 1),
                            "flags": span["flags"],
                            "page": pno
                        })
    return spans

# 2. Identify heading font sizes
def infer_heading_sizes(spans):
    sizes = [s["size"] for s in spans]
    freq = Counter(sizes)
    if not freq:
        return [], None
    body_size, _ = freq.most_common(1)[0]
    heading_sizes = sorted([sz for sz in freq if sz > body_size], reverse=True)
    return heading_sizes[:3], body_size

# 3. Detect numbered headings
numbered_re = re.compile(r"^(\d+(?:\.\d+){0,2})\s+(.+)$")
def classify_numbered(text):
    match = numbered_re.match(text)
    if not match:
        return None, None
    depth = match.group(1).count('.') + 1
    return f"H{min(depth, 3)}", match.group(2).strip()

# 4. Detect language using langid
def detect_language(text):
    try:
        if len(text.strip()) < 5:
            return None
        return langid.classify(text)[0]
    except:
        return None

# 5. Build title and outline
def build_outline(spans, detect_languages=True):
    heading_sizes, _ = infer_heading_sizes(spans)
    title = None
    seen_title = set()
    outline = []

    for s in spans:
        lang = detect_language(s["text"]) if detect_languages else None

        # Title: first heading-level text on page 0
        if s["page"] == 0 and s["size"] in heading_sizes and not title:
            title = s["text"]
            seen_title.add(s["text"])
            continue

        # Numbered headings (1., 1.2., etc.)
        lvl, txt = classify_numbered(s["text"])
        if lvl:
            outline.append({
                "level": lvl,
                "text": txt,
                "page": s["page"],
                "lang": lang
            })
            continue

        # Font size–based headings
        if s["size"] in heading_sizes and s["text"] not in seen_title:
            idx = heading_sizes.index(s["size"])
            outline.append({
                "level": f"H{idx + 1}",
                "text": s["text"],
                "page": s["page"],
                "lang": lang
            })

    return title or "", outline

# 6. Process all PDFs in input/
if __name__ == "__main__":
    input_dir = os.path.join("app", "input")
    output_dir = os.path.join("app", "output")
    os.makedirs(output_dir, exist_ok=True)

    for pdf_path in glob.glob(os.path.join(input_dir, "*.pdf")):
        print(f"Processing: {pdf_path}")
        try:
            doc = fitz.open(pdf_path)
            spans = extract_spans(doc)
            title, outline = build_outline(spans, detect_languages=True)
            output = {"title": title, "outline": outline}

            out_file = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
            out_path = os.path.join(output_dir, out_file)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved to: {out_path}")
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
