import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class SignupScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        # 1. Vibrant Team Colors (Vibrant Pastel)
        self.bg_color = (255, 255, 255)
        self.c_pink = (255, 182, 193)
        self.c_green = (180, 238, 180)
        self.c_blue = (173, 216, 230)
        self.c_black = (30, 30, 30)
        self.c_staff = (235, 235, 235)

        cx, cy = self.app.WIDTH // 2, self.app.HEIGHT // 2

        # 2. Input Fields
        self.user_box = InputBox(cx - 150, cy - 120, 300, 45)
        self.pass_box = InputBox(cx - 150, cy - 40, 300, 45, is_password=True)
        
        # Current color selection (Default: blue)
        self.selected_color = "blue"
        
        # 3. Team Selection Buttons (Named by Color)
        btn_y = cy + 50
        self.btn_blue = Button(cx - 155, btn_y, 100, 45, "BLUE", 
                               color=self.c_blue, action=lambda: self.set_team("blue"))
        
        self.btn_pink = Button(cx - 50, btn_y, 100, 45, "PINK", 
                               color=self.c_pink, action=lambda: self.set_team("pink"))
        
        self.btn_green = Button(cx + 55, btn_y, 100, 45, "GREEN", 
                                color=self.c_green, action=lambda: self.set_team("green"))

        # Finalize Action
        self.confirm_btn = Button(cx - 150, cy + 130, 300, 50, "JOIN TEAM", 
                                  color=self.c_black, action=self.handle_finalize)
        
        self.back_btn = Button(40, 40, 100, 40, "BACK", 
                               color=(200, 200, 200), action=lambda: self.app.switch_screen("LOGIN"))

        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 56, bold=True)
        self.font_label = pygame.font.SysFont("Source Sans 3, Arial", 18, bold=True)
        self.time = 0
        

    def set_team(self, color_name):
        """Update the selected team color."""
        self.selected_color = color_name
        print(f"DEBUG: Team {color_name.upper()} selected.")

    def draw_decorations(self, screen):
        """Visual feedback: Only the color of the pulsing circle changes."""
        self.time += 0.02
        cx, cy = self.app.WIDTH // 2, self.app.HEIGHT // 2
        
        # Background Staff Lines
        
        # 1. Get active color based on selection
        active_color = getattr(self, f"c_{self.selected_color}")
        
        # 2. Pulsing effect
        pulse = math.sin(self.time * 2) * 15
        
        # 3. [FIXED SHAPE] Always draw a circle, only varying the color
        base_radius = 180
        pygame.draw.circle(screen, active_color, (cx, cy + 70), base_radius + int(pulse), 3)

    def handle_finalize(self):
        """Save the chosen username and team color to shared_data."""
        username = self.user_box.text.strip()
        if username:
            self.app.player_trie.insert(username)
            self.app.shared_data["username"] = username
            self.app.shared_data["faction"] = self.selected_color # Save color as team
            self.app.switch_screen("MENU")

    def handle_events(self, events):
        for event in events:
            self.user_box.handle_event(event)
            self.pass_box.handle_event(event)
            self.btn_blue.handle_event(event)
            self.btn_pink.handle_event(event)
            self.btn_green.handle_event(event)
            self.confirm_btn.handle_event(event)
            self.back_btn.handle_event(event)

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)
        
        # Title
        title_surf = self.font_title.render("SELECT YOUR COLOR", True, self.c_black)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 90))
        # Title underline matches the selected color
        underline_color = getattr(self, f"c_{self.selected_color}")
        pygame.draw.rect(screen, underline_color, (title_rect.centerx - 60, title_rect.bottom + 5, 120, 4))
        screen.blit(title_surf, title_rect)

        # Labels
        u_label = self.font_label.render("ACCOUNT ID", True, (150, 150, 150))
        f_label = self.font_label.render("JOIN A COLOR FACTION", True, (150, 150, 150))
        screen.blit(u_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 - 150))
        screen.blit(f_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 + 20))

        self.user_box.draw(screen)
        self.pass_box.draw(screen)
        self.btn_blue.draw(screen)
        self.btn_pink.draw(screen)
        self.btn_green.draw(screen)
        self.confirm_btn.draw(screen)
        self.back_btn.draw(screen)
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