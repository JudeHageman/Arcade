"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character

class Attacker(Character):
    """High damage, moderate defense, moderate speed"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Attacker"
        self.hp = 100
        self.max_hp = 100
        self.attack = 25
        self.defense = 15
        self.speed = 15
        self.consecutive_hits = 0
        
        try:
            self.image = pygame.image.load('../graphics/characters/thief/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            try:
                self.import_player_assets(animate=True)
            except:
                pass
    
    def special_ability(self):
        damage_multiplier = 1 + (0.5 * self.consecutive_hits)
        return int(self.attack * damage_multiplier)
    
    @staticmethod
    def get_display_name():
        return "Attacker"
    
    @staticmethod
    def get_description():
        return "A high damage character with a chained attack ability that cannot heal or repair light."
    
    @staticmethod
    def get_preview_image():
        return '../graphics/characters/attacker.png'


class Defender(Character):
    """High defense, low damage, low speed"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Defender"
        self.hp = 100
        self.max_hp = 100
        self.attack = 5
        self.defense = 25
        self.speed = 5
        self.shield_cooldown = 0
        
        try:
            self.image = pygame.image.load('../graphics/characters/cleric/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            try:
                self.import_player_assets(animate=True)
            except:
                pass

    def special_ability(self):
        defense_boost = int(self.defense + (0.5 * self.shield_cooldown))
        return defense_boost
    
    @staticmethod
    def get_display_name():
        return "Defender"
    
    @staticmethod
    def get_description():
        return "A high defense character with a shield ability that cannot heal or repair light."
    
    @staticmethod
    def get_preview_image():
        return '../graphics/characters/defender.png'


class Healer(Character):
    """Low damage, low defense, moderate speed"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Healer"
        self.hp = 100
        self.max_hp = 100
        self.attack = 5
        self.defense = 5
        self.speed = 15
        self.stationary_time = 0
        
        try:
            self.image = pygame.image.load('../graphics/characters/wizard/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            try:
                self.import_player_assets(animate=True)
            except:
                pass

    def special_ability(self):
        heal_amount = 15 + (5 * self.stationary_time)
        return heal_amount
    
    @staticmethod
    def get_display_name():
        return "Healer"
    
    @staticmethod
    def get_description():
        return "A healing character with a heal ability that cannot repair light."
    
    @staticmethod
    def get_preview_image():
        return '../graphics/characters/healer.png'


class Repairer(Character):
    """Low damage, low defense, high speed"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Repairer"
        self.hp = 100
        self.max_hp = 100
        self.attack = 5
        self.defense = 5
        self.speed = 25
        self.recent_repairs = 0
        
        try:
            self.image = pygame.image.load('../graphics/characters/hobbit/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            try:
                self.import_player_assets(animate=True)
            except:
                pass
    
    def special_ability(self):
        repair_amount = max(10, 30 - (2 * self.recent_repairs))
        return repair_amount
    
    @staticmethod
    def get_display_name():
        return "Repairer"
    
    @staticmethod
    def get_description():
        return "A utility character with a repair ability that cannot heal themself."
    
    @staticmethod
    def get_preview_image():
        return '../graphics/characters/repairer.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)
    return character_classes
