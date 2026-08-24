# -*- coding: utf-8 -*-
"""Proyección de Islandia y trazado de rutas a paths SVG."""
import json, math

W, H = 1000.0, 660.0
LAT0 = 64.9
COS = math.cos(math.radians(LAT0))
BOUNDS = (-24.65, 62.95, -13.35, 66.62)  # lon_min, lat_min, lon_max, lat_max


def _scale():
    lo0, la0, lo1, la1 = BOUNDS
    sx = W / ((lo1 - lo0) * COS)
    sy = H / (la1 - la0)
    s = min(sx, sy)
    dx = (W - (lo1 - lo0) * COS * s) / 2
    dy = (H - (la1 - la0) * s) / 2
    return s, dx, dy


S, DX, DY = _scale()


def proj(lon, lat):
    lo0, la0, lo1, la1 = BOUNDS
    x = (lon - lo0) * COS * S + DX
    y = (la1 - lat) * S + DY
    return round(x, 1), round(y, 1)


def coastline(path="iceland-natural-earth.geojson", min_pts=12, eps=0.9):
    gj = json.load(open(path))
    geom = gj["geometry"] if gj["type"] == "Feature" else gj["features"][0]["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        ring = poly[0]
        pts = [proj(lon, lat) for lon, lat in ring]
        keep = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - keep[-1][0]) + abs(p[1] - keep[-1][1]) > eps:
                keep.append(p)
        if len(keep) < min_pts:
            continue
        out.append("M" + "L".join("%g %g" % p for p in keep) + "Z")
    return " ".join(out)


def bezier_cmds(points, tension=0.5):
    """Catmull-Rom a bezier, devolviendo un comando por tramo entre puntos."""
    if len(points) < 2:
        return []
    if len(points) == 2:
        return ["L%g %g" % points[1]]
    cmds = []
    ext = [points[0]] + list(points) + [points[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension * 2, p1[1] + (p2[1] - p0[1]) / 6.0 * tension * 2)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension * 2, p2[1] - (p3[1] - p1[1]) / 6.0 * tension * 2)
        cmds.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return cmds


def smooth(points, tension=0.5):
    """Catmull-Rom -> cubic bezier, para un trazo de expedición sin picos."""
    if len(points) < 2:
        return ""
    p = points
    if len(p) == 2:
        return "M%g %g L%g %g" % (p[0][0], p[0][1], p[1][0], p[1][1])
    d = ["M%g %g" % p[0]]
    ext = [p[0]] + p + [p[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension * 2, p1[1] + (p2[1] - p0[1]) / 6.0 * tension * 2)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension * 2, p2[1] - (p3[1] - p1[1]) / 6.0 * tension * 2)
        d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return " ".join(d)


def route_paths(route, coords):
    """Trazado esquemático de una ruta, partido en un tramo por día.

    Devuelve (camino_completo, tramos, nodos). Cada tramo lleva el número de día
    al que pertenece, para poder encenderlo cuando se está leyendo ese día.
    """
    kef = proj(-22.6056, 63.9850)
    pts, owner, nodes = [kef], [0], []
    for day in route["dias_detalle"]:
        dpts = []
        for s in day["stops"]:
            c = coords.get(s)
            if c:
                dpts.append(proj(c[1], c[0]))
        if dpts:
            mx = sum(q[0] for q in dpts) / len(dpts)
            my = sum(q[1] for q in dpts) / len(dpts)
            anchor = min(dpts, key=lambda q: (q[0] - mx) ** 2 + (q[1] - my) ** 2)
        else:
            anchor = pts[-1]
        nodes.append({"d": day["d"], "x": anchor[0], "y": anchor[1]})
        if abs(anchor[0] - pts[-1][0]) + abs(anchor[1] - pts[-1][1]) > 2:
            pts.append(anchor)
            owner.append(day["d"])
    if abs(pts[-1][0] - kef[0]) + abs(pts[-1][1] - kef[1]) > 2:
        pts.append(kef)
        owner.append(owner[-1])                 # la vuelta al aeropuerto es del último día
    cmds = bezier_cmds(pts, 0.4)
    full = "M%g %g " % pts[0] + " ".join(cmds)
    segs, i = [], 0
    while i < len(cmds):
        d = owner[i + 1]
        j = i
        while j < len(cmds) and owner[j + 1] == d:
            j += 1
        segs.append({"d": d, "path": "M%g %g " % pts[i] + " ".join(cmds[i:j])})
        i = j
    return full, segs, nodes


def route_geometry(route, coords):
    """Compatibilidad: solo el trazado completo y los nodos."""
    full, _segs, nodes = route_paths(route, coords)
    return full, nodes
