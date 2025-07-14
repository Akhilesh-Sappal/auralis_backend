import fitz  # PyMuPDF
from docx import Document
import os
from fastapi import UploadFile, HTTPException

class Extractor:
    async def read_file(self, file: UploadFile) -> str:
        file_bytes = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            return self._from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            return self._from_docx(file_bytes)
        elif filename.endswith(".txt"):
            return file_bytes.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    def _from_pdf(self, file_bytes):
        text = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _from_docx(self, file_bytes):
        with open("temp.docx", "wb") as f:
            f.write(file_bytes)
        doc = Document("temp.docx")
        text = "\n".join([para.text for para in doc.paragraphs])
        os.remove("temp.docx")
        return text






