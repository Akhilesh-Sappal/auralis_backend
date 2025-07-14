import requests
import os

DEEPGRAM_API_KEY = "f881d5dda60d8f6490784d7573f37fb44381af56"
TOGETHER_API_KEY = "a7dea59b9ea43fe753177742c313650031e6f4694a75dc1196575a2b41ee241f"

LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
DEFAULT_PROMPT = "Summarize this meeting transcript:\n\n"

class MeetingAnalysis:
    def __init__(self, audio_path: str):
        self.audio_path = audio_path

    def transcribe(self) -> str:
        try:
            with open(self.audio_path, "rb") as f:
                audio_data = f.read()

            url = "https://api.deepgram.com/v1/listen"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/mp3",  # Change based on your actual file type
            }

            params = {
                "model": "nova-3",
                "language": "en",
                "smart_format": "true"
            }

            response = requests.post(url, headers=headers, params=params, data=audio_data)

            if response.status_code == 200:
                return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
            else:
                raise Exception(f"Deepgram error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Transcription failed: {e}")

    def summarize(self, transcript: str, prompt: str = DEFAULT_PROMPT) -> str:
        try:
            full_prompt = f"{prompt.strip()}{transcript.strip()}"

            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "temperature": 0.3
            }

            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post("https://api.together.xyz/v1/chat/completions", json=payload, headers=headers)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"Summarization failed: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Summarization failed: {e}")
