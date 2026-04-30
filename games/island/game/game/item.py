"""
item.py - Item class for inventory system

Defines items that can be collected and stored in inventory.
Features specialized classes for Weapons, Armor, Consumables, and Quest Items.

Author: Minju Seo
Date: 2026-04-21
Lab: Lab 6 - Sparse World Map (Island Gardener Edition)
"""

import pygame

class Item:
    """Base class for all items in Island Gardener."""
    
    def __init__(self, name, item_type, description, image_path, value=0, stackable=False, max_stack=1):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.image_path = image_path
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = 1
        
        # Load image
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
        except:
            # Fallback: Gray box with initials
            self.image = pygame.Surface((64, 64))
            self.image.fill((150, 150, 150))
            font = pygame.font.Font(None, 20)
            text = font.render(item_type[:3].upper(), True, (0, 0, 0))
            text_rect = text.get_rect(center=(32, 32))
            self.image.blit(text, text_rect)
    
    def __str__(self):
        if self.stackable and self.quantity > 1:
            return f"{self.name} x{self.quantity}"
        return self.name
    
    def __repr__(self):
        return f"Item(name='{self.name}', type='{self.item_type}', qty={self.quantity})"
    
    def use(self, character):
        print(f"Used {self.name}")
        return False

    def can_stack_with(self, other):
        return (self.stackable and 
                isinstance(other, Item) and
                self.name == other.name and
                self.item_type == other.item_type and
                self.quantity < self.max_stack)


class Weapon(Item):
    """Weapon items to purify the land more effectively."""
    def __init__(self, name, description, image_path, attack_bonus, value=0):
        super().__init__(name, "weapon", description, image_path, value, stackable=False)
        self.attack_bonus = attack_bonus
    
    def use(self, character):
        print(f"{character.character_name} equipped {self.name} (+{self.attack_bonus} purification power)")
        if hasattr(character, 'attack'):
            character.attack += self.attack_bonus
        return False


class Armor(Item):
    """Protective gear for cute animal characters."""
    def __init__(self, name, description, image_path, defense_bonus, value=0):
        super().__init__(name, "armor", description, image_path, value, stackable=False)
        self.defense_bonus = defense_bonus
    
    def use(self, character):
        print(f"{character.character_name} equipped {self.name} (+{self.defense_bonus} defense)")
        if hasattr(character, 'defense'):
            character.defense += self.defense_bonus
        return False


class Consumable(Item):
    """Potions and food that restore HP or give buffs."""
    def __init__(self, name, description, image_path, effect_type, effect_amount, value=0, max_stack=99):
        super().__init__(name, "consumable", description, image_path, value, stackable=True, max_stack=max_stack)
        self.effect_type = effect_type 
        self.effect_amount = effect_amount
    
    def use(self, character):
        if self.effect_type == "heal":
            if hasattr(character, 'hp'):
                character.hp = min(character.hp + self.effect_amount, character.max_hp)
                print(f"{character.character_name} ate {self.name} and healed {self.effect_amount} HP")
        elif self.effect_type == "speed":
            print(f"{character.character_name} used {self.name}! Speed buff +{self.effect_amount}")
        
        return True # Consumed after use


class QuestItem(Item):
    """Special items for Island Gardener story and land reclamation."""
    def __init__(self, name, description, image_path, quest_id=None):
        super().__init__(name, "quest", description, image_path, value=0, stackable=False)
        self.quest_id = quest_id
    
    def use(self, character):
        print(f"{self.name} is a special item: {self.description}")
        return False


# =============
# ISLAND GARDENER ITEMS
# =============

def create_example_items():
    """Returns a list of starting items for Island Gardener."""
    items = []

    # 1. Weapons
    items.append(Weapon("Polished Seashell Scepter", 
                        "A pearlescent shell that hums with the sound of the ocean.", 
                        "../../graphics/items/seashell_scepter.png", attack_bonus=12, value=150))
    
    items.append(Weapon("Thorny Vine Whip", 
                        "A flexible vine for striking rivals from a distance.", 
                        "../../graphics/items/vine_whip.png", attack_bonus=15, value=180))

    # 2. Armor
    items.append(Armor("Woven Grass Hula Skirt", 
                       "Hand-braided grass that smells like a summer meadow.", 
                       "../../graphics/items/grass_skirt.png", defense_bonus=8, value=90))
    
    items.append(Armor("Hollowed Coconut Helm", 
                       "A thick shell carved with a cute face.", 
                       "../../graphics/items/coconut_helm.png", defense_bonus=15, value=140))

    # 3. Consumables
    items.append(Consumable("Sun-Baked Sweet Potato", 
                            "A warm treat baked in the sand. Restores 40 HP.", 
                            "../../graphics/items/sweet_potato.png", effect_type="heal", effect_amount=40, value=30))
    
    items.append(Consumable("Sparkling Berry Juice", 
                            "A fizzy pink drink that gives a sugar rush.", 
                            "../../graphics/items/berry_juice.png", effect_type="speed", effect_amount=5, value=45))

    # 4. Quest/Special Items
    items.append(QuestItem("The Whispering Conch", 
                           "A shell that tells you where rare plants are hiding.", 
                           "../../graphics/items/whispering_conch.png", quest_id="NAV_01"))
    
    items.append(QuestItem("Rainbow Seed Pouch", 
                           "Glowing seeds used to claim and bloom a Plant Node.", 
                           "../../graphics/items/seed_pouch.png", quest_id="TERRITORY_01"))

    print(f"Successfully loaded {len(items)} items for Island Gardener.")
    return items


if __name__ == "__main__":
    # Quick Test
    pygame.init()
    pygame.display.set_mode((1, 1)) # Dummy display for image loading
    test_items = create_example_items()
    for i in test_items:
        print(f"Loaded: {i.name} ({i.item_type})")