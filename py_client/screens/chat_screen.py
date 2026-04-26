import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class ChatScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        # 1. Theme Colors (Resonance Style)
        self.bg_color = (255, 255, 255)
        self.c_pink = (255, 182, 193)
        self.c_green = (180, 238, 180)
        self.c_blue = (173, 216, 230)
        self.c_black = (30, 30, 30)
        self.c_staff = (235, 235, 235)

        # 2. Dynamic Centering for Responsive Layout
        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

        # 3. UI Components
        # Centered Chat Area dimensions
        self.chat_w, self.chat_h = 800, 450
        self.chat_rect = pygame.Rect(cx - self.chat_w//2, cy - 230, self.chat_w, self.chat_h)

        # Message input and Send button at the bottom of chat area
        input_w = 690
        self.msg_input = InputBox(self.chat_rect.x, self.chat_rect.bottom + 15, input_w, 45)
        self.send_btn = Button(self.chat_rect.x + input_w + 10, self.chat_rect.bottom + 15, 
                               100, 45, "SEND", color=self.c_blue, action=self.send_message)
        
        # Navigation
        self.back_btn = Button(40, 40, 100, 40, "BACK", color=self.c_pink, 
                               action=lambda: self.app.switch_screen("MENU"))

        # Fonts
        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 56, bold=True)
        self.font_msg = pygame.font.SysFont("Source Sans 3, Arial", 20)
        self.time = 0

        # Mock Message history
        self.messages = [{"user": "System", "text": "Welcome to the Resonance Global Chat!"}]

    def draw_decorations(self, screen):
        """Diagonal staff lines and pastel resonance circles."""
        self.time += 0.02
        
        # 1. Subtle Diagonal Staff Lines (Lowered density for chat clarity)
        line_spacing = 30
        slope = 0.08
        start_y_base = 400
        
        staff_lines_y = []
        for i in range(5):
            y_offset = i * line_spacing
            start_pos = (0, start_y_base + y_offset)
            end_pos = (self.app.WIDTH, start_y_base + y_offset - (self.app.WIDTH * slope))
            pygame.draw.line(screen, self.c_staff, start_pos, end_pos, 2)
            staff_lines_y.append(start_y_base + y_offset)

        # 2. Pastel Resonance Circles
        res_positions = [
            (150, 250, 60, self.c_pink), 
            (1130, 200, 80, self.c_blue), 
            (100, 650, 90, self.c_green), 
            (1180, 600, 70, self.c_pink)
        ]
        for x, y, base_radius, color in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 5
            pygame.draw.circle(screen, color, (x, y), int(base_radius + pulse), 3)

        # 3. Floating Music Notes (Avoiding the Chat Area center)
        note_positions = [
            (80, 400, self.c_black, False),
            (1150, 350, self.c_blue, False),
            (250, staff_lines_y[2], self.c_black, True),
            (1000, staff_lines_y[0], self.c_green, True)
        ]

        for x, y_base, color, on_line in note_positions:
            if on_line:
                y_calc = y_base - (x * slope)
                hover = math.sin(self.time * 5 + x) * 3
            else:
                y_calc = y_base
                hover = math.sin(self.time + x * 0.01) * 10
            self.draw_music_note(screen, (x, y_calc + hover), color)

    def draw_music_note(self, screen, pos, color):
        x, y = int(pos[0]), int(pos[1])
        head_radius = 10
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + head_radius - 2, y), (x + head_radius - 2, y - 30), 3)
        pygame.draw.line(screen, color, (x + head_radius - 2, y - 30), (x + head_radius + 12, y - 20), 3)

    def send_message(self):
        text = self.msg_input.text.strip()
        if text:
            self.messages.append({"user": "Me", "text": text})
            self.msg_input.text = ""
            # Resetting text surface (assuming InputBox logic from your code)
            self.msg_input.txt_surface = self.msg_input.font.render("", True, (30, 30, 30))

    def handle_events(self, events):
        for event in events:
            self.msg_input.handle_event(event)
            self.send_btn.handle_event(event)
            self.back_btn.handle_event(event)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.msg_input.active:
                    self.send_message()

    def draw_messages(self, screen):
        """Render the chat log inside the centered box."""
        # Chat area background
        pygame.draw.rect(screen, (255, 255, 255), self.chat_rect, border_radius=15)
        # Subtle border for authority
        pygame.draw.rect(screen, self.c_black, self.chat_rect, 2, border_radius=15)

        # Render message list
        y_pos = self.chat_rect.y + 25
        for msg in self.messages[-16:]: # Show more messages due to larger height
            chat_text = f"{msg['user']}: {msg['text']}"
            color = self.c_blue if msg['user'] == "Me" else self.c_black
            msg_surf = self.font_msg.render(chat_text, True, color)
            screen.blit(msg_surf, (self.chat_rect.x + 20, y_pos))
            y_pos += 26

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)

        # Centered Title
        title_surf = self.font_title.render("GLOBAL CHAT", True, self.c_black)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 85))
        pygame.draw.rect(screen, self.c_black, (title_rect.centerx - 60, title_rect.bottom + 5, 120, 3))
        screen.blit(title_surf, title_rect)

        # UI Elements
        self.draw_messages(screen)
        self.msg_input.draw(screen)
        self.send_btn.draw(screen)
        self.back_btn.draw(screen)