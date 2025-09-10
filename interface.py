# interface.py
import streamlit as st
import tempfile
import os

from main import run  # use the full pipeline

st.set_page_config(page_title="PDF Summarizer", layout="wide")

st.title("📄 Multi-Modal PDF Summarizer")
st.markdown("Upload a PDF (with text, diagrams, and graphs) and get a summarized report.")

# File uploader
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        input_path = tmp.name

    st.success("✅ PDF uploaded successfully!")

    # Run summarization
    if st.button("Summarize PDF"):
        with st.spinner("Summarizing with Gemini... this may take a minute ⏳"):
            output_path = os.path.join(tempfile.gettempdir(), "summarized_report.pdf")
            run(input_path, output_path)

        st.success("🎉 Summarization complete!")
        st.download_button(
            label="⬇️ Download Summarized Report",
            data=open(output_path, "rb").read(),
            file_name="summarized_report.pdf",
            mime="application/pdf"
        )
