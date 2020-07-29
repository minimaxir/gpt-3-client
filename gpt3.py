from gpt3_client import GPT3Client
import fire
from rich.prompt import Prompt, Confirm
from rich import print
from rich.text import Text
from json import JSONDecodeError
import os


def gpt3_app(
    image=False,
    prompt="Once upon a time",
    temperature: float = 0.0,
    max_tokens=32,
    stop: str = "",
    bg: tuple = (31, 36, 40),
    accent: tuple = (0, 64, 0),
    interactive=False,
    pngquant=False,
    output_txt=None,
    output_img=None,
    include_prompt=True,
    include_coloring=True,
):

    divider_color_str = "white"
    divider = Text("-" * 10 + "\n", style=divider_color_str)
    gpt3 = GPT3Client(image=image)

    if interactive:
        prompt = Prompt.ask("[i]Enter a prompt for the GPT-3 API[/i]")

    if os.path.exists(prompt):
        with open(prompt, "r", encoding="utf-8") as f:
            prompt = f.read()

    try:
        gpt3.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            bg=bg,
            accent=accent,
            pngquant=pngquant,
            output_txt=output_txt,
            output_img=output_img,
            include_prompt=include_prompt,
            include_coloring=include_coloring,
        )

        print(divider)

        if interactive:
            continue_gen = True
            while continue_gen:
                continue_gen = Confirm.ask(
                    "[i]Do you wish to continue generating from the same prompt?[/i]"
                )

                if continue_gen:

                    gpt3.generate(
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stop=stop,
                        bg=bg,
                        accent=accent,
                        pngquant=pngquant,
                        output_txt=output_txt,
                        output_img=output_img,
                        include_prompt=include_prompt,
                        include_coloring=include_coloring,
                    )

                    print(divider)

    except KeyboardInterrupt:
        print("\n\n[red italic]Generation interrupted![/]")
    except JSONDecodeError:
        print("\n\n[red italic]The JSON from the API was misparsed![/]")

    try:
        gpt3.close()
    except Exception:
        pass


if __name__ == "__main__":
    fire.Fire(gpt3_app)
