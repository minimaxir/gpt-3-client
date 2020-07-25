import yaml
import json
import os
import httpx
import time
import imgmaker
import logging

logger = logging.getLogger("GPT3Client")
logger.setLevel(logging.INFO)


class GPT3Client:
    def __init__(self):

        assert os.getenv(
            "OPENAI_API_SECRET_KEY"
        ), "The OPENAI_API_SECRET_KEY Environment variable has not been set."

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_SECRET_KEY')}",
        }

        try:
            self.imgmaker = imgmaker()
        except ImportError:
            logging.warn(
                "imgmaker failed to load Chrome: you will not be able to generate images."
            )
            self.imgmaker = None

    def generate(
        self,
        prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 128,
        model: str = "davinci",
    ):

        data = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://api.openai.com/v1/engines/{model}/completions",
                headers=self.headers,
                data=data,
                timeout=None,
            )
        r_json = r.json()
        if "choices" not in r_json:
            return ""
        return r_json["choices"][0]["text"]
