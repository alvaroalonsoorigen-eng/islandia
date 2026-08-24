# -*- coding: utf-8 -*-
"""Genera el HTML autocontenido del planificador de Islandia."""
import base64, html, json, os, sys, urllib.parse
import content as C
import geo, images

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, os.environ.get("OUTNAME", "islandia-2027.html"))
ONLY = [x for x in os.environ.get("ONLY_ROUTES", "").split(",") if x]
MAXPH = int(os.environ.get("MAX_PHOTOS", "0"))
HEROES = ["landmannalaugar", "midnightsun", "hornstrandir"]

def e(s):
    return html.escape(str(s), quote=False)

def font_css():
    css, seen = [], {}
    for line in open(os.path.join(BASE, "fonts", "latin.txt")).read().splitlines():
        fam, wght, name = line.split("|")
        p = os.path.join(BASE, "fonts", name)
        h = os.path.getsize(p)
        if (fam, h) in seen:
            continue
        seen[(fam, h)] = 1
        b64 = base64.b64encode(open(p, "rb").read()).decode()
        rng = wght if " " in wght else wght
        css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;"
                   "src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam, rng, b64))
    return "\n".join(css)

def lib(name):
    return open(os.path.join(BASE, "lib", name), encoding="utf-8").read()

# --------------------------------------------------------------------- mapas
COAST = geo.coastline(eps=0.45)
COORDS = json.load(open(os.path.join(BASE, "coords.json")))

def map_svg(route=None, cls="rmap"):
    if route is None:
        used = set()
        for r in C.ROUTES:
            for day in r["dias_detalle"]:
                used.update(day["stops"])
        pts = []
        for s in sorted(used):
            c = COORDS.get(s)
            if not c:
                continue
            x, y = geo.proj(c[1], c[0])
            pts.append('<circle class="spot" cx="%g" cy="%g" r="3.4"/>' % (x, y))
        kx, ky = geo.proj(-22.6056, 63.9850)
        inner = "".join(pts) + ('<g class="kef"><circle cx="%g" cy="%g" r="6"/>'
                                '<text x="%g" y="%g">KEF</text></g>' % (kx, ky, kx + 12, ky + 4))
        nodes = ""
    else:
        d, nds = geo.route_geometry(route, COORDS)
        inner = '<path class="trace" d="%s"/>' % d
        nodes = "".join(
            '<g class="node" data-day="%d" transform="translate(%g,%g)">'
            '<circle class="halo" r="13"/><circle class="dot" r="5.5"/>'
            '<text y="3.6">%d</text></g>' % (n["d"], n["x"], n["y"], n["d"]) for n in nds)
    return ('<svg class="%s" viewBox="0 0 1000 660" role="img" aria-label="Mapa de Islandia con el trazado">'
            '<path class="coast" d="%s"/>%s%s</svg>') % (cls, COAST, inner, nodes)

# --------------------------------------------------------------------- CSS
CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --ink:#080D10; --ink1:#0D1418; --ink2:#121D23; --line:rgba(124,198,222,.16); --line2:rgba(124,198,222,.32);
  --bone:#E9F1F3; --dim:#8DA3AC; --dim2:#61757E;
  --glacier:#7CC6DE; --sulfur:#F2B233; --moss:#6FA86A; --rust:#C25E38;
  --shadow:0 18px 50px -20px rgba(0,0,0,.9);
  --disp:'Bricolage Grotesque',system-ui,sans-serif;
  --body:'Instrument Sans',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
  --gut:clamp(18px,4vw,64px);
}
html{scroll-behavior:smooth}
body{margin:0;background:var(--ink);color:var(--bone);font-family:var(--body);
  font-size:clamp(15px,.55vw + 13px,17.5px);line-height:1.62;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:60;opacity:.055;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E")}
img{max-width:100%;display:block}
a{color:var(--glacier);text-decoration:none;border-bottom:1px solid var(--line2)}
:focus-visible{outline:2px solid var(--sulfur);outline-offset:3px}
h1,h2,h3,h4{font-family:var(--disp);font-weight:800;letter-spacing:-.028em;line-height:.98;margin:0}
p{margin:0 0 .9em}
.wrap{max-width:1320px;margin:0 auto;padding:0 var(--gut)}
.mono{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--glacier);margin:0 0 1.1em}
.lede{font-size:clamp(17px,1.1vw + 13px,22px);color:#C6D6DB;max-width:62ch}

/* ---------------- nav ---------------- */
.topbar{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);
  background:linear-gradient(#080D10ee,#080D10cc);border-bottom:1px solid var(--line)}
.topbar .wrap{display:flex;align-items:center;gap:22px;height:56px;overflow-x:auto;scrollbar-width:none}
.topbar .wrap::-webkit-scrollbar{display:none}
.brand{font-family:var(--disp);font-weight:800;font-size:15px;letter-spacing:-.02em;border:0;white-space:nowrap}
.brand span{color:var(--sulfur)}
.topbar nav{display:flex;gap:4px;margin-left:auto}
.topbar nav a{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--dim);border:1px solid transparent;padding:6px 9px;border-radius:4px;white-space:nowrap}
.topbar nav a:hover,.topbar nav a[aria-current=true]{color:var(--bone);border-color:var(--line2);background:#ffffff08}

/* ---------------- hero ---------------- */
.hero{position:relative;min-height:min(94vh,860px);display:flex;align-items:flex-end;overflow:hidden;
  border-bottom:1px solid var(--line)}
.hero-bg{position:absolute;inset:0}
.hero-bg img{width:100%;height:100%;object-fit:cover;opacity:.68;filter:saturate(.92) contrast(1.04)}
.hero-bg::after{content:"";position:absolute;inset:0;
  background:radial-gradient(130% 100% at 76% 6%,rgba(8,13,16,.05),#080D10 72%),linear-gradient(rgba(8,13,16,.35),#080D10 92%)}
.hero .hmap{position:absolute;right:1%;top:9%;width:min(54%,660px);opacity:.85;pointer-events:none}
.hero .wrap{position:relative;padding-top:clamp(90px,16vh,180px);padding-bottom:clamp(40px,7vh,84px);width:100%}
.hero h1{font-size:clamp(52px,11.5vw,168px);line-height:.86;margin:0 0 .35em;max-width:16ch}
.hero h1 em{font-style:normal;display:block;color:var(--sulfur);
  -webkit-text-stroke:0;text-shadow:0 0 60px rgba(242,178,51,.28)}
.hero-data{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;margin:2.6em 0 0;
  border:1px solid var(--line);background:var(--line);max-width:900px}
.hero-data>div{background:#0B1216;padding:14px 16px}
.hero-data dt{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim2)}
.hero-data dd{margin:6px 0 0;font-family:var(--disp);font-weight:700;font-size:24px;letter-spacing:-.02em}
.hero-data dd small{font-family:var(--body);font-weight:400;font-size:12px;color:var(--dim);letter-spacing:0}

/* ---------------- secciones ---------------- */
section{padding:clamp(56px,9vh,120px) 0;border-bottom:1px solid var(--line)}
.shead{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;margin-bottom:2.2em}
.shead h2{font-size:clamp(30px,4.4vw,60px);max-width:22ch}
.shead .num{font-family:var(--mono);font-size:11px;letter-spacing:.2em;color:var(--sulfur)}
.shead p{color:var(--dim);max-width:52ch;margin:0}

/* comparador de ventanas */
.windows{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}
.win{border:1px solid var(--line);background:linear-gradient(#0E1720,#0B1116);padding:clamp(20px,2.4vw,34px);border-radius:8px;position:relative}
.win.best{border-color:rgba(242,178,51,.5);box-shadow:0 0 0 1px rgba(242,178,51,.12),var(--shadow)}
.win .tag{position:absolute;top:-11px;left:24px;font-family:var(--mono);font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;background:var(--sulfur);color:#12181B;padding:4px 10px;border-radius:3px;font-weight:600}
.win.alt .tag{background:var(--ink2);color:var(--dim);border:1px solid var(--line2)}
.win h3{font-size:clamp(24px,2.6vw,34px);margin-bottom:.3em}
.win .dates{font-family:var(--mono);font-size:12.5px;letter-spacing:.06em;color:var(--glacier);margin-bottom:1.4em}
.meter{height:5px;background:#ffffff12;border-radius:99px;overflow:hidden;margin:0 0 6px}
.meter i{display:block;height:100%;background:linear-gradient(90deg,var(--glacier),var(--sulfur))}
.win.alt .meter i{background:linear-gradient(90deg,#3d5a66,#6a7c85)}
.meter-lab{font-family:var(--mono);font-size:10px;letter-spacing:.14em;color:var(--dim2);margin-bottom:1.6em}
.win dl{margin:0 0 1.4em;display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:14.5px}
.win dt{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim2);padding-top:4px}
.win dd{margin:0;color:#C6D6DB}
.blk{margin:0 0 1.3em}
.blk h4{font-family:var(--mono);font-weight:500;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim2);margin:0 0 .7em;padding-bottom:.5em;border-bottom:1px solid var(--line)}
ul.ticks{list-style:none;margin:0;padding:0;font-size:14.5px}
ul.ticks li{position:relative;padding-left:20px;margin-bottom:.5em;color:#C1D1D7}
ul.ticks li::before{content:"";position:absolute;left:0;top:.55em;width:8px;height:8px;border-radius:2px;background:var(--moss)}
ul.ticks.cold li::before{background:var(--glacier)}
ul.ticks.warn li::before{background:var(--rust);border-radius:99px}
.verdict{border-left:2px solid var(--sulfur);padding:2px 0 2px 16px;margin-top:1.6em;font-size:15.5px;color:#DCE7EA}
.win.alt .verdict{border-color:var(--dim2)}

/* escalera de duración */
.ladder{border:1px solid var(--line);border-radius:8px;overflow:hidden}
.rung{display:grid;grid-template-columns:88px 1fr;gap:0;border-bottom:1px solid var(--line);background:#0B1116}
.rung:last-child{border-bottom:0}
.rung.optimo{background:linear-gradient(90deg,rgba(242,178,51,.1),transparent 60%)}
.rung .d{padding:18px 12px;text-align:center;border-right:1px solid var(--line);background:#0A1014}
.rung .d b{font-family:var(--disp);font-size:26px;display:block;line-height:1}
.rung .d span{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;color:var(--dim2)}
.rung .c{padding:16px 20px;display:grid;grid-template-columns:1fr auto;gap:4px 20px;align-items:start}
.rung .c p{margin:0;font-size:15px}
.rung .c .nota{color:var(--dim);font-size:13.5px;grid-column:1}
.rung .c .km{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--glacier);white-space:nowrap;grid-row:1/3}
.rung.optimo .c .km{color:var(--sulfur)}
.badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;border:1px solid var(--line2);
  color:var(--dim);padding:3px 7px;border-radius:3px;margin-left:8px;vertical-align:2px}
.rung.optimo .badge{border-color:var(--sulfur);color:var(--sulfur)}

/* tabla comparativa */
.cmp{width:100%;border-collapse:collapse;font-size:14px}
.cmp th,.cmp td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.cmp thead th{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim2);
  border-bottom:1px solid var(--line2)}
.cmp tbody tr:hover{background:#ffffff06}
.cmp .rt{font-family:var(--disp);font-weight:700;font-size:16px;letter-spacing:-.01em;white-space:nowrap}
.cmp .rt a{border:0;color:var(--bone)}
.cmp .rt a:hover{color:var(--sulfur)}
.cmp .rid{font-family:var(--mono);font-size:10px;color:var(--sulfur);letter-spacing:.1em;display:block}
.cmp td.n{font-family:var(--mono);font-size:12.5px;color:var(--glacier);white-space:nowrap}
.bars{display:inline-flex;gap:3px;vertical-align:1px}
.bars i{width:7px;height:12px;background:#ffffff1a;border-radius:1px}
.bars i.on{background:var(--sulfur)}
.tblscroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px}

/* ---------------- ruta ---------------- */
.route{padding-top:clamp(48px,7vh,90px)}
.route-head{position:relative;margin-bottom:2.4em}
.route-head .rid{font-family:var(--disp);font-weight:800;font-size:clamp(80px,16vw,220px);line-height:.8;
  color:transparent;-webkit-text-stroke:1px var(--line2);position:absolute;right:0;top:-.16em;z-index:0;pointer-events:none}
.route-head .kicker{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--glacier);margin:0 0 .8em}
.route-head h2{font-size:clamp(38px,6.4vw,86px);position:relative;z-index:1}
.route-head .claim{font-size:clamp(16px,1vw + 12px,21px);color:#C6D6DB;max-width:44ch;margin:.7em 0 0;position:relative;z-index:1}
.route-body{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:clamp(24px,3.4vw,56px);align-items:start}
.route-aside{position:sticky;top:76px}
.map-wrap{border:1px solid var(--line);border-radius:8px;background:
  linear-gradient(#0A1216,#0A1216) padding-box,
  repeating-linear-gradient(0deg,#ffffff05 0 1px,transparent 1px 34px),
  repeating-linear-gradient(90deg,#ffffff05 0 1px,transparent 1px 34px);
  background-blend-mode:normal;padding:6px;margin-bottom:14px;position:relative}
.maphint{font-size:11.5px;color:var(--dim2);margin:-6px 0 14px;line-height:1.45}
.map-wrap::after{content:attr(data-lab);position:absolute;bottom:8px;right:10px;font-family:var(--mono);
  font-size:8.5px;letter-spacing:.14em;color:var(--dim2);text-transform:uppercase}
svg.rmap{width:100%;height:auto;display:block}
svg .coast{fill:#0E181D;stroke:var(--line2);stroke-width:1.1;vector-effect:non-scaling-stroke}
svg .trace{fill:none;stroke:var(--sulfur);stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round;
  filter:drop-shadow(0 0 6px rgba(242,178,51,.35))}
svg .spot{fill:var(--glacier);opacity:.9}
svg.hmap .coast{fill:rgba(14,24,29,.55);stroke:rgba(124,198,222,.5)}
svg .kef circle{fill:none;stroke:var(--sulfur);stroke-width:1.4}
svg .kef text{font-family:var(--mono);font-size:10px;fill:var(--sulfur);letter-spacing:.1em}
svg .node{cursor:pointer}
svg .node .halo{fill:rgba(242,178,51,.14);opacity:0;transition:opacity .25s}
svg .node .dot{fill:#0A1014;stroke:var(--sulfur);stroke-width:1.6;transition:fill .25s,r .25s}
svg .node text{font-family:var(--mono);font-size:9px;fill:var(--bone);text-anchor:middle;pointer-events:none;opacity:.75}
svg .node:hover .halo,svg .node.on .halo{opacity:1}
svg .node.on .dot{fill:var(--sulfur)}
svg .node.on text{fill:#12181B;opacity:1;font-weight:600}
.stats{display:grid;grid-template-columns:auto 1fr;gap:1px;margin:0 0 14px;border:1px solid var(--line);background:var(--line)}
.stats dt,.stats dd{background:#0B1216;margin:0;padding:8px 12px;font-size:13.5px}
.stats dt{font-family:var(--mono);font-size:9.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--dim2);padding-top:11px}
.stats dd{color:#C6D6DB}
.stats dd b{font-family:var(--disp);font-size:17px;letter-spacing:-.01em}
.aside-lists{display:grid;gap:14px;margin-bottom:14px}
.warn{border:1px solid rgba(194,94,56,.4);background:rgba(194,94,56,.08);padding:12px 14px;border-radius:6px;
  font-size:13.5px;color:#EBC9BA;margin:0 0 14px}
.warn b{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--rust);margin-bottom:.4em}
.trim{font-size:13px;color:var(--dim);border-top:1px dashed var(--line2);padding-top:12px;margin:0}
.trim b{color:var(--glacier);font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;display:block;margin-bottom:.3em}
.route-sum{font-size:clamp(15px,.5vw + 13px,17.5px);color:#C6D6DB;max-width:70ch;margin:0 0 2.2em}

/* días */
.days{list-style:none;margin:0;padding:0;counter-reset:day}
.day{border-top:1px solid var(--line);padding:26px 0 30px;transition:opacity .4s}
.day:first-child{border-top:1px solid var(--line2)}
.day-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:.7em}
.day-head .dn{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--sulfur);
  border:1px solid var(--line2);padding:4px 8px;border-radius:3px;background:#ffffff06}
.day.on .day-head .dn{background:var(--sulfur);color:#12181B;border-color:var(--sulfur)}
.day-head h3{font-size:clamp(20px,1.7vw,28px);flex:1 1 auto;min-width:200px}
.day-head .km{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--dim)}
.day>p{color:#BDCDD3;max-width:74ch;margin:0 0 1.2em}
.stops{display:grid;grid-template-columns:repeat(auto-fill,minmax(224px,1fr));gap:14px}
.stop{margin:0;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:#0B1216;
  display:flex;flex-direction:column}
.stops>*{min-width:0}
.stop .sw{position:relative;width:100%;min-width:0;aspect-ratio:3/2;overflow:hidden;background:#0E181D}
.stop .sw .swiper-wrapper{position:absolute;inset:0}
.stop .swiper-slide{height:100%;background:#0E181D;overflow:hidden}
.stop .swiper-slide img{width:100%;height:100%;object-fit:cover}
.stop figcaption{padding:11px 12px 12px}
.stop figcaption b{display:block;font-family:var(--disp);font-weight:700;font-size:15px;letter-spacing:-.01em;margin-bottom:.25em}
.stop figcaption span{font-size:12.5px;color:var(--dim);line-height:1.45;display:block}
.stop .credit{font-family:var(--mono);font-size:8px;letter-spacing:.06em;color:var(--dim2);padding:0 12px 10px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.stop .swiper-button-next,.stop .swiper-button-prev{--swiper-navigation-size:12px;color:#fff;
  width:26px;height:26px;background:#0a1014b3;border-radius:99px;opacity:0;transition:opacity .2s}
.stop:hover .swiper-button-next,.stop:hover .swiper-button-prev{opacity:.9}
.stop .swiper-pagination{bottom:6px!important}
.stop .swiper-pagination-bullet{background:#fff;opacity:.4;width:5px;height:5px}
.stop .swiper-pagination-bullet-active{background:var(--sulfur);opacity:1;width:14px;border-radius:99px}
.stop .nph{position:absolute;top:8px;left:8px;z-index:2;font-family:var(--mono);font-size:8.5px;letter-spacing:.1em;
  background:#0a1014b3;color:#cfe3ea;padding:3px 6px;border-radius:99px}

/* extras, dinero, reservas, practico */
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.card{border:1px solid var(--line);border-radius:8px;background:#0B1216;overflow:hidden}
.card .ph{aspect-ratio:3/2;background:#0E181D}
.card .ph img{width:100%;height:100%;object-fit:cover}
.card .bd{padding:16px 18px}
.card h3{font-size:20px;margin-bottom:.4em}
.card p{font-size:14px;color:var(--dim);margin:0}
.money{width:100%;border-collapse:collapse;font-size:14.5px}
.money td,.money th{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.money thead th{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim2)}
.money td:nth-child(2){font-family:var(--mono);font-size:13px;color:var(--sulfur);white-space:nowrap}
.money td:nth-child(3){color:var(--dim);font-size:13.5px}
.money tfoot td{border-bottom:0;border-top:1px solid var(--line2);font-family:var(--disp);font-weight:700;font-size:17px}
.money tfoot td:nth-child(2){font-size:17px;color:var(--sulfur);font-family:var(--disp)}
.tl{list-style:none;margin:0;padding:0}
.tl li{display:grid;grid-template-columns:minmax(140px,190px) 1fr;gap:4px 24px;padding:16px 0;border-top:1px solid var(--line)}
.tl li:first-child{border-top:0}
.tl .when{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--glacier);padding-top:3px}
.tl .what{font-family:var(--disp);font-weight:700;font-size:18px;margin:0 0 .2em}
.tl .why{color:var(--dim);font-size:14px;margin:0}
footer{padding:clamp(40px,7vh,80px) 0;color:var(--dim2);font-size:13px;border:0}
footer h3{font-size:22px;color:var(--bone);margin-bottom:.8em}
footer a{color:var(--dim)}
details.creds summary{cursor:pointer;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--glacier);margin-bottom:1em}
.credlist{columns:2 320px;column-gap:28px;font-size:11px;line-height:1.55;max-height:420px;overflow:auto;
  border:1px solid var(--line);padding:14px;border-radius:6px}
.credlist div{break-inside:avoid;margin-bottom:.35em}

@media (max-width:900px){
  .route-body{grid-template-columns:1fr}
  .route-aside{position:static}
  .map-wrap{max-width:520px}
  .hero .hmap{position:relative;right:auto;top:auto;width:100%;max-width:420px;margin:2em 0 0;opacity:.6}
  .tl li{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *{animation-duration:.001s!important;transition-duration:.001s!important}
}
"""

# --------------------------------------------------------------------- JS
JS = """
(function(){
  var GAL=window.__GAL,IMG=window.__IMG,NAMES=window.__NAMES,TAGS=window.__TAGS;
  function slide(p,n,total){
    return '<div class="swiper-slide">'+(total>1?'<span class="nph">'+n+'/'+total+'</span>':'')+
      '<img alt="" decoding="async" data-k="'+p.k+'"></div>';
  }
  function card(slug){
    var ph=GAL[slug]||[],n=ph.length;
    var nav=n>1?'<div class="swiper-button-prev"></div><div class="swiper-button-next"></div><div class="swiper-pagination"></div>':'';
    var cr=ph.length?('© '+(ph[0].a||'Commons')+' · '+(ph[0].l||'CC')):'';
    return '<figure class="stop" data-slug="'+slug+'">'+
      '<div class="sw swiper"><div class="swiper-wrapper">'+
      ph.map(function(p,i){return slide(p,i+1,n)}).join('')+'</div>'+nav+'</div>'+
      '<figcaption><b>'+(NAMES[slug]||slug)+'</b><span>'+(TAGS[slug]||'')+'</span></figcaption>'+
      '<span class="credit">'+cr+'</span></figure>';
  }
  // 1. pintar las tarjetas de cada día cuando se acercan a la pantalla
  function vh(){return window.innerHeight||document.documentElement.clientHeight||screen.height||800}
  var boxes=[].slice.call(document.querySelectorAll('.stops'));
  function fill(box){
    if(box.__done)return; box.__done=1;
    box.innerHTML=(box.dataset.stops||'').split(',').filter(Boolean).map(card).join('');
    box.querySelectorAll('img[data-k]').forEach(function(im){im.src=IMG[im.dataset.k]});
    box.querySelectorAll('.stop').forEach(function(fig){
      var ph=(GAL[fig.dataset.slug]||[]);
      if(ph.length<2)return;
      new Swiper(fig.querySelector('.swiper'),{rewind:true,speed:420,
        pagination:{el:fig.querySelector('.swiper-pagination'),clickable:true},
        navigation:{nextEl:fig.querySelector('.swiper-button-next'),prevEl:fig.querySelector('.swiper-button-prev')},
        keyboard:{enabled:true,onlyInViewport:true},
        on:{slideChange:function(){var r=ph[this.activeIndex];
          if(r)fig.querySelector('.credit').textContent='© '+(r.a||'Commons')+' · '+(r.l||'CC')}}});
    });
  }
  var ticking=false;
  function sweep(){
    ticking=false;
    var margin=vh()+1400;
    for(var i=0;i<boxes.length;i++){
      var b=boxes[i]; if(b.__done)continue;
      var r=b.getBoundingClientRect();
      if(r.top<margin&&r.bottom>-margin)fill(b);
    }
  }
  function onScroll(){if(!ticking){ticking=true;requestAnimationFrame(sweep)}}
  addEventListener('scroll',onScroll,{passive:true});
  addEventListener('resize',onScroll);
  sweep();
  // red de seguridad: si algo impide medir la pantalla, se pintan por lotes al quedar libre
  var idle=window.requestIdleCallback||function(f){setTimeout(f,600)};
  (function drip(){
    var left=boxes.filter(function(b){return !b.__done});
    if(!left.length)return;
    if(document.querySelectorAll('.stop').length===0)left.slice(0,4).forEach(fill);
    idle(function(){setTimeout(drip,1200)});
  })();

  addEventListener('beforeprint',function(){boxes.forEach(fill);
    document.querySelectorAll('svg .trace').forEach(function(p){p.style.strokeDashoffset=0})});

  // 2. dibujar el trazado del mapa a la vez que se leen los días
  var reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
  if(window.gsap&&window.ScrollTrigger&&!reduce){
    gsap.registerPlugin(ScrollTrigger);
    document.querySelectorAll('.route').forEach(function(rt){
      var path=rt.querySelector('svg .trace'),list=rt.querySelector('.days');
      if(!path||!list)return;
      var len=path.getTotalLength();
      gsap.set(path,{strokeDasharray:len,strokeDashoffset:len});
      gsap.to(path,{strokeDashoffset:0,ease:'none',
        scrollTrigger:{trigger:list,start:'top 78%',end:'bottom 65%',scrub:.6}});
    });
  }else{
    document.querySelectorAll('svg .trace').forEach(function(p){p.style.strokeDashoffset=0});
  }

  // 3. día activo <-> nodo del mapa
  document.querySelectorAll('.route').forEach(function(rt){
    var days=rt.querySelectorAll('.day'),nodes=rt.querySelectorAll('svg .node');
    function mark(d){
      days.forEach(function(x){x.classList.toggle('on',x.dataset.day===d)});
      nodes.forEach(function(x){x.classList.toggle('on',x.dataset.day===d)});
    }
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){if(en.isIntersecting)mark(en.target.dataset.day)});
    },{rootMargin:'-45% 0px -45% 0px'});
    days.forEach(function(d){
      io.observe(d);
      d.addEventListener('mouseenter',function(){mark(d.dataset.day)});
    });
    nodes.forEach(function(n){
      n.addEventListener('click',function(){
        var t=rt.querySelector('.day[data-day="'+n.dataset.day+'"]');
        if(t)t.scrollIntoView({block:'center',behavior:reduce?'auto':'smooth'});
      });
    });
  });

  // 4. sección activa en la barra
  var links=[].slice.call(document.querySelectorAll('.topbar nav a'));
  var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'))}).filter(Boolean);
  var sio=new IntersectionObserver(function(es){
    es.forEach(function(en){
      if(!en.isIntersecting)return;
      links.forEach(function(a){a.setAttribute('aria-current',a.getAttribute('href')==='#'+en.target.id)});
    });
  },{rootMargin:'-20% 0px -70% 0px'});
  secs.forEach(function(s){sio.observe(s)});
})();
"""

# --------------------------------------------------------------------- HTML
def bars(n, total=5):
    return '<span class="bars">' + "".join('<i class="%s"></i>' % ("on" if i < n else "") for i in range(total)) + "</span>"

def window_card(w):
    best = w["id"] == "junio"
    L = []
    L.append('<div class="win %s">' % ("best" if best else "alt"))
    L.append('<span class="tag">%s</span>' % e(w["tag"]))
    L.append("<h3>%s</h3>" % e(w["titulo"]))
    L.append('<p class="dates">%s</p>' % e(w["fechas"]))
    L.append('<div class="meter"><i style="width:%d%%"></i></div>'
             '<div class="meter-lab">Acceso a sitios: %d de 100</div>' % (w["score"], w["score"]))
    L.append("<dl><dt>Luz</dt><dd>%s</dd><dt>Temp.</dt><dd>%s</dd></dl>" % (e(w["luz"]), e(w["temp"])))
    for key, title, cls in (("abierto", "Qué está abierto", "cold"), ("fauna", "Fauna", ""), ("contras", "Lo que cuesta", "warn")):
        L.append('<div class="blk"><h4>%s</h4><ul class="ticks %s">%s</ul></div>' %
                 (title, cls, "".join("<li>%s</li>" % e(i) for i in w[key])))
    L.append('<p class="verdict">%s</p></div>' % e(w["veredicto"]))
    return "".join(L)

def route_article(r):
    L = []
    L.append('<article class="route" id="ruta-%s">' % r["id"])
    L.append('<div class="wrap"><header class="route-head"><span class="rid" aria-hidden="true">%s</span>'
             '<p class="kicker">%s</p><h2>%s</h2><p class="claim">%s</p></header>' %
             (r["id"], e(r["kicker"]), e(r["name"]), e(r["claim"])))
    L.append('<div class="route-body"><aside class="route-aside">')
    L.append('<div class="map-wrap" data-lab="Trazado esquemático">%s</div>'
             '<p class="maphint">Los círculos son los días. Al pasar por un día se enciende en el mapa; '
             'al pulsar un círculo, salta a ese día.</p>' % map_svg(r))
    L.append("<dl class=\"stats\">"
             "<dt>Días</dt><dd><b>%d</b></dd>"
             "<dt>Kilómetros</dt><dd><b>%s</b> aprox.</dd>"
             "<dt>Al volante</dt><dd>%s</dd>"
             "<dt>Vehículo</dt><dd>%s</dd>"
             "<dt>Exigencia</dt><dd>%s</dd>"
             "<dt>Ventana</dt><dd>%s</dd></dl>" %
             (r["dias"], "{:,}".format(r["km"]).replace(",", "."), e(r["cond"]), e(r["vehiculo"]),
              bars(r["dif"]), e(r["ventana"])))
    L.append('<div class="aside-lists"><div class="blk"><h4>Por qué esta</h4><ul class="ticks">%s</ul></div>'
             '<div class="blk"><h4>Qué dejáis fuera</h4><ul class="ticks warn">%s</ul></div></div>' %
             ("".join("<li>%s</li>" % e(i) for i in r["porque"]),
              "".join("<li>%s</li>" % e(i) for i in r["sacrificas"])))
    L.append('<p class="warn"><b>Antes de meterse</b>%s</p>' % e(r["aviso"]))
    L.append('<p class="trim"><b>Si son 9 días</b>%s</p>' % e(r["recorte"]))
    L.append("</aside><div>")
    L.append('<p class="route-sum">%s</p>' % e(r["resumen"]))
    L.append('<ol class="days">')
    for d in r["dias_detalle"]:
        km = "%d km" % d["km"] if d["km"] else "sin coche"
        L.append('<li class="day" data-day="%d"><div class="day-head"><span class="dn">Día %02d</span>'
                 '<h3>%s</h3><span class="km">%s</span></div><p>%s</p>'
                 '<div class="stops" data-stops="%s"></div></li>' %
                 (d["d"], d["d"], e(d["t"]), km, e(d["x"]), ",".join(d["stops"])))
    L.append("</ol></div></div></div></article>")
    return "".join(L)

def main():
    if ONLY:
        C.ROUTES = [r for r in C.ROUTES if r["id"] in ONLY]
    used = set()
    for r in C.ROUTES:
        for d in r["dias_detalle"]:
            used.update(d["stops"])
    used |= {"askja", "sprengisandur", "heimaey"}
    IMG, GAL, HEROIMG, credits = images.build(used, hero_slugs=HEROES)
    if MAXPH:
        for k in GAL:
            GAL[k] = GAL[k][:MAXPH]
        keep = {p["k"] for v in GAL.values() for p in v}
        IMG = {k: v for k, v in IMG.items() if k in keep}
    total_photos = sum(len(v) for v in GAL.values())

    NAMES = {k: v["name"] for k, v in json.load(open(os.path.join(BASE, "sites.json"))).items()}
    NAMES.update(C.NOMBRES_EXTRA)
    NAMES = {k: v for k, v in NAMES.items() if k in GAL}
    n_paradas = len(used - {"askja", "sprengisandur", "heimaey"})
    favicon = ("data:image/svg+xml," + urllib.parse.quote(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 660'>"
        "<rect width='1000' height='660' fill='%230A1014'/>"
        "<path d='" + COAST + "' fill='%23F2B233' stroke='%23F2B233' stroke-width='14'/></svg>"))
    H = ['<meta charset="utf-8">',
         '<link rel="icon" href="%s">' % favicon,
         '<title>Islandia salvaje · 6 rutas para junio de 2027</title>',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<meta name="color-scheme" content="dark">',
         "<style>%s</style>" % font_css(), "<style>%s</style>" % CSS,
         "<style>%s</style>" % lib("swiper.min.css")]

    # ---- barra
    navlinks = [("#cuando", "Fechas"), ("#dias", "Días"), ("#rutas", "Rutas")]
    navlinks += [("#ruta-%s" % r["id"], r["id"]) for r in C.ROUTES]
    navlinks += [("#dinero", "Dinero"), ("#reservas", "Reservas"), ("#practico", "Práctico")]
    H.append('<div class="topbar"><div class="wrap"><a class="brand" href="#top">ISLANDIA <span>2027</span></a><nav>%s</nav></div></div>'
             % "".join('<a href="%s">%s</a>' % (h, t) for h, t in navlinks))

    # ---- hero
    H.append('<header class="hero" id="top"><div class="hero-bg"><img alt="Landmannalaugar" src="%s"></div>%s'
             '<div class="wrap"><p class="eyebrow">%s</p><h1>Islandia<em>salvaje</em></h1>'
             '<p class="lede">Seis rutas posibles para dos personas con una camper, ordenadas por lo que de verdad '
             'decide el viaje: la fecha. Comparad, elegid una y ajustadla. Cada parada lleva fotos reales del sitio.</p>'
             '<dl class="hero-data">'
             '<div><dt>Ventana recomendada</dt><dd>17–28 jun<small> 2027, con el solsticio dentro</small></dd></div>'
             '<div><dt>Duración</dt><dd>11 días<small> 9 funcionan; 11 es el punto dulce</small></dd></div>'
             '<div><dt>Rutas</dt><dd>4 + 2<small> cuatro propias y dos clásicas</small></dd></div>'
             '<div><dt>Paradas</dt><dd>%d<small> con %d fotos reales</small></dd></div>'
             '<div><dt>Auroras</dt><dd>No<small> se cambian por acceso total</small></dd></div>'
             '</dl></div></header>' % (HEROIMG[HEROES[0]], map_svg(None, "rmap hmap"), e(C.META["pareja"]),
                                       n_paradas, total_photos))

    # ---- cuándo
    H.append('<section id="cuando"><div class="wrap"><div class="shead"><span class="num">01 · Fechas</span>'
             '<h2>La fecha decide el 70 %% del viaje</h2>'
             '<p>Las dos ventanas que barajáis no son variantes de lo mismo: cambian qué carreteras existen. '
             'Semana Santa de 2027 cae del 21 al 28 de marzo, muy temprana.</p></div>'
             '<div class="windows">%s</div></div></section>'
             % "".join(window_card(w) for w in C.VENTANAS))

    # ---- días
    rungs = []
    for d in C.DURACION:
        badge = ""
        if d["estado"] == "optimo":
            badge = '<span class="badge">Recomendado</span>'
        elif d["estado"] == "justo":
            badge = '<span class="badge">Vuestra idea</span>'
        rungs.append('<div class="rung %s"><div class="d"><b>%s</b><span>días</span></div>'
                     '<div class="c"><p>%s%s</p><span class="km">%s km</span>'
                     '<p class="nota">%s</p></div></div>' %
                     (d["estado"], e(d["dias"]), e(d["que"]), badge, e(d["km"]), e(d["nota"])))
    H.append('<section id="dias"><div class="wrap"><div class="shead"><span class="num">02 · Duración</span>'
             '<h2>Nueve días llegan, once cambian el viaje</h2>'
             '<p>Con 9 días hay que elegir entre dar la vuelta completa o entrar al interior. '
             'Los dos días extra son los que permiten hacer las dos cosas y aún tener margen para un día de lluvia.</p></div>'
             '<div class="ladder">%s</div></div></section>' % "".join(rungs))

    # ---- comparador
    rows = []
    for r in C.ROUTES:
        rows.append('<tr><td class="rt"><span class="rid">Ruta %s</span><a href="#ruta-%s">%s</a></td>'
                    '<td class="n">%d</td><td class="n">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                    (r["id"], r["id"], e(r["name"]), r["dias"], "{:,}".format(r["km"]).replace(",", "."),
                     bars(r["dif"]), e(r["vehiculo"]), e(r["porque"][0]), e(r["sacrificas"][0])))
    H.append('<section id="rutas"><div class="wrap"><div class="shead"><span class="num">03 · Rutas</span>'
             '<h2>Seis maneras de recorrerla</h2><p>Las cuatro primeras son propuestas propias, con el interior y '
             'los fiordos del oeste como protagonistas. Las dos últimas son las clásicas, para comparar.</p></div>'
             '<div class="tblscroll"><table class="cmp"><thead><tr><th>Ruta</th><th>Días</th><th>Km</th>'
             '<th>Exigencia</th><th>Vehículo</th><th>Lo mejor</th><th>Lo que se pierde</th></tr></thead>'
             '<tbody>%s</tbody></table></div></div></section>' % "".join(rows))

    for r in C.ROUTES:
        H.append(route_article(r))

    # ---- extras
    extras = [("askja", "Askja y Holuhraun", "Dos días más por la F88 o la F905 para ver una caldera con un lago dentro y el campo de lava de 2014. Abre a finales de junio."),
              ("sprengisandur", "Sprengisandur", "Cruzar la isla por el desierto central, 200 km sin nada. Une el sur con Mývatn en un día largo."),
              ("heimaey", "Vestmannaeyjar", "Ferry de 35 minutos desde Landeyjahöfn: un volcán de 1973, frailecillos por miles y un campo de fútbol con acantilado.")]
    H.append('<section id="extras"><div class="wrap"><div class="shead"><span class="num">04 · Extensiones</span>'
             '<h2>Si estiráis a 13 días</h2><p>Tres bloques que encajan encima de cualquiera de las rutas sin rehacerla.</p></div>'
             '<div class="grid3">%s</div></div></section>' %
             "".join('<div class="card"><div class="ph"><img alt="%s" decoding="async" src="%s"></div>'
                     '<div class="bd"><h3>%s</h3><p>%s</p></div></div>' %
                     (e(t), IMG[GAL[s][0]["k"]], e(t), e(x)) for s, t, x in extras if GAL.get(s)))

    # ---- dinero
    money = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (e(a), e(b), e(c)) for a, b, c in C.PRESUPUESTO)
    H.append('<section id="dinero"><div class="wrap"><div class="shead"><span class="num">05 · Dinero</span>'
             '<h2>Lo que cuesta, para dos, en junio</h2><p>Cifras de referencia para 10 días. La camper y los vuelos '
             'son el 60 %% del total y son justo lo que sube si se espera.</p></div>'
             '<div class="tblscroll"><table class="money"><thead><tr><th>Concepto</th><th>Rango</th><th>Notas</th></tr></thead>'
             '<tbody>%s</tbody><tfoot><tr><td>Total pareja, 10 días</td><td>4.000 – 7.000 €</td>'
             '<td>La horquilla baja es camper 2WD y cocinar casi siempre; la alta, 4x4 con pistas F y actividades guiadas.</td>'
             '</tr></tfoot></table></div></div></section>' % money)

    # ---- reservas
    H.append('<section id="reservas"><div class="wrap"><div class="shead"><span class="num">06 · Reservas</span>'
             '<h2>El orden en que hay que reservar</h2><p>Estamos en agosto de 2026: vais con tiempo, pero dos cosas '
             'se agotan un año antes.</p></div><ol class="tl">%s</ol></div></section>' %
             "".join('<li><div class="when">%s</div><div><p class="what">%s</p><p class="why">%s</p></div></li>' %
                     (e(a), e(b), e(c)) for a, b, c in C.RESERVAS))

    # ---- práctico
    H.append('<section id="practico"><div class="wrap"><div class="shead"><span class="num">07 · Práctico</span>'
             '<h2>Seis cosas que conviene tener claras</h2></div><div class="grid3">%s</div></div></section>' %
             "".join('<div class="card"><div class="bd"><h3>%s</h3><p>%s</p></div></div>' % (e(p["t"]), e(p["x"]))
                     for p in C.PRACTICO))

    # ---- footer
    seen, cred_html = set(), []
    for title, author, lic, page in credits:
        if title in seen:
            continue
        seen.add(title)
        cred_html.append("<div>%s · %s (%s)</div>" % (e(title), e(author or "autor no indicado"), e(lic)))
    H.append('<footer><div class="wrap"><h3>Fotos y fuentes</h3>'
             '<p style="max-width:70ch">Las %d fotos vienen de Wikimedia Commons y están incrustadas en este archivo '
             'para que funcione sin conexión. Uso personal, no comercial. Autoría y licencia de cada una, debajo.</p>'
             '<details class="creds"><summary>Ver el listado de %d fotos</summary><div class="credlist">%s</div></details>'
             '<p style="margin-top:2em">Fechas de apertura de pistas F: road.is y umferdin.is (Vegagerðin). '
             'Meteorología: vedur.is. Refugios del Laugavegur: Ferðafélag Íslands. Precios de camper y actividades: '
             'medias de mercado de la temporada 2026, a revisar al reservar. %s.</p></div></footer>'
             % (total_photos, len(cred_html), "".join(cred_html), e(C.META["fecha_doc"])))

    # ---- datos + scripts
    H.append("<script>window.__IMG=%s;window.__GAL=%s;window.__NAMES=%s;window.__TAGS=%s;</script>"
             % (json.dumps(IMG), json.dumps(GAL, ensure_ascii=False),
                json.dumps(NAMES, ensure_ascii=False), json.dumps(C.TAGS, ensure_ascii=False)))
    H.append("<script>%s</script>" % lib("swiper.min.js"))
    H.append("<script>%s</script>" % lib("gsap.min.js"))
    H.append("<script>%s</script>" % lib("scrolltrigger.min.js"))
    H.append("<script>%s</script>" % JS)

    doc = "\n".join(H)
    open(OUT, "w", encoding="utf-8").write(doc)
    print("HTML: %.1f MB · %d fotos · %d paradas (+3 extensiones)" % (len(doc.encode()) / 1e6, total_photos, n_paradas))

if __name__ == "__main__":
    main()
