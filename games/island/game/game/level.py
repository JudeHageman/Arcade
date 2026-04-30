"""
level.py - Game level with NPC dialog support

Lab 7 — NPC Dialog with Graphs
"""

import pygame
from settings import *
from tile import Tile
from map_loader import load_layer
from character import Character
from subcharacter import get_all_character_classes
from network_client import NetworkClient
from inventory_ui import InventoryUI
from item import create_example_items
from time_travel import TimeTravel
from enemy import Enemy, ENEMY_SPAWN_DATA 
from weapon import Weapon as WeaponSprite
from npc import NPC
from dialog_ui import DialogUI
import sys
from support import import_cut_graphics, import_csv_layout
from datastructures.patrol_path import PatrolPath

class Level:
    def __init__(self, player_name, character_class,
                 server_host='localhost', server_port=8080, serializer='text'):
        self.display_surface = pygame.display.get_surface()

        self.visible_sprites   = YSortCameraGroup()
        self.obstacle_sprites  = pygame.sprite.Group()
        self.current_attack    = None
        self.attack_sprites    = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.character_class = character_class

        self.create_map()

        self.network   = NetworkClient(player_name, server_host, server_port, serializer)
        self.connected = self.network.connect()
        self.player.level = self

        self.other_players     = {}
        self.font              = pygame.font.Font(None, 24)
        self.connection_status = "Connecting..."

        self.inventory_ui = InventoryUI(self.player.inventory)
        self.inventory_ui.character = self.player
        self.add_starting_items()
        self.team_kills = 0
        self.time_travel       = TimeTravel(max_history=180)
        self.is_time_traveling = False
        self.enemy_history     = []
        self.enemy_future      = []

        self.enemies = pygame.sprite.Group()
        self.create_enemies()

        self.show_enemy_debug = False

        # NPC / dialog system
        self.npcs       = pygame.sprite.Group()
        self.dialog_ui  = None        # active DialogUI, or None
        self.create_npcs()
        
    # ------------------------------------------------------------------
    # Map, enemies, NPCs
    # ------------------------------------------------------------------

    def _load_gid_map(self, tmx_path):
        """Parse a Tiled .tmx file and return a global GID -> Surface dict.

        Looks for tileset images by filename in the same directory as the TMX,
        ignoring the absolute source paths Tiled stores in .tsx files.
        Scales tiles to TILESIZE if the tileset uses a different tile size.
        Returns an empty dict if the TMX cannot be read.
        """
        import xml.etree.ElementTree as ET
        import os
       
        gid_map = {}
        tmx_dir = os.path.dirname(os.path.abspath(tmx_path))

        try:
            tree = ET.parse(tmx_path)
        except Exception:
            return gid_map

        for ts_elem in tree.getroot().findall('tileset'):
            firstgid = int(ts_elem.get('firstgid', 1))
            tsx_source = ts_elem.get('source', '')
            tsx_path = os.path.join(tmx_dir, tsx_source)
            try:
                tsx_tree = ET.parse(tsx_path)
            except Exception:
                continue

            tsx_root = tsx_tree.getroot()
            tw = int(tsx_root.get('tilewidth',  TILESIZE))
            th = int(tsx_root.get('tileheight', TILESIZE))
            cols_declared = int(tsx_root.get('columns', 0))

            img_elem = tsx_root.find('image')
            if img_elem is None:
                continue

            img_name = os.path.basename(img_elem.get('source', ''))
            img_path = os.path.join(tmx_dir, img_name)
            try:
                sheet = pygame.image.load(img_path).convert_alpha()
            except Exception as e:
                 
                continue

            cols = cols_declared if cols_declared > 0 else sheet.get_width() // tw
            rows = sheet.get_height() // th
            for r in range(rows):
                for c in range(cols):
                    gid = firstgid + r * cols + c
                    rect = pygame.Rect(c * tw, r * th, tw, th)
                    try:
                        surf = sheet.subsurface(rect)
                        if tw != TILESIZE or th != TILESIZE:
                            surf = pygame.transform.scale(surf, (TILESIZE, TILESIZE))
                        gid_map[gid] = surf
                    except Exception:
                        pass

        return gid_map

    def create_map(self):
         
        
        
        set1 = import_cut_graphics('../../graphics/tiles/2.png')
        self.tile_graphics = set1
        print(f"[System] Graphics loaded: {len(self.tile_graphics)} tiles")

        LAYERS = [
            
            ('map/map_FloorBlocks.csv', 'boundary', [self.visible_sprites, self.obstacle_sprites]),
            ('map/map_Grass.csv', 'floor', [self.visible_sprites]),  
            ('map/map_Objects.csv', 'object', [self.visible_sprites, self.obstacle_sprites]),
        ]

        floor_blocks_loaded = False
        for csv_path, sprite_type, groups in LAYERS:
            try:
                layer = load_layer(csv_path) 
                entries = list(layer.items())
                
                if not entries: continue
                print(f"[Map] {csv_path}: {len(entries)} tiles")

                for (row, col), tile_id in entries:
                    x = col * TILESIZE
                    y = row * TILESIZE
                    
                    tile_index = int(tile_id)
                    
                    if 0 <= tile_index < len(self.tile_graphics):
                        surf = self.tile_graphics[tile_index]
                        if sprite_type == 'boundary':
                             
                            Tile((x, y), groups, 'invisible')
                            floor_blocks_loaded = True
                        else:
                             
                            Tile((x, y), groups, sprite_type, surf)
                    else:
                         
                        Tile((x, y), groups, sprite_type)
                        
            except Exception as e:
                print(f"[Map] {csv_path} failed: {e}")

        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x, y = col_index * TILESIZE, row_index * TILESIZE
                if col == 'p':
                    self.player = self.character_class((x, y), [self.visible_sprites], self.obstacle_sprites, is_local=True)
                    self.player.create_attack = self.create_attack
                    self.player.destroy_attack = self.destroy_attack

    def add_starting_items(self):
        for item in create_example_items():
            self.player.inventory.add_item(item)
        for item in self.player.inventory.items:
            if item.item_type == 'weapon':
                self.player.equipped_weapon = item
                break

    def create_enemies(self):
        try:
            for data in ENEMY_SPAWN_DATA:
                combat_kwargs = dict(
                    health=data.get("health", 60),
                    exp=data.get("exp", 30),
                    attack_damage=data.get("attack_damage", 10),
                    notice_radius=data.get("notice_radius", 200),
                    attack_radius=data.get("attack_radius", 60),
                    damage_player=self.damage_player,
                )
                if data["patrol_type"] == "random":
                    enemy = Enemy(
                        name=data["name"],
                        start_x=data["spawn"][0],
                        start_y=data["spawn"][1],
                        patrol_path=None,
                        patrol_type="random",
                        obstacle_sprites=self.obstacle_sprites,
                        speed=data["speed"],
                        sprite_name=data["name"].lower().replace(' ', '_'),
                        **combat_kwargs
                    )
                else:
                    patrol_path = PatrolPath(data["patrol_type"])
                    for waypoint in data["waypoints"]:
                        patrol_path.add_waypoint(waypoint[0], waypoint[1], wait_time=1.0)
                    enemy = Enemy(
                        name=data["name"],
                        start_x=data["spawn"][0],
                        start_y=data["spawn"][1],
                        patrol_path=patrol_path,
                        obstacle_sprites=self.obstacle_sprites,
                        speed=data["speed"],
                        sprite_name=data["name"].lower().replace(' ', '_'),
                        **combat_kwargs
                    )
                self.enemies.add(enemy)
                self.visible_sprites.add(enemy)
                self.obstacle_sprites.add(enemy)
                self.attackable_sprites.add(enemy)
        except Exception as e:
            print(f"Enemy setup error: {e}")

    def create_npcs(self):
        """Spawn NPCs defined in dialog_data.py."""
        try:
            from dialog_data import NPC_DATA
            for entry in NPC_DATA:
                npc = NPC(
                    entry["name"],
                    entry["grid_x"],
                    entry["grid_y"],
                    entry["dialog"],
                    entry["sprite_name"],
                    self.npcs,
                    self.visible_sprites,
                )
                # Store ai_handler on the npc for use when dialog opens
                npc.ai_handler = entry.get("ai_handler", None)
            print(f"Spawned {len(self.npcs)} NPC(s).  Press T near an NPC to talk.")
        except Exception as exc:
            print(f"NPC setup error: {exc}")

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def create_attack(self):
        self.current_attack = WeaponSprite(self.player,
                                           [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        for attack_sprite in list(self.attack_sprites):
            for enemy in pygame.sprite.spritecollide(
                    attack_sprite, self.attackable_sprites, False):
                enemy.get_damage(self.player)

    def damage_player(self, amount):
        self.player.take_damage(amount)

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def update_network(self):
        if not self.connected:
            self.connection_status = "Disconnected"
            return

        character_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        self.network.send_update(self.player.rect.x, self.player.rect.y,
                                  character_type, status)
        updates = self.network.get_updates()

        if updates:
            self.connection_status = (
                f"Connected - {len(updates)} players online "
                f"({self.network.serializer.upper()})"
            )
            current_ids = set()
            for pid, data in updates.items():
                current_ids.add(pid)
                if pid == self.network.my_player_id:
                    continue
                if pid not in self.other_players:
                    ctype = data.get('character_type', '').lower()
                    if not ctype:
                        continue
                    CharClass = None
                    for cls in get_all_character_classes():
                        if cls.get_display_name().lower() == ctype:
                            CharClass = cls
                            break
                    CharClass = CharClass or Character
                    op = CharClass(
                        (data['x'], data['y']),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        player_id=pid, is_local=False
                    )
                    op.name = data['name']
                    self.other_players[pid] = op
                else:
                    op = self.other_players[pid]
                    op.set_position(data['x'], data['y'])
                    op.name = data['name']
                    if 'status' in data:
                        op.status = data['status']

            for pid in set(self.other_players) - current_ids:
                self.other_players[pid].kill()
                del self.other_players[pid]

            self.player.other_players = list(self.other_players.values())

    # ------------------------------------------------------------------
    # Dialog helpers
    # ------------------------------------------------------------------

    def _get_nearby_npc(self):
        """Return the first NPC within interaction range, or None."""
        for npc in self.npcs:
            if npc.is_nearby(self.player.rect):
                return npc
        return None

    def handle_dialog_input(self, events):
        """Open dialog on T press if an NPC is nearby; drive active dialog."""
        if self.dialog_ui:
            self.dialog_ui.handle_events(events)
            if self.dialog_ui.is_done():
                self.dialog_ui = None
            return True   # dialog is active — suppress normal movement

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                npc = self._get_nearby_npc()
                if npc:
                    self.dialog_ui = DialogUI(
                        npc.name,
                        npc.dialog_graph,
                        ai_handler=npc.ai_handler
                    )
        return False

    # ------------------------------------------------------------------
    # HUD / drawing helpers
    # ------------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            self.inventory_ui.handle_event(event, self.player)

    def draw_names(self):
        if self.network.my_player_id is not None:
            name_text = f"{self.network.player_name} ({self.player.character_name})"
            surf = self.font.render(name_text, True, (0, 255, 0))
            rect = surf.get_rect(center=(self.player.rect.centerx,
                                         self.player.rect.top - 10))
            self.display_surface.blit(
                surf, self.visible_sprites.offset_from_world(rect.topleft))
        for op in self.other_players.values():
            surf = self.font.render(op.name, True, (100, 100, 255))
            rect = surf.get_rect(center=(op.rect.centerx, op.rect.top - 10))
            self.display_surface.blit(
                surf, self.visible_sprites.offset_from_world(rect.topleft))

    def draw_npc_hints(self):
        offset = (self.visible_sprites.offset.x, self.visible_sprites.offset.y)
        for npc in self.npcs:
            if npc.is_nearby(self.player.rect):
                npc.draw_hint(self.display_surface, offset)

    def draw_status(self):
         
        status_color = (0, 255, 0) if self.connected else (255, 100, 100)
        self.display_surface.blit(
            self.font.render(self.connection_status, True, status_color), (10, 10))
        self.display_surface.blit(
            self.font.render("I: Inventory | SPACE: Attack | T: Talk to NPC",
                             True, (255, 255, 255)), (10, 40))

         
        bar_rect  = pygame.Rect(10, 70, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        ratio     = max(0.0, self.player.hp / max(1, self.player.max_hp))
        fill_rect = pygame.Rect(10, 70, int(HEALTH_BAR_WIDTH * ratio), BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR,     bar_rect)
        pygame.draw.rect(self.display_surface, HEALTH_COLOR,    fill_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bar_rect, 2)
        
         
        self.display_surface.blit(
            self.font.render(f"HP {self.player.hp}/{self.player.max_hp}",
                             True, (255, 255, 255)),
            (10 + HEALTH_BAR_WIDTH + 8, 70))

         
        self.display_surface.blit(
            self.font.render(f"XP: {self.player.exp}", True, (255, 215, 0)),
            (10, 100))

         
        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg   = f"Weapon: {w.name}  (+{w.attack_bonus} atk)"
            color = (255, 200, 100)
        else:
            msg   = "Weapon: none  (I → select → Equip)"
            color = (150, 150, 150)
         
        self.display_surface.blit(
            self.font.render(f"XP: {self.player.exp}", True, (255, 215, 0)),
            (10, 100))

        team_name = getattr(self.player, 'team', 'None')
        team_kills = getattr(self, 'team_kills', 0)
        
        t_color = (255, 255, 255)
        if team_name.lower() == 'red': t_color = (255, 100, 100)
        elif team_name.lower() == 'blue': t_color = (100, 100, 255)
        elif team_name.lower() == 'green': t_color = (100, 255, 100)

        team_msg = f" |  Team {team_name}: {team_kills}"
        self.display_surface.blit(
            self.font.render(team_msg, True, t_color), (180, 100))  

        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg   = f"Weapon: {w.name}  (+{w.attack_bonus} atk)"
            color = (255, 200, 100)
        else:
            msg   = "Weapon: none  (I → select → Equip)"
            color = (150, 150, 150)
        self.display_surface.blit(
            self.font.render(msg, True, color), (10, 125))
    # ------------------------------------------------------------------
    # Time travel
    # ------------------------------------------------------------------

    def _snapshot_enemies(self):
        enemies = []
        for enemy in self.enemies:
            enemies.append({
                'x': enemy.rect.x, 'y': enemy.rect.y,
                'target_waypoint': enemy.target_waypoint,
                'patrol_active': enemy.patrol_active,
                'is_waiting': enemy.is_waiting,
                'wait_timer': enemy.wait_timer,
                'patrol_current':   enemy.patrol_path.current   if enemy.patrol_path else None,
                'patrol_direction': enemy.patrol_path.direction if enemy.patrol_path else None,
                'wander_target': getattr(enemy, 'wander_target', None),
                'health': enemy.health,
                'combat_status': enemy.combat_status,
            })
        return {'enemies': enemies, 'player_hp': self.player.hp}

    def _restore_enemies(self, snapshot):
        enemy_list = snapshot['enemies'] if isinstance(snapshot, dict) else snapshot
        for enemy, state in zip(self.enemies, enemy_list):
            enemy.rect.x = state['x']; enemy.rect.y = state['y']
            enemy.x = float(enemy.rect.x); enemy.y = float(enemy.rect.y)
            enemy.hitbox.center = enemy.rect.center
            enemy.target_waypoint = state['target_waypoint']
            enemy.patrol_active   = state['patrol_active']
            enemy.is_waiting      = state['is_waiting']
            enemy.wait_timer      = state['wait_timer']
            if enemy.patrol_path:
                enemy.patrol_path.current   = state['patrol_current']
                enemy.patrol_path.direction = state['patrol_direction']
            if hasattr(enemy, 'wander_target'):
                enemy.wander_target = state['wander_target']
            enemy.health        = state.get('health', enemy.health)
            enemy.combat_status = state.get('combat_status', 'patrol')
        if isinstance(snapshot, dict):
            self.player.hp = snapshot.get('player_hp', self.player.hp)
            self.player.vulnerable = True

    def record_player_state(self):
        if not self.is_time_traveling and not self.connected:
            prev = self.time_travel.get_history_size()
            self.time_travel.record_state(self.player.rect.x, self.player.rect.y)
            if self.time_travel.get_history_size() > prev:
                self.enemy_history.append(self._snapshot_enemies())
                while len(self.enemy_history) > self.time_travel.max_history:
                    self.enemy_history.pop(0)
                self.enemy_future.clear()

    def handle_time_travel_input(self, events):
        if self.connected:
            self.is_time_traveling = False
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.time_travel.can_rewind():
                    state = self.time_travel.rewind()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_history:
                            self.enemy_future.append(self.enemy_history.pop())
                            if self.enemy_history:
                                self._restore_enemies(self.enemy_history[-1])
                elif event.key == pygame.K_f and self.time_travel.can_replay():
                    state = self.time_travel.replay()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_future:
                            snap = self.enemy_future.pop()
                            self.enemy_history.append(snap)
                            self._restore_enemies(snap)
                else:
                    self.is_time_traveling = False

    def draw_time_travel_ui(self):
        font_small = pygame.font.Font(None, 24)
        if not self.connected:
            if self.is_time_traveling:
                font_large = pygame.font.Font(None, 48)
                text = font_large.render("⏪ TIME TRAVELING", True, (255, 100, 100))
                self.display_surface.blit(text, text.get_rect(center=(WIDTH // 2, 50)))
            self.display_surface.blit(
                font_small.render(
                    f"History: {self.time_travel.get_history_size()} | "
                    f"Future: {self.time_travel.get_future_size()}",
                    True, (255, 255, 255)), (10, 155))
            self.display_surface.blit(
                font_small.render("R: Rewind | F: Replay", True, (200, 200, 200)),
                (10, 178))
        else:
            self.display_surface.blit(
                font_small.render("Time travel disabled (multiplayer)",
                                  True, (150, 150, 150)), (10, 155))

    # ------------------------------------------------------------------
    # Enemy debug
    # ------------------------------------------------------------------

    def handle_enemy_debug_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.show_enemy_debug = not self.show_enemy_debug
                elif event.key == pygame.K_m:
                    for enemy in self.enemies:
                        enemy.reset_patrol()

    def draw_enemy_debug(self):
        if not self.show_enemy_debug:
            return
        offset = (self.visible_sprites.offset.x, self.visible_sprites.offset.y)
        y_off = 200
        for enemy in self.enemies:
            surf = pygame.font.Font(None, 20).render(
                enemy.get_debug_status(), True, (255, 255, 100))
            self.display_surface.blit(surf, (10, y_off))
            y_off += 22
            enemy.draw_debug_info(self.display_surface, offset)

    # level.py 의 game_over_logic 수정
    def game_over_logic(self):
        self.player.exp = max(0, self.player.exp - 20)
        self.player.hp = self.player.max_hp
        
        # 1. 좌표를 안전한 곳으로! (좌표를 100, 100 같은 시작 지점으로 바꿔봐)
        self.player.rect.topleft = (100, 100) 
        self.player.hitbox.center = self.player.rect.center

        # 2. 부활 시 2초간 무적 부여 (매우 중요!)
        self.player.vulnerable = False
        self.player.hurt_time = pygame.time.get_ticks() + 2000 # 2초 보너스
        
        print(f"사망! 안전 구역으로 후송되었습니다. 현재 점수: {self.player.exp}")
    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, events):
        # --- Dialog takes priority: freeze movement while talking ---
        dialog_active = self.handle_dialog_input(events)

        if not dialog_active:
            self.handle_events(events)
            self.handle_time_travel_input(events)
            self.handle_enemy_debug_input(events)
            self.update_network()
            self.player.update()
            for op in self.other_players.values():
                op.update()
            if not self.is_time_traveling:
                for enemy in list(self.enemies):
                    enemy.enemy_update(self.player)
                self.enemies.update()
                self.player_attack_logic()

        # Always draw the world
        self.visible_sprites.custom_draw(self.player)

        if not dialog_active:
            self.record_player_state()

        self.draw_names()
        self.draw_npc_hints()
        self.draw_status()
        self.draw_time_travel_ui()
        self.draw_enemy_debug()

        if self.inventory_ui.active:
            self.inventory_ui.draw(self.display_surface)

        # Draw dialog box on top of everything
        if self.dialog_ui:
            self.dialog_ui.draw(self.display_surface)
        self.player.update()
        
        # 플레이어 사망 체크
        if self.player.hp <= 0:
            self.game_over_logic()


# ---------------------------------------------------------------------------

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width  = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
         
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        
        for sprite in self.sprites():
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'floor':
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

         
        render_sprites = [s for s in self.sprites() if not (hasattr(s, 'sprite_type') and s.sprite_type == 'floor')]
        
        for sprite in sorted(render_sprites, key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
    def offset_from_world(self, world_pos):
        return pygame.math.Vector2(world_pos) - self.offset
    
    #for session.py
    def get_current_scores(self):
   
        return (self.player.exp, self.team_kills, self.player.team)
