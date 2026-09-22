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
    "        .--.        ",
    "       |o_o |       ",
    "       |:_/ |       ",
    "      //   \\ \\      ",
    "     (|     | )     ",
    "    /'\\_   _/`\\     ",
    "    \\___)=(___/     ",
]

# Mascote da janela de stats, no mesmo peso do pinguim que fica no banner.
STATS_ART = [
    "    /\\_/\\       ",
    "   ( o.o )      ",
    "    > ^ <       ",
    "   /|   |\\      ",
    "  (_|   |_)     ",
    "     | |        ",
    "    ~   ~       ",
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

S = 2     # renderiza em 2x; o README exibe com metade da largura (telas HiDPI)
TB = 36 * S   # altura da barra de titulo
FS = 17 * S   # corpo da fonte, unico para todas as janelas
LH = 25 * S   # entrelinha
PADX = 26 * S

def _dimensoes():
    """Caixa unica: todas as janelas usam a maior largura e altura necessarias,
    para ficarem simetricas lado a lado na pagina."""
    cw = largura_char(FS)
    art_w = max(len(l) for l in NEOFETCH_ART)
    lab_w = max(len(k) for k, _ in NEOFETCH_CAMPOS)
    val_w = max(len(v) for _, v in NEOFETCH_CAMPOS)
    largura_neofetch = art_w + 3 + lab_w + 2 + val_w
    largura_stats = max(len(k) for k, _ in STATS) + 2 + 12
    largura_langs = max(len(k) for k, _ in LANGS) + 2 + 24 + 8
    cols = max(largura_neofetch, largura_stats, largura_langs, len(HOST) + 22)
    linhas = max(2 + max(len(NEOFETCH_ART), len(NEOFETCH_CAMPOS) + 2),
                 2 + len(STATS) + 1 + len(LANGS))
    return int(PADX * 2 + cols * cw), TB + 16 * S + LH * linhas + 20 * S, cw



def moldura(W, H, c):
    """Janela de terminal: barra de titulo, botoes e borda."""
    img = Image.new("RGB", (W, H), c["BG"])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], 8 * S, fill=c["BG"], outline=c["BORDER"], width=S)
    d.rounded_rectangle([0, 0, W - 1, TB], 8 * S, fill=c["WIN"])
    d.rectangle([0, TB - 8 * S, W - 1, TB], fill=c["WIN"])
    d.line([(0, TB), (W - 1, TB)], fill=c["BORDER"], width=S)
    for i, cor in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([16 * S + i * 20 * S, 12 * S, 27 * S + i * 20 * S, 23 * S], fill=cor)
    t = f"{HOST}: ~"
    d.text(((W - d.textlength(t, font=f(FONT_R, 14 * S))) / 2, 11 * S), t, font=f(FONT_R, 14 * S), fill=c["DIM"])
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


W_BOX, H_BOX, CW = _dimensoes()


def banner(tema):
    """Janela principal: arte do nome a esquerda, campos a direita (estilo neofetch)."""
    c = TEMAS[tema]
    art_w = int(max(len(l) for l in NEOFETCH_ART) * CW)
    lab_w = int(max(len(k) for k, _ in NEOFETCH_CAMPOS) * CW)
    img, d = moldura(W_BOX, H_BOX, c)
    y = TB + 16 * S
    prompt(d, PADX, y, "neofetch", FS, c, CW)
    y += LH * 2
    ay = y
    for l in NEOFETCH_ART:
        d.text((PADX, ay), l, font=f(FONT_R, FS), fill=c["VERDE"]); ay += LH
    cx, cy = PADX + art_w + int(CW * 3), y
    d.text((cx, cy), "felipe", font=f(FONT_B, FS), fill=c["VERDE"])
    d.text((cx + CW * 6, cy), "@", font=f(FONT_R, FS), fill=c["FG"])
    d.text((cx + CW * 7, cy), "felipe-sauer", font=f(FONT_B, FS), fill=c["AZUL"])
    cy += LH
    d.text((cx, cy), "-" * 34, font=f(FONT_R, FS), fill=c["DIM"]); cy += LH
    for k, v in NEOFETCH_CAMPOS:
        if k:
            d.text((cx, cy), f"{k}:", font=f(FONT_B, FS), fill=c["AZUL"])
            d.text((cx + lab_w + int(CW * 2), cy), v, font=f(FONT_R, FS), fill=c["FG"])
        cy += LH
    return img


def stats(tema):
    c, BARRA, cw = TEMAS[tema], 24, CW
    lab_w = max(len(k) for k, _ in STATS)
    lang_w = max(len(k) for k, _ in LANGS)
    img, d = moldura(W_BOX, H_BOX, c)
    y = TB + 16 * S
    prompt(d, PADX, y, "gh profile --stats", FS, c, cw); y += LH * 2

    # mascote encostado a direita, espelhando o pinguim que fica a esquerda no banner
    ax = W_BOX - PADX - int(max(len(l) for l in STATS_ART) * cw) - int(cw * 2)
    ay = y
    for l in STATS_ART:
        d.text((ax, ay), l, font=f(FONT_R, FS), fill=c["VERDE"])
        ay += LH

    for k, v in STATS:
        d.text((PADX, y), k.ljust(lab_w), font=f(FONT_R, FS), fill=c["AZUL"])
        d.text((PADX + (lab_w + 2) * cw, y), v, font=f(FONT_B, FS), fill=c["FG"])
        y += LH
    y += LH
    for k, pct in LANGS:
        d.text((PADX, y), k.ljust(lang_w), font=f(FONT_R, FS), fill=c["AZUL"])
        # barras desenhadas, nao escritas com "█": o bloco deixa emendas visiveis
        bx = int(PADX + (lang_w + 2) * cw)
        trilho = int(BARRA * cw)
        altura = int(LH * 0.58)
        topo = int(y + (LH - altura) / 2)
        raio = max(2, int(2 * S))
        d.rounded_rectangle([bx, topo, bx + trilho, topo + altura], raio, fill=c["TRACK"])
        cheio = int(trilho * pct / 100)
        if cheio > raio * 2:
            d.rounded_rectangle([bx, topo, bx + cheio, topo + altura], raio, fill=c["VERDE"])
        elif cheio > 0:
            d.rectangle([bx, topo, bx + cheio, topo + altura], fill=c["VERDE"])
        d.text((bx + trilho + int(cw * 2), y), f"{pct}%", font=f(FONT_R, FS), fill=c["FG"])
        y += LH
    return img


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for nome, fn in (("banner", banner), ("stats", stats)):
        for tema in ("dark", "light"):
            sufixo = "" if tema == "dark" else "-light"
            caminho = os.path.join(OUT_DIR, f"{nome}{sufixo}.png")
            fn(tema).save(caminho, optimize=True)
            print(caminho)
