import os
import openai
from fastapi import HTTPException

class DocumentClassifier:
    def __init__(self):
        os.environ["TOGETHER_API_KEY"] = "a7dea59b9ea43fe753177742c313650031e6f4694a75dc1196575a2b41ee241f"
        self.client = openai.OpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1"
        )

    async def classify(self, content: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
               messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a professional document classification assistant.\n\n"
                            "Your task is to accurately classify the provided document into one of the predefined categories.\n\n"
                            "Guidelines:\n"
                            "- Carefully analyze the content to determine the document's primary purpose and subject matter.\n"
                            "- Base your classification strictly on the content, without guessing or using prior assumptions.\n"
                            "- Return only the most appropriate category label from the list provided.\n"
                            "- If the document does not fit clearly into any category, respond with 'Unclear' or 'Other'.\n"
                            "- Do not provide explanations unless explicitly asked.\n"
                            "- Be concise, accurate, and neutral in your labeling.\n"

                            "Classify the following document into one of the following categories:\n"
                            "['Legal', 'Medical', 'Financial', 'Technical', 'Educational', 'Marketing', 'News', 'Personal', 'Other']\n\n"
                        )
                    },
                    {
                        "role": "user",
                        "content":content
                    }
                ]

            )
            return { "class": response.choices[0].message.content.strip() }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
