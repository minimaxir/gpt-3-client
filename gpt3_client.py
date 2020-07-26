import json
import os
import httpx
import imgmaker
import logging
from math import exp
from rich.console import Console
from rich.text import Text

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
        stop: str = "",
        model: str = "davinci",
        bg: tuple = (31, 36, 40),
        accent: tuple = (0, 64, 0),
    ):

        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": stop,
            "stream": True,
            "logprobs": 1,
        }

        console = Console()
        console.clear()
        gen_text = Text()

        gen_text.append(prompt, style="bold")
        console.print(gen_text)

        with httpx.stream(
            "POST",
            f"https://api.openai.com/v1/engines/{model}/completions",
            headers=self.headers,
            data=json.dumps(data),
            timeout=None,
        ) as r:
            for chunk in r.iter_text():
                text = chunk[6:]  # JSON chunks are prepended with "data: "
                if len(text) < 10 and "[DONE]" in text:
                    break

                # tokens is a list of 1-element dicts
                tokens = json.loads(text)["choices"][0]["logprobs"]["top_logprobs"]
                for token_dict in tokens:
                    token, log_prob = list(token_dict.items())[0]

                    console.clear()
                    gen_text.append(
                        token, style=f"on {self.derive_token_bg(log_prob, bg, accent)}"
                    )
                    console.print(gen_text)

        console.clear()

        # Create a new console to print and save the final generation.
        console_final = Console(record=True)
        console_final.print(gen_text)
        console_final.save_html("test.html", inline_styles=True)

    def derive_token_bg(self, log_prob: float, bg: tuple, accent: tuple):
        prob = exp(log_prob)

        color = (
            int(max(bg[0] + accent[0] * prob, bg[0])),
            int(max(bg[1] + accent[1] * prob, bg[1])),
            int(max(bg[2] + accent[2] * prob, bg[2])),
        )

        return f"rgb({min(color[0], 255)},{min(color[1], 255)},{min(color[2], 255)})"
