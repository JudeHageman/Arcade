import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class PlayerSearchScreen(BaseScreen):
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
            "panel_bg": (252, 252, 252),
            "highlight": (240, 245, 255)
        }

         
        self.search_results = []
        self.selected_profile = None
        self.scroll_y = 0
        self.row_height = 45 
        self.max_scroll = 0

         
        self.search_input = InputBox(0, 0, 300, 40)
        self.search_btn = Button(0, 0, 120, 40, "SEARCH", color=self.colors["blue"], action=self.fetch_search)
        
        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
         
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

         
        self.font_title = pygame.font.SysFont("Arial", max(int(36 * s), 24), bold=True)
        self.font_list = pygame.font.SysFont("Arial", max(int(17 * s), 13))
        self.font_detail = pygame.font.SysFont("Consolas", max(int(16 * s), 12))
        self.row_height = int(45 * s)

         
        self.title_y = self.nav_height + int(25 * s)
        search_y = self.title_y + int(55 * s)
        
        input_w = int(350 * s)
        self.search_input.rect = pygame.Rect(cx - int(240 * s), search_y, input_w, int(40 * s))
        self.search_btn.rect = pygame.Rect(self.search_input.rect.right + int(15 * s), search_y, int(120 * s), int(40 * s))

         
        panel_y = search_y + int(60 * s)
        panel_h = max(self.app.HEIGHT - panel_y - int(40 * s), 300)
        
         
        self.list_rect = pygame.Rect(cx - int(510 * s), panel_y, int(350 * s), panel_h)
         
        self.detail_rect = pygame.Rect(self.list_rect.right + int(20 * s), panel_y, int(650 * s), panel_h)
        
         
        self.update_scroll_limit()

    def update_scroll_limit(self):
        total_height = len(self.search_results) * self.row_height
        self.max_scroll = max(0, total_height - self.list_rect.height + 20)

    def fetch_search(self):
        prefix = self.search_input.text.strip()
        if prefix and hasattr(self.app, 'network'):
            self.scroll_y = 0
            self.app.network.send_action("query", query="player_search", prefix=prefix)

    def load_results(self, results):
        self.search_results = results
        self.update_scroll_limit()

    def load_profile(self, profile_data):
        self.selected_profile = profile_data

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()

            self.search_input.handle_event(event)
            self.search_btn.handle_event(event)
            
             
            if event.type == pygame.MOUSEWHEEL:
                if self.list_rect.collidepoint(pygame.mouse.get_pos()):
                    self.scroll_y -= event.y * 30
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

             
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.list_rect.collidepoint(event.pos):
                     
                    clicked_y = event.pos[1] - self.list_rect.y - 10 + self.scroll_y
                    index = clicked_y // self.row_height
                    if 0 <= index < len(self.search_results) and hasattr(self.app, 'network'):
                        self.app.network.send_action("query", query="player_profile", 
                                                   username=self.search_results[index]["username"])

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
         
        for i in range(5):
            y = self.list_rect.centery + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(60 * s)), 2)
         
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time)*5), 3)
         
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (200 + i * 400) * s
            ny = (self.nav_height + 40 + (i % 2) * 40) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 3 + i) * 12), note_colors[i % 3])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 10 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 28 * s), int(3 * s))
        pygame.draw.line(screen, color, (x + r - 2, y - 28 * s), (x + r + 10 * s, y - 18 * s), int(3 * s))

    def draw(self, screen):
        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        s = self.scale
         
        title_surf = self.font_title.render("PLAYER DATABASE", True, self.colors["black"])
        screen.blit(title_surf, (self.app.WIDTH // 2 - title_surf.get_width() // 2, self.title_y))
        
        self.search_input.draw(screen)
        self.search_btn.color = theme_color  
        self.search_btn.draw(screen)

         
        pygame.draw.rect(screen, self.colors["panel_bg"], self.list_rect, border_radius=int(10*s))
        pygame.draw.rect(screen, theme_color, self.list_rect, 2, border_radius=int(10*s))
        
         
        old_clip = screen.get_clip()
        screen.set_clip(self.list_rect.inflate(-4, -4))
        
        for i, res in enumerate(self.search_results):
            item_y = self.list_rect.y + 10 + (i * self.row_height) - self.scroll_y
            if item_y + self.row_height > self.list_rect.y and item_y < self.list_rect.bottom:
                item_rect = pygame.Rect(self.list_rect.x + 5, item_y, self.list_rect.w - 10, self.row_height - 5)
                
                # 마우스 오버 하이라이트
                if item_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, self.colors["highlight"], item_rect, border_radius=8)
                
                txt = self.font_list.render(f"{res['username']} [{res['team'].upper()}]", True, self.colors["black"])
                screen.blit(txt, (item_rect.x + 15, item_rect.y + (item_rect.h//2 - txt.get_height()//2)))
        
        screen.set_clip(old_clip)

        # 3. 상세 프로필 (오른쪽 패널)
        pygame.draw.rect(screen, self.colors["panel_bg"], self.detail_rect, border_radius=int(10*s))
        pygame.draw.rect(screen, theme_color, self.detail_rect, 2, border_radius=int(10*s))

        if self.selected_profile:
            p = self.selected_profile
            # 프로필 헤더 (팀 색깔 강조)
            header_text = f"USER PROFILE: {p.get('username')}"
            h_surf = self.font_title.render(header_text, True, theme_color)
            screen.blit(h_surf, (self.detail_rect.x + 30, self.detail_rect.y + 30))
            
            lines = [
                f"TEAM: {p.get('team', 'N/A').upper()}",
                f"TOTAL GAMES: {p.get('total_games', 0)}",
                f"TOTAL SCORE: {p.get('total_score', 0):,}",
                f"LAST ACTIVE: {p.get('last_played', 'Never')[:16].replace('T', ' ')}"
            ]
            for i, line in enumerate(lines):
                surf = self.font_detail.render(line, True, self.colors["black"])
                screen.blit(surf, (self.detail_rect.x + 35, self.detail_rect.y + 90 + i * int(35 * s)))
        else:
            msg = self.font_list.render("Select a player to view details", True, (180, 180, 180))
            screen.blit(msg, (self.detail_rect.centerx - msg.get_width()//2, self.detail_rect.centery))