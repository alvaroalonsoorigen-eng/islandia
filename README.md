# Islandia 2027, seis rutas salvajes

Planificador de un viaje en pareja a Islandia con camper, en un único archivo HTML que
funciona sin conexión: **[index.html](index.html)** (14 MB, fotos incrustadas en base64).

Publicado con GitHub Pages: `https://alvaroalonsoorigen-eng.github.io/islandia/`

## Qué contiene

- **Comparación de fechas**: segunda quincena de junio de 2027 frente a los días
  posteriores a Semana Santa (que en 2027 cae del 21 al 28 de marzo), con lo que está
  abierto y cerrado en cada ventana.
- **Escala de duración**: qué cabe en 7-8, 9, 11 y 13-14 días.
- **Seis rutas** comparables entre sí, cuatro propias y dos clásicas, con mapa
  esquemático por días, kilómetros, exigencia, vehículo necesario y qué se sacrifica:
  1. Fuego interior (interior: Kerlingarfjöll, Landmannalaugar, Eldgjá, Laki), 10 días
  2. La vuelta salvaje (anillo antihorario con fiordos del este), 11 días
  3. Los fiordos del oeste (Látrabjarg, Dynjandi, Hornstrandir, Strandir), 11 días
  4. Cuatro días sin coche (Laugavegur de refugio en refugio), 11 días
  5. Clásica: sur, Círculo Dorado y Snæfellsnes, 9 días
  6. Clásica: la carretera 1 en nueve días
- **102 paradas** con carrusel de fotos reales de cada sitio, presupuesto orientativo,
  calendario de reservas y avisos prácticos (vados, viento, seguros, campings).

El mapa de cada ruta es interactivo: los círculos son los días, se encienden al leer y
al pulsarlos salta al día correspondiente.

## Fotografías

Las 301 fotos vienen de **Wikimedia Commons** y se muestran con autoría y licencia en el
pie de cada tarjeta y en el listado completo del final del documento. Reparto de
licencias: CC BY-SA 4.0 (139), CC BY-SA 2.0 (40), CC BY 2.0 (31), CC BY-SA 3.0 (28),
CC BY 4.0 (20), CC BY 3.0 (16), CC0 (16), dominio público (9), CC BY-SA 2.0 de (8),
GFDL 1.2 (4), CC BY 2.5 dk (1). Ninguna tiene cláusula NC o ND.

Cada imagen conserva la licencia de su autor. Si reutilizas este documento, mantén la
atribución y respeta el share-alike de las CC BY-SA y la GFDL.

## Regenerar el HTML

Los originales de las fotos y las librerías no están en el repositorio; se recuperan de
sus fuentes con dos scripts. Requiere Python 3 y Pillow.

```bash
cd fuentes
python3 descargar_librerias.py     # Swiper, GSAP y las tipografías
python3 descargar_fotos.py         # las 301 fotos desde Commons (tarda ~10 min)
python3 build.py                   # genera fuentes/islandia-2027.html
```

`content.py` guarda todo el texto: rutas, días, presupuesto y pies de foto. `build.py`
monta el HTML, `geo.py` proyecta la costa de Islandia y los trazados, `images.py` recorta
y codifica las fotos, y `photos.json` es la selección revisada a mano con su autoría.

## Aviso

Es un documento de planificación, no una guía publicada. Los precios son medias de
mercado de 2026 y las fechas de apertura de las pistas F son promedios históricos: el
dato real de cada día está en [road.is](https://www.road.is) y el viento en
[vedur.is](https://www.vedur.is).
