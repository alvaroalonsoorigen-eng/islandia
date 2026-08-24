# -*- coding: utf-8 -*-
"""Recorte y codificación base64 de las fotos seleccionadas."""
import base64, io, json, os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
CARD = (640, 427)
HERO = (1680, 945)


def encode(path, size, quality):
    im = Image.open(path).convert("RGB")
    r = size[0] / size[1]
    if im.width / im.height > r:
        w = int(im.height * r)
        im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
    else:
        h = int(im.width / r)
        top = int((im.height - h) * 0.38)
        im = im.crop((0, top, im.width, top + h))
    if im.width > size[0]:
        im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def build(used, hero_slugs=(), card_q=44, hero_q=52):
    photos = json.load(open(os.path.join(BASE, "photos.json")))
    IMG, GAL, credits = {}, {}, []
    for slug in sorted(used):
        items = photos.get(slug, [])
        out = []
        for i, p in enumerate(items):
            key = "%s%d" % (slug, i)
            IMG[key] = encode(os.path.join(BASE, p["file"]), CARD, card_q)
            out.append({"k": key, "a": p["author"][:80], "l": p["license"]})
            credits.append((p["title"], p["author"][:90], p["license"], p["page"]))
        GAL[slug] = out
    HEROIMG = {s: encode(os.path.join(BASE, photos[s][0]["file"]), HERO, hero_q) for s in hero_slugs}
    return IMG, GAL, HEROIMG, credits
