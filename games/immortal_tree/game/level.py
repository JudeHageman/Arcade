import pygame
from settings import *
from tile import Tile, Tree
from character import Character
from network_client import NetworkClient

class Level:
    def __init__(self, player_name, team, server_host='localhost', server_port=8080, serializer='text'):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()
        
        # Team assignment
        self.team = team

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()

        # Tree health display - initialize BEFORE create_map
        self.target_tree = None  # Currently targeted tree for health bar
        self.main_tree = None  # The shared tree health object

        # Score tracking - all scores start fresh
        self.individual_score = 0
        self.team_scores = {'blue': 0, 'pink': 0, 'green': 0, 'default': 0}
        self.is_combo_active = False  # Flag for combo state
        self.last_attack_time = 0  # Track when player last attacked
        
        # Global 1-second window system for team score - now per team
        self.game_start_time = pygame.time.get_ticks()
        self.current_window_attacks = {'blue': {}, 'pink': {}, 'green': {}, 'default': {}}  # team -> {player_id -> attack count}
        self.last_window_checked = -1  # Track which window we last processed
        self.last_window_team_total = 0  # Total attacks counted in current window for team score
        self.combo_established_this_window = False  # True once 2+ players detected in window
        self.remote_attack_times = {}  # player_id -> last time their attack was counted (for debounce)

        # Sprite setup
        self.create_map()

        # Network setup with serializer
        self.network = NetworkClient(player_name, server_host, server_port, serializer)
        self.connected = self.network.connect()

        # Track other players
        self.other_players = {}  # player_id -> Character sprite

        # Font for displaying names
        self.font = pygame.font.Font(None, 24)

        # Connection status
        self.connection_status = "Connecting..."

    def create_map(self):
        """Create the game map and player"""
        from support import import_csv_to_sparse
        
        # Create a shared tree object for all tree blocks
        self.main_tree = Tree((0, 0), [])
        
        layouts = {
            'boundary': import_csv_to_sparse('map/map_FloorBlocks.csv'),
            'object': import_csv_to_sparse('map/map_Objects.csv'),
            'tree': import_csv_to_sparse('map/map_TreeHitbox.csv')
        }
        
        for style, layout in layouts.items():
            if type(layout) == dict or hasattr(layout, 'items'):
                for key_val in layout.items():
                    (row, col), val = key_val
                    x = col * TILESIZE
                    y = row * TILESIZE
                    
                    if style == 'boundary':
                        Tile((x, y), [self.obstacle_sprites], 'boundary')
                    elif style == 'object':
                        Tile((x, y), [self.obstacle_sprites], 'object')
                    elif style == 'tree':
                        tree_block = Tree((x, y), [self.tree_sprites], shared_tree=self.main_tree)

        player_spawned = False
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                if col == 'p':
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE
                    self.player = Character(
                        (x, y), [self.visible_sprites], self.obstacle_sprites, is_local=True, team=self.team
                    )
                    player_spawned = True
        
        if player_spawned == False:
            self.player = Character(
                (5 * TILESIZE, 5 * TILESIZE), [self.visible_sprites], self.obstacle_sprites, is_local=True, team=self.team
            )

    def update_network(self):
        """Handle network synchronization"""
        if not self.connected:
            self.connection_status = "Disconnected"
            return

        # Send our position, character type, status, and scores to server
        character_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        tree_health = self.main_tree.health if self.main_tree else -1
        tree_regen_count = self.main_tree.regen_count if self.main_tree else 0
        self.network.send_update(self.player.rect.x, self.player.rect.y, character_type, status, self.player.is_attacking, self.individual_score, 0, self.team, tree_health, tree_regen_count)

        # Get updates from server
        updates = self.network.get_updates()

        if updates:
            self.connection_status = f"Connected - {len(updates)} players online ({self.network.serializer.upper()})"

            current_player_ids = set()

            for player_id, data in updates.items():
                current_player_ids.add(player_id)

                if player_id == self.network.my_player_id:
                    continue

                if player_id not in self.other_players:
                    # Get team from network data, default to 'blue' if not present
                    other_team = data.get('team', 'blue')
                    other_player = Character(
                        (data['x'], data['y']),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        player_id=player_id,
                        is_local=False,
                        team=other_team
                    )
                    other_player.name = data['name']
                    if 'is_attacking' in data:
                        other_player.is_attacking = data['is_attacking']
                    self.other_players[player_id] = other_player
                else:
                    other_player = self.other_players[player_id]
                    other_player.set_position(data['x'], data['y'])
                    other_player.name = data['name']
                    if 'status' in data:
                        other_player.status = data['status']
                    if 'is_attacking' in data:
                        other_player.is_attacking = data['is_attacking']
                    # Update team and reload sprite+animations if team changed
                    if 'team' in data and data['team'] != other_player.team:
                        other_player.team = data['team']
                        other_player.image = other_player._load_base_sprite()
                        other_player.animations = other_player._build_static_animations()
                
                # Sync tree health:
                if 'tree_health' in data and data['tree_health'] >= 0 and self.main_tree:
                    sender_regen = data.get('tree_regen_count', 0)
                    if sender_regen > self.main_tree.regen_count:
                        # Remote client triggered a regen we haven't seen yet
                        self.main_tree.health = data['tree_health']
                        self.main_tree.regen_count = sender_regen
                        self.main_tree.last_healed_time = pygame.time.get_ticks()
                    elif sender_regen == self.main_tree.regen_count and data['tree_health'] < self.main_tree.health:
                        # Same regen epoch - sync damage only
                        self.main_tree.health = data['tree_health']
                    # sender_regen < local regen_count → stale pre-regen message, discard

            disconnected = set(self.other_players.keys()) - current_player_ids
            for player_id in disconnected:
                self.other_players[player_id].kill()
                del self.other_players[player_id]

            self.player.other_players = list(self.other_players.values())

    def handle_events(self, events):
        """Handle pygame events (pass from main game loop)"""
        return

    def check_attacks(self):
        """Check if player is attacking nearby trees and track the closest tree."""
        # Always find the closest tree on the map
        closest_tree = None
        closest_distance = float('inf')

        for tree in self.tree_sprites:
            distance = self.player.rect.center
            tree_pos = tree.rect.center
            dist = ((distance[0] - tree_pos[0])**2 + (distance[1] - tree_pos[1])**2)**0.5

            if dist < closest_distance:
                closest_distance = dist
                closest_tree = tree

        # Always show the closest tree's health bar
        self.target_tree = closest_tree

        current_time = pygame.time.get_ticks()
        # Calculate which 5-second window we're in
        elapsed_time = current_time - self.game_start_time
        current_window = elapsed_time // 5000
        
        # Reset tracking when window changes
        if current_window != self.last_window_checked:
            self.current_window_attacks = {'blue': {}, 'pink': {}, 'green': {}, 'default': {}}
            self.last_window_checked = current_window
            self.last_window_team_total = 0
            self.combo_established_this_window = False
            self.is_combo_active = False

        # Track other players' attacks in current window by team (excluding default)
        for player_id, other_player in self.other_players.items():
            if hasattr(other_player, 'is_attacking') and other_player.is_attacking and hasattr(other_player, 'team'):
                player_team = other_player.team
                if player_team == 'default':
                    continue
                last_counted = self.remote_attack_times.get(player_id, 0)
                if current_time - last_counted > 200:
                    self.remote_attack_times[player_id] = current_time
                    if player_id not in self.current_window_attacks[player_team]:
                        self.current_window_attacks[player_team][player_id] = 0
                    self.current_window_attacks[player_team][player_id] += 1

        # Apply damage only if attacking and within attack range
        attack_range = TILESIZE * 2
        if self.player.is_attacking and closest_tree and closest_distance < attack_range and self.main_tree:
            self.main_tree.take_damage(self.player.attack_damage)
            
            # Award individual score for attacking
            if current_time - self.last_attack_time > 200:  # Prevent score spam
                self.individual_score += 1
                self.last_attack_time = current_time
                
                # Add local player attack to current window for their team (skip if default)
                if self.team != 'default':
                    if "local" not in self.current_window_attacks[self.team]:
                        self.current_window_attacks[self.team]["local"] = 0
                    self.current_window_attacks[self.team]["local"] += 1

        # Award team score immediately when 2+ teammates have attacked in this window
        if self.team != 'default':
            window_data = self.current_window_attacks[self.team]
            if len(window_data) >= 2:
                if not self.combo_established_this_window:
                    # Combo just became active - award ALL accumulated attacks from all players
                    initial_points = sum(window_data.values())
                    self.team_scores[self.team] += initial_points
                    self.last_window_team_total = initial_points
                    self.combo_established_this_window = True
                    self.is_combo_active = True
                else:
                    # Combo already established - award each new attack as +1
                    new_total = sum(window_data.values())
                    if new_total > self.last_window_team_total:
                        gained = new_total - self.last_window_team_total
                        self.team_scores[self.team] += gained
                        self.last_window_team_total = new_total
            else:
                self.is_combo_active = False

    def update_trees(self):
        """Update all trees and the main tree."""
        # Update main tree regeneration
        if self.main_tree:
            self.main_tree.update()
        # Update individual blocks (though they don't need updating now)
        for tree in self.tree_sprites:
            tree.update()

    def draw_tree_health_bar(self):
        """Draw HUD in top left corner with username, scores, tree health and attack hint."""
        if self.main_tree is None:
            return
        
        # Get team color
        team_color = TEAM_COLORS.get(self.team, (255, 255, 255))

        y_offset = 10
        line_height = 25
        x = 10

        # Username
        username_text = self.network.player_name
        username_surface = self.font.render(username_text, True, team_color)
        self.display_surface.blit(username_surface, (x, y_offset))
        y_offset += line_height

        # Individual score
        individual_text = f"Individual Score: {self.individual_score}"
        individual_surface = self.font.render(individual_text, True, team_color)
        self.display_surface.blit(individual_surface, (x, y_offset))
        y_offset += line_height

        # Team score (N/A for default team)
        if self.team == 'default':
            team_text = "Team Score: N/A"
        else:
            team_text = f"Team Score: {self.team_scores[self.team]}"
        team_surface = self.font.render(team_text, True, team_color)
        self.display_surface.blit(team_surface, (x, y_offset))
        y_offset += line_height

        # Tree health
        health_text = f"Immortal Tree: {int(self.main_tree.health)}/{int(self.main_tree.max_health)}"
        health_surface = self.font.render(health_text, True, team_color)
        self.display_surface.blit(health_surface, (x, y_offset))
        y_offset += line_height

        # Attack hint
        attack_text = "Press Space to Attack"
        attack_surface = self.font.render(attack_text, True, team_color)
        self.display_surface.blit(attack_surface, (x, y_offset))
        y_offset += line_height

        # Combo attack display (message only, appears when 2+ players attack together)
        combo_text = "Combo Attack with Team"
        combo_surface = self.font.render(combo_text, True, team_color)
        self.display_surface.blit(combo_surface, (x, y_offset))

    def draw_names(self):
        """Draw player names above their heads"""
        if self.network.my_player_id is not None:
            name_text = self.network.player_name
            name_surface = self.font.render(name_text, True, TEAM_COLORS.get(self.team, (255, 255, 255)))
            name_rect = name_surface.get_rect(
                center=(self.player.rect.centerx, self.player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

        for other_player in self.other_players.values():
            other_color = TEAM_COLORS.get(getattr(other_player, 'team', 'blue'), (255, 255, 255))
            name_surface = self.font.render(other_player.name, True, other_color)
            name_rect = name_surface.get_rect(
                center=(other_player.rect.centerx, other_player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

    def run(self, events):
        """Main update loop"""
        self.handle_events(events)

        self.update_network()
        self.check_attacks()
        self.update_trees()

        # Update player and remote players
        self.player.update()
        for other_player in self.other_players.values():
            other_player.update()

        # Draw (Y-sorted; custom_draw does NOT call update())
        self.visible_sprites.custom_draw(self.player)

        self.draw_names()
        self.draw_tree_health_bar()


class YSortCameraGroup(pygame.sprite.Group):
    """Camera that follows player and sorts sprites by Y position"""

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        
        try:
            from support import _resolve_asset_path

            self.floor_surf = pygame.image.load(
                _resolve_asset_path('../graphics/tilemap/ground.png')
            ).convert()
            self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))
        except Exception:
            self.floor_surf = None

    def custom_draw(self, player):
        """Draw sprites sorted by Y position"""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        if self.floor_surf != None:
            floor_offset = self.floor_rect.topleft - self.offset
            self.display_surface.blit(self.floor_surf, floor_offset)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def offset_from_world(self, world_pos):
        """Convert world position to screen position"""
        return pygame.math.Vector2(world_pos) - self.offset
