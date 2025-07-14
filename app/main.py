# app/main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.services.extract import Extractor
from app.services.summarize import Summarizer
from app.services.document_classifier import DocumentClassifier
from app.services.transcribe import MeetingAnalysis
import tempfile
from starlette.concurrency import run_in_threadpool
import httpx
import os
import shutil

app = FastAPI()

extractor = Extractor()
summarizer = Summarizer()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create the folder if it doesn't exist

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "your-together-api-key")
MODEL_NAME = "meta-llama/Llama-3-8b-chat-hf"

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat_endpoint(chat_req: ChatRequest):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": chat_req.prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )

    if response.status_code != 200:
        data = response.json()
        return {"error": data.get("error", "Something went wrong")}

    reply = response.json()["choices"][0]["message"]["content"]
    return {"response": reply}


@app.post("/summarize")
async def summarize_post(text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    if text and text.strip():
        content = text
    elif file:
        content = await extractor.read_file(file)
    else:
        return {"error": "Please provide either text or file."}
    return await summarizer.summarize(content)


@app.post("/classify")
async def classify_post(files: List[UploadFile] = File(...)):
    results = []
    classifier = DocumentClassifier()
    for file in files:
        content = await extractor.read_file(file)
        if not content.strip():
            results.append({"filename": file.filename, "error": "Could not extract text."})
            continue
        result = await classifier.classify(content)
        results.append({"filename": file.filename, "classification": result})
    return results


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        suffix = file.filename.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        analyzer = MeetingAnalysis(tmp_path)
        transcript = await run_in_threadpool(analyzer.transcribe)
        summary = await run_in_threadpool(analyzer.summarize, transcript)

        return {"transcript": transcript, "summary": summary}

    except Exception as e:
        return {"error": str(e)}


@app.post("/parse-pdf-markdown")
async def parse_pdf_markdown(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)

        # Save the file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        from app.services.parse import parse2
        m = parse2(file_location, file.filename)
        return m

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
