import pygame
import os
import sys
import subprocess
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox
import json

class GamesScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        self.nav_height = 110
        
        self.colors = {
            "white": (255, 255, 255),
            "black": (30, 30, 30),
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "staff": (235, 235, 235),
            "chat_bg": (245, 245, 245)
        }

        # Game metadata with server keys to match the dynamic port info
        self.game_data = [
            {
                "name": "Immortal Tree",
                "server_key": "Immortal Tree",
                "path": "../../games/immortal_tree/game/main.py",
                "default_port": "8080"
            },
            {
                "name": "Island Gardener",
                "server_key": "Island Gardener",
                "path": "../../games/island/code/game/main.py",
                "default_port": "8081"
            },
            {
                "name": "MELODY DASH",
                "server_key": "Game 3",
                "path": "../../games/game_3/main.py",
                "default_port": "8082"
            }
        ]
        
        self.game_chats = {g["name"]: [] for g in self.game_data}
        self.play_items = []
        self.active_games = [] # Tracks running subprocesses
        self.time = 0
        
        self.refresh_layout()

    def refresh_layout(self):
        """Recalculate UI positioning based on current window scale"""
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2
        start_y = self.nav_height + int(60 * s)
        
        self.font_name = pygame.font.SysFont("Arial", max(int(22 * s), 16), bold=True)
        self.font_chat = pygame.font.SysFont("Arial", max(int(14 * s), 11))
        
        self.play_items = []
        card_w, card_h = int(300 * s), int(420 * s)
        spacing = int(40 * s)
        total_w = (len(self.game_data) * card_w) + ((len(self.game_data)-1) * spacing)
        start_x = cx - total_w // 2

        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])

        for i, game in enumerate(self.game_data):
            x = start_x + i * (card_w + spacing)
            
            # PLAY Button
            btn = Button(x + int(40 * s), start_y + card_h - int(60 * s), 
                         card_w - int(80 * s), int(40 * s), "PLAY", 
                         color=theme_color, 
                         action=lambda p=game["path"], n=game["name"]: self.launch_game(p, n))
            
            # Per-game chat InputBox
            input_box = InputBox(x + int(20 * s), start_y + card_h - int(110 * s), 
                                 card_w - int(40 * s), int(35 * s))
            
            self.play_items.append({
                "rect": pygame.Rect(x, start_y, card_w, card_h), 
                "btn": btn, 
                "input": input_box,
                "name": game["name"],
                "server_key": game["server_key"]
            })

    def launch_game(self, path, game_name):
        """Look up the correct port from shared_data and launch the game process"""
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        game_dir = os.path.dirname(abs_path)
        
        username = self.app.shared_data.get("username", "Guest")
        team = self.app.shared_data.get("team", "blue").lower()
        
        # Fetch dynamic game info received from server 'global' packet
        all_games_info = self.app.shared_data.get("games_info", {})
        game_config = next((g for g in self.game_data if g["name"] == game_name), None)
        
        # Determine target port based on server mapping
        info = all_games_info.get(game_config["server_key"], {})
        port = str(info.get("port", game_config["default_port"]))
        resonance = info.get("resonance", True)

        try:
            cmd = [sys.executable, abs_path, username, "--port", port]
            if resonance:
                cmd.extend(["--team", team])

            # Launch and pipe stdout to capture final scores on exit
            proc = subprocess.Popen(cmd, cwd=game_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.active_games.append({
                "process": proc,
                "name": game_name,
                "launch_time": pygame.time.get_ticks()
            })
            print(f"🚀 [LAUNCH] {game_name} on Port {port} (PID: {proc.pid})")
            
        except Exception as e:
            print(f"❌ [LAUNCH ERROR] {e}")

    def update(self):
        for game in self.active_games[:]:
            proc = game["process"]
            ret = proc.poll()
            if ret is not None:
                print(f"✅ 종료 감지: {game['name']}, returncode={ret}")
                try:
                    stdout, _ = proc.communicate(timeout=3)
                except Exception as e:
                    print(f"communicate 실패: {e}")
                    stdout = ""
                print(f"stdout: '{stdout}'")
                self.handle_game_end(game["name"], stdout)
                self.active_games.remove(game)

    def handle_game_end(self, game_name, output):
        print(f"--- [DEBUG] Raw Output from {game_name} ---\n{output}\n--- [END DEBUG] ---")

        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("[USER]"):
                try:
                    json_str = line[len("[USER]"):].strip()
                    data = json.loads(json_str)
                    if data.get("action") == "score":
                        self.app.network.send_action(
                            "score",
                            game=data.get("game", game_name),
                            individual_score=data.get("individual_score", 0),
                            team=data.get("team", "blue"),
                            team_score=data.get("team_score", 0),
                            game_time=data.get("game_time", 0)
                        )
                        print(f"📊 [SCORE SENT] {game_name} -> {data}")
                except Exception as e:
                    print(f"❌ [SCORE PARSE ERROR] {e}")

            # ↓ 이 부분이 빠져있었어요!
            elif "FINAL_SCORE" in line.upper():
                try:
                    score = int(line.split(':')[-1].strip())
                    team = self.app.shared_data.get("team", "blue")
                    self.app.network.send_action(
                        "score",
                        game=game_name,
                        individual_score=score,
                        team=team,
                        team_score=0,
                        game_time=0
                    )
                    print(f"📊 [SCORE SENT] {game_name} -> {score}")
                except Exception as e:
                    print(f"❌ [SCORE PARSE ERROR] {e}")
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()

            for item in self.play_items:
                item["btn"].handle_event(event)
                item["input"].handle_event(event)
                
                # Send game-specific chat message on Enter
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if item["input"].active:
                        msg = item["input"].text.strip()
                        if msg and hasattr(self.app, 'network'):
                            self.app.network.send_action("chat", game=item["name"], message=msg)
                            item["input"].text = ""

    def add_message(self, game_name, sender, message):
        """Called by NetworkManager to update the mini-chat UI"""
        if game_name in self.game_chats:
            self.game_chats[game_name].append(f"{sender}: {message}")

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
        for i in range(5):
            y = self.nav_height + int(350 * s) + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(50 * s)), 2)
        
        # Pulsing resonance circle
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time) * 5), 3)

    def draw(self, screen):
        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        s = self.scale
        for item in self.play_items:
            rect = item["rect"]
            # Card background
            pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=int(15*s))
            pygame.draw.rect(screen, theme_color, rect, 3, border_radius=int(15*s))
            
            # Title
            name_surf = self.font_name.render(item["name"], True, self.colors["black"])
            screen.blit(name_surf, (rect.x + int(20*s), rect.y + int(20*s)))
            
            # Mini Chat Area
            chat_area = pygame.Rect(rect.x + int(15*s), rect.y + int(60*s), rect.w - int(30*s), int(230*s))
            pygame.draw.rect(screen, self.colors["chat_bg"], chat_area, border_radius=int(10*s))
            
            msgs = self.game_chats.get(item["name"], [])[-10:]
            for i, msg in enumerate(msgs):
                # Simple text truncation for small cards
                if len(msg) > 30: msg = msg[:27] + "..."
                msg_surf = self.font_chat.render(msg, True, (80, 80, 80))
                screen.blit(msg_surf, (chat_area.x + int(10*s), chat_area.y + int(10*s) + (i * int(20*s))))

            item["input"].draw(screen)
            item["btn"].color = theme_color
            item["btn"].draw(screen)