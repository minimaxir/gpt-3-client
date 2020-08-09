# gpt-3-client

A client for OpenAI's GPT-3 API, intended to be used for more _ad hoc_ testing of prompt without using the web interface. This approach allows more customization of th

In addition to generating text via the API, the client:

- Prints the generated text to console, with a **bolded** prompt.
  - Allows for coloring the text by prediction quality
- Automatically saves each generated text to a file
- Automatically creates a sharable, social-media-optimized image using imgmaker.

NB: This project is intended more for personal use, and as a result may not be as actively supported as my other projects intended for productionization.

## Install

First, install the Python requirements:

```sh
pip3 install httpx rich imgmaker
```

Then download this repostory and `cd` into the downloaded folder.

Optionally, if you want to generate images of the generated text, you'll also need to have the latest version of Chrome install and download the corresponding chromedriver:

```sh
imgmaker chromedriver
```

You will also need to export your OpenAI API key to the `OPENAI_API_SECRET_KEY` environment variable (this is more secure than putting it in a plaintext file). In bash/zsh, you can do this by:

```sh
export OPENAI_API_SECRET_KEY=<key>
```

## Usage

This GPT-3 client is intended to be interacted with _entirely_ via the command line . (due to how rich works, it will not work well in a Notebook)

You can invoke the client via:

```sh
python3 gpt3.py
```

The generation output will be stored in a text file in the `txt_output` folder, corresponding to a hash of the prompt and the temperature (e.g. `e286222c__0_7.txt`)

By default, it will generate from the prompt "Once upon a time". To specify a custom prompt, you can do:

```sh
python3 gpt3.py --prompt "I am a pony"
```

For longer prompts, you can put the prompt in a `prompt.txt` file instead:

```sh
python3 gpt3.py --prompt "prompt.txt" --max_tokens 256
```

## CLI Arguments

- `image`: Whether to render an image of the generated text (requires imgmaker) _[Default: False]_
- `prompt`: Prompt for GPT-3; either text or a path to a file. _[Default: "Once upon a time"]_
- `temperature`: Generation creativity; the higher, the crazier. _[Default: 0.7]_
- `max_tokens`: Number of tokens generated _[Default: 0.7]_
- `stop`: Token to use to stop generation. _[Default: ""]_
- `bg`: RGB tuple representing the base for coloration: you should set to the background of the terminal. _[Default: (31, 36, 40)]_
- `accent`: Accent color to blend with the `bg` to indicate prediction strength. _[Default: (0, 64, 0)]_
- `interactive`: Enters an "interactive" mode where you can provide prompts repeatedly. _[Default: False]_
- `pngquant`: If using `image`, uses pngquant to massively compress it. Requires pngquant installed on your system. _[Default: False]_
- `output_txt`: Specify output text file, overriding default behavior if not None. _[Default: None]_
- `output_img`: Specify output image file, overriding default behavior if not None. _[Default: None]_
- `include_prompt`: Include prompt in the generation output. _[Default: False]_
- `include_coloring`: Use probability coloring _[Default: True]_
- `watermark`: Specify watermark text on the generated image. Supports Markdown formatting. _[Default: "Generated using GPT-3 via OpenAI's API"]_

## Maintainer/Creator

Max Woolf ([@minimaxir](https://minimaxir.com))

_Max's open-source projects are supported by his [Patreon](https://www.patreon.com/minimaxir) and [GitHub Sponsors](https://github.com/sponsors/minimaxir). If you found this project helpful, any monetary contributions to the Patreon are appreciated and will be put to good creative use._

## License

MIT

## Disclaimer

This repo has no affiliation with OpenAI.
