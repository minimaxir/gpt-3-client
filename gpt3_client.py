import json
import os
import httpx
from imgmaker import imgmaker
import logging
from math import exp
from rich.console import Console
from rich.text import Text
import hashlib
import codecs
from bs4 import BeautifulSoup
import re
from datetime import datetime

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

    def close(self):
        if self.imgmaker:
            self.imgmaker.close()

    def generate(
        self,
        prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 32,
        stop: str = "",
        model: str = "davinci",
        bg: tuple = (31, 36, 40),
        accent: tuple = (0, 64, 0),
        pngquant: bool = False,
        output_txt: str = None,
        output_img: str = None,
        include_prompt: bool = True,
        include_coloring: bool = True,
    ):

        assert isinstance(stop, str), "stop is not a str."

        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": stop,
            "stream": True,
            "logprobs": 1,
        }

        console = Console(record=True)

        if include_prompt:
            console.clear()
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

                    if token == stop or token == "<|endoftext|>":
                        break

                    if token.startswith("bytes:") and not temp_token:
                        # We need to hold the 2-byte token to the next 1-byte token
                        # to get the full bytestring to decode
                        #
                        # The API-returned tokens are in the form:
                        # "bytes:\xe2\x80" and "bytes:\x9d"
                        temp_token = token[6:]
                        temp_prob = log_prob
                    else:
                        if temp_token:
                            bytestring = temp_token + token[6:]

                            # https://stackoverflow.com/a/37059682/9314418
                            token = codecs.escape_decode(bytestring, "utf-8")[0].decode(
                                "utf-8"
                            )
                            temp_token = None
                            log_prob = temp_prob  # the true prob is the first one
                        text = Text(
                            token,
                            style=f"on {self.derive_token_bg(log_prob, bg, accent, include_coloring,)}",
                            end="\n" if token == "\n" else "",
                        )
                        console.print(text, end="")

        # Export the generated text as HTML.
        raw_html = self.replace_hex_colors(
            console.export_html(inline_styles=True, code_format="{code}")
        )
        html = BeautifulSoup(raw_html, features="html.parser")

        plain_text = html.text.strip()

        # Render the HTML as an image
        prompt_hash = hashlib.sha256(bytes(prompt, "utf-8")).hexdigest()[0:8]
        temp_string = str(temperature).replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_img:
            img_file_name = output_img
        else:
            img_file_name = f"img_output/{timestamp}__{prompt_hash}__{temp_string}.png"

        if self.imgmaker:
            self.imgmaker.generate(
                "dark.html",
                {
                    "html": raw_html.replace("\n", "</br>"),
                    "accent": f"rgb({accent[0]},{accent[1]},{accent[2]})",
                    "watermark": "Curated by **Max Woolf (@minimaxir)** "
                    + "— Generated using GPT-3 via OpenAI's API",
                },
                width=450,
                height=600,
                downsample=False,
                output_file=img_file_name,
                use_pngquant=pngquant,
            )

        # Save the generated text to a plain-text file
        if output_txt:
            txt_file_name = output_txt
        else:
            txt_file_name = f"txt_output/{prompt_hash}__{temp_string}.txt"

        with open(txt_file_name, "a", encoding="utf-8") as f:
            f.write(plain_text + "\n" + "=" * 20 + "\n")

        console.line()

    def derive_token_bg(
        self, log_prob: float, bg: tuple, accent: tuple, include_coloring: bool
    ):
        prob = exp(log_prob)

        if include_coloring:
            color = (
                int(max(bg[0] + accent[0] * prob, bg[0])),
                int(max(bg[1] + accent[1] * prob, bg[1])),
                int(max(bg[2] + accent[2] * prob, bg[2])),
            )
        else:
            color = bg

        return f"rgb({min(color[0], 255)},{min(color[1], 255)},{min(color[2], 255)})"

    def replace_hex_colors(self, html: str):
        """
        Headless Chrome requires inline styles to be
        in rbg instead of hex format.
        """

        hex_colors = set(re.findall(r"(#.{6})\"", html))

        for hex_color in hex_colors:
            # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python/29643643

            h = hex_color.lstrip("#")
            rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

            rgb_str = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

            html = re.sub(hex_color, rgb_str, html)

        return html
