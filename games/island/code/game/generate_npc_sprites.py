"""
generate_npc_sprites.py - Create placeholder NPC sprites

Run this once to generate simple colored idle.png files so the game
runs immediately.  Replace each file with your own 64x64 pixel art
before submitting (Part 3).

Usage:
    python code/game/generate_npc_sprites.py
"""

import os

REPO_ROOT  = os.path.join(os.path.dirname(__file__), '..', '..')
NPC_DIR    = os.path.join(REPO_ROOT, 'graphics', 'npcs')
SIZE       = 64

# (folder_name, fill_color_RGB, label)
PLACEHOLDERS = [
    ("town_elder", (180, 140,  80), "Elder"),
    ("merchant",   ( 80, 160,  80), "Merch"),
    ("sage",       (140,  80, 200), "Sage"),
]


def make_placeholder(folder, color, label):
    path = os.path.join(NPC_DIR, folder)
    os.makedirs(path, exist_ok=True)
    img_path = os.path.join(path, "idle.png")

    if os.path.isfile(img_path):
        print(f"  Skipping {img_path}  (already exists)")
        return

    try:
        # Try with Pillow first
        from PIL import Image, ImageDraw, ImageFont
        img  = Image.new("RGBA", (SIZE, SIZE), (*color, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(255, 255, 255), width=3)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            font = ImageFont.load_default()
        draw.text((8, 24), label, fill=(255, 255, 255), font=font)
        img.save(img_path)
        print(f"  Created {img_path}")
    except ImportError:
        # Pillow not available — create a minimal 1x1 PNG (valid file, tiny)
        # This is a 64x64 solid-colour PNG encoded as raw bytes.
        _write_minimal_png(img_path, color)
        print(f"  Created {img_path}  (minimal PNG — install Pillow for coloured placeholder)")


def _write_minimal_png(path, color):
    """Write a minimal valid 1×1 PNG in the requested colour, scaled to 64×64 via pygame."""
    try:
        import pygame
        pygame.init()
        surf = pygame.Surface((SIZE, SIZE))
        surf.fill(color)
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 3)
        font = pygame.font.SysFont(None, 18)
        label_surf = font.render("NPC", True, (255, 255, 255))
        surf.blit(label_surf, (8, 24))
        pygame.image.save(surf, path)
        pygame.quit()
    except Exception as exc:
        print(f"    Could not create {path}: {exc}")
        print("    Install Pillow (pip install Pillow) or pygame to generate placeholders.")


if __name__ == "__main__":
    print("Generating NPC placeholder sprites...")
    for folder, color, label in PLACEHOLDERS:
        make_placeholder(folder, color, label)
    print("\nDone. Replace each idle.png with your own 64x64 art before submitting.")
