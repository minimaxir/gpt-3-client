from gpt3_client import GPT3Client
import fire
from rich.prompt import Prompt, Confirm
from rich import print
from rich.text import Text


def gpt3_app(
    image=False,
    prompt="Once upon a time",
    temperature: float = 0.0,
    max_tokens=32,
    stop="",
    bg: tuple = (31, 36, 40),
    accent: tuple = (0, 64, 0),
    interactive=False,
):

    # divider_color_str = f"rgb({accent[0]},{accent[1]},{accent[2]})"
    divider_color_str = "white"
    divider = Text("\n" + "-" * 10 + "\n\n", style=divider_color_str)
    gpt3 = GPT3Client(image=image)

    if interactive:
        prompt = Prompt.ask("[i]Enter a prompt for the GPT-3 API[/i]")

    gpt3.generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
        bg=bg,
        accent=accent,
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
                )

                print(divider)


if __name__ == "__main__":
    fire.Fire(gpt3_app)
