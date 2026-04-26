import pygame
import math
from screens.base_screen import BaseScreen
from ui.button import Button
from ui.input_box import InputBox

class ProfileScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        
        # 1. Vibrant Team Colors
        self.bg_color = (255, 255, 255)
        self.c_blue = (100, 200, 255)
        self.c_pink = (255, 120, 180)
        self.c_green = (120, 230, 120)
        self.c_black = (30, 30, 30)
        self.c_staff = (235, 235, 235)

        # 2. Dynamic Layout Logic
        cx = self.app.WIDTH // 2
        cy = self.app.HEIGHT // 2

        # 3. UI Components
        self.box_w = 600
        
        # Search Section
        input_w = 440
        self.search_input = InputBox(cx - self.box_w//2, cy + 60, input_w, 45)
        self.search_btn = Button(cx - self.box_w//2 + input_w + 10, cy + 60, 150, 45, 
                                 "FIND PLAYER", color=self.c_green, action=self.perform_search)
        
        self.back_btn = Button(40, 40, 100, 40, "BACK", color=(200, 200, 200), 
                               action=lambda: self.app.switch_screen("MENU"))

        # Fonts
        self.font_title = pygame.font.SysFont("Source Sans 3, Arial", 56, bold=True)
        self.font_label = pygame.font.SysFont("Source Sans 3, Arial", 22, bold=True)
        self.font_data = pygame.font.SysFont("Source Sans 3, Arial", 20)
        self.time = 0

        # Data placeholders
        self.searched_player = None
        self.searched_stats = None

    def draw_decorations(self, screen):
        """Diagonal staff and resonance circles based on the selected faction color."""
        self.time += 0.02
        
        # Get active faction color
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = getattr(self, f"c_{faction_name}")
        
        # 1. Diagonal Staff Lines
        line_spacing = 30
        slope = 0.1
        start_y_base = 380 
        for i in range(5):
            y_offset = i * line_spacing
            start_pos = (0, start_y_base + y_offset)
            end_pos = (self.app.WIDTH, start_y_base + y_offset - (self.app.WIDTH * slope))
            pygame.draw.line(screen, self.c_staff, start_pos, end_pos, 2)

        # 2. Resonance Circles (Fixed as circles, colors are dynamic)
        res_positions = [(180, 200, 55), (1100, 250, 75), (200, 620, 85), (1080, 580, 65)]
        for x, y, base_radius in res_positions:
            pulse = math.sin(self.time * 1.5 + x) * 4
            pygame.draw.circle(screen, theme_color, (x, y), int(base_radius + pulse), 3)

        # 3. Floating Notes
        note_positions = [(120, 450), (1150, 400), (800, 150), (400, 500)]
        for x, y_base in note_positions:
            y_calc = y_base - (x * slope)
            hover = math.sin(self.time * 5 + x) * 3
            self.draw_music_note(screen, (x, y_calc + hover), self.c_black)

    def draw_music_note(self, screen, pos, color):
        x, y = int(pos[0]), int(pos[1])
        head_radius = 11
        pygame.draw.circle(screen, color, (x, y), head_radius)
        pygame.draw.line(screen, color, (x + 7, y), (x + 7, y - 30), 3)
        pygame.draw.line(screen, color, (x + 7, y - 30), (x + 18, y - 20), 3)

    def draw_my_profile(self, screen):
        """Render personal card with Nickname and Team color."""
        cx = self.app.WIDTH // 2
        current_user = self.app.shared_data.get("username", "Guest")
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = getattr(self, f"c_{faction_name}")
        
        # Card background
        card_rect = pygame.Rect(cx - self.box_w//2, 160, self.box_w, 140)
        pygame.draw.rect(screen, (255, 255, 255), card_rect, border_radius=15)
        pygame.draw.rect(screen, self.c_black, card_rect, 2, border_radius=15)
        
        # Nickname (PLAYER ID)
        name_surf = self.font_label.render(f"PLAYER ID: {current_user}", True, self.c_black)
        screen.blit(name_surf, (card_rect.x + 30, card_rect.y + 25))
        
        # Team Info (Highlighted with Team Color)
        faction_surf = self.font_label.render(f"TEAM: {faction_name.upper()}", True, theme_color)
        screen.blit(faction_surf, (card_rect.x + 30, card_rect.y + 60))
        
        # Stats
        stats_text = "Rank: S-Class  |  Total Wins: 154  |  Win Rate: 78%"
        stats_surf = self.font_data.render(stats_text, True, (100, 100, 100))
        screen.blit(stats_surf, (card_rect.x + 30, card_rect.y + 95))

    def perform_search(self):
        query = self.search_input.text.strip()
        if query:
            results = self.app.player_trie.get_all_with_prefix(query)
            if results:
                self.searched_player = results[0]
                self.searched_stats = {"Rank": "Active", "Wins": 10}
            else:
                self.searched_player = "Not Found"
                self.searched_stats = None

    def draw_search_results(self, screen):
        if self.searched_player:
            cx = self.app.WIDTH // 2
            res_rect = pygame.Rect(cx - self.box_w//2, self.app.HEIGHT - 180, self.box_w, 110)
            pygame.draw.rect(screen, (252, 252, 252), res_rect, border_radius=15)
            pygame.draw.rect(screen, self.c_staff, res_rect, 2, border_radius=15)

            if self.searched_player == "Not Found" or self.searched_stats is None:
                msg = self.font_label.render("No player found with that name.", True, (200, 50, 50))
                screen.blit(msg, (res_rect.x + 30, res_rect.y + 40))
            else:
                res_title = self.font_label.render(f"Result: {self.searched_player}", True, self.c_blue)
                screen.blit(res_title, (res_rect.x + 30, res_rect.y + 20))
                
                rank = self.searched_stats.get('Rank', 'N/A')
                wins = self.searched_stats.get('Wins', 0)
                stats_surf = self.font_data.render(f"Current Rank: {rank}  |  Total Wins: {wins}", True, (80, 80, 80))
                screen.blit(stats_surf, (res_rect.x + 30, res_rect.y + 60))

    def handle_events(self, events):
        for event in events:
            self.search_input.handle_event(event)
            self.search_btn.handle_event(event)
            self.back_btn.handle_event(event)

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_decorations(screen)

        # Page Title with Faction colored underline
        faction_name = self.app.shared_data.get("faction", "blue")
        theme_color = getattr(self, f"c_{faction_name}")

        title_surf = self.font_title.render("PLAYER PROFILE", True, self.c_black)
        title_rect = title_surf.get_rect(center=(self.app.WIDTH // 2, 90))
        pygame.draw.rect(screen, theme_color, (title_rect.centerx - 80, title_rect.bottom + 5, 160, 3))
        screen.blit(title_surf, title_rect)

        # Draw components
        self.draw_my_profile(screen)
        self.search_input.draw(screen)
        self.search_btn.draw(screen)
        self.draw_search_results(screen)
        self.back_btn.draw(screen)