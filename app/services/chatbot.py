# chat.py

import openai

openai.api_key = "a7dea59b9ea43fe753177742c313650031e6f4694a75dc1196575a2b41ee241f"  # ✅ Set your key here
openai.api_base = "https://api.together.xyz/v1"

class ChatBot:
    def _init_(self, model="mistralai/Mixtral-8x7B-Instruct-v0.1"):
        self.model = model
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def send_message(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=0.7,
            max_tokens=200
        )

        reply = response['choices'][0]['message']['content']
        self.messages.append({"role": "assistant", "content": reply})
        return reply