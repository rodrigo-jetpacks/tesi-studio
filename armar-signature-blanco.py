#!/usr/bin/env python3
"""
Tesi Studio — Signature sobre fondo blanco limpio (6x3 grilla)
"""

from PIL import Image, ImageDraw, ImageFilter
import os, glob, sys

COLS = 6
ROWS = 3
TOTAL = COLS * ROWS

# Canvas grande, fondo blanco puro
CANVAS_W = 4200
CANVAS_H = 2200

# Márgenes y espaciado
MARGIN_X = 120
MARGIN_Y = 120
GAP = 40

# Tamaño de cada celda
CELL_W = (CANVAS_W - 2 * MARGIN_X - (COLS - 1) * GAP) // COLS
CELL_H = (CANVAS_H - 2 * MARGIN_Y - (ROWS - 1) * GAP) // ROWS

PIECES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piezas")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signature-fondo-blanco.png")


def process_piece(path, tw, th):
    img = Image.open(path).convert('RGBA')
    sr = img.width / img.height
    tr = tw / th
    if sr > tr:
        nw = int(img.height * tr)
        off = (img.width - nw) // 2
        img = img.crop((off, 0, off + nw, img.height))
    else:
        nh = int(img.width / tr)
        off = (img.height - nh) // 2
        img = img.crop((0, off, img.width, off + nh))
    img = img.resize((tw, th), Image.LANCZOS)
    return img


def main():
    exts = ['*.jpg','*.jpeg','*.png','*.webp','*.JPG','*.JPEG','*.PNG']
    files = []
    for e in exts:
        files.extend(glob.glob(os.path.join(PIECES_DIR, e)))
    files.sort()

    if len(files) < TOTAL:
        print(f"Necesito {TOTAL} piezas, encontré {len(files)}")
        while len(files) < TOTAL:
            files.append(files[len(files) % len(files)])
    files = files[:TOTAL]

    print(f"Armando grilla {COLS}x{ROWS} sobre fondo blanco...")

    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (255, 255, 255, 255))

    for i, f in enumerate(files):
        row = i // COLS
        col = i % COLS
        x = MARGIN_X + col * (CELL_W + GAP)
        y = MARGIN_Y + row * (CELL_H + GAP)

        # Sombra suave
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle([x+3, y+3, x+CELL_W+3, y+CELL_H+3], fill=(0, 0, 0, 35))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
        canvas = Image.alpha_composite(canvas, shadow)

        # Pieza
        piece = process_piece(f, CELL_W, CELL_H)
        canvas.paste(piece, (x, y), piece)

        r, c = row+1, col+1
        print(f"  [{r},{c}] {os.path.basename(f)}")

    canvas.save(OUTPUT, 'PNG', quality=95)
    print(f"\n✅ Guardado: {OUTPUT}")


if __name__ == '__main__':
    main()
