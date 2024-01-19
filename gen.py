
from dotenv import load_dotenv
import random
import replicate
import re
import drawsvg as draw
import datetime

width = 30
height = 20

llm_model = "mistralai/mixtral-8x7b-instruct-v0.1"


def gen_prompt(task, examples, input):
    prompt = f"Task: {task}\n"
    prompt += "---\n"
    prompt += "Examples:\n"
    for example in examples:
        prompt += f"Input: {example['in']}\n"
        prompt += f"Output: {example['out']}\n\n"
    prompt += "---\n"
    prompt += f"Input: {input}\n"
    prompt += "Output: "
    return prompt


def prompt_llm(prompt, tokens=64):
    while True:
        out = "".join(replicate.run(llm_model, input={"prompt": prompt, "max_new_tokens": tokens}))
        if len(out) > 0:
            return out


def get_words():
    if not hasattr(get_words, "words"):
        with open("diceware.txt", "r") as f:
            get_words.words = f.readlines()
            
    out_words = []
    for _ in range(5):
        while True:
            w = random.choice(get_words.words).strip()
            if w not in out_words:
                out_words.append(w)
                break

    return out_words


def hex_to_rgb(hex):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def get_colors(words, num_colors=3):
    task = f"Generate {num_colors} interesting/specific colors, listing color name and then hex code, inspired by a list of words. Be creative, don't be afraid to use uncommon colors."
    examples = [
        {'in': "festivity oxymoron fancied playmate smith", 'out': "Merry Melange #B84A2C, Smith's Forge #956E37, Dreamy Paradox #3978C2"},
        {'in': "harmonica eardrum implant blissful arena", 'out': "Reed Amber #A98C6F, Shell Pink #E0D2CC, Nirvana Blue #5EA7D8"},
        {'in': "defender karaoke dispense dreamt habitant", 'out': "Defensive Tactics #495A62, Stage Light Spectrum #FA9230, Midnight Phantasm #0A043C"},
        {'in': "naturist fretted jitters poser crudely", 'out': "Whispering Fern #78B79F, Impulsive Ruby #BC2E4F, Shadowed Umber #423E36"},
        {'in': "path smooth monday paramedic germless", 'out': "Medicinal Green #8FB390, Soothing Mist #CEE3F8, Formula Teal #1F8A70"},
    ]

    prompt = gen_prompt(task, examples, ", ".join(words))
    while True:
        llm_gen = prompt_llm(prompt)
        matches = re.findall(r'#[0-9A-Fa-f]{6}', llm_gen)
        if len(matches) >= num_colors:
            return [hex_to_rgb(match) for match in matches][:num_colors]


def draw_something(colors):
    d = draw.Drawing(width, height)
    # Create gradient
    gradient = draw.LinearGradient(0, 0, width, height)
    gradient.add_stop(0, rgb_to_hex(colors[0]))
    gradient.add_stop(.5, rgb_to_hex(colors[1]))
    gradient.add_stop(1, rgb_to_hex(colors[2]))

    p = draw.Rectangle(0, 0, width, height, fill=gradient)
    d.append(p)

    d.set_render_size(600)
    d.save_svg(f'out/{datetime.datetime.now():%y-%m-%d_%H-%M-%S}.svg')


def generate():
    words = get_words()
    print(words)
    colors = get_colors(words)
    print(colors)
    draw_something(colors)


def main():
    load_dotenv()
    generate()


if __name__ == "__main__":
    main()