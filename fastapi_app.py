# fastapi_app.py

import os
import tempfile
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# import your pipeline runner
from main import run  

app = FastAPI(
    title="PDF Summarizer API",
    description="Upload a PDF and get a summarized version.",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "✅ FastAPI PDF Summarizer is running!"}

@app.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and receive a summarized PDF in return.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_input_path = None
    tmp_output_path = None

    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
            tmp_input.write(await file.read())
            tmp_input_path = tmp_input.name

        # Define output file path
        tmp_output_path = tmp_input_path.replace(".pdf", "_summary.pdf")

        # Run your summarization pipeline
        run(tmp_input_path, tmp_output_path)

        if not os.path.exists(tmp_output_path):
            raise HTTPException(status_code=500, detail="Summarization failed: output file not created.")

        # Return summarized file
        return FileResponse(
            path=tmp_output_path,
            filename="summary.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        # Log the full traceback to console / Render logs
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary files
        if tmp_input_path and os.path.exists(tmp_input_path):
            os.remove(tmp_input_path)
        if tmp_output_path and os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)
