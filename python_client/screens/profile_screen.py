import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class ProfileScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        
        # 1. 색상 설정 (딕셔너리로 관리하는 게 에러 방지에 훨씬 좋아!)
        self.colors = {
            "white": (255, 255, 255),
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "staff": (235, 235, 235),
            "gray": (150, 150, 150)
        }

        self.scale = max(self.app.WIDTH / 1280, 0.6)
        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

        # 2. UI 컴포넌트
        self.box_w = int(600 * self.scale)
        input_w = int(440 * self.scale)
        self.search_input = InputBox(cx - self.box_w//2, cy + int(60 * self.scale), input_w, int(45 * self.scale))
        self.search_btn = Button(cx - self.box_w//2 + input_w + 10, cy + int(60 * self.scale), 
                                 int(150 * self.scale), int(45 * self.scale), 
                                 "FIND PLAYER", color=self.colors["green"], action=self.perform_search)
        
        self.back_btn = Button(40, 40, 100, 40, "< BACK", color=self.colors["staff"], 
                               action=lambda: self.app.switch_screen("MENU"))

        # 폰트
        self.font_title = pygame.font.SysFont("Arial", int(56 * self.scale), bold=True)
        self.font_label = pygame.font.SysFont("Arial", int(22 * self.scale), bold=True)
        self.font_data = pygame.font.SysFont("Arial", int(18 * self.scale))
        
        self.time = 0
        # ⭐ 서버에서 온 결과를 담을 리스트
        self.search_results = [] 
        self.status_msg = ""

    def perform_search(self):
        """서버에 Trie 검색 요청 보내기"""
        query = self.search_input.text.strip()
        if query:
            # 서버로 요청 전송
            self.app.network.send_action("query", query="player_search", prefix=query)
            self.status_msg = f"Searching for '{query}'..."
        else:
            self.status_msg = "Please enter a name."

    # ⭐ [추가] 서버에서 검색 결과가 도착하면 NetworkManager가 이 함수를 호출해!
    def update_search_results(self, results):
        self.search_results = results # [{'username': 'minju', 'team': 'pink'}, ...]
        if not results:
            self.status_msg = "No players found."
        else:
            self.status_msg = f"Found {len(results)} matches:"

    def draw_search_results(self, screen):
        """검색된 유저 리스트를 화면에 그리기"""
        if not self.search_results and not self.status_msg:
            return

        cx = self.app.WIDTH // 2
        s = self.scale
        start_y = self.app.HEIGHT - int(220 * s)

        # 상태 메시지 (Searching... 등)
        if self.status_msg:
            msg_surf = self.font_data.render(self.status_msg, True, self.colors["gray"])
            screen.blit(msg_surf, (cx - self.box_w//2, start_y - int(30 * s)))

        # 결과 리스트 (최대 3개만 보여주기)
        for i, player in enumerate(self.search_results[:3]):
            res_rect = pygame.Rect(cx - self.box_w//2, start_y + (i * int(60 * s)), self.box_w, int(50 * s))
            pygame.draw.rect(screen, (250, 250, 250), res_rect, border_radius=10)
            pygame.draw.rect(screen, self.colors["staff"], res_rect, 2, border_radius=10)

            name_text = self.font_label.render(player['username'], True, self.colors["black"])
            team_text = self.font_data.render(player['team'].upper(), True, self.colors.get(player['team'], self.colors["blue"]))
            
            screen.blit(name_text, (res_rect.x + 20, res_rect.y + int(12 * s)))
            screen.blit(team_text, (res_rect.right - team_text.get_width() - 20, res_rect.y + int(15 * s)))

    def draw_decorations(self, screen):
        self.time += 0.02
        s = self.scale
        # ⭐ shared_data의 키를 "team"으로 통일!
        team_name = self.app.shared_data.get("team", "blue")
        theme_color = self.colors.get(team_name, self.colors["blue"])
        
        # 오선 및 공명 원 그리기 (기존 로직 유지)
        for i in range(5):
            y = int(400 * s) + (i * int(30 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(100 * s)), 2)
        
        res_positions = [(180*s, 200*s, 55*s), (self.app.WIDTH - 180*s, 250*s, 75*s)]
        for x, y, r in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 4
            pygame.draw.circle(screen, theme_color, (int(x), int(y)), int(r + pulse), 3)

    def draw(self, screen):
        screen.fill(self.colors["white"])
        self.draw_decorations(screen)

         
        team_name = self.app.shared_data.get("team", "blue")
        theme_color = self.colors.get(team_name, self.colors["blue"])
        
        title_surf = self.font_title.render("PLAYER PROFILE", True, self.colors["black"])
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, int(90 * self.scale)))
        pygame.draw.rect(screen, theme_color, (title_rect.centerx - 80, title_rect.bottom + 5, 160, 3))
        screen.blit(title_surf, title_rect)

        self.draw_my_profile(screen)
        self.search_input.draw(screen)
        self.search_btn.draw(screen)
        self.draw_search_results(screen)  
        self.back_btn.draw(screen)

     
    def draw_my_profile(self, screen):
        cx = self.app.WIDTH // 2
        name = self.app.shared_data.get("username", "Guest")
        team = self.app.shared_data.get("team", "blue")
        theme_color = self.colors.get(team, self.colors["blue"])
        
        card_rect = pygame.Rect(cx - self.box_w//2, int(160 * self.scale), self.box_w, int(140 * self.scale))
        pygame.draw.rect(screen, (255, 255, 255), card_rect, border_radius=15)
        pygame.draw.rect(screen, self.colors["black"], card_rect, 2, border_radius=15)
        
        screen.blit(self.font_label.render(f"PLAYER ID: {name}", True, self.colors["black"]), (card_rect.x + 30, card_rect.y + 25))
        screen.blit(self.font_label.render(f"TEAM: {team.upper()}", True, theme_color), (card_rect.x + 30, card_rect.y + 60))

    def handle_events(self, events):
        for event in events:
            self.search_input.handle_event(event)
            self.search_btn.handle_event(event)
            self.back_btn.handle_event(event)