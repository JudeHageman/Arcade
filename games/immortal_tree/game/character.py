import pygame
from settings import *
from support import _resolve_asset_path

class Character(pygame.sprite.Sprite):
    """Single playable Character class with networking support."""

    SPRITE_SIZE = (128, 128)
    
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True, team='blue'):
        super().__init__(groups)
        
        # Team assignment
        self.team = team
        
        # Basic sprite setup
        self.character_name = "character"
        self.image = self._load_base_sprite()

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()

        # Character identity and movement

        # Graphics setup
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animations = self._build_static_animations()

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 16
        self.obstacle_sprites = obstacle_sprites
        
        # Attack
        self.is_attacking = False
        self.attack_damage = 25
        self.last_attack_time = 0
        self.attack_cooldown = 0.2  # seconds
        
        # Network properties (from project-01)
        self.player_id = player_id
        self.is_local = is_local
        self.name = ""
        self.other_players = []
        
        # For smooth network interpolation (remote players only)
        if not is_local:
            self.target_x = pos[0]
            self.target_y = pos[1]
            self.interpolation_speed = 0.3

    def _load_base_sprite(self):
        """Load the team-specific sprite and scale it to the game size."""
        # Use team-specific sprite (blue.png, pink.png, or green.png)
        sprite_filename = f'{self.team}.png'
        sprite_path = _resolve_asset_path(f'../graphics/characters/{sprite_filename}')

        try:
            image = pygame.image.load(sprite_path).convert_alpha()
            return pygame.transform.smoothscale(image, self.SPRITE_SIZE)
        except Exception as e:
            print(f"Failed to load {sprite_filename}: {e}")
            fallback = pygame.Surface(self.SPRITE_SIZE, pygame.SRCALPHA)
            fallback.fill((255, 0, 255))
            return fallback

    def _build_static_animations(self):
        """Use the base sprite for every direction when the character is static."""
        animations = {}
        for direction in ['up', 'down', 'left', 'right']:
            frame = self.image.copy()
            animations[direction] = [frame]
            animations[f'{direction}_idle'] = [frame.copy()]
        return animations

    def input(self):
        """Handle input - only for local player"""
        if not self.is_local:
            return

        keys = pygame.key.get_pressed()

        # Movement input
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

        # Attack input
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                self.last_attack_time = current_time
            else:
                self.is_attacking = False
        else:
            self.is_attacking = False

    def get_status(self):
        """Update animation status"""
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status:
                self.status = self.status + '_idle'
    
    def move(self, speed):
        """Move the character"""
        if self.is_local:
            # Local player: physics-based movement
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')
            
            self.rect.center = self.hitbox.center
        else:
            # Remote players: smooth interpolation
            self.interpolate_to_target()
    
    def set_position(self, x, y):
        """Set position (network update)"""
        if self.is_local:
            self.rect.x = x
            self.rect.y = y
            self.hitbox.center = self.rect.center
        else:
            self.target_x = x
            self.target_y = y
    
    def interpolate_to_target(self):
        """Smoothly move towards target position"""
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        
        self.rect.x += dx * self.interpolation_speed
        self.rect.y += dy * self.interpolation_speed
        self.hitbox.center = self.rect.center
    
    def collision(self, direction):
        """Handle collision with obstacles (not with other players)"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                # Check if sprite has hitbox attribute
                sprite_box = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
                if sprite_box.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite_box.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite_box.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                sprite_box = sprite.hitbox if hasattr(sprite, 'hitbox') else sprite.rect
                if sprite_box.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite_box.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite_box.bottom
    
    def animate(self):
        """Animate the character"""
        if self.animations is None:
            return
            
        # Get current animation
        anim_key = self.status.replace("_idle", "").replace("_attack", "")
        if anim_key not in self.animations:
            anim_key = 'down'
        
        animation = self.animations[anim_key]
        
        # Safety check: if animation list is empty, skip
        if not animation or len(animation) == 0:
            return

        # Loop over the frame index 
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
        pass

    def update(self):
        """Update character state"""
        self.input()
        self.get_status()
        if self.animations:
            self.animate()
        self.move(self.speed)

    def special_ability(self):
        """Special ability - override in subclasses"""
        pass