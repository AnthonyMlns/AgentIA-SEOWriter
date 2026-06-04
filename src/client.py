import time
import json
from openai import OpenAI


class DeepSeekClient:
    def __init__(self, config: dict):
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
        )
        self.model = config["model"]
        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]
        self.timeout = config["timeout"]
        self.retry_attempts = config["retry_attempts"]

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None
        for attempt in range(self.retry_attempts + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                )
                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                if attempt < self.retry_attempts:
                    time.sleep(2 ** attempt)
                continue

        raise RuntimeError(f"API call failed after {self.retry_attempts + 1} attempts: {last_error}")

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict:
        text = self.chat(system_prompt, user_prompt)
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
