import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class LoginScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        # 1. Vibrant Pastel Color Palette (Original colors with higher saturation)
        self.bg_color = (255, 255, 255)
        self.c_pink = (255, 182, 193)
        self.c_green = (180, 238, 180)
        self.c_blue = (173, 216, 230)
        self.c_black = (30, 30, 30)
        self.c_staff = (235, 235, 235)   # Subtle gray for staff lines

        # 2. Dynamic Centering Logic
        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

        # 3. UI Components
        self.user_box = InputBox(cx - 150, cy - 60, 300, 50)
        self.pass_box = InputBox(cx - 150, cy + 30, 300, 50, is_password=True)
        
        # Buttons with Vibrant Pastel accents
        self.login_btn = Button(cx - 155, cy + 110, 145, 55, "LOGIN", color=self.c_blue, action=self.handle_login)
        self.signup_btn = Button(cx + 10, cy + 110, 145, 55, "SIGN UP", color=self.c_pink, action=self.handle_signup)

        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 72, bold=True)
        self.font_label = pygame.font.SysFont("Source Sans 3, Arial", 18, bold=True)
        self.time = 0

    def draw_decorations(self, screen):
        """Clean and vibrant design with diagonal staff and resonance circles."""
        self.time += 0.02
        
        # 1. Diagonal Staff Lines
        line_spacing = 30
        slope = 0.1 
        start_y_base = 300
        
        staff_lines_y = []
        for i in range(5):
            y_offset = i * line_spacing
            start_pos = (0, start_y_base + y_offset)
            end_pos = (self.app.WIDTH, start_y_base + y_offset - (self.app.WIDTH * slope))
            pygame.draw.line(screen, self.c_staff, start_pos, end_pos, 2)
            staff_lines_y.append(start_y_base + y_offset)

        # 2. Vibrant Resonance Circles (Pulsing background)
        res_positions = [
            (250, 250, 50, self.c_pink), 
            (1000, 220, 70, self.c_blue), 
            (150, 580, 80, self.c_green), 
            (1150, 530, 60, self.c_pink)
        ]
        for x, y, base_radius, color in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 4
            pygame.draw.circle(screen, color, (x, y), int(base_radius + pulse), 3)

        # 3. Musical Notes (Repositioned to avoid Title area)
        note_positions = [
            (150, staff_lines_y[1], self.c_black, True),
            (380, staff_lines_y[3], self.c_blue, True),
            (550, staff_lines_y[0], self.c_black, True),
            (750, 550, self.c_green, False),
            (950, staff_lines_y[4], self.c_pink, True),
            (1100, staff_lines_y[2], self.c_black, True),
            (250, 500, self.c_blue, False)
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
        """Minimalist music note."""
        x, y = int(pos[0]), int(pos[1])
        head_radius = 11   
        stem_len = 32      
        flag_size = 10     
        
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + head_radius - 2, y), (x + head_radius - 2, y - stem_len), 3)
        pygame.draw.line(screen, color, (x + head_radius - 2, y - stem_len), (x + head_radius + 12, y - stem_len + flag_size), 3)

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)

        # Main Title
        title_surf = self.font_title.render("RESONANCE", True, self.c_black)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 140))
        
        # Accent line with vibrant Blue
        pygame.draw.rect(screen, self.c_blue, (title_rect.centerx - 60, title_rect.bottom + 5, 120, 3))
        screen.blit(title_surf, title_rect)
        
        # Labels
        u_label = self.font_label.render("ACCOUNT ID", True, (140, 140, 140))
        p_label = self.font_label.render("ACCESS KEY", True, (140, 140, 140))
        screen.blit(u_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 - 90))
        screen.blit(p_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 + 0))

        # UI Elements
        self.user_box.draw(screen)
        self.pass_box.draw(screen)
        self.login_btn.draw(screen)
        self.signup_btn.draw(screen)

    def handle_login(self):
        username = self.user_box.text.strip()
        if username and self.app.player_trie.search(username):
            self.app.shared_data["username"] = username
            self.app.switch_screen("MENU")
        else:
            print("DEBUG: User not found.")

    def handle_signup(self):
        self.app.switch_screen("SIGNUP")

    def handle_events(self, events):
        for event in events:
            self.user_box.handle_event(event)
            self.pass_box.handle_event(event)
            self.login_btn.handle_event(event)
            self.signup_btn.handle_event(event)