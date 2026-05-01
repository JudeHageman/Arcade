import pygame
import sys
import os
import math
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
from support import import_cut_graphics, import_csv_layout
from datastructures.patrol_path import PatrolPath

class Level:
    def __init__(self, player_name, character_class,
                 server_host='localhost', server_port=8081, serializer='text', team='default'):
        
        # --- 1. 기본 인프라 설정 ---
        self.display_surface = pygame.display.get_surface()
        self.team = team # 런처에서 받은 팀 정보
        self.player_name = player_name
        self.character_class = character_class

        # 스프라이트 관리 그룹
        self.visible_sprites    = YSortCameraGroup()
        self.obstacle_sprites   = pygame.sprite.Group()
        self.attack_sprites     = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.enemies            = pygame.sprite.Group()
        self.npcs               = pygame.sprite.Group()

        # 게임 상태 변수
        self.current_attack    = None
        self.team_kills        = 0
        self.show_enemy_debug  = False
        self.connection_status = "Connecting..."
        self.other_players     = {}
        self.font              = pygame.font.Font(None, 24)

        # --- 2. 맵 및 플레이어 생성 ---
        self.create_map()

        # --- 3. 네트워크 시스템 ---
        self.network   = NetworkClient(player_name, server_host, server_port, serializer)
        self.connected = self.network.connect()
        self.player.level = self # 플레이어에게 레벨 참조 연결

        # --- 4. 인벤토리 및 아이템 ---
        self.inventory_ui = InventoryUI(self.player.inventory)
        self.inventory_ui.character = self.player
        self.add_starting_items()

        # --- 5. 타임 트래블 시스템 ---
        self.time_travel       = TimeTravel(max_history=180)
        self.is_time_traveling = False
        self.enemy_history     = []
        self.enemy_future      = []

        # --- 6. NPC 및 대화 시스템 ---
        self.dialog_ui = None 
        self.create_npcs()

        # --- 7. 적(Enemy) 생성 ---
        self.create_enemies()

        import threading
        import socket

        def start_ping_listener():
            try:
                # 8081 포트를 열고 서버의 확인 전화를 기다림
                ping_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ping_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                ping_sock.bind(('localhost', server_port)) # server_port는 8081
                ping_sock.listen(1)
                
                while True:
                    # 서버가 접속하면 "아, 얘 살아있네" 하고 연결만 수락하고 바로 닫음
                    conn, addr = ping_sock.accept()
                    conn.close() 
            except Exception as e:
                # 이미 포트가 열려있거나 에러가 나면 출력
                print(f"ℹ️ Heartbeat listener status: {e}")

        # 게임 흐름을 방해하지 않게 별도 쓰레드로 실행
        threading.Thread(target=start_ping_listener, daemon=True).start()

    # ------------------------------------------------------------------
    # 맵 생성 및 초기화
    # ------------------------------------------------------------------

    def create_map(self):
        """TMX 기반 레이어 로드 및 플레이어 배치"""
        # 그래픽 데이터 로드
        try:
            self.tile_graphics = import_cut_graphics('../../graphics/tiles/2.png')
        except:
            print("⚠️ Warning: Graphics path error. Fallback to default tiles.")
            self.tile_graphics = []

        LAYERS = [
            ('map/map_FloorBlocks.csv', 'boundary', [self.visible_sprites, self.obstacle_sprites]),
            ('map/map_Grass.csv', 'floor', [self.visible_sprites]),  
            ('map/map_Objects.csv', 'object', [self.visible_sprites, self.obstacle_sprites]),
        ]

        for csv_path, sprite_type, groups in LAYERS:
            try:
                layer = load_layer(csv_path)
                for (row, col), tile_id in layer.items():
                    x, y = col * TILESIZE, row * TILESIZE
                    tile_index = int(tile_id)
                    
                    if 0 <= tile_index < len(self.tile_graphics):
                        surf = self.tile_graphics[tile_index]
                        if sprite_type == 'boundary':
                            Tile((x, y), groups, 'invisible')
                        else:
                            Tile((x, y), groups, sprite_type, surf)
                    else:
                        # 그래픽 없을 시 기본 더미 타일
                        Tile((x, y), groups, sprite_type)
            except Exception as e:
                print(f"[Map Error] {csv_path}: {e}")

        # 플레이어 배치 (WORLD_MAP 배열 검색)
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                if col == 'p':
                    x, y = col_index * TILESIZE, row_index * TILESIZE
                    # 플레이어 생성
                    self.player = self.character_class((x, y), [self.visible_sprites], self.obstacle_sprites, is_local=True)
                    
                    # 🚨 팀 정보 및 이름 주입
                    self.player.team = self.team 
                    self.player.name = self.player_name
                    
                    self.player.create_attack = self.create_attack
                    self.player.destroy_attack = self.destroy_attack

    def add_starting_items(self):
        for item in create_example_items():
            self.player.inventory.add_item(item)
        # 무기 자동 장착
        for item in self.player.inventory.items:
            if item.item_type == 'weapon':
                self.player.equipped_weapon = item
                break

    # ------------------------------------------------------------------
    # 적(Enemy) 및 NPC 생성
    # ------------------------------------------------------------------

    def create_enemies(self):
        try:
            for data in ENEMY_SPAWN_DATA:
                combat_kwargs = {
                    "health": data.get("health", 60),
                    "exp": data.get("exp", 30),
                    "attack_damage": data.get("attack_damage", 10),
                    "notice_radius": data.get("notice_radius", 200),
                    "attack_radius": data.get("attack_radius", 60),
                    "damage_player": self.damage_player,
                }
                
                # 순찰 경로(Patrol Path) 설정
                patrol_path = None
                if data["patrol_type"] != "random":
                    patrol_path = PatrolPath(data["patrol_type"])
                    for wp in data["waypoints"]:
                        patrol_path.add_waypoint(wp[0], wp[1], wait_time=1.0)

                enemy = Enemy(
                    name=data["name"],
                    start_x=data["spawn"][0],
                    start_y=data["spawn"][1],
                    patrol_path=patrol_path,
                    patrol_type=data["patrol_type"],
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
        try:
            from dialog_data import NPC_DATA
            for entry in NPC_DATA:
                npc = NPC(
                    entry["name"], entry["grid_x"], entry["grid_y"],
                    entry["dialog"], entry["sprite_name"],
                    self.npcs, self.visible_sprites
                )
                npc.ai_handler = entry.get("ai_handler", None)
        except Exception as e:
            print(f"NPC setup error: {e}")

    # ------------------------------------------------------------------
    # 전투 및 로직 함수
    # ------------------------------------------------------------------

    def get_current_scores(self):
        """세션 기록을 위한 데이터 반환 (개인점수, 팀점수, 팀명)"""
        return (self.player.exp, self.team_kills, self.player.team)

    def create_attack(self):
        self.current_attack = WeaponSprite(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        for attack_sprite in list(self.attack_sprites):
            hits = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
            for enemy in hits:
                enemy.get_damage(self.player)

    def damage_player(self, amount):
        if self.player.vulnerable:
            self.player.take_damage(amount)

    def game_over_logic(self):
        """사망 시 리스폰 로직"""
        self.player.hp = self.player.max_hp
        self.player.rect.topleft = (100, 100) # 안전 구역 리스폰
        self.player.hitbox.center = self.player.rect.center
        self.player.vulnerable = False # 부활 무적
        self.player.hurt_time = pygame.time.get_ticks() + 2000

    # ------------------------------------------------------------------
    # 네트워크 업데이트
    # ------------------------------------------------------------------

    def update_network(self):
        if not self.connected:
            self.connection_status = "Offline"
            return

        char_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        self.network.send_update(self.player.rect.x, self.player.rect.y, char_type, status)
        
        updates = self.network.get_updates()
        if updates:
            self.connection_status = f"Connected - {len(updates)} Players"
            current_ids = set()
            for pid, data in updates.items():
                current_ids.add(pid)
                if pid == self.network.my_player_id: continue
                
                # 타 플레이어 스프라이트 관리
                if pid not in self.other_players:
                    self.other_players[pid] = Character(
                        (data['x'], data['y']), [self.visible_sprites], 
                        self.obstacle_sprites, player_id=pid, is_local=False
                    )
                op = self.other_players[pid]
                op.rect.x, op.rect.y = data['x'], data['y']
                op.name = data.get('name', 'Player')
                op.status = data.get('status', 'down_idle')

            # 접속 종료된 플레이어 삭제
            for pid in list(self.other_players.keys()):
                if pid not in current_ids:
                    self.other_players[pid].kill()
                    del self.other_players[pid]

    # ------------------------------------------------------------------
    # 입출력 및 UI 드로잉
    # ------------------------------------------------------------------

    def handle_dialog_input(self, events):
        if self.dialog_ui:
            self.dialog_ui.handle_events(events)
            if self.dialog_ui.is_done(): self.dialog_ui = None
            return True # 대화 중 이동 차단

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                for npc in self.npcs:
                    if npc.is_nearby(self.player.rect):
                        self.dialog_ui = DialogUI(npc.name, npc.dialog_graph, ai_handler=npc.ai_handler)
                        return True
        return False

    def handle_events(self, events):
        for event in events:
            self.inventory_ui.handle_event(event, self.player)

    def draw_status(self):
        """HUD 정보 표시"""
        # 연결 및 기본 정보
        c = (0, 255, 0) if self.connected else (255, 100, 100)
        self.display_surface.blit(self.font.render(self.connection_status, True, c), (10, 10))
        
        # 체력 바
        pygame.draw.rect(self.display_surface, (50, 50, 50), (10, 70, HEALTH_BAR_WIDTH, BAR_HEIGHT))
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.display_surface, (255, 50, 50), (10, 70, int(HEALTH_BAR_WIDTH * hp_ratio), BAR_HEIGHT))
        
        # 🚨 팀 정보 UI
        team_name = getattr(self.player, 'team', 'None').upper()
        t_color = (100, 255, 100) if team_name == 'GREEN' else (255, 100, 255) if team_name == 'PINK' else (255, 255, 255)
        self.display_surface.blit(self.font.render(f"XP: {self.player.exp} | TEAM: {team_name}", True, t_color), (10, 100))

    def run(self, events):
        """메인 업데이트 루프"""
        dialog_active = self.handle_dialog_input(events)

        if not dialog_active:
            self.handle_events(events)
            self.update_network()
            self.player.update()
            
            # 적 및 전투 업데이트 (타임트래블 중이 아닐 때만)
            if not self.is_time_traveling:
                for enemy in list(self.enemies):
                    enemy.enemy_update(self.player)
                self.enemies.update()
                self.player_attack_logic()

        # 화면 그리기
        self.visible_sprites.custom_draw(self.player)
        self.draw_status()
        
        # UI 레이어 (가장 위)
        if self.inventory_ui.active: self.inventory_ui.draw(self.display_surface)
        if self.dialog_ui: self.dialog_ui.draw(self.display_surface)

        if self.player.hp <= 0: self.game_over_logic()

# ---------------------------------------------------------------------------
# 카메라 정렬 그룹
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

        # 1. 바닥(Floor) 먼저 그리기
        for sprite in self.sprites():
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'floor':
                self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)

        # 2. Y축 정렬하여 캐릭터 및 오브젝트 그리기
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'floor': continue
            self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)