<<<<<<< HEAD
"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character

class Assassin(Character):
    """
    TODO: Implement class
    
    """
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        
        self.image = pygame.image.load('../../graphics/characters/assassin/down/assassin_south.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # Stats
        self.hp = 650
        self.max_hp = 650
        self.attack = 250
        self.defense = 30
        self.speed = 80
        self.first_attack = True

        self.import_player_assets()

    
    def special_ability(self):
        """Implements The Characters Special Ability"""
        if self.first_attack == True:
            self.attack *= 2
            self.first_attack = False
    

    @staticmethod
    def get_display_name():
         """Displays Character Name"""
         return "Assassin"
    
    @staticmethod
    def get_description():
        """Displays A Character Description"""
        return "A silent killer who thrives in shadows and chaos. Trained in stealth, speed, and precision, the Assassin strikes swiftly at vulnerable targets before vanishing into the crowd."
    
    @staticmethod
    def get_preview_image():
        """Returns Character Preview Image"""       
        return '../../graphics/characters/assassin/down/assassin_south.png'


class Knight(Character):
    """
    TODO: Implement class
    
    """
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        
        # TODO: Set character image
        self.image = pygame.image.load('../../graphics/characters/knight/down/knight_south.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # TODO: Set stats
        self.hp = 750
        self.max_hp = 750
        self.attack = 220
        self.defense = 45
        self.speed = 40

        self.import_player_assets()

    def special_ability(self):
        """Implements The Characters Special Ability"""
        if self.hp < self.max_hp / 2 and not self.buff_active:
            self.attack *= 1.1
            self.defense *= 1.1
            self.buff_active = True 
    
    @staticmethod
    def get_display_name():
        """Displays Character Name"""
        return "Knight"
    
    @staticmethod
    def get_description():
        """Displays A Character Description"""
        return "The Knight is the reliable frontline fighter, balanced in offense and defense. Not exceptional in any one area, but versatile and dependable."
    
    @staticmethod
    def get_preview_image():
        """Returns Character Preview Image"""
        return '../graphics/characters/knight/down/knight_south.png'
    

class Hospitaller(Character):
    """
    TODO: Implement class
    
    """
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        
        # TODO: Set character image
        self.image = pygame.image.load('../../graphics/characters/hospitaller/down/hospitaller_south.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # TODO: Set stats
        self.hp = 850
        self.max_hp = 850
        self.attack = 250
        self.defense = 50
        self.speed = 40

        self.import_player_assets()

    
    
    def special_ability(self):
        self.hp *= 1.3
    
    @staticmethod
    def get_display_name():
        return "Hospitaller"
    
    @staticmethod
    def get_description():
        return "Bound by sacred vows of service, the Hospitaller fights not for glory, but to defend the faithful and heal the suffering. Clad in heavy armor and guided by prayer, they stand as shields for the weak."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/hospitaller/down/hospitaller_south.png'
    
class Paladin(Character):
    """
    Paladin Class    
    """
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        
        # TODO: Set character image
        self.image = pygame.image.load('../../graphics/characters/paladin/down/paladin_south.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # TODO: Set stats
        self.hp = 800
        self.max_hp = 800
        self.attack = 300
        self.defense = 65
        self.speed = 25

        self.import_player_assets()
    
    def special_ability(self):
        # TODO: Implement special ability
        self.attack *= 1.5
        self.hp += 150
    
    @staticmethod
    def get_display_name():
        # TODO
        return "Paladin"
    
    @staticmethod
    def get_description():
        # TODO
        return "Holy warriors who embody faith and strength. Paladins are heavily armored, slow but devastating in combat, often leading charges or defending allies."
    
    @staticmethod
    def get_preview_image():
        # TODO
        return '../../graphics/characters/paladin/down/paladin_south.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character' and cls.__name__.startswith('Character'):
            character_classes.append(cls)
    return character_classes
||||||| 82bc39c
=======
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
>>>>>>> origin/main
