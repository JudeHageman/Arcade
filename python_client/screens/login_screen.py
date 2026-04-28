import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class LoginScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
         
        self.colors = {
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "white": (255, 255, 255),
            "staff": (235, 235, 235)
        }
        
        self.selected_faction = "blue"
        self.bg_color = self.colors["white"]

        cx, cy = self.app.WIDTH // 2, self.app.HEIGHT // 2

        
        self.user_box = InputBox(cx - 150, cy - 100, 300, 50)
        self.pass_box = InputBox(cx - 150, cy - 30, 300, 50, is_password=True)

        btn_y = cy + 50
        self.btn_blue = Button(cx - 155, btn_y, 100, 45, "BLUE", color=self.colors["blue"], action=lambda: self.set_faction("blue"))
        self.btn_pink = Button(cx - 50, btn_y, 100, 45, "PINK", color=self.colors["pink"], action=lambda: self.set_faction("pink"))
        self.btn_green = Button(cx + 55, btn_y, 100, 45, "GREEN", color=self.colors["green"], action=lambda: self.set_faction("green"))

        self.start_btn = Button(cx - 150, cy + 130, 300, 55, "START RESONANCE", color=self.colors["staff"], action=self.handle_start)

        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 72, bold=True)
        self.font_label = pygame.font.SysFont("Source Sans 3, Arial", 18, bold=True)
        self.time = 0

    def set_faction(self, faction):
        self.selected_faction = faction

    def handle_start(self):
        username = self.user_box.text.strip()
        if not username: return
        self.app.shared_data["username"] = username
        self.app.shared_data["faction"] = self.selected_faction
        if not self.app.player_trie.search(username):
            self.app.player_trie.insert(username)
        self.app.switch_screen("MENU")

    def draw_music_note(self, screen, pos, color):
         
        x, y = int(pos[0]), int(pos[1])
        head_radius = 11   
        stem_len = 32      
        flag_size = 10     
        
         
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + head_radius - 2, y), (x + head_radius - 2, y - stem_len), 3)
        pygame.draw.line(screen, color, (x + head_radius - 2, y - stem_len), (x + head_radius + 12, y - stem_len + flag_size), 3)

    def draw_decorations(self, screen):
        self.time += 0.02
        cx, cy = self.app.WIDTH // 2, self.app.HEIGHT // 2
        theme_color = self.colors[self.selected_faction]

         
        line_spacing = 30
        slope = 0.1 
        start_y_base = 320
        staff_lines_y = []
        for i in range(5):
            y_offset = i * line_spacing
            start_pos = (0, start_y_base + y_offset)
            end_pos = (self.app.WIDTH, start_y_base + y_offset - (self.app.WIDTH * slope))
            pygame.draw.line(screen, self.colors["staff"], start_pos, end_pos, 2)
            staff_lines_y.append(start_y_base + y_offset)

         
        res_positions = [(250, 250, 55), (1000, 220, 75), (200, 600, 85), (1150, 550, 65)]
        for x, y, r in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 5
            pygame.draw.circle(screen, theme_color, (x, y), int(r + pulse), 3)

         
        note_positions = [
            (150, staff_lines_y[1], self.colors["blue"], True),
            (380, staff_lines_y[3], self.colors["pink"], True),
            (550, staff_lines_y[0], self.colors["green"], True),
            (750, 550, self.colors["pink"], False),
            (950, staff_lines_y[4], self.colors["blue"], True),
            (1100, staff_lines_y[2], self.colors["green"], True),
            (250, 500, self.colors["blue"], False)
        ]

        for x, y_base, note_color, on_line in note_positions:
            if on_line:
                y_calc = y_base - (x * slope)
                hover = math.sin(self.time * 5 + x) * 3 
            else:
                y_calc = y_base
                hover = math.sin(self.time + x * 0.01) * 10
            
            self.draw_music_note(screen, (x, y_calc + hover), note_color)

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)

        theme_color = self.colors[self.selected_faction]
        title_surf = self.font_title.render("RESONANCE", True, self.colors["black"])
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 120))
        pygame.draw.rect(screen, theme_color, (title_rect.centerx - 80, title_rect.bottom + 5, 160, 4))
        screen.blit(title_surf, title_rect)

         
        u_label = self.font_label.render("ACCOUNT ID", True, (150, 150, 150))
        f_label = self.font_label.render("CHOOSE YOUR TEAM & START", True, (150, 150, 150))
        screen.blit(u_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 - 130))
        screen.blit(f_label, (self.app.WIDTH // 2 - 150, self.app.HEIGHT // 2 + 20))

        self.user_box.draw(screen)
        self.pass_box.draw(screen)
        self.btn_blue.draw(screen)
        self.btn_pink.draw(screen)
        self.btn_green.draw(screen)
        self.start_btn.draw(screen)

    def update(self): pass
    def handle_events(self, events):
        for event in events:
            self.user_box.handle_event(event)
            self.pass_box.handle_event(event)
            self.btn_blue.handle_event(event)
            self.btn_pink.handle_event(event)
            self.btn_green.handle_event(event)
            self.start_btn.handle_event(event)