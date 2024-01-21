
from dotenv import load_dotenv
import random
import re
import drawsvg as draw
import datetime
from utils import *
import ai

width = 30
height = 20

seed = random.randint(0, 2**32-1)
print(f"seed={seed}")
random.seed(seed)

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


def get_colors(words, num_colors=3):
    task = f"Generate {num_colors} interesting/specific colors, listing color name and then hex code, inspired by a list of words. Be creative, don't be afraid to use uncommon colors. Do not describe the colors, just name and hex."
    examples = [
        {'in': "festivity oxymoron fancied playmate smith", 'out': "Merry Melange #B84A2C, Smith's Forge #956E37, Dreamy Paradox #3978C2"},
        {'in': "harmonica eardrum implant blissful arena", 'out': "Reed Amber #A98C6F, Shell Pink #E0D2CC, Nirvana Blue #5EA7D8"},
        {'in': "defender karaoke dispense dreamt habitant", 'out': "Defensive Tactics #495A62, Stage Light Spectrum #FA9230, Midnight Phantasm #0A043C"},
        {'in': "naturist fretted jitters poser crudely", 'out': "Whispering Fern #78B79F, Impulsive Ruby #BC2E4F, Shadowed Umber #423E36"},
        {'in': "path smooth monday paramedic germless", 'out': "Medicinal Green #8FB390, Soothing Mist #CEE3F8, Formula Teal #1F8A70"},
    ]

    prompt = ai.gen_llm_prompt(task, examples, ", ".join(words))
    while True:
        llm_gen = ai.prompt_llm(prompt)
        matches = re.findall(r'#[0-9A-Fa-f]{6}', llm_gen)
        if len(matches) >= num_colors:
            return [hex_to_rgb(match) for match in matches][:num_colors]


def get_base_color(colors, offset=20):
    is_light = colors_are_light(colors)

    # sometimes, just pick one of the colours, the most contrasty one
    if random.random() < 0.2:
        return list(sorted(colors, key=lambda c: sum(c)))[0 if is_light else len(colors)-1] 

    # by default, pick a contrasting neutral
    base = (offset, offset, offset) if is_light else (255-offset, 255-offset, 255-offset)
    return tuple(c+random.randint(-offset, offset) for c in base)


def draw_bg(d: draw.Drawing, colors):
    is_light = colors_are_light(colors)

    filter = draw.Filter()

    freq = random_range(0.5, 0.7)
    octaves = random.randint(5, 7)
    filter.append(draw.FilterItem("feTurbulence", type="fractalNoise", baseFrequency=str(freq), numOctaves=str(octaves), result='noise'))
    
    scale = random_range(2, 10)
    diffuse_color = random.choice(colors) if random.random() < .5 else (220, 220, 220)
    diffuse = draw.FilterItem("feDiffuseLighting", in_='noise', lighting_color=rgb_to_hex(diffuse_color), surfaceScale=str(scale))
    diffuse.append(draw.FilterItem("feDistantLight", azimuth="45", elevation="60"))
    filter.append(diffuse)

    if not is_light:
        filter.append(draw.FilterItem("feColorMatrix", type="matrix", values="-1 0 0 0 1 0 -1 0 0 1 0 0 -1 0 1 0 0 0 1 0"))
    
    bgbg = draw.Rectangle(0, 0, "100%", "100%", fill="none", filter=filter)
    d.append(bgbg)

    gradient = draw.LinearGradient(0, random_range(0, height), width, random_range(0, height))
    for i, color in enumerate(colors):
        stop_base = i / (len(colors) - 1)

        if i != 0 and i != len(colors) - 1:
            stop_jitter = 0.1
            stop = clamp01(random_range(stop_base - stop_jitter, stop_base + stop_jitter))
        else:
            stop = stop_base
        alpha = random.randint(80, 200)
        gradient.add_stop(stop, rgb_to_hex(color) + "%02x" % alpha)

    bg = draw.Rectangle(0, 0, "100%", "100%", fill=gradient)
    d.append(bg)


def draw_line(d: draw.Drawing, base, blurred=False):
    path_points = int(2 ** random_range(2, 4)) + 1
    points = []
    for i in range(path_points):
        x_center = lerp(width * 0.1, width * 0.9, (i + 1)/(path_points + 1))
        x_jitter_range = (width/(path_points + 1)) * 0.5
        x = random_range(x_center - x_jitter_range, x_center + x_jitter_range)
        y = random_range(3, height-3)
        points.append((x, y))
    points.sort(key=lambda p: p[0])

    sw = random_range(2, 6) if blurred else random_range(.5, 2)
    alpha = random.randint(30, 90) if blurred else 255
    p = draw.Path(stroke_width=sw, 
                  stroke=rgb_to_hex(base) + "%02x" % alpha, 
                  backdrop_filter="blur(10px)" if blurred else "none",
                  fill='none'
    )
    p.M(points[0][0], points[0][1])
    for point in points[1:]:
        p.L(point[0], point[1])
    d.append(p)


def draw_something(colors, base):
    d = draw.Drawing(width, height)

    global seed
    d.append_title(str(seed))

    draw_bg(d, colors)
    draw_line(d, base)
    draw_line(d, base, True)

    d.width *= 20
    d.height *= 20

    d.save_svg(f'out/{datetime.datetime.now():%y-%m-%d_%H-%M-%S}.svg')
    d.save_svg(f'out/latest.svg')


def generate():

    words = get_words(5)
    print(words)

    colors = get_colors(words, random.randint(3, 5))
    print(colors)

    base = get_base_color(colors)

    draw_something(colors, base)


def main():
    load_dotenv()
    generate()


if __name__ == "__main__":
    main()