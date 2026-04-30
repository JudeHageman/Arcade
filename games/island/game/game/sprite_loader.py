"""
sprite_loader.py - Unified sprite loading system for characters and NPCs

Handles two sprite organization patterns:
1. Animated: graphics/characters/wizard/down/0.png, down/1.png, etc.
2. Static: graphics/characters/wizard.png (single image for all directions)

Author: [System - Lab 5]
Date: 2026-04-02
"""

import pygame
import os
import re

class SpriteLoader:
    """Handles sprite loading for both characters and NPCs with flexible organization."""
    
    @staticmethod
    def load_character_sprites(character_name, base_path="../../graphics/characters"):
        """
        Load sprites for a character.
        """
        return SpriteLoader._load_sprites(character_name, base_path, is_character=True)
    
    @staticmethod
    def load_enemy_sprites(enemy_name, base_path="../../graphics/enemies"):
        """
        Load sprites for an enemy.  
        """
        return SpriteLoader._load_sprites(enemy_name, base_path, is_character=False)

    @staticmethod
    def load_npc_sprites(npc_name, base_path="../../graphics/npcs"):
        """Deprecated: use load_enemy_sprites instead."""
        return SpriteLoader._load_sprites(npc_name, base_path, is_character=False)
    
    @staticmethod
    def _load_sprites(name, base_path, is_character=True):
        """
        Internal method to load sprites with flexible organization.
        """
        animations = {}
        statuses = ['up', 'down', 'left', 'right', 'up_idle', 'down_idle', 'left_idle', 'right_idle']
        
        character_dir = os.path.join(base_path, name)
        
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            animations = SpriteLoader._load_animated_sprites(character_dir, statuses)
        else:
             
            name_lower = name.lower()
            possible_filenames = [
                f"{name}.png", 
                f"{name_lower}.png", 
                f"{name.replace(' ', '_')}.png",
                f"{name_lower.replace(' ', '_')}.png"
            ]
            
            static_path = None
            for filename in possible_filenames:
                temp_path = os.path.join(base_path, filename)
                if os.path.exists(temp_path):
                    static_path = temp_path
                    break
            
            if static_path:
                animations = SpriteLoader._load_static_sprite(static_path, statuses)
            else:
                 
                animations = SpriteLoader._create_default_sprites(name, statuses, is_character)
        
        return animations
    
    @staticmethod
    def _load_animated_sprites(character_dir, statuses):
        """Load animated sprites from subdirectory structure."""
        animations = {}
        for status in statuses:
            animations[status] = []
            direction = status.replace('_idle', '')
            sprite_dir = os.path.join(character_dir, direction)
            
            if os.path.exists(sprite_dir) and os.path.isdir(sprite_dir):
                try:
                    all_files = os.listdir(sprite_dir)
                    png_files = [f for f in all_files if f.lower().endswith('.png')]
                    png_files.sort(key=SpriteLoader._extract_number)
                    
                    for png_file in png_files:
                        image_path = os.path.join(sprite_dir, png_file)
                        image = pygame.image.load(image_path).convert_alpha()
                        animations[status].append(image)
                except:
                    pass
            
            if not animations[status]:
                animations[status] = [SpriteLoader._create_single_default_sprite(direction)]
        return animations
    
    @staticmethod
    def _load_static_sprite(image_path, statuses):
        """Load single static sprite for all statuses."""
        animations = {}
        try:
            static_image = pygame.image.load(image_path).convert_alpha()
            static_image = pygame.transform.scale(static_image, (64, 64))
            for status in statuses:
                animations[status] = [static_image.copy()]
        except:
            for status in statuses:
                animations[status] = [SpriteLoader._create_single_default_sprite('down')]
        return animations
    
    @staticmethod
    def _create_default_sprites(name, statuses, is_character=True):
        """Create default sprites when images are missing."""
        animations = {}
        default_color = (128, 128, 128)
        for status in statuses:
            direction = status.replace('_idle', '') if '_idle' in status else status
            sprite = SpriteLoader._create_single_default_sprite(direction, default_color)
            animations[status] = [sprite]
        return animations
    
    @staticmethod
    def _create_single_default_sprite(direction, color=(128, 128, 128)):
        """Create a single default sprite with directional indicator."""
        sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
        sprite.fill(color)
        pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)
        return sprite
    
    @staticmethod
    def _extract_number(filename):
        """Extract number from filename for sorting."""
        nums = re.findall(r'\d+', filename)
        return int(nums[0]) if nums else 0

    @staticmethod
    def get_sprite_info(name, base_path):
        """Get information about available sprites for debugging."""
        character_dir = os.path.join(base_path, name)
        static_path = os.path.join(base_path, f"{name}.png")
        
        info = {'name': name, 'type': 'none', 'directories': [], 'files': []}
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            info['type'] = 'animated'
        elif os.path.exists(static_path):
            info['type'] = 'static'
        else:
            info['type'] = 'default'
        return info