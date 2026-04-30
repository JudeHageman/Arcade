import pygame
import math
import os
import sys
import subprocess
from screens.base_screen import BaseScreen
from ui.button import Button

class CatalogScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        
        self.colors = {
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "white": (255, 255, 255),
            "staff": (235, 235, 235)
        }

         
        self.game_data = [
            {"name": "LUMBERJACK", "path": "../../games/immortal_tree/game/main.py", "desc": " "},
            {"name": "ISLAND", "path": "../../games/island/game/game/main.py", "desc": " "},
            {"name": "MELODY DASH", "path": "../../games/game_3/main.py", "desc": "Music platformer"}
        ]

        self.play_buttons = []
        self.back_btn = None
        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
         
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx, cy = self.app.WIDTH // 2, self.app.HEIGHT // 2

         
        self.font_title = pygame.font.SysFont("Arial", max(int(54 * s), 32), bold=True)
        self.font_card = pygame.font.SysFont("Arial", max(int(24 * s), 18), bold=True)
        self.font_desc = pygame.font.SysFont("Arial", max(int(16 * s), 12))

         
        self.back_btn = Button(int(40 * s), int(40 * s), int(120 * s), int(45 * s), 
                               "< BACK", color=self.colors["staff"], action=lambda: self.app.switch_screen("MENU"))

        
        self.play_buttons = []
        card_w = int(280 * s)
        card_h = int(380 * s)
        spacing = int(40 * s)
        total_w = (len(self.game_data) * card_w) + ((len(self.game_data) - 1) * spacing)
        
        start_x = cx - total_w // 2
        y_pos = cy - card_h // 2 + int(40 * s)

        for i, game in enumerate(self.game_data):
            x = start_x + i * (card_w + spacing)
            
             
            btn = Button(x + int(40 * s), y_pos + card_h - int(75 * s), 
                         card_w - int(80 * s), int(50 * s), "PLAY", 
                         color=self.colors["black"], 
                         action=lambda p=game["path"]: self.select_game(p))
            
            self.play_buttons.append({
                "rect": pygame.Rect(x, y_pos, card_w, card_h),
                "btn": btn,
                "name": game["name"],
                "desc": game["desc"]
            })

    def select_game(self, game_path):
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), game_path))
        game_dir = os.path.dirname(abs_path)
        username = self.app.shared_data.get("username", "Guest")
        
        try:
             
            process = subprocess.Popen([sys.executable, abs_path, username], cwd=game_dir)
            
             
            self.app.shared_data["current_game_process"] = process
            
            self.app.switch_screen("CHAT")
        except Exception as e:
            print(f"ERROR: {e}")

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
         
        for i in range(5):
            y = int(500 * s) + (i * int(30 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(100 * s)), 2)
        
         
        pygame.draw.circle(screen, theme_color, (self.app.WIDTH - int(100*s), int(100*s)), int(60*s + math.sin(self.time)*5), 3)
        
         
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(4):
            nx = (200 + i * 300) * s
            ny = (100 + (i % 2) * 50) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 3 + i) * 15), note_colors[i % 3])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 10 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 28 * s), int(3 * s))
        pygame.draw.line(screen, color, (x + r - 2, y - 28 * s), (x + r + 10 * s, y - 18 * s), int(3 * s))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()
            
            self.back_btn.handle_event(event)
            for item in self.play_buttons:
                item["btn"].handle_event(event)

    def draw(self, screen):
         
        faction = self.app.shared_data.get("faction", "blue")
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

         
        title_surf = self.font_title.render("GAME CATALOG", True, self.colors["black"])
        screen.blit(title_surf, (self.app.WIDTH // 2 - title_surf.get_width() // 2, int(80 * self.scale)))

         
        s = self.scale
        for item in self.play_buttons:
            rect = item["rect"]
            
            
            pygame.draw.rect(screen, self.colors["white"], rect, border_radius=int(15 * s))
            pygame.draw.rect(screen, theme_color, rect, int(3 * s), border_radius=int(15 * s))
            
             
            name_surf = self.font_card.render(item["name"], True, self.colors["black"])
            desc_surf = self.font_desc.render(item["desc"], True, (150, 150, 150))
            
            screen.blit(name_surf, (rect.x + int(20 * s), rect.y + int(30 * s)))
            screen.blit(desc_surf, (rect.x + int(20 * s), rect.y + int(70 * s)))
            
             
            item["btn"].color = theme_color
            item["btn"].draw(screen)

        self.back_btn.draw(screen)