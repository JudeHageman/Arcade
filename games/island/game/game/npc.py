"""
npc.py - Non-Player Character sprite

This file is PROVIDED. Do not modify it.

NPCs stand in the world and the player can approach them to start a
conversation (press T when nearby).  Each NPC carries a DialogGraph.
"""

import os
import pygame

INTERACT_RADIUS = 150   # pixels — how close the player must be to see the hint


class NPC(pygame.sprite.Sprite):
    """
    A stationary NPC that the player can talk to.

    Parameters
    ----------
    name         : Display name shown at the top of the dialog box.
    grid_x       : Tile column where the NPC stands.
    grid_y       : Tile row where the NPC stands.
    dialog_graph : DialogGraph instance (from dialog_graph.py).
    sprite_name  : Name of the subfolder under graphics/npcs/.
                   Must contain idle.png (or any .png as a fallback).
    groups       : Pygame sprite groups to join.
    """

    def __init__(self, name, grid_x, grid_y, dialog_graph,
                 sprite_name, *groups):
        super().__init__(*groups)

        self.name         = name
        self.dialog_graph = dialog_graph
        self.sprite_name  = sprite_name

        self.image = self._load_image(sprite_name)
        self.rect  = self.image.get_rect(topleft=(grid_x * 64, grid_y * 64))
        self.hitbox = self.rect.inflate(-10, -10)

        self._hint_font = pygame.font.Font(None, 22)
        self._name_font = pygame.font.Font(None, 20)

    # ------------------------------------------------------------------

    def _load_image(self, sprite_name):
        base = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'graphics', 'npcs', sprite_name
        )
        for candidate in ['idle.png', 'npc.png']:
            path = os.path.join(base, candidate)
            if os.path.isfile(path):
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(surf, (64, 64))
                except Exception:
                    pass

        # Fallback: colored rectangle with name label
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        surf.fill((100, 190, 255, 220))
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 3)
        label = pygame.font.Font(None, 16).render(sprite_name[:10], True, (0, 0, 0))
        surf.blit(label, (4, 26))
        return surf

    # ------------------------------------------------------------------

    def is_nearby(self, player_rect):
        """Return True if the player centre is within INTERACT_RADIUS."""
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        return (dx * dx + dy * dy) ** 0.5 < INTERACT_RADIUS

    def draw_hint(self, surface, camera_offset):
        """Draw '[T] Talk' above the NPC when the player is nearby."""
        sx = self.rect.centerx - camera_offset[0]
        sy = self.rect.top     - camera_offset[1] - 24

        hint = self._hint_font.render("[T] Talk", True, (255, 255, 180))
        surface.blit(hint, hint.get_rect(center=(sx, sy)))

        name_surf = self._name_font.render(self.name, True, (200, 230, 255))
        surface.blit(name_surf, name_surf.get_rect(center=(sx, sy - 18)))

    def update(self):
        pass   # stationary; extend here if you want idle animations
