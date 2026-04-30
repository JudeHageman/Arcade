import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    """A single tile in the world map."""

    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        """Initialize a tile."""
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface

        # Objects are tall (2 tiles) — offset them upward so their base
        # sits on the correct tile.
        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)

        # Slightly inset hitbox makes movement feel tighter and more natural.
        self.hitbox = self.rect.inflate(0, -10)


class Tree(pygame.sprite.Sprite):
    """Tree hitbox with health and regeneration."""

    MAX_HEALTH = 1000000
    REGEN_TIME = 5.0  # seconds between full regenerations
    MESSAGE_DURATION = 2.0  # seconds to display message

    def __init__(self, pos, groups, shared_tree=None):
        """Initialize a tree with an invisible hitbox."""
        super().__init__(groups)
        # Invisible sprite - just for collision detection
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()

        # Reference to shared tree health
        self.shared_tree = shared_tree

        # If this is the main tree object, initialize health
        if shared_tree is None:
            self.health = self.MAX_HEALTH
            self.max_health = self.MAX_HEALTH
            self.last_healed_time = pygame.time.get_ticks()  # When tree last healed to full
            self.just_regenerated = False  # Flag to show message
            self.message_time = None  # When message was created
            self.regen_count = 0  # Increments each regen for network sync

    def take_damage(self, amount):
        """Damage the tree."""
        self.health = max(0, self.health - amount)

    def update(self):
        """Update regeneration - restore to full health every 10 seconds."""
        # Only main tree (shared_tree is None) has regeneration logic
        if self.shared_tree is not None:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed_since_heal = (current_time - self.last_healed_time) / 1000.0
        
        # Heal every 5 seconds if not at full health
        if self.health < self.max_health and elapsed_since_heal >= self.REGEN_TIME:
            self.health = self.MAX_HEALTH
            self.last_healed_time = current_time
            self.just_regenerated = True
            self.message_time = current_time
            self.regen_count += 1
