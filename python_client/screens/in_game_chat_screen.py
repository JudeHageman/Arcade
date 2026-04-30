import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox
import subprocess

class InGameChatScreen(BaseScreen):
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

         
        self.global_messages = [{"user": "System", "text": "Global Channel Live."}]
        self.team_messages = [{"user": "System", "text": "Team Channel Live."}]

         
        self.global_input = InputBox(0, 0, 100, 40)
        self.team_input = InputBox(0, 0, 100, 40)
         
        self.quit_btn = Button(0, 0, 100, 40, "QUIT & RETURN", color=self.colors["pink"], action=self.handle_quit)

        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
        """창 크기에 따라 모든 요소를 5:5 비율로 재배치 (최소 크기 보호 로직 포함)"""
         
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        
         
        side_pad = int(100 * s)
        top_pad = int(70 * s)
        bottom_pad = int(100 * s)
        gap = int(40 * s)

         
        total_available_h = max(self.app.HEIGHT - top_pad - bottom_pad - gap, 300)
        section_h = total_available_h // 2   

         
        g_chat_h = int(section_h * 0.75)
        self.global_rect = pygame.Rect(side_pad, top_pad, self.app.WIDTH - (side_pad * 2), g_chat_h)
        self.global_input.rect = pygame.Rect(side_pad, self.global_rect.bottom + int(8*s), self.global_rect.width, int(42*s))

         
        t_section_y = self.global_input.rect.bottom + gap
        self.team_rect = pygame.Rect(side_pad, t_section_y, self.global_rect.width, g_chat_h)
        self.team_input.rect = pygame.Rect(side_pad, self.team_rect.bottom + int(8*s), self.global_rect.width, int(42*s))

         
        btn_w, btn_h = int(260 * s), int(48 * s)
        self.quit_btn.rect = pygame.Rect(self.app.WIDTH//2 - btn_w//2, self.app.HEIGHT - int(75*s), btn_w, btn_h)

         
        self.font_title = pygame.font.SysFont("Arial", max(int(36 * s), 24), bold=True)
        self.font_label = pygame.font.SysFont("Arial", max(int(18 * s), 14), bold=True)
        self.font_msg = pygame.font.SysFont("Arial", max(int(15 * s), 12))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                 
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()

            self.global_input.handle_event(event)
            self.team_input.handle_event(event)
            self.quit_btn.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.process_chat_send()

    
    def handle_quit(self):
        process = self.app.shared_data.get("current_game_process")
        
        if process and process.poll() is None:
            print("DEBUG: Terminating game process...")
            process.terminate()
            try:
                process.wait(timeout=3)  # [USER] stdout이 나올 때까지 최대 3초 기다림
            except subprocess.TimeoutExpired:
                process.kill()
        
        self.app.shared_data["current_game_process"] = None
        self.app.switch_screen("CATALOG")

    def draw_decorations(self, screen, theme_color):
         
        self.time += 0.02
        s = self.scale
         
        for i in range(5):
            y = int(500*s) + (i * int(25*s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(80*s)), 2)
         
        pygame.draw.circle(screen, theme_color, (int(80*s), int(80*s)), int(45*s + math.sin(self.time)*5), 3)
         
        for i, color_name in enumerate(["blue", "green", "pink"]):
            nx = (200 + i*400) * s
            ny = (60 + (i%2)*20) * s
            hover = math.sin(self.time * 4 + i) * (10 * s)
            self.draw_music_note(screen, (nx, ny + hover), self.colors[color_name])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 10 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 28*s), int(3*s))
        pygame.draw.line(screen, color, (x + r - 2, y - 28*s), (x + r + 10*s, y - 18*s), int(3*s))

    def draw_chat_box(self, screen, rect, title, messages, color):
        """채팅 박스와 메시지를 화면에 그림"""
        s = self.scale
        if rect.height < 10: return
        
        # 배경 및 테두리
        pygame.draw.rect(screen, self.colors["white"], rect, border_radius=int(10*s))
        pygame.draw.rect(screen, color, rect, 2, border_radius=int(10*s))
        
        # 타이틀 레이블
        lbl = self.font_label.render(title, True, color)
        screen.blit(lbl, (rect.x + 5, rect.y - int(22*s)))

        # 메시지 렌더링 (폰트 높이에 맞춰 동적 간격 조절)
        line_height = self.font_msg.get_linesize()
        max_msgs = max(rect.height // line_height, 1)
        y_off = rect.y + 10
        
        for msg in messages[-int(max_msgs):]:
            txt = self.font_msg.render(f"{msg['user']}: {msg['text']}", True, self.colors["black"])
            screen.blit(txt, (rect.x + 12, y_off))
            y_off += line_height
    def update(self): pass

    def draw(self, screen):
        
        faction = self.app.shared_data.get("faction", "blue")
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

         
        title = self.font_title.render("GAME DASHBOARD", True, self.colors["black"])
        screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, int(15*self.scale)))

        
        self.draw_chat_box(screen, self.global_rect, "GLOBAL CHAT", self.global_messages, self.colors["blue"])
        self.global_input.draw(screen)

         
        self.draw_chat_box(screen, self.team_rect, f"TEAM {faction.upper()} CHAT", self.team_messages, theme_color)
        self.team_input.draw(screen)

        self.quit_btn.draw(screen)

    def load_history(self, history):
        """로그인 시 서버에서 받은 과거 채팅 기록을 UI에 로드"""
        # history는 {'GameName': [{'sender': '...', 'message': '...'}, ...]} 구조
        # 여기서는 편의상 모든 게임의 기록을 GLOBAL에 합치거나 특정 게임만 필터링해서 보여줌
        self.global_messages = []
        for game_name, msgs in history.items():
            for m in msgs:
                self.global_messages.append({"user": m['sender'], "text": m['message']})
        print(f"--- UI DEBUG: Loaded {len(self.global_messages)} historical messages ---")

    def append_message(self, chat_type, user, text):
        """실시간으로 들어오는 메시지를 리스트에 추가"""
        new_msg = {"user": user, "text": text}
        if chat_type == "global":
            self.global_messages.append(new_msg)
        else:
            self.team_messages.append(new_msg)
            
        # 메시지가 너무 많으면 위에서부터 지워줌 (성능 최적화)
        if len(self.global_messages) > 100: self.global_messages.pop(0)

    def process_chat_send(self):
        """채팅 입력 후 엔터 쳤을 때 서버로 전송 (모더레이터 검사 포함)"""
        # 1. 글로벌 채팅 전송
        if self.global_input.active and self.global_input.text.strip():
            msg = self.global_input.text.strip()
            is_valid, reason = self.app.moderator.validate_message(self.app.shared_data["username"], msg)
            
            if is_valid:
                self.app.network.send_action("chat", game="Immortal Tree", message=msg)
                self.global_input.text = ""
            else:
                self.global_messages.append({"user": "System", "text": f"Blocked: {reason}"})

        # 2. 팀 채팅 전송
        elif self.team_input.active and self.team_input.text.strip():
            msg = self.team_input.text.strip()
            # 팀 채팅은 별도의 채널로 전송 (서버 로직에 따라 수정 가능)
            self.app.network.send_action("chat", game="TeamChannel", message=msg)
            self.team_input.text = ""


    def append_message(self, chat_type, user, text):
        """NetworkManager가 호출하여 새 메시지를 UI 리스트에 추가"""
        new_msg = {"user": user, "text": text}
        
        if chat_type == "global":
            self.global_messages.append(new_msg)
            if len(self.global_messages) > 100: self.global_messages.pop(0)
        else:
            self.team_messages.append(new_msg)
            if len(self.team_messages) > 100: self.team_messages.pop(0)
            
        print(f"--- UI DEBUG: Message added to {chat_type} ({user}) ---")