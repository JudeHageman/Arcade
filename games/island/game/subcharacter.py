
# 최신버전
import pygame
from character import Character 

# ==========================================
# 1. Gardening Sheep
# ==========================================
class GardeningSheep(Character):
    def __init__(self, pos, groups, obstacle_sprites, is_local=False, player_id=None):
        super().__init__(
    pos=pos, 
    groups=groups, 
    obstacle_sprites=obstacle_sprites, 
    player_id=player_id, 
    is_local=is_local
)
        self.character_name = "sheep" 
        self.hp = 110; self.max_hp = 110; self.attack = 10; self.defense = 12; self.speed = 15
        self.import_player_assets() 

    def import_player_assets(self):
        path = '../graphics/characters/sheep.png' 
        try:
            # Load original high-res image
            original_surf = pygame.image.load(path).convert_alpha()
            # Scale down to standard tile size (64x64)
            surface = pygame.transform.scale(original_surf, (64, 64))
            
            self.image = surface
            self.rect = self.image.get_rect(center=self.hitbox.center)
            self.animations = {
                'up': [surface], 'down': [surface], 'left': [surface], 'right': [surface],
                'up_idle': [surface], 'down_idle': [surface], 'left_idle': [surface], 'right_idle': [surface]
            }
        except Exception as e:
            print(f"Failed to load image at {path}: {e}")
            self.image = pygame.Surface((64, 64)); self.image.fill('red')
            self.animations = {'down': [self.image]}

    def special_ability(self):
        self.speed += 5
        return "Speed Boosted"
    
    @staticmethod
    def get_display_name(): return "Gardening Sheep"
    @staticmethod
    def get_description(): return "A fluffy support character. Ability: Bloom Walk"
    @staticmethod
    def get_preview_image(): return '../graphics/characters/sheep.png'


# ==========================================
# 2. Beach Digger Rabbit
# ==========================================
class BeachDiggerRabbit(Character):
    def __init__(self, pos, groups, obstacle_sprites, is_local=False, player_id=None):
        super().__init__(
            pos=pos, 
            groups=groups, 
            obstacle_sprites=obstacle_sprites, 
            player_id=player_id, 
            is_local=is_local
        )      
        self.character_name = "rabbit" 
        self.hp = 90; self.max_hp = 90; self.attack = 14; self.defense = 8; self.speed = 22
        self.import_player_assets()

    def import_player_assets(self):
        path = '../graphics/characters/rabbit.png'
        try:
            original_surf = pygame.image.load(path).convert_alpha()
            surface = pygame.transform.scale(original_surf, (64, 64))
            
            self.image = surface
            self.rect = self.image.get_rect(center=self.hitbox.center)
            self.animations = {
                'up': [surface], 'down': [surface], 'left': [surface], 'right': [surface],
                'up_idle': [surface], 'down_idle': [surface], 'left_idle': [surface], 'right_idle': [surface]
            }
        except:
            self.image = pygame.Surface((64, 64)); self.image.fill('blue')

    def special_ability(self):
        self.defense += 10
        return "Burrowed"
    
    @staticmethod
    def get_display_name(): return "Beach-Digger Rabbit"
    @staticmethod
    def get_description(): return "High-speed scout. Ability: Quick Burrow"
    @staticmethod
    def get_preview_image(): return '../graphics/characters/rabbit.png'


# ==========================================
# 3. Fruit Basket Panda
# ==========================================
class FruitBasketPanda(Character):
    def __init__(self, pos, groups, obstacle_sprites, is_local=False, player_id=None):
        super().__init__(
            pos=pos, 
            groups=groups, 
            obstacle_sprites=obstacle_sprites, 
            player_id=player_id, 
            is_local=is_local
        )  
        self.character_name = "panda" 
        self.hp = 140; self.max_hp = 140; self.attack = 12; self.defense = 15; self.speed = 10
        self.import_player_assets()

    def import_player_assets(self):
        path = '../graphics/characters/panda.png'
        try:
            original_surf = pygame.image.load(path).convert_alpha()
            surface = pygame.transform.scale(original_surf, (64, 64))
            
            self.image = surface
            self.rect = self.image.get_rect(center=self.hitbox.center)
            self.animations = {
                'up': [surface], 'down': [surface], 'left': [surface], 'right': [surface],
                'up_idle': [surface], 'down_idle': [surface], 'left_idle': [surface], 'right_idle': [surface]
            }
        except:
            self.image = pygame.Surface((64, 64)); self.image.fill('green')

    def special_ability(self):
        self.hp = min(self.hp + 20, self.max_hp)
        return "Healed"
    
    @staticmethod
    def get_display_name(): return "Fruit-Basket Panda"
    @staticmethod
    def get_description(): return "Sturdy healer. Ability: Mango Toss"
    @staticmethod
    def get_preview_image(): return '../graphics/characters/panda.png'


# ==========================================
# 4. Sand Castle Puppy
# ==========================================
class SandCastlePuppy(Character):
    def __init__(self, pos, groups, obstacle_sprites, is_local=False, player_id=None):
        super().__init__(
            pos=pos, 
            groups=groups, 
            obstacle_sprites=obstacle_sprites, 
            player_id=player_id, 
            is_local=is_local
        )
        self.character_name = "puppy" 
        self.hp = 130; self.max_hp = 130; self.attack = 15; self.defense = 18; self.speed = 12
        self.import_player_assets()

    def import_player_assets(self):
        path = '../graphics/characters/puppy.png'
        try:
            original_surf = pygame.image.load(path).convert_alpha()
            surface = pygame.transform.scale(original_surf, (64, 64))
            
            self.image = surface
            self.rect = self.image.get_rect(center=self.hitbox.center)
            self.animations = {
                'up': [surface], 'down': [surface], 'left': [surface], 'right': [surface],
                'up_idle': [surface], 'down_idle': [surface], 'left_idle': [surface], 'right_idle': [surface]
            }
        except:
            self.image = pygame.Surface((64, 64)); self.image.fill('yellow')

    def special_ability(self):
        self.defense += 20
        return "Shielded"
    
    @staticmethod
    def get_display_name(): return "Sand-Castle Puppy"
    @staticmethod
    def get_description(): return "Defensive tank. Ability: Sand Shield"
    @staticmethod
    def get_preview_image(): return '../graphics/characters/puppy.png'


# ==========================================
# Function for Level class to retrieve all classes
# ==========================================
def get_all_character_classes():
    return [
        GardeningSheep, 
        BeachDiggerRabbit, 
        FruitBasketPanda, 
        SandCastlePuppy
    ]

# Add these aliases at the bottom of subcharacter.py 
# to let level.py find them using the old names.
Character1 = GardeningSheep
Character2 = BeachDiggerRabbit
Character3 = FruitBasketPanda
Character4 = SandCastlePuppy