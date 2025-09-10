# main.py
import os
from pdf_reader import extract_pages_text_and_images
from summarizer import summarize_pdf_pages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

def write_summary_pdf(summary_records, output_path="pdf_summary_report.pdf", source_filename="input.pdf"):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 20*mm
    y = height - margin

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, f"Auto PDF Summary — Source: {os.path.basename(source_filename)}")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, y, datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
    y -= 15

    # Table of contents (page short summaries)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Table of contents (page — short summary):")
    y -= 12
    c.setFont("Helvetica", 9)
    for rec in summary_records:
        line = f"Page {rec['page_no']}: {rec['combined_short'][:120]}"
        c.drawString(margin, y, line)
        y -= 10
        if y < 50:
            c.showPage()
            y = height - margin

    # Detailed per-page summaries
    for rec in summary_records:
        c.showPage()
        y = height - margin
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Page {rec['page_no']} Summary")
        y -= 14
        c.setFont("Helvetica", 10)
        # text summary
        if rec['text_summary']:
            lines = rec['text_summary'].split("\n")
            for ln in lines:
                for chunk in chunk_text_for_pdf(ln, 100):
                    c.drawString(margin, y, chunk)
                    y -= 10
                    if y < 50:
                        c.showPage()
                        y = height - margin
        else:
            c.drawString(margin, y, "(No extractable text on this page)")
            y -= 12

        # image summaries
        if rec['image_summaries']:
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(margin, y, "Image(s) analysis:")
            y -= 12
            c.setFont("Helvetica", 9)
            for imr in rec['image_summaries']:
                desc_lines = imr['desc'].split("\n")
                for dln in desc_lines:
                    for chunk in chunk_text_for_pdf(dln, 100):
                        c.drawString(margin+8, y, chunk)
                        y -= 9
                        if y < 50:
                            c.showPage()
                            y = height - margin
        else:
            c.drawString(margin, y, "No images on this page.")
            y -= 12

    c.save()

def chunk_text_for_pdf(text, max_len=100):
    """Small helper to break long lines for reportlab."""
    res = []
    while len(text) > max_len:
        res.append(text[:max_len])
        text = text[max_len:]
    if text:
        res.append(text)
    return res

def run(pdf_path: str, out_pdf: str = "pdf_summary_report.pdf"):
    pages = extract_pages_text_and_images(pdf_path, ocr_on_fail=True)
    summaries = summarize_pdf_pages(pages, model="gemini-1.5-flash")
    write_summary_pdf(summaries, output_path=out_pdf, source_filename=pdf_path)
    print("Summary written to:", out_pdf)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to input PDF")
    parser.add_argument("--out", default="pdf_summary_report.pdf", help="Output summary PDF")
    args = parser.parse_args()
    run(args.pdf, args.out)
