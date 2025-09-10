# summarizer.py
import io
from gemini_client import GeminiClient
from image_ocr import extract_image_metadata
from tqdm import tqdm

# Initialize Gemini client once
client = GeminiClient()

def chunk_text(text: str, max_chars: int = 35000):
    """Naive chunker by chars; tune for model context size."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start+max_chars]
        # try to break at last newline or sentence end
        last_break = max(chunk.rfind("\n"), chunk.rfind("."))
        if last_break > int(0.5*max_chars):
            chunk = text[start:start+last_break+1]
            start = start + last_break + 1
        else:
            start += max_chars
        chunks.append(chunk)
    return chunks

def summarize_pdf_pages(page_records: list, model="gemini-1.5-flash"):
    """
    page_records: output of extract_pages_text_and_images()
    returns: list of per-page dicts:
      {'page_no', 'text_summary', 'image_summaries': [{'meta','desc'}], 'combined_short'}
    """
    outputs = []
    for rec in tqdm(page_records, desc="Summarizing pages"):
        page_no = rec["page_no"]
        text = rec["text"]

        # Summarize text — chunk if necessary
        text_summary = ""
        if text.strip():
            chunks = chunk_text(text)
            chunk_summaries = []
            for c in chunks:
                s = client.summarize_text(c)
                chunk_summaries.append(s.strip())
            text_summary = "\n".join(chunk_summaries)
        else:
            text_summary = ""  # no text available

        # Summarize images
        image_summaries = []
        for img in rec["images"]:
            meta = extract_image_metadata(img)
            # Convert PIL image → bytes for Gemini
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            desc = client.analyze_image(buf.getvalue())
            image_summaries.append({"meta": meta, "desc": desc.strip()})

        # Create a short combined page summary for quick table of contents
        combined_short = ""
        if text_summary:
            combined_short += text_summary.split("\n")[0]
        if image_summaries:
            combined_short += " | Image: " + (
                image_summaries[0]["desc"].split("\n")[0]
                if image_summaries[0]["desc"] else "image"
            )

        outputs.append({
            "page_no": page_no,
            "text_summary": text_summary,
            "image_summaries": image_summaries,
            "combined_short": combined_short
        })
    return outputs
