#!/usr/bin/env python3
"""
Gera as imagens do perfil GitHub (banner, neofetch e stats) nos temas dark e light.

    python3 profile-assets.py            # gera os 6 arquivos em ./assets

Os dados de stats ficam em STATS e podem ser atualizados com:
    gh api graphql -f query='{ user(login:"felipesauer"){ ... } }'
"""
import os
from PIL import Image, ImageDraw, ImageFont

def _fonte(estilo):
    """Localiza JetBrains Mono no sistema; cai para DejaVu Sans Mono se faltar."""
    import subprocess
    for familia in ("JetBrains Mono", "DejaVu Sans Mono"):
        try:
            caminho = subprocess.check_output(
                ["fc-match", f"{familia}:style={estilo}", "-f", "%{file}"],
                text=True, stderr=subprocess.DEVNULL).strip()
            if caminho and estilo.lower() in caminho.lower():
                return caminho
            if caminho and familia == "DejaVu Sans Mono":
                return caminho
        except Exception:
            pass
    return "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

FONT_R = _fonte("Regular")
FONT_B = _fonte("Bold")
f = lambda p, s: ImageFont.truetype(p, s)

HOST = "felipe@felipe-sauer"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

TEMAS = {
    "dark": dict(BG=(13, 17, 23), WIN=(22, 27, 34), BORDER=(48, 54, 61),
                 VERDE=(138, 226, 52), AZUL=(114, 159, 207),
                 FG=(211, 215, 207), DIM=(110, 118, 129), TRACK=(34, 42, 54)),
    "light": dict(BG=(255, 255, 255), WIN=(246, 248, 250), BORDER=(208, 215, 222),
                  VERDE=(26, 127, 55), AZUL=(9, 105, 218),
                  FG=(31, 35, 40), DIM=(110, 119, 129), TRACK=(215, 222, 229)),
}

def _carrega_stats():
    """Le assets/stats.json (gerado pelo workflow); usa fallback se nao existir."""
    import json
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "stats.json")
    try:
        with open(caminho) as fh:
            d = json.load(fh)
        return ([("Public repos", str(d["repos"])), ("Total stars", str(d["stars"])),
                 ("Followers", str(d["followers"])), ("Commits (last year)", str(d["commits"]))],
                [(l["lang"], l["pct"]) for l in d["langs"][:4]])
    except Exception:
        return ([("Public repos", "10"), ("Total stars", "38"),
                 ("Followers", "16"), ("Commits (last year)", "1442")],
                [("TypeScript", 86.1), ("PHP", 8.6), ("JavaScript", 3.7), ("Python", 1.1)])

STATS, LANGS = _carrega_stats()

NEOFETCH_ART = [
    "        .--.        ", "       |o_o |       ", "       |:_/ |       ",
    "      //   \\ \\      ", "     (|     | )     ", "    /'\\_   _/`\\     ",
    "    \\___)=(___/     ",
]
NEOFETCH_CAMPOS = [
    ("OS", "Full Stack Developer"), ("Host", "Brazil"),
    ("Kernel", "TypeScript / PHP"), ("Shell", "bash on Linux"),
    ("Packages", "10 public repositories"), ("", ""),
    ("Backend", "Node.js, Laravel, REST APIs"),
    ("Frontend", "React, Next.js, TailwindCSS"),
    ("Database", "PostgreSQL, MySQL, Neo4j"),
    ("Infra", "Docker, GitHub Actions, Cloudflare"),
    ("Quality", "TS strict, PHPStan max, tests"),
    ("AI", "coding agents, decision auditing"),
]

TB = 36  # altura da barra de titulo


def moldura(W, H, c):
    """Janela de terminal: barra de titulo, botoes e borda."""
    img = Image.new("RGB", (W, H), c["BG"])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], 8, fill=c["BG"], outline=c["BORDER"])
    d.rounded_rectangle([0, 0, W - 1, TB], 8, fill=c["WIN"])
    d.rectangle([0, TB - 8, W - 1, TB], fill=c["WIN"])
    d.line([(0, TB), (W - 1, TB)], fill=c["BORDER"])
    for i, cor in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([16 + i * 20, 12, 27 + i * 20, 23], fill=cor)
    t = f"{HOST}: ~"
    d.text(((W - d.textlength(t, font=f(FONT_R, 14))) / 2, 11), t, font=f(FONT_R, 14), fill=c["DIM"])
    return img, d


def prompt(d, x, y, cmd, fs, c, cw):
    """Desenha o PS1 padrao do Debian: \\u@\\h verde, \\w azul."""
    d.text((x, y), HOST, font=f(FONT_B, fs), fill=c["VERDE"]);  x += len(HOST) * cw
    d.text((x, y), ":", font=f(FONT_R, fs), fill=c["FG"]);      x += cw
    d.text((x, y), "~", font=f(FONT_B, fs), fill=c["AZUL"]);    x += cw
    d.text((x, y), "$ ", font=f(FONT_R, fs), fill=c["FG"]);     x += cw * 2
    if cmd:
        d.text((x, y), cmd, font=f(FONT_R, fs), fill=c["FG"])
    return x + len(cmd) * cw


def largura_char(fs):
    return ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength("M", font=f(FONT_R, fs))


def banner(tema):
    # mesma escala do neofetch (FS 17 / LH 25) para as duas janelas casarem na pagina
    c, FS, LH, PADX = TEMAS[tema], 17, 25, 26
    cw = largura_char(FS)
    saida = ["Full Stack Developer",
             "TypeScript  PHP  React  Node.js  Laravel  PostgreSQL  Docker"]
    maior = max([len(HOST) + 4 + len("cat profile.txt")] + [len(s) for s in saida])
    W, H = int(PADX * 2 + maior * cw), TB + 18 + LH * 5 + 14
    img, d = moldura(W, H, c)
    y = TB + 18
    prompt(d, PADX, y, "cat profile.txt", FS, c, cw); y += LH
    d.text((PADX, y - 2), "Felipe Sauer", font=f(FONT_B, 32), fill=c["VERDE"]); y += LH + 14
    for s in saida:
        d.text((PADX, y), s, font=f(FONT_R, FS), fill=c["FG"]); y += LH
    x = prompt(d, PADX, y, "", FS, c, cw)
    d.rectangle([x, y + 2, x + cw - 2, y + FS + 4], fill=c["FG"])
    return img


def neofetch(tema):
    c, FS, LH, PADX = TEMAS[tema], 17, 25, 26
    cw = largura_char(FS)
    art_w = int(max(len(l) for l in NEOFETCH_ART) * cw)
    lab_w = int(max(len(k) for k, _ in NEOFETCH_CAMPOS) * cw)
    val_w = int(max(len(v) for _, v in NEOFETCH_CAMPOS) * cw)
    W = int(PADX * 2 + art_w + cw * 3 + lab_w + cw * 2 + val_w)
    W = max(W, int(PADX * 2 + (len(HOST) + 12) * cw))
    H = TB + 16 + LH * (len(NEOFETCH_CAMPOS) + 4) + 14
    img, d = moldura(W, H, c)
    y = TB + 16
    prompt(d, PADX, y, "neofetch", FS, c, cw); y += LH * 2
    ay = y
    for l in NEOFETCH_ART:
        d.text((PADX, ay), l, font=f(FONT_R, FS), fill=c["VERDE"]); ay += LH
    cx, cy = PADX + art_w + int(cw * 3), y
    d.text((cx, cy), "felipe", font=f(FONT_B, FS), fill=c["VERDE"])
    d.text((cx + cw * 6, cy), "@", font=f(FONT_R, FS), fill=c["FG"])
    d.text((cx + cw * 7, cy), "felipe-sauer", font=f(FONT_B, FS), fill=c["AZUL"])
    cy += LH
    d.text((cx, cy), "-" * 34, font=f(FONT_R, FS), fill=c["DIM"]); cy += LH
    for k, v in NEOFETCH_CAMPOS:
        if k:
            d.text((cx, cy), f"{k}:", font=f(FONT_B, FS), fill=c["AZUL"])
            d.text((cx + lab_w + int(cw * 2), cy), v, font=f(FONT_R, FS), fill=c["FG"])
        cy += LH
    return img


def stats(tema):
    c, FS, LH, PADX, BARRA = TEMAS[tema], 17, 25, 26, 24
    cw = largura_char(FS)
    lab_w = max(len(k) for k, _ in STATS)
    lang_w = max(len(k) for k, _ in LANGS)
    linhas = 2 + len(STATS) + 2 + len(LANGS)
    W = int(PADX * 2 + max(len(HOST) + 14, lang_w + 3 + BARRA + 8) * cw)
    H = TB + 16 + LH * (linhas + 1) + 14
    img, d = moldura(W, H, c)
    y = TB + 16
    prompt(d, PADX, y, "gh profile --stats", FS, c, cw); y += LH * 2
    for k, v in STATS:
        d.text((PADX, y), k.ljust(lab_w), font=f(FONT_R, FS), fill=c["AZUL"])
        d.text((PADX + (lab_w + 2) * cw, y), v, font=f(FONT_B, FS), fill=c["FG"])
        y += LH
    y += LH
    for k, pct in LANGS:
        d.text((PADX, y), k.ljust(lang_w), font=f(FONT_R, FS), fill=c["AZUL"])
        bx = PADX + (lang_w + 2) * cw
        cheio = int(round(BARRA * pct / 100))
        d.text((bx, y), "█" * cheio, font=f(FONT_R, FS), fill=c["VERDE"])
        d.text((bx + cheio * cw, y), "░" * (BARRA - cheio), font=f(FONT_R, FS), fill=c["TRACK"])
        d.text((bx + (BARRA + 2) * cw, y), f"{pct}%", font=f(FONT_R, FS), fill=c["FG"])
        y += LH
    return img


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for nome, fn in (("banner", banner), ("neofetch", neofetch), ("stats", stats)):
        for tema in ("dark", "light"):
            sufixo = "" if tema == "dark" else "-light"
            caminho = os.path.join(OUT_DIR, f"{nome}{sufixo}.png")
            fn(tema).save(caminho, optimize=True)
            print(caminho)
