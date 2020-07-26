from gpt3_client import GPT3Client
import fire


def gpt3_app(
    image=False,
    prompt="Once upon a time",
    temperature=0,
    max_tokens=32,
    stop="",
    bg: tuple = (31, 36, 40),
    accent: tuple = (0, 64, 0),
):

    gpt3 = GPT3Client(image=image)
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
