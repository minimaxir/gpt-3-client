import json
import os
import httpx
import imgmaker
import logging

logger = logging.getLogger("GPT3Client")
logger.setLevel(logging.INFO)


class GPT3Client:
    def __init__(self, image: bool = True):

        assert os.getenv(
            "OPENAI_API_SECRET_KEY"
        ), "The OPENAI_API_SECRET_KEY Environment variable has not been set."

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_SECRET_KEY')}",
        }

        self.imgmaker = None
        if image:
            try:
                self.imgmaker = imgmaker()
            except ImportError:
                logging.warn(
                    "imgmaker failed to load Chrome: you will not be able to generate images."
                )

    def generate(
        self,
        prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 32,
        model: str = "davinci",
    ):

        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        with httpx.stream(
            "POST",
            f"https://api.openai.com/v1/engines/{model}/completions",
            headers=self.headers,
            data=json.dumps(data),
            timeout=None,
        ) as r:
            for chunk in r.iter_text():

                text = chunk[6:]  # JSON chunks are prepended with "data: "
                if "[DONE]" in text:
                    return
                print(json.loads(text)["choices"][0]["text"])
