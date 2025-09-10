# fastapi_app.py
import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from main import run  # your pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # or ["http://localhost:3000"] for frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        input_path = tmp.name

    # Output file
    output_path = os.path.join(tempfile.gettempdir(), "summarized_report.pdf")

    # Run pipeline
    run(input_path, output_path)

    # Return summarized PDF
    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="summarized_report.pdf"
    )
