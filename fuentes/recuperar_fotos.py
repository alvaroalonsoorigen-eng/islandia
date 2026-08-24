#!/usr/bin/env python3
"""Saca las fotos ya codificadas del index.html anterior para no volver a bajarlas.

Genera imgcache.json, que build.py usa en lugar de recortar y codificar otra vez
las fotos originales. Útil para cambiar diseño, mapas o textos sin tocar Commons.
"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, "..", "index.html")

s = open(HTML, encoding="utf-8").read()
m = re.search(r"window\.__IMG=(\{.*?\});window\.__GAL=", s, re.S)
if not m:
    raise SystemExit("no encuentro window.__IMG en el HTML")
cache = json.loads(m.group(1))
print("fotos de tarjeta recuperadas:", len(cache))

hero = re.search(r'<div class="hero-bg"><img alt="([^"]*)" src="(data:image/jpeg;base64,[^"]+)"', s)
if hero:
    cache["hero:" + hero.group(1)] = hero.group(2)
    print("foto de portada recuperada:", hero.group(1))

json.dump(cache, open(os.path.join(BASE, "imgcache.json"), "w"))
print("imgcache.json: %.1f MB" % (os.path.getsize(os.path.join(BASE, "imgcache.json")) / 1e6))
