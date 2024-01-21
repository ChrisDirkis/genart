import random
import replicate
import requests 
from PIL import Image

llm_model = "mistralai/mixtral-8x7b-instruct-v0.1"
anime_model = "cjwbw/anything-v3-better-vae:09a5805203f4c12da649ec1923bb7729517ca25fcac790e640eaa9ed66573b65"


def gen_llm_prompt(task, examples, input):
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
        out = "".join(replicate.run(llm_model, input={"prompt": prompt, "max_new_tokens": tokens, "seed": random.randint(0, 2**32-1)}))
        if len(out) > 0:
            return out


default_negative_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name"

def prompt_anime(prompt, width=512, height=512, negative_prompt=None): 
    negative_prompt = negative_prompt if negative_prompt else default_negative_prompt
    input = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "negative_prompt": negative_prompt,
        "scheduler": "K_EULER_ANCESTRAL",
        "num_inference_steps": 20,
        "seed": random.randint(0, 2**32-1),
    }
    out_url = replicate.run(anime_model, input=input)[0]
    return Image.open(requests.get(out_url, stream=True).raw)