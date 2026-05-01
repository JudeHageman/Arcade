import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class LeaderboardScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        self.nav_height = 110  # 상단 바 높이

        self.colors = {
            "white": (255, 255, 255),
            "black": (30, 30, 30),
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "staff": (235, 235, 235),
            "row_bg": (248, 248, 248)
        }

        # --- 데이터 저장소 ---
        self.rank_data = [] 
        self.own_rank = None
        self.sort_options = ["best_score", "total_score", "play_time"]
        self.current_sort = "best_score"

        # --- UI 컴포넌트 미리 생성 ---
        self.game_input = InputBox(0, 0, 250, 40)
        self.game_input.text = "Immortal Tree"
        self.load_btn = Button(0, 0, 100, 40, "LOAD", color=(100, 200, 100), action=self.fetch_leaderboard)
        self.option_buttons = []
        
        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
        """네비게이션 바 아래로 모든 요소 재배치 및 스케일링"""
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

        # 폰트 설정
        self.font_title = pygame.font.SysFont("Arial", max(int(36 * s), 24), bold=True)
        self.font_header = pygame.font.SysFont("Arial", max(int(20 * s), 15), bold=True)
        self.font_row = pygame.font.SysFont("Arial", max(int(18 * s), 13))

        # 1. 상단 컨트롤 영역 (검색창 + 정렬 버튼)
        ctrl_y = self.nav_height + int(30 * s)
        
        # 검색창 위치
        self.game_input.rect = pygame.Rect(cx - int(480 * s), ctrl_y, int(220 * s), int(40 * s))
        
        # 정렬 버튼 위치
        labels = ["Best Score", "Total Score", "Play Time"]
        btn_w, btn_h = int(160 * s), int(40 * s)
        spacing = int(10 * s)
        btn_start_x = self.game_input.rect.right + spacing

        self.option_buttons = []
        for i, label in enumerate(labels):
            btn = Button(btn_start_x + i * (btn_w + spacing), ctrl_y, btn_w, btn_h, label,
                         color=self.colors["staff"],
                         action=lambda opt=self.sort_options[i]: self.set_sort(opt))
            self.option_buttons.append(btn)

        # 로드 버튼
        self.load_btn.rect = pygame.Rect(cx + int(390 * s), ctrl_y, int(90 * s), int(40 * s))

        # 2. 테이블 영역
        self.table_y = ctrl_y + int(70 * s)
        self.table_rect = pygame.Rect(cx - int(500 * s), self.table_y + int(40 * s), int(1000 * s), 0) # 높이는 나중에
        self.table_rect.height = max(self.app.HEIGHT - self.table_rect.y - int(40 * s), 200)

    def set_sort(self, option):
        self.current_sort = option
        self.fetch_leaderboard()

    def fetch_leaderboard(self):
        game_name = self.game_input.text.strip()
        if game_name and hasattr(self.app, 'network'):
            self.app.network.send_action("query", query="leaderboard", game=game_name, sort_by=self.current_sort, top_n=20)

    def load_data(self, data):
        self.rank_data = data.get("rows", [])
        self.own_rank = data.get("own_rank")

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
        # 배경 오선
        for i in range(5):
            y = self.table_rect.centery + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(60 * s)), 2)
        # 팀 공명 원
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time)*5), 3)
        # 알록달록 음표
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (150 + i * 400) * s
            ny = (self.nav_height + 40 + (i % 2) * 40) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 3 + i) * 12), note_colors[i % 3])

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
            self.game_input.handle_event(event)
            self.load_btn.handle_event(event)
            for btn in self.option_buttons: btn.handle_event(event)

    def update(self): pass

    def draw(self, screen):
        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        s = self.scale
        # 1. 상단 컨트롤 영역 그리기
        self.game_input.draw(screen)
        for i, btn in enumerate(self.option_buttons):
            if self.current_sort == self.sort_options[i]:
                pygame.draw.rect(screen, theme_color, (btn.rect.x - 2, btn.rect.y - 2, btn.rect.w + 4, btn.rect.h + 4), 2, border_radius=8)
                btn.color = theme_color
            else:
                btn.color = self.colors["staff"]
            btn.draw(screen)
        self.load_btn.draw(screen)

        # 2. 내 순위 강조 표시
        if self.own_rank:
            rank_surf = self.font_header.render(f"YOUR RANK: #{self.own_rank}", True, theme_color)
            screen.blit(rank_surf, (self.table_rect.x, self.table_y + int(10 * s)))

        # 3. 테이블 헤더
        header_rect = pygame.Rect(self.table_rect.x, self.table_rect.y, self.table_rect.width, int(40 * s))
        pygame.draw.rect(screen, theme_color, header_rect, border_radius=int(8 * s))
        
        screen.blit(self.font_header.render("RANK", True, self.colors["white"]), (header_rect.x + int(20 * s), header_rect.y + int(8 * s)))
        screen.blit(self.font_header.render("PLAYER NAME", True, self.colors["white"]), (header_rect.x + int(150 * s), header_rect.y + int(8 * s)))
        screen.blit(self.font_header.render("SCORE / VALUE", True, self.colors["white"]), (header_rect.right - int(180 * s), header_rect.y + int(8 * s)))

        # 4. 데이터 리스트
        for i, row in enumerate(self.rank_data):
            row_y = header_rect.bottom + int(15 * s) + (i * int(35 * s))
            if row_y + int(30 * s) > self.table_rect.bottom: break

            if i % 2 == 0:
                pygame.draw.rect(screen, self.colors["row_bg"], (self.table_rect.x, row_y - 5, self.table_rect.width, int(30 * s)), border_radius=5)

            rank_num = f"{i+1:02}"
            name = row.get("username", "Unknown")
            val = row.get("score", 0)
            
            # 상위 3등은 팀 컬러로 강조
            color = theme_color if i < 3 else (80, 80, 80)
            screen.blit(self.font_row.render(rank_num, True, color), (header_rect.x + int(25 * s), row_y))
            screen.blit(self.font_row.render(name, True, self.colors["black"]), (header_rect.x + int(150 * s), row_y))
            screen.blit(self.font_row.render(f"{val:,}", True, self.colors["black"]), (header_rect.right - int(180 * s), row_y))