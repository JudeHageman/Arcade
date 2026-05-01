# screens/profile_screen.py
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button

class ProfileScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.nav_height = 110
        
        
        self.colors = {
            "white": (255, 255, 255),
            "black": (30, 30, 30),
            "gray": (200, 200, 200),
            "light_gray": (248, 248, 248),
             
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120)
        }

          
        self.profile_data = {} 
        
         
        self.font_name = pygame.font.SysFont("arial", 42, bold=True)
        self.font_label = pygame.font.SysFont("arial", 20, bold=True)
        self.font_value = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_history = pygame.font.SysFont("arial", 16)

         
        self.logout_btn = Button(self.app.WIDTH - 150, self.app.HEIGHT - 80, 120, 45, 
                                 "LOGOUT", color=(255, 100, 100), action=self.app.network.logout)
        
        self.refresh_layout()

    def refresh_layout(self):
         
        self.card_rect = pygame.Rect(150, 180, 400, 450)
         
        self.stats_rect = pygame.Rect(580, 180, 550, 450)

    def fetch_profile(self):
         
        print("--- NETWORK: Requesting my profile data ---")
        self.app.network.send_action("query", query="profile")

    def load_data(self, data):
         
        self.profile_data = data
        print(f"--- UI DEBUG: Profile loaded for {data.get('username')} ---")

    def draw_decorations(self, screen, theme_color):
         
        for i in range(5):
            y = 150 + (i * 25)
            pygame.draw.line(screen, (240, 240, 240), (0, y), (self.app.WIDTH, y), 2)
             
            pygame.draw.circle(screen, theme_color, (100, 500), 150, 1)

    def draw(self, screen):
         
        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        # 2. 왼쪽: 유저 아이덴티티 카드
        pygame.draw.rect(screen, theme_color, self.card_rect, border_radius=20)
        # 아바타 서클
        pygame.draw.circle(screen, self.colors["white"], (self.card_rect.centerx, self.card_rect.y + 100), 70)
        
        # 유저네임 및 팀명
        username = self.profile_data.get("username", "GUEST").upper()
        name_surf = self.font_name.render(username, True, self.colors["white"])
        screen.blit(name_surf, (self.card_rect.centerx - name_surf.get_width()//2, self.card_rect.y + 190))
        
        team_surf = self.font_label.render(f"TEAM {faction.upper()}", True, self.colors["white"])
        screen.blit(team_surf, (self.card_rect.centerx - team_surf.get_width()//2, self.card_rect.y + 250))

         
        pygame.draw.rect(screen, self.colors["light_gray"], self.stats_rect, border_radius=20)
        pygame.draw.rect(screen, theme_color, self.stats_rect, 2, border_radius=20)

        stats = [
            ("TOTAL GAMES", self.profile_data.get("total_games", 0)),
            ("TOTAL SCORE", f"{self.profile_data.get('total_score', 0):,}"),
            ("BEST SCORE", f"{self.profile_data.get('best_score', 0):,}"),
            ("PLAY TIME", f"{self.profile_data.get('total_time', 0)}s")
        ]

        for i, (label, val) in enumerate(stats):
            y = self.stats_rect.y + 40 + (i * 70)
            lbl_surf = self.font_label.render(label, True, (100, 100, 100))
            val_surf = self.font_value.render(str(val), True, self.colors["black"])
            screen.blit(lbl_surf, (self.stats_rect.x + 40, y))
            screen.blit(val_surf, (self.stats_rect.x + 40, y + 25))

        # 4. 최근 히스토리 한 줄 요약
        history = self.profile_data.get("score_history", [])
        if history:
            h_y = self.stats_rect.y + 320
            pygame.draw.line(screen, theme_color, (self.stats_rect.x + 40, h_y), (self.stats_rect.right - 40, h_y), 2)
            latest = history[0]
            history_text = f"LATEST: {latest.get('game')} - {latest.get('score')} pts ({latest.get('timestamp')[:10]})"
            h_surf = self.font_history.render(history_text, True, (120, 120, 120))
            screen.blit(h_surf, (self.stats_rect.x + 40, h_y + 20))

        self.logout_btn.draw(screen)

    def handle_events(self, events):
        for event in events:
            self.logout_btn.handle_event(event)