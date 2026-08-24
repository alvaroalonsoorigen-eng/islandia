#!/usr/bin/env python3
"""Vuelve a descargar de Wikimedia Commons las fotos que usa el planificador.

photos.json guarda, por cada parada, el título del archivo en Commons y la ruta
local donde lo espera images.py. Este script recupera esas rutas para poder
regenerar el HTML desde cero.

    python3 descargar_fotos.py        # descarga lo que falte
"""
import json, os, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
API = "https://commons.wikimedia.org/w/api.php"
UA = "IcelandTripPlanner/1.0 (uso personal; contacto en el repositorio)"


def thumb_url(title, width=1280):
    q = {"action": "query", "format": "json", "formatversion": "2",
         "titles": "File:" + title, "prop": "imageinfo",
         "iiprop": "url", "iiurlwidth": str(width)}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        d = json.loads(r.read().decode())
    pages = d.get("query", {}).get("pages") or []
    if not pages or "imageinfo" not in pages[0]:
        return None
    return pages[0]["imageinfo"][0].get("thumburl")


def main():
    photos = json.load(open(os.path.join(BASE, "photos.json")))
    total = sum(len(v) for v in photos.values())
    hechas = fallos = 0
    for slug, items in photos.items():
        for p in items:
            dest = os.path.join(BASE, p["file"])
            if os.path.exists(dest) and os.path.getsize(dest) > 20000:
                hechas += 1
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                u = thumb_url(p["title"])
                if not u:
                    raise RuntimeError("sin thumbnail")
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = r.read()
                open(dest, "wb").write(data)
                hechas += 1
                print("%4d/%d  %s" % (hechas, total, p["file"]))
            except Exception as e:
                fallos += 1
                print("  fallo: %s (%s)" % (p["file"], e))
            time.sleep(1.2)          # Commons corta si se baja más rápido
    print("descargadas %d de %d, %d fallos" % (hechas, total, fallos))


main()
