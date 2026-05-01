import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class InGameChatScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        self.nav_height = 110  # 상단 메뉴 높이 고정
        
        self.colors = {
            "white": (255, 255, 255),
            "black": (30, 30, 30),
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "chat_bg": (252, 252, 252),
            "staff": (235, 235, 235)
        }

        self.team_messages = [] 
        self.chat_input = InputBox(0, 0, 100, 45)
        # 종료 버튼은 아래쪽에 배치
        self.quit_btn = Button(0, 0, 220, 45, "QUIT & RETURN", color=self.colors["black"], action=self.handle_quit)

        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
        """네비게이션 바 아래로 레이아웃 재배치 (최소 배율 0.6)"""
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

        # 폰트 설정
        self.font_title = pygame.font.SysFont("Arial", max(int(36 * s), 24), bold=True)
        self.font_msg = pygame.font.SysFont("Arial", max(int(17 * s), 13))
        self.font_ui = pygame.font.SysFont("Arial", max(int(18 * s), 14), bold=True)

        # 1. 타이틀 위치 (nav_height 아래)
        self.title_y = self.nav_height + int(25 * s)

        # 2. 채팅 박스 위치 (타이틀 아래)
        chat_w = int(900 * s)
        # 화면 높이에 맞춰 채팅창 높이 조절 (하단 버튼 공간 제외)
        chat_h = max(self.app.HEIGHT - self.title_y - int(220 * s), 250)
        self.chat_rect = pygame.Rect(cx - chat_w // 2, self.title_y + int(60 * s), chat_w, chat_h)
        
        # 3. 입력창 위치 (채팅 박스 바로 아래)
        self.chat_input.rect = pygame.Rect(self.chat_rect.x, self.chat_rect.bottom + int(15 * s), chat_w, int(45 * s))

        # 4. 종료 버튼 (맨 아래)
        btn_w, btn_h = int(240 * s), int(48 * s)
        self.quit_btn.rect = pygame.Rect(cx - btn_w // 2, self.app.HEIGHT - int(80 * s), btn_w, btn_h)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()

            self.chat_input.handle_event(event)
            self.quit_btn.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.process_send()

    def process_send(self):
        msg = self.chat_input.text.strip()
        if msg and hasattr(self.app, 'network'):
            self.app.network.send_action("team_chat", message=msg)
            self.chat_input.text = ""

    def append_message(self, data):
        sender = data.get('sender', 'Unknown')
        message = data.get('message', '')
        timestamp = data.get('timestamp', '')[11:16] # HH:MM

        if sender and message:
            self.team_messages.append({"user": sender, "text": message, "time": timestamp})
            if len(self.team_messages) > 100: self.team_messages.pop(0)

    def handle_quit(self):
        # 점수 전송 및 프로세스 종료 (기존 로직 유지)
        my_last_score = self.app.shared_data.get("last_score", 0) 
        current_game = self.app.shared_data.get("selected_game", "unknown_game")

        if hasattr(self.app, 'network_manager') and self.app.network_manager:
            self.app.network_manager.send_score(current_game, my_last_score)

        process = self.app.shared_data.get("current_game_process")
        if process and process.poll() is None:
            process.terminate()
        
        self.app.switch_screen("CATALOG")

    def draw_decorations(self, screen, theme_color):
        self.time += 0.02
        s = self.scale
        # 오선
        for i in range(5):
            y = self.chat_rect.centery + (i * int(25 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(60 * s)), 2)
        # 팀 공명 원
        pygame.draw.circle(screen, theme_color, (int(80 * s), self.nav_height + int(80 * s)), int(45 * s + math.sin(self.time)*5), 3)
        # 알록달록 음표
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (150 + i * 450) * s
            ny = (self.nav_height + 40 + (i%2)*40) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time*4 + i)*10), note_colors[i%3])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 10 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 28*s), int(3*s))
        pygame.draw.line(screen, color, (x + r - 2, y - 28*s), (x + r + 10*s, y - 18*s), int(3*s))

    def draw(self, screen):
        faction = self.app.shared_data.get("team", "blue").lower()
        theme_color = self.colors.get(faction, self.colors["blue"])
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        # 1. 제목 (네비게이션 바 아래)
        title_surf = self.font_title.render(f"TEAM {faction.upper()} DASHBOARD", True, theme_color)
        screen.blit(title_surf, (self.app.WIDTH//2 - title_surf.get_width()//2, self.title_y))

        # 2. 채팅 박스
        s = self.scale
        pygame.draw.rect(screen, self.colors["chat_bg"], self.chat_rect, border_radius=int(12*s))
        pygame.draw.rect(screen, theme_color, self.chat_rect, 2, border_radius=int(12*s))

        # 3. 메시지 렌더링 (박스 안으로 제한)
        line_height = int(28 * s)
        max_lines = (self.chat_rect.height - 30) // line_height
        y_pos = self.chat_rect.y + 15
        
        # 박스 영역을 벗어나지 않게 클리핑 설정 (Surface 사용 가능 시)
        for msg in self.team_messages[-int(max_lines):]:
            # 텍스트가 너무 길면 잘라버림 (박스 폭 - 여백)
            limit = self.chat_rect.width - 40
            display_text = f"[{msg['time']}] {msg['user']}: {msg['text']}"
            
            # 간단한 Truncation 로직: 텍스트가 너무 길면 '...' 추가
            if self.font_msg.size(display_text)[0] > limit:
                while self.font_msg.size(display_text + "...")[0] > limit:
                    display_text = display_text[:-1]
                display_text += "..."

            msg_surf = self.font_msg.render(display_text, True, self.colors["black"])
            screen.blit(msg_surf, (self.chat_rect.x + 15, y_pos))
            y_pos += line_height

        # 4. 입력창 및 버튼
        self.chat_input.draw(screen)
        self.quit_btn.draw(screen)