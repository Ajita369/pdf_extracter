# 📘 PDF Outline Extractor – Adobe “Connecting the Dots” Challenge (Round 1A)

This tool extracts a structured outline from PDFs, including:
- **Title**
- **Headings** (`H1`, `H2`, `H3`)
- **Page number**
- **Language tag**

It is designed to be:
- 🔌 **Fully offline**
- 🐳 **Docker-compatible**
- ⚡️ **<10s runtime** for 50-page PDFs on CPU
- 💻 **Cross-platform (Windows/Linux, AMD64)**

---

## 🧠 Approach

### 1. Text Extraction
- Uses `PyMuPDF` to extract all text spans (with font size & page index).

### 2. Heading Detection
- **Font Size Clustering** to infer heading tiers (H1–H3).
- **Numbered Headings** override font logic via regex (e.g., `1.`, `1.2.3`).

### 3. Title Inference
- First span on page 0 with largest heading-size is selected as title.
- Fallback to largest font on page 0 if not found.

### 4. Language Tagging
- Uses `langid` to detect and tag language for each heading.

```text
PDF_EXTRACTER/
│
├── app/
│   ├── input/     # Place input PDFs here
│   ├── output/    # Extracted JSON files will appear here
│   └── schema/    # Reserved for optional future schema
│
├── extract_outline.py  # Main extraction script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Build environment
└── README.md           # You are here
```

## 📥 Requirements

### If running locally without Docker

```bash
pip install -r requirements.txt
```

<details>
<summary>requirements.txt</summary>

```text
pymupdf>=1.22.5  
langid>=1.1.6
```
</details>

## 🐳 Docker Instructions


1. Build Image

```bash
docker build --platform=linux/amd64 -t pdf-extracter .
```

2. Run (Linux / Mac / WSL):

```bash
docker run --rm \
  -v "$(pwd)/app/input:/app/input" \
  -v "$(pwd)/app/output:/app/output" \
  --platform=linux/amd64 \
  pdf-extracter
```
## 🧪 Output Format


1. Build Image

```bash
docker build --platform=linux/amd64 -t pdf-extracter .
```

2. Run (Linux / Mac / WSL):

```bash
docker run --rm \
  -v "$(pwd)/app/input:/app/input" \
  -v "$(pwd)/app/output:/app/output" \
  --platform=linux/amd64 \
  pdf-extracter
```
## 🧪 Output Format

Each `filename.pdf` inside `app/input/` generates a corresponding `filename.json` inside `app/output/`.

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1, "lang": "en" },
    { "level": "H2", "text": "What is AI?", "page": 2, "lang": "en" },
    { "level": "H3", "text": "History of AI", "page": 3, "lang": "en" }
  ]
}
```
## ✅ Adobe Round Constraints Met

| Constraint                          | Status                        |
|------------------------------------|-------------------------------|
| ⏱ ≤ 10s runtime (50 pages)         | ✅ (with tuned input size)    |
| 📦 ≤ 200MB model size              | ✅ (uses langid + rules)      |
| 🌐 Fully offline                   | ✅                            |
| 💻 CPU-only, AMD64                | ✅                            |
| 📁 Works on multiple PDFs          | ✅                            |
| 🧠 Multilingual Headings           | ✅                            |

---

## 👩‍💻 Author

Made with ❤️ by **Chitra Singh** and **Ajita Gupta**

For **Adobe GenAI Challenge 2025 – Round 1A (PDF Outline Extraction)**  
Built using `PyMuPDF`, `langid`, and `Docker`

