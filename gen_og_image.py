# -*- coding: utf-8 -*-
"""Vygeneruje og-image.png (statický náhled pro sdílení).
Spustí se jednou ručně — obrázek se s obsahem webu nemění."""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))

d = json.load(open(os.path.join(BASE, "content", "data.json"), encoding="utf-8"))
site = d["site"]
name = site["name"]
tagline = site["tagline"]

W, H = 1200, 630
top = np.array([24, 20, 14], dtype=float)   # teplá černá
bot = np.array([6, 6, 7], dtype=float)
y = np.linspace(0, 1, H)[:, None, None]
base = top[None, None, :] * (1 - y) + bot[None, None, :] * y
arr = np.broadcast_to(base, (H, W, 3)).copy()
xx, yy = np.meshgrid(np.arange(W), np.arange(H))
d = np.sqrt((xx - W * 0.5) ** 2 + (yy - H * 0.42) ** 2)
glow = np.clip(1 - d / 900, 0, 1)
# šampaňské zlato (R 201, G 162, B 103)
arr[:, :, 0] = np.clip(arr[:, :, 0] + glow * 70, 0, 255)
arr[:, :, 1] = np.clip(arr[:, :, 1] + glow * 45, 0, 255)
arr[:, :, 2] = np.clip(arr[:, :, 2] + glow * 22, 0, 255)

img = Image.fromarray(arr.astype(np.uint8))
draw = ImageDraw.Draw(img)


def load_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


f_title = load_font(["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], 96)
f_sub = load_font(["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"], 30)
draw.text((80, 224), name, font=f_title, fill=(242, 239, 231))
draw.text((82, 362), tagline.upper(), font=f_sub, fill=(201, 162, 103))
img.save(os.path.join(BASE, "og-image.png"))
print("og-image.png OK")
