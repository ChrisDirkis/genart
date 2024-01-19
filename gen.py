
from dotenv import load_dotenv
import random
import replicate
import re
import drawsvg as draw
import datetime
import itertools

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


def get_words(num=5):
    if not hasattr(get_words, "words"):
        with open("diceware.txt", "r") as f:
            get_words.words = f.readlines()
            
    out_words = []
    for _ in range(num):
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
    task = f"Generate {num_colors} interesting/specific colors, listing color name and then hex code, inspired by a list of words. Be creative, don't be afraid to use uncommon colors. Do not describe the colors, just name and hex."
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


def get_base_color(colors, offset=20):
    is_light = sum(sum(color) for color in colors) / (len(colors) * 3) > 120

    # sometimes, just pick one of the colours, the most contrasty one
    if random.random() < 0.2:
        return list(sorted(colors, key=lambda c: sum(c)))[0 if is_light else len(colors)-1] 

    # by default, pick a contrasting neutral
    base = (offset, offset, offset) if is_light else (255-offset, 255-offset, 255-offset)
    return tuple(c+random.randint(-offset, offset) for c in base)


def random_range(start, end):
    return start + random.random() * (end - start)


def clamp01(x):
    return max(0, min(1, x))

def draw_bg_gradient(d: draw.Drawing, colors):
    gradient = draw.LinearGradient(0, random_range(0, height), width, random_range(0, height))
    for i, color in enumerate(colors):
        stop_base = i / (len(colors) - 1)

        if i != 0 and i != len(colors) - 1:
            stop_jitter = 0.1
            stop = clamp01(random_range(stop_base - stop_jitter, stop_base + stop_jitter))
        else:
            stop = stop_base

        gradient.add_stop(stop, rgb_to_hex(color))

    bg = draw.Rectangle(0, 0, width, height, fill=gradient)
    d.append(bg)


def lerp(a, b, t):
    return a + (b - a) * t


def draw_line(d: draw.Drawing, base):
    path_points = int(2 ** random_range(2, 4)) + 1
    points = []
    for i in range(path_points):
        x_center = lerp(width * 0.1, width * 0.9, (i + 1)/(path_points + 1))
        x_jitter_range = (width/(path_points + 1)) * 0.5
        x = random_range(x_center - x_jitter_range, x_center + x_jitter_range)
        y = random_range(3, height-3)
        points.append((x, y))
    points.sort(key=lambda p: p[0])

    p = draw.Path(stroke_width=random_range(0.5, 4), stroke=rgb_to_hex(base), fill='none')
    p.M(points[0][0], points[0][1])
    for point in points[1:]:
        p.L(point[0], point[1])
    d.append(p)


def draw_something(colors, base):
    d = draw.Drawing(width, height)

    draw_bg_gradient(d, colors)
    draw_line(d, base)

    d.save_svg(f'out/{datetime.datetime.now():%y-%m-%d_%H-%M-%S}.svg')


def generate():
    words = get_words(5)
    print(words)
    colors = get_colors(words, random.randint(2, 5))
    base = get_base_color(colors)

    draw_something(colors, base)


def main():
    load_dotenv()
    generate()


if __name__ == "__main__":
    main()