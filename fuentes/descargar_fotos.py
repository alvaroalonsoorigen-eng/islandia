#!/usr/bin/env python3
"""Vuelve a descargar de Wikimedia Commons las fotos que usa el planificador.

photos.json guarda, por cada parada, el título del archivo en Commons y la ruta
local donde lo espera images.py. Este script recupera esas rutas para poder
regenerar el HTML desde cero.

    python3 descargar_fotos.py        # descarga lo que falte
"""
import concurrent.futures, json, os, sys, time, urllib.parse, urllib.request

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


def una(p):
    """Descarga una foto. Commons devuelve 429 si se aprieta: se reintenta con espera."""
    dest = os.path.join(BASE, p["file"])
    if os.path.exists(dest) and os.path.getsize(dest) > 20000:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for intento in range(4):
        try:
            u = thumb_url(p["title"])
            if not u:
                raise RuntimeError("sin thumbnail en Commons")
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) < 20000:
                raise RuntimeError("archivo demasiado pequeño")
            open(dest, "wb").write(data)
            return True
        except Exception as e:
            if "429" in str(e):
                time.sleep(5 + 7 * intento)
            else:
                time.sleep(1.5)
            ultimo = e
    print("  fallo: %s (%s)" % (p["file"], ultimo), file=sys.stderr)
    return False


def main():
    photos = json.load(open(os.path.join(BASE, "photos.json")))
    tareas = [p for v in photos.values() for p in v]
    hechas = 0
    with concurrent.futures.ThreadPoolExecutor(4) as ex:   # más hilos y Commons corta
        for ok in ex.map(una, tareas):
            hechas += 1 if ok else 0
            if hechas % 25 == 0:
                print("%d/%d" % (hechas, len(tareas)), flush=True)
    print("descargadas %d de %d" % (hechas, len(tareas)))


main()
