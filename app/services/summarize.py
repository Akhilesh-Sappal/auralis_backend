import os
import openai
from fastapi import HTTPException

class Summarizer:
    def __init__(self):
        os.environ["TOGETHER_API_KEY"] = "a7dea59b9ea43fe753177742c313650031e6f4694a75dc1196575a2b41ee241f"
        self.client = openai.OpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1"
        )

    async def summarize(self, content: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional summarization assistant.\n\n"
                            "Your task is to carefully read the provided content and generate a high-quality summary that is:\n"
                            "- Accurate and faithful to the original content\n"
                            "- Clear, concise, and logically structured\n"
                            "- Free from repetition or unnecessary detail\n"
                            "- Completely neutral, without inserting personal opinions\n"
                            "- Optimized for quick understanding by busy professionals\n\n"
                            "Rules:\n"
                            "- Do not add any new information or interpretation.\n"
                            "- Focus on capturing the main ideas and key details.\n"
                            "- Maintain the original tone and purpose of the content.\n"
                            "- If the text is long, condense it into 4–6 sentences.\n"
                            "- If appropriate, you may use bullet points for clarity."
                        )
                    },
                    {
                        "role": "user",
                        "content": f'Summarize the following content:\n\n"""\n{content}\n"""'
                    }
                ]
            )
            return { "summary": response.choices[0].message.content.strip() }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
