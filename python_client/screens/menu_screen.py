# screens/menu_screen.py
import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button

class MenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        
        self.colors = {
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "white": (255, 255, 255),
            "staff": (230, 230, 230)
        }

        # --- 상단 네비게이션 버튼 설정 ---
        self.nav_buttons = []
        nav_names = ["GAMES", "CATALOG", "CHAT", "RANKING", "SEARCH", "HISTORY", "PROFILE", "LOGOUT"]
        
        btn_w = self.app.WIDTH // len(nav_names) - 10
        btn_h = 40
        
        for i, name in enumerate(nav_names):
            bx = 5 + i * (btn_w + 10)
            by = 15
            
            if name == "LOGOUT":
                action = self.handle_logout
                color = (255, 150, 150) # 로그아웃은 연한 빨강
            else:
                # 버튼 클릭 시 해당 화면으로 전환
                # (ArcadeApp에 등록된 화면 키값과 이름을 맞춰야 해!)
                screen_key = name if name != "RANKING" else "LEADERBOARD"
                action = lambda k=screen_key: self.app.switch_screen(k)
                color = self.colors["staff"]

            self.nav_buttons.append(Button(bx, by, btn_w, btn_h, name, color=color, action=action))

        self.font_user = pygame.font.SysFont("Source Sans 3, Arial", 18, bold=True)
        self.font_main = pygame.font.SysFont("Source Sans 3, Arial", 24, bold=True)
        self.time = 0

    def handle_logout(self):
        """로그아웃 처리"""
        if hasattr(self.app.network, "logout"):
            self.app.network.logout()
        else:
            self.app.shared_data["authenticated"] = False
            self.app.switch_screen("LOGIN")

    def draw_music_note(self, screen, pos, color):
        """음표 그리기 함수 (복구!)"""
        x, y = int(pos[0]), int(pos[1])
        head_radius = 11   
        stem_len = 32      
        flag_size = 10     
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + head_radius - 2, y), (x + head_radius - 2, y - stem_len), 3)
        pygame.draw.line(screen, color, (x + head_radius - 2, y - stem_len), (x + head_radius + 12, y - stem_len + flag_size), 3)

    def draw_decorations(self, screen):
        """오선지 및 파동 장식 그리기 (복구!)"""
        self.time += 0.02
        faction_name = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction_name, self.colors["blue"])
        
        # 오선지 그리기
        line_spacing = 30
        slope = 0.05
        start_y_base = 400 
        staff_lines_y = []
        for i in range(5):
            y_curr = start_y_base + (i * line_spacing)
            pygame.draw.line(screen, self.colors["staff"], (0, y_curr), (self.app.WIDTH, y_curr - 60), 2)
            staff_lines_y.append(y_curr)

        # 파동 원 그리기
        res_positions = [(200, 300, 50), (1000, 250, 70), (150, 600, 80), (1100, 550, 60)]
        for x, y, r in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 5
            pygame.draw.circle(screen, theme_color, (x, y), int(r + pulse), 2)

        # 음표 배치
        for i, y_base in enumerate(staff_lines_y):
            nx = 200 + i * 250
            ny = y_base - (nx * slope) + math.sin(self.time * 3 + nx) * 5
            self.draw_music_note(screen, (nx, ny), theme_color)

    def draw_header(self, screen):
        """상단 유저 정보 표시"""
        username = self.app.shared_data.get("username", "Guest")
        team = self.app.shared_data.get("team", "blue").upper()
        
        # 상단 바 배경
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, self.app.WIDTH, 110))
        
        user_info = f"PLAYER: {username} | TEAM: {team}"
        info_surf = self.font_user.render(user_info, True, (80, 80, 80))
        screen.blit(info_surf, (20, 75))

    def draw(self, screen):
        screen.fill(self.colors["white"])
        
        # 1. 배경 장식
        self.draw_decorations(screen)
        
        # 2. 헤더와 네비게이션 버튼
        self.draw_header(screen)
        for btn in self.nav_buttons:
            btn.draw(screen)
            
        # 3. 중앙 텍스트
        msg = "SELECT A MENU TO START THE RESONANCE"
        msg_surf = self.font_main.render(msg, True, (150, 150, 150))
        screen.blit(msg_surf, (self.app.WIDTH//2 - msg_surf.get_width()//2, self.app.HEIGHT//2))

    def handle_events(self, events):
        for event in events:
            for btn in self.nav_buttons:
                btn.handle_event(event)