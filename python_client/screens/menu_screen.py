import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button

class MenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        # 1. Vibrant Team Colors
        self.bg_color = (255, 255, 255)
        self.c_pink = (255, 182, 193)
        self.c_green = (180, 238, 180)
        self.c_blue = (173, 216, 230)
        self.c_black = (30, 30, 30)
        self.c_staff = (235, 235, 235)

        # 2. Dynamic Centering
        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

        # 3. UI Components
        btn_w, btn_h = 350, 55
        spacing = 15
        start_y = cy - 40 

        self.buttons = [
            Button(cx - btn_w//2, start_y, btn_w, btn_h, "GAME CATALOG", 
                   color=self.c_green, action=lambda: self.app.switch_screen("CATALOG")),
            
            Button(cx - btn_w//2, start_y + (btn_h + spacing), btn_w, btn_h, "LEADERBOARD", 
                   color=self.c_blue, action=lambda: self.app.switch_screen("LEADERBOARD")),
            
            Button(cx - btn_w//2, start_y + (btn_h + spacing) * 2, btn_w, btn_h, "LIVE CHAT", 
                   color=self.c_pink, action=lambda: self.app.switch_screen("CHAT")),
                   
            Button(cx - btn_w//2, start_y + (btn_h + spacing) * 3, btn_w, btn_h, "MY PROFILE", 
                   color=self.c_blue, action=lambda: self.app.switch_screen("PROFILE"))
        ]

        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 64, bold=True)
        self.font_user = pygame.font.SysFont("Source Sans 3, Arial", 20, bold=True)
        self.time = 0

    def draw_decorations(self, screen):
        """Authoritative layout: Only the color of the circles changes based on the faction."""
        self.time += 0.02
        
        # Get active faction color from shared_data
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = getattr(self, f"c_{faction_name}")
        
        # 1. Diagonal Staff Lines
        line_spacing = 30
        slope = 0.1
        start_y_base = 350 
        for i in range(5):
            y_offset = i * line_spacing
            start_pos = (0, start_y_base + y_offset)
            end_pos = (self.app.WIDTH, start_y_base + y_offset - (self.app.WIDTH * slope))
            pygame.draw.line(screen, self.c_staff, start_pos, end_pos, 2)

        # 2. Resonance Circles (Shapes fixed as circles, colors are dynamic)
        res_positions = [
            (200, 280, 55), (1050, 250, 75), 
            (150, 620, 85), (1100, 600, 65)
        ]
        for x, y, base_radius in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 4
            # Draw hollow circles using the faction's theme color
            pygame.draw.circle(screen, theme_color, (x, y), int(base_radius + pulse), 3)

        # 3. Scattered Musical Notes
        note_positions = [(200, 500), (450, 420), (850, 580), (1100, 450)]
        for x, y_base in note_positions:
            y_calc = y_base - (x * slope)
            hover = math.sin(self.time * 5 + x) * 3
            self.draw_music_note(screen, (x, y_calc + hover), self.c_black)

    def draw_music_note(self, screen, pos, color):
        x, y = int(pos[0]), int(pos[1])
        head_radius = 11   
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + 7, y), (x + 7, y - 32), 3)
        pygame.draw.line(screen, color, (x + 7, y - 32), (x + 18, y - 22), 3)

    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)

        # Title with theme-colored underline
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = getattr(self, f"c_{faction_name}")

        title_surf = self.font_title.render("MAIN DASHBOARD", True, self.c_black)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 130))
        pygame.draw.rect(screen, theme_color, (title_rect.centerx - 80, title_rect.bottom + 5, 160, 3))
        screen.blit(title_surf, title_rect)
        
        # User Status: Display Name + Faction Color Name
        username = self.app.shared_data.get("username", "Guest")
        user_text = f"Logged in as: {username} [{faction_name.upper()} TEAM]"
        user_surf = self.font_user.render(user_text, True, (130, 130, 130))
        screen.blit(user_surf, (self.app.WIDTH // 2 - user_surf.get_width() // 2, 185))

        # Buttons
        for btn in self.buttons:
            btn.draw(screen)