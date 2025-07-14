# services/parse.py

import requests
import os
import json
from groq import Groq
from pydantic import BaseModel, Field, ValidationError # pip install pydantic
from typing import List
import instructor # pip install instructor


from dotenv import load_dotenv
load_dotenv()


LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "llx-IVUUsEDR5yUY5cALwPWwYPsGHCbZ1ixNPRLvGapensKwxIWF")
LLAMA_API_URL = "https://api.llamaindex.ai/api/v1/parsing/markdown"
client = Groq()
instructor_client = instructor.patch(client)


# Define a schema with Pydantic (Python's equivalent to Zod)
class InvoiceInfo(BaseModel):
    invoice_number: str
    invoice_date: str
    address: str 
    email: str
    item_description: List[str] = Field(description="Names of items in the invoice")
    quantity: List[float] = Field(description="Quantities of each item")





def parse2(file_path,filename):
    from llama_cloud_services import LlamaParse

    parser = LlamaParse(
        api_key=LLAMA_API_KEY,  # can also be set in your env as LLAMA_CLOUD_API_KEY
        num_workers=4,       # if multiple files passed, split in `num_workers` API calls
        verbose=True,
        language="en",       # optionally define a language, default=en
    )
    result = parser.parse(file_path=file_path)
    final_result = result.dict()
    markdown_content = extract_markdown_only(final_result)
    extraction_result = extract(markdown_content)
    return extraction_result   

def extract_markdown_only(response):
    pages = response.get('pages', [])
    markdown_result = []

    for page in pages:
        md_content = page.get('md', '').strip()
        if md_content:
            markdown_result.append(md_content)

    return "\n\n--- PAGE BREAK ---\n\n".join(markdown_result)




def extract(markdown_content):




    # Prompt design is critical for structured outputs
    system_prompt = """
                You are professional Invoice extractor . Extract the required fields mentioned in pydantic class.

    """


    recipe = instructor_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=InvoiceInfo,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": markdown_content}
        ],
        max_retries=2  # Instructor will retry if validation fails
    )
    print(recipe)
    return recipe.dict()