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
            "staff": (235, 235, 235)
        }

        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

         
        btn_w, btn_h = 350, 55
        spacing = 20
         
        start_y = cy - 20 

        self.buttons = [
            Button(cx - btn_w//2, start_y, btn_w, btn_h, "GAME CATALOG", 
                   color=self.colors["green"], action=lambda: self.app.switch_screen("CATALOG")),
            
            Button(cx - btn_w//2, start_y + (btn_h + spacing), btn_w, btn_h, "LEADERBOARD", 
                   color=self.colors["blue"], action=lambda: self.app.switch_screen("LEADERBOARD")),
            
            Button(cx - btn_w//2, start_y + (btn_h + spacing) * 2, btn_w, btn_h, "MY PROFILE", 
                   color=self.colors["pink"], action=lambda: self.app.switch_screen("PROFILE"))
        ]

        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 64, bold=True)
        self.font_user = pygame.font.SysFont("Source Sans 3, Arial", 20, bold=True)
        self.time = 0

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
        
         
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = self.colors.get(faction_name, self.colors["blue"])
        
         
        line_spacing = 30
        slope = 0.1
        start_y_base = 350 
        staff_lines_y = []
        for i in range(5):
            y_offset = i * line_spacing
            y_curr = start_y_base + y_offset
            pygame.draw.line(screen, self.colors["staff"], (0, y_curr), (self.app.WIDTH, y_curr - 100), 2)
            staff_lines_y.append(y_curr)

         
        res_positions = [(200, 280, 55), (1050, 250, 75), (150, 620, 85), (1100, 600, 65)]
        for x, y, r in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 4
            pygame.draw.circle(screen, theme_color, (x, y), int(r + pulse), 3)

         
        note_positions = [
            (120, staff_lines_y[1], self.colors["blue"], True),
            (450, staff_lines_y[3], self.colors["green"], True),
            (850, staff_lines_y[0], self.colors["pink"], True),
            (1150, 450, self.colors["blue"], False),
            (300, 600, self.colors["green"], False),
            (950, 150, self.colors["pink"], False)
        ]

        for x, y_base, note_color, on_line in note_positions:
            if on_line:
                y_calc = y_base - (x * slope)
                hover = math.sin(self.time * 5 + x) * 3
            else:
                y_calc = y_base
                hover = math.sin(self.time + x * 0.01) * 10
            
            self.draw_music_note(screen, (x, y_calc + hover), note_color)

    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.colors["white"])
        self.draw_decorations(screen)

         
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = self.colors.get(faction_name, self.colors["blue"])

        title_surf = self.font_title.render("MAIN DASHBOARD", True, self.colors["black"])
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 130))
        pygame.draw.rect(screen, theme_color, (title_rect.centerx - 80, title_rect.bottom + 5, 160, 3))
        screen.blit(title_surf, title_rect)
        
        
        username = self.app.shared_data.get("username", "Guest")
        user_text = f"Logged in as: {username} [{faction_name.upper()} TEAM]"
        user_surf = self.font_user.render(user_text, True, (130, 130, 130))
        screen.blit(user_surf, (self.app.WIDTH // 2 - user_surf.get_width() // 2, 185))

         
        for btn in self.buttons:
            btn.draw(screen)