#!/usr/bin/env python3
"""
Tesi Studio — Armador de Signature (6x3 grilla sobre pan de oro)

USO:
  1. Poné las 18 fotos de piezas individuales en la carpeta "piezas/"
     (las ordena alfabéticamente: fila 1 = primeras 6, fila 2 = siguientes 6, fila 3 = últimas 6)
  2. Corré: python3 armar-signature.py
  3. El resultado se guarda como "signature-composicion.png"

Las piezas se recortan al centro y se ponen sobre un fondo dorado con marco acrílico.
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import glob
import sys

# === CONFIGURACIÓN ===
COLS = 6
ROWS = 3
TOTAL_PIECES = COLS * ROWS  # 18

# Tamaño final del canvas (px) — proporcional a 180x90cm → ratio 2:1
CANVAS_W = 3600
CANVAS_H = 1800

# Marco acrílico (borde transparente alrededor)
FRAME_BORDER = 40  # px de marco acrílico
FRAME_COLOR = (240, 240, 240, 200)  # gris muy claro, semi-transparente

# Área interior (donde va el oro + piezas)
INNER_W = CANVAS_W - (FRAME_BORDER * 2)
INNER_H = CANVAS_H - (FRAME_BORDER * 2)

# Márgenes del oro al borde de las piezas
MARGIN_X = int(INNER_W * 0.06)  # margen lateral
MARGIN_Y = int(INNER_H * 0.08)  # margen superior/inferior
GAP_X = int(INNER_W * 0.04)     # espacio entre columnas
GAP_Y = int(INNER_H * 0.06)     # espacio entre filas

# Tamaño de cada pieza en la grilla
PIECE_W = (INNER_W - 2 * MARGIN_X - (COLS - 1) * GAP_X) // COLS
PIECE_H = (INNER_H - 2 * MARGIN_Y - (ROWS - 1) * GAP_Y) // ROWS

# Color del fondo de oro (base, antes de textura)
GOLD_BASE = (205, 175, 100)
GOLD_LIGHT = (235, 210, 140)
GOLD_DARK = (180, 150, 70)

# Carpeta de piezas
PIECES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piezas")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signature-composicion.png")
OUTPUT_WHITE_BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signature-producto-fondo-blanco.png")


def create_gold_background(w, h):
    """Crea un fondo dorado con textura tipo pan de oro."""
    import random
    random.seed(42)

    img = Image.new('RGB', (w, h), GOLD_BASE)
    draw = ImageDraw.Draw(img)

    # Variaciones de tono para simular hojas de oro
    block_size = w // 4
    for by in range(0, h, block_size):
        for bx in range(0, w, block_size):
            # Cada bloque tiene un tono ligeramente distinto (simula hojas individuales de oro)
            r_offset = random.randint(-15, 15)
            g_offset = random.randint(-12, 12)
            b_offset = random.randint(-8, 8)
            color = (
                max(0, min(255, GOLD_BASE[0] + r_offset)),
                max(0, min(255, GOLD_BASE[1] + g_offset)),
                max(0, min(255, GOLD_BASE[2] + b_offset))
            )
            draw.rectangle([bx, by, bx + block_size, by + block_size], fill=color)

            # Líneas de unión entre hojas de oro
            if bx > 0:
                line_color = (GOLD_DARK[0], GOLD_DARK[1], GOLD_DARK[2])
                draw.line([(bx, by), (bx, by + block_size)], fill=line_color, width=2)
            if by > 0:
                line_color = (GOLD_DARK[0], GOLD_DARK[1], GOLD_DARK[2])
                draw.line([(bx, by), (bx + block_size, by)], fill=line_color, width=2)

    # Reflejos sutiles
    for _ in range(30):
        rx = random.randint(0, w)
        ry = random.randint(0, h)
        rw = random.randint(50, 200)
        rh = random.randint(20, 60)
        highlight = Image.new('RGBA', (rw, rh), (*GOLD_LIGHT, 40))
        img.paste(Image.alpha_composite(
            img.crop((rx, ry, min(rx+rw, w), min(ry+rh, h))).convert('RGBA'),
            highlight.crop((0, 0, min(rw, w-rx), min(rh, h-ry)))
        ).convert('RGB'), (rx, ry))

    # Suavizar un poco
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    return img


def process_piece(img_path, target_w, target_h):
    """Carga una pieza, la recorta al centro y redimensiona."""
    img = Image.open(img_path).convert('RGBA')

    # Calcular crop centrado para mantener la proporción del target
    src_ratio = img.width / img.height
    tgt_ratio = target_w / target_h

    if src_ratio > tgt_ratio:
        # Imagen más ancha: recortar lados
        new_w = int(img.height * tgt_ratio)
        offset = (img.width - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img.height))
    else:
        # Imagen más alta: recortar arriba/abajo
        new_h = int(img.width / tgt_ratio)
        offset = (img.height - new_h) // 2
        img = img.crop((0, offset, img.width, offset + new_h))

    # Redimensionar
    img = img.resize((target_w, target_h), Image.LANCZOS)

    return img


def add_soft_shadow(canvas, x, y, w, h, offset=4, blur=6, opacity=60):
    """Agrega una sombra suave detrás de una pieza."""
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        [x + offset, y + offset, x + w + offset, y + h + offset],
        fill=(0, 0, 0, opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    canvas = Image.alpha_composite(canvas, shadow)
    return canvas


def main():
    # Buscar piezas
    if not os.path.exists(PIECES_DIR):
        os.makedirs(PIECES_DIR)
        print(f"\n📁 Creé la carpeta '{PIECES_DIR}'")
        print(f"   Poné ahí las 18 fotos de las piezas y volvé a correr el script.")
        print(f"   Se ordenan alfabéticamente: las primeras 6 = fila 1, etc.\n")
        sys.exit(0)

    extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.JPEG', '*.PNG']
    piece_files = []
    for ext in extensions:
        piece_files.extend(glob.glob(os.path.join(PIECES_DIR, ext)))
    piece_files.sort()

    if len(piece_files) == 0:
        print(f"\n❌ No encontré imágenes en '{PIECES_DIR}'")
        print(f"   Poné las 18 fotos ahí y volvé a correr.\n")
        sys.exit(1)

    if len(piece_files) < TOTAL_PIECES:
        print(f"\n⚠️  Encontré {len(piece_files)} piezas, necesito {TOTAL_PIECES}.")
        print(f"   Voy a repetir las que tengo para llenar la grilla.\n")
        while len(piece_files) < TOTAL_PIECES:
            piece_files.append(piece_files[len(piece_files) % len(piece_files)])

    piece_files = piece_files[:TOTAL_PIECES]

    print(f"\n🎨 Armando Signature con {TOTAL_PIECES} piezas...")
    print(f"   Canvas: {CANVAS_W}x{CANVAS_H}px")
    print(f"   Pieza: {PIECE_W}x{PIECE_H}px")
    print(f"   Grilla: {COLS}x{ROWS}\n")

    for i, f in enumerate(piece_files):
        row = i // COLS + 1
        col = i % COLS + 1
        print(f"   [{row},{col}] {os.path.basename(f)}")

    # 1. Crear fondo dorado
    print(f"\n✨ Creando fondo de pan de oro...")
    gold_bg = create_gold_background(INNER_W, INNER_H)

    # 2. Crear canvas con marco acrílico
    canvas = Image.new('RGBA', (CANVAS_W, CANVAS_H), (255, 255, 255, 0))

    # Marco acrílico (rectángulo semi-transparente)
    frame = Image.new('RGBA', (CANVAS_W, CANVAS_H), FRAME_COLOR)
    # Recortar interior del marco
    frame_draw = ImageDraw.Draw(frame)
    frame_draw.rectangle(
        [FRAME_BORDER, FRAME_BORDER, CANVAS_W - FRAME_BORDER, CANVAS_H - FRAME_BORDER],
        fill=(0, 0, 0, 0)
    )

    # Pegar fondo dorado
    canvas.paste(gold_bg, (FRAME_BORDER, FRAME_BORDER))

    # Convertir a RGBA para composición
    canvas = canvas.convert('RGBA')

    # 3. Colocar piezas
    print(f"🧵 Colocando piezas en la grilla...")
    for i, piece_path in enumerate(piece_files):
        row = i // COLS
        col = i % COLS

        x = FRAME_BORDER + MARGIN_X + col * (PIECE_W + GAP_X)
        y = FRAME_BORDER + MARGIN_Y + row * (PIECE_H + GAP_Y)

        # Sombra suave
        canvas = add_soft_shadow(canvas, x, y, PIECE_W, PIECE_H)

        # Pieza
        piece_img = process_piece(piece_path, PIECE_W, PIECE_H)
        canvas.paste(piece_img, (x, y), piece_img)

    # 4. Agregar marco acrílico encima
    canvas = Image.alpha_composite(canvas, frame)

    # 5. Guardar composición (fondo transparente para flexibilidad)
    canvas.save(OUTPUT_FILE, 'PNG', quality=95)
    print(f"\n✅ Guardado: {OUTPUT_FILE}")

    # 6. Versión con fondo blanco (para producto)
    white_bg = Image.new('RGBA', (CANVAS_W + 200, CANVAS_H + 200), (255, 255, 255, 255))
    # Sombra del marco completo
    shadow_full = Image.new('RGBA', white_bg.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_full)
    shadow_draw.rectangle(
        [100 + 6, 100 + 6, 100 + CANVAS_W + 6, 100 + CANVAS_H + 6],
        fill=(0, 0, 0, 40)
    )
    shadow_full = shadow_full.filter(ImageFilter.GaussianBlur(radius=10))
    white_bg = Image.alpha_composite(white_bg, shadow_full)
    white_bg.paste(canvas, (100, 100), canvas)
    white_bg.save(OUTPUT_WHITE_BG, 'PNG', quality=95)
    print(f"✅ Versión fondo blanco: {OUTPUT_WHITE_BG}")

    print(f"\n🎉 Listo! Usá 'signature-producto-fondo-blanco.png' para el Shot 4 (comedor).\n")


if __name__ == '__main__':
    main()
