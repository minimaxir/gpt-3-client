from gpt3_client import GPT3Client
import fire
from rich.prompt import Prompt, Confirm


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

    gpt3 = GPT3Client(image=image)

    if interactive:
        prompt = Prompt.ask("Enter a prompt for the GPT-3 API")

    gpt3.generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
        bg=bg,
        accent=accent,
    )

    if interactive:
        continue_gen = True
        while continue_gen:
            continue_gen = Confirm.ask(
                "Do you wish to continue generating from the same prompt?"
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


if __name__ == "__main__":
    fire.Fire(gpt3_app)
