import json
import os
import httpx
import imgmaker
import logging
from math import exp
from rich.console import Console
from rich.text import Text
import hashlib
import codecs

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

        console = Console(record=True)

        prompt_text = Text(prompt, style="bold", end="")
        console.print(prompt_text, end="")

        with httpx.stream(
            "POST",
            f"https://api.openai.com/v1/engines/{model}/completions",
            headers=self.headers,
            data=json.dumps(data),
            timeout=None,
        ) as r:
            for chunk in r.iter_text():
                # print(chunk)
                text = chunk[6:]  # JSON chunks are prepended with "data: "
                if len(text) < 10 and "[DONE]" in text:
                    break

                temp_token = None
                logprobs = json.loads(text)["choices"][0]["logprobs"]
                tokens = logprobs["tokens"]
                token_logprobs = logprobs["token_logprobs"]
                for i in range(len(tokens)):
                    token = tokens[i]
                    log_prob = token_logprobs[i]

                    if token.startswith("bytes:") and not temp_token:
                        # We need to hold the 2-byte token to the next 1-byte token
                        # to get the full bytestring to decode
                        #
                        # The API-returned tokens are in the form:
                        # "bytes:\xe2\x80" and "bytes:\x9d"
                        temp_token = token[6:]
                    else:
                        if temp_token:
                            bytestring = temp_token + token[6:]

                            # https://stackoverflow.com/a/37059682/9314418
                            token = codecs.escape_decode(bytestring, "utf-8")[0].decode(
                                "utf-8"
                            )
                            temp_token = None
                        text = Text(
                            token,
                            style=f"on {self.derive_token_bg(log_prob, bg, accent)}",
                            end="\n" if token == "\n" else "",
                        )
                        console.print(text, end="")

        # Save the generated text to a plain-text file
        # The file name will always be same for a given prompt and temperature
        file_name = hashlib.sha256(bytes(prompt, "utf-8")).hexdigest()[0:8]
        temp_string = str(temperature).replace(".", "_")

        export_text = console.export_text()

        with open(f"{file_name}__{temp_string}.txt", "a", encoding="utf-8") as f:
            f.write(export_text + "\n" + "=" * 20 + "\n")

        console.save_html("test.html", inline_styles=True)

        console.line()

    def derive_token_bg(self, log_prob: float, bg: tuple, accent: tuple):
        prob = exp(log_prob)

        color = (
            int(max(bg[0] + accent[0] * prob, bg[0])),
            int(max(bg[1] + accent[1] * prob, bg[1])),
            int(max(bg[2] + accent[2] * prob, bg[2])),
        )

        return f"rgb({min(color[0], 255)},{min(color[1], 255)},{min(color[2], 255)})"
