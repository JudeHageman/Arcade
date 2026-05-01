import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button

class CatalogScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        self.nav_height = 110   
        
         
        self.colors = {
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "white": (255, 255, 255),
            "staff": (235, 235, 235),
            "row_bg": (248, 248, 248)
        }

        self.catalog_data = [] 
        self.sort_options = ["most_played", "highest_avg_score", "most_recently_active"]
        self.current_sort = "most_played"
        
        self.option_buttons = []
        self.time = 0
        
         
        self.refresh_layout()

    def refresh_layout(self):
         
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

         
        self.font_title = pygame.font.SysFont("Arial", max(int(42 * s), 28), bold=True)
        self.font_label = pygame.font.SysFont("Arial", max(int(18 * s), 14), bold=True)
        self.font_data = pygame.font.SysFont("Consolas", max(int(15 * s), 12))

         
        self.title_y = self.nav_height + int(35 * s)

         
        labels = ["Most Played", "Highest Avg Score", "Recently Active"]
        btn_w, btn_h = int(230 * s), int(40 * s)
        spacing = int(15 * s)
        total_btns_w = (len(labels) * btn_w) + ((len(labels)-1) * spacing)
        
        btn_start_x = cx - total_btns_w // 2
        btn_y = self.title_y + int(70 * s)  

        self.option_buttons = []
        for i, label in enumerate(labels):
            btn = Button(btn_start_x + i * (btn_w + spacing), btn_y, btn_w, btn_h, label,
                         color=self.colors["staff"],
                         action=lambda opt=self.sort_options[i]: self.set_sort(opt))
            self.option_buttons.append(btn)

         
        list_y = btn_y + int(60 * s)
        
        list_h = max(self.app.HEIGHT - list_y - int(40 * s), 200)
        list_w = int(1000 * s)
        
        self.list_rect = pygame.Rect(cx - list_w // 2, list_y, list_w, list_h)

    def set_sort(self, option):
        self.current_sort = option
        self.fetch_data()

    def fetch_data(self):
         
        if hasattr(self.app, "network"):
            self.app.network.send_action("query", query="games_catalog", sort_by=self.current_sort)

    def load_rows(self, rows):
        self.catalog_data = rows

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
         
        for i in range(5):
            y = self.list_rect.centery + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(60 * s)), 2)
        
         
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time) * 5), 3)

        
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (200 + i * 400) * s
            ny = (self.nav_height + 50 + (i % 2) * 30) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 3 + i) * 10), note_colors[i % 3])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 9 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 25 * s), int(3 * s))
        pygame.draw.line(screen, color, (x + r - 2, y - 25 * s), (x + r + 10 * s, y - 16 * s), int(3 * s))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()
            
            for btn in self.option_buttons:
                btn.handle_event(event)

    def update(self): pass

    def draw(self, screen):
         
        faction = self.app.shared_data.get("faction", "blue")
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        
        title_surf = self.font_title.render("ARCADE STATISTICS", True, self.colors["black"])
        screen.blit(title_surf, (self.app.WIDTH // 2 - title_surf.get_width() // 2, self.title_y))

         
        for i, btn in enumerate(self.option_buttons):
            if self.current_sort == self.sort_options[i]:
                 
                pygame.draw.rect(screen, theme_color, (btn.rect.x - 3, btn.rect.y - 3, btn.rect.w + 6, btn.rect.h + 6), 3, border_radius=8)
                btn.color = theme_color
            else:
                btn.color = self.colors["staff"]
            btn.draw(screen)

         
        s = self.scale
        pygame.draw.rect(screen, self.colors["white"], self.list_rect, border_radius=int(12 * s))
        pygame.draw.rect(screen, theme_color, self.list_rect, 2, border_radius=int(12 * s))

        if not self.catalog_data:
            msg = self.font_label.render("Connecting to server...", True, (180, 180, 180))
            screen.blit(msg, (self.list_rect.centerx - msg.get_width() // 2, self.list_rect.centery))
        else:
             
            for i, row in enumerate(self.catalog_data):
                curr_y = self.list_rect.y + int(15 * s) + (i * int(35 * s))
                
                 
                if curr_y + int(25 * s) > self.list_rect.bottom: break

                 
                if i % 2 == 0:
                    row_bg = pygame.Rect(self.list_rect.x + 5, curr_y - 4, self.list_rect.width - 10, int(30 * s))
                    pygame.draw.rect(screen, self.colors["row_bg"], row_bg, border_radius=6)

                name = row.get('name', 'Unknown Game')
                sessions = row.get('total_sessions', 0)
                avg = row.get('avg_score', 0)
                last_played = row.get('last_played', '')[:19].replace('T', ' ')
                
                 
                text = f"{i+1:02}. {name:<18} | Play: {sessions:>5} | Avg: {avg:>8.1f} | {last_played}"
                text_surf = self.font_data.render(text, True, self.colors["black"])
                screen.blit(text_surf, (self.list_rect.x + int(20 * s), curr_y))