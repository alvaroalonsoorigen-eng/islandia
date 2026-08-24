#!/usr/bin/env python3
"""Descarga las librerías y tipografías que build.py incrusta en el HTML.

No se guardan en el repositorio: se bajan de sus fuentes oficiales.
    Swiper 11  (MIT)         carruseles de fotos
    GSAP 3.12  + ScrollTrigger   dibujado del trazado al hacer scroll
    Bricolage Grotesque, Instrument Sans, IBM Plex Mono (OFL, Google Fonts)
"""
import os, re, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"
LIBS = {
    "swiper.min.js": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js",
    "swiper.min.css": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css",
    "gsap.min.js": "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js",
    "scrolltrigger.min.js": "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js",
}
GF = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800"
      "&family=Instrument+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap")


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()


def main():
    os.makedirs(os.path.join(BASE, "lib"), exist_ok=True)
    for name, url in LIBS.items():
        open(os.path.join(BASE, "lib", name), "wb").write(get(url))
        print("lib/" + name)

    fdir = os.path.join(BASE, "fonts")
    os.makedirs(fdir, exist_ok=True)
    css = get(GF).decode()
    lineas = []
    for bloque in re.findall(r"@font-face\s*\{[^}]*\}", css):
        rango = re.search(r"unicode-range:([^;]+);", bloque)
        if not rango or "U+0000-00FF" not in rango.group(1):
            continue                       # solo el subconjunto latino
        fam = re.search(r"font-family:\s*'([^']+)'", bloque).group(1)
        peso = re.search(r"font-weight:\s*([^;]+);", bloque).group(1).strip()
        url = re.search(r"url\((https://[^)]+)\)", bloque).group(1)
        nombre = re.sub(r"\W+", "_", fam + "_" + peso) + ".woff2"
        open(os.path.join(fdir, nombre), "wb").write(get(url))
        lineas.append("%s|%s|%s" % (fam, peso, nombre))
        print("fonts/" + nombre)
    open(os.path.join(fdir, "latin.txt"), "w").write("\n".join(lineas))
    print("listo")


main()
