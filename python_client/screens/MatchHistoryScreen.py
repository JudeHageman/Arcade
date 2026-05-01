import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class MatchHistoryScreen(BaseScreen):
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
            "row_bg": (248, 248, 248),
            "panel": (252, 252, 252)
        }

        # --- 데이터 저장소 ---
        self.history_data = [] 
        self.scroll_y = 0
        self.row_height = 45
        self.max_scroll = 0

         
        self.user_input = InputBox(0, 0, 250, 40)
        self.user_input.text = self.app.shared_data.get("username", "")
        
        self.game_input = InputBox(0, 0, 250, 40)
        self.game_input.placeholder = "Game Filter (Optional)"
        
        self.load_btn = Button(0, 0, 100, 40, "LOAD", color=self.colors["blue"], action=self.fetch_history)
        
        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
         
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

        # 폰트 설정
        self.font_title = pygame.font.SysFont("Arial", max(int(36 * s), 24), bold=True)
        self.font_header = pygame.font.SysFont("Arial", max(int(18 * s), 14), bold=True)
        self.font_row = pygame.font.SysFont("Consolas", max(int(16 * s), 12))
        self.row_height = int(45 * s)

        # 1. 상단 컨트롤 영역 (입력창들)
        ctrl_y = self.nav_height + int(30 * s)
        self.title_y = ctrl_y
        
        input_y = ctrl_y + int(50 * s)
        input_w = int(250 * s)
        
        self.user_input.rect = pygame.Rect(cx - int(320 * s), input_y, input_w, int(40 * s))
        self.game_input.rect = pygame.Rect(self.user_input.rect.right + int(15 * s), input_y, input_w, int(40 * s))
        self.load_btn.rect = pygame.Rect(self.game_input.rect.right + int(15 * s), input_y, int(100 * s), int(40 * s))

        # 2. 테이블 영역 배치
        table_y = input_y + int(65 * s)
        self.table_rect = pygame.Rect(cx - int(550 * s), table_y + int(40 * s), int(1100 * s), 0)
        self.table_rect.height = max(self.app.HEIGHT - self.table_rect.y - int(40 * s), 250)
        
        # 스크롤 한계 갱신
        self.update_scroll_limit()

    def update_scroll_limit(self):
        total_height = len(self.history_data) * self.row_height
        self.max_scroll = max(0, total_height - self.table_rect.height + 20)

    def fetch_history(self):
        target_user = self.user_input.text.strip()
        game_filter = self.game_input.text.strip()
        if target_user and hasattr(self.app, 'network'):
            self.scroll_y = 0
            self.app.network.send_action("query", query="match_history", 
                                       username=target_user, 
                                       game=game_filter if game_filter else None)

    def load_data(self, rows):
        self.history_data = rows
        self.update_scroll_limit()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()

            self.user_input.handle_event(event)
            self.game_input.handle_event(event)
            self.load_btn.handle_event(event)

            if event.type == pygame.MOUSEWHEEL:
                if self.table_rect.collidepoint(pygame.mouse.get_pos()):
                    self.scroll_y -= event.y * 30
                    self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
         
        for i in range(5):
            y = self.table_rect.centery + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(70 * s)), 2)
         
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time)*5), 3)
         
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (250 + i * 400) * s
            ny = (self.nav_height + 40 + (i % 2) * 40) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 4 + i) * 10), note_colors[i % 3])

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
         
        title_surf = self.font_title.render("MATCH HISTORY", True, self.colors["black"])
        screen.blit(title_surf, (self.app.WIDTH // 2 - title_surf.get_width() // 2, self.title_y))
        
        self.user_input.draw(screen)
        self.game_input.draw(screen)
        self.load_btn.color = theme_color
        self.load_btn.draw(screen)

         
        header_y = self.table_rect.y - int(40 * s)
        header_rect = pygame.Rect(self.table_rect.x, header_y, self.table_rect.width, int(40 * s))
        pygame.draw.rect(screen, theme_color, header_rect, border_radius=int(8 * s))
        
         
        col_w = self.table_rect.width
        cols = [("DATE", 20), ("GAME", 250), ("INDIV", 550), ("TEAM", 720), ("TIME", 880)]
        for text, x_off in cols:
            surf = self.font_header.render(text, True, self.colors["white"])
            screen.blit(surf, (header_rect.x + int(x_off * s), header_rect.y + int(10 * s)))

         
        pygame.draw.rect(screen, self.colors["panel"], self.table_rect, border_radius=int(10*s))
        
        old_clip = screen.get_clip()
        screen.set_clip(self.table_rect.inflate(-4, -4))
        
        for i, row in enumerate(self.history_data):
            row_y = self.table_rect.y + (i * self.row_height) - self.scroll_y
            
            if row_y + self.row_height > self.table_rect.y and row_y < self.table_rect.bottom:
                 
                if i % 2 == 0:
                    pygame.draw.rect(screen, self.colors["row_bg"], (self.table_rect.x + 5, row_y, self.table_rect.w - 10, self.row_height - 2), border_radius=5)
                
                 
                date = row.get("timestamp", "")[:16].replace("T", " ")
                game = row.get("game", "N/A")
                indiv = row.get("individual_score", 0)
                team_score = row.get("team_score", 0)
                duration = f"{row.get('game_time', 0)}s"

                 
                screen.blit(self.font_row.render(date, True, self.colors["black"]), (header_rect.x + int(20 * s), row_y + int(12 * s)))
                screen.blit(self.font_row.render(game, True, self.colors["black"]), (header_rect.x + int(250 * s), row_y + int(12 * s)))
                screen.blit(self.font_row.render(str(indiv), True, self.colors["black"]), (header_rect.x + int(550 * s), row_y + int(12 * s)))
                screen.blit(self.font_row.render(str(team_score), True, self.colors["black"]), (header_rect.x + int(720 * s), row_y + int(12 * s)))
                screen.blit(self.font_row.render(duration, True, self.colors["black"]), (header_rect.x + int(880 * s), row_y + int(12 * s)))

        screen.set_clip(old_clip)
        pygame.draw.rect(screen, theme_color, self.table_rect, 2, border_radius=int(10*s))