# client/screens/leaderboard_screen.py
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button

class LeaderboardScreen(BaseScreen):
    def __init__(self, app):
        """
        Initialize the Leaderboard Screen with a clean table layout.
        """
        super().__init__(app)
        
        # UI design settings: Light Mode
        self.bg_color = (250, 250, 250)
        self.grid_color = (235, 235, 235)
        self.font_title = pygame.font.SysFont("arial", 36, bold=True)
        self.font_header = pygame.font.SysFont("arial", 22, bold=True)
        self.font_row = pygame.font.SysFont("arial", 20)

        # UI Components
        # Back button to return to the Menu screen
        self.back_btn = Button(50, 50, 100, 40, "BACK", 
                               action=lambda: self.app.switch_screen("MENU"))

        # Mock data: This will be replaced with real data from the server/Websocket
        self.rank_data = [
            {"rank": 1, "name": "Player_Alpha", "score": 15200},
            {"rank": 2, "name": "Gamer_X", "score": 14850},
            {"rank": 3, "name": "Resonance_Top", "score": 13200},
            {"rank": 4, "name": "Swift_Gardener", "score": 11500},
            {"rank": 5, "name": "Pixel_Master", "score": 9800}
        ]

    def handle_events(self, events):
        """
        Handle navigation and UI interaction events.
        """
        for event in events:
            self.back_btn.handle_event(event)

    def update(self):
        """
        Update logic (e.g., refreshing data from server).
        """
        pass

    def draw_grid(self, screen):
        """
        Draw background grid lines for a technical, clean aesthetic.
        """
        for x in range(0, 800, 40):
            pygame.draw.line(screen, self.grid_color, (x, 0), (x, 600))
        for y in range(0, 600, 40):
            pygame.draw.line(screen, self.grid_color, (0, y), (800, y))

    def draw_table_headers(self, screen):
        """
        Draw the headers for the leaderboard table (Rank, Name, Score).
        """
        header_y = 160
        pygame.draw.line(screen, (0, 0, 0), (100, header_y + 35), (700, header_y + 35), 2)
        
        screen.blit(self.font_header.render("RANK", True, (0, 0, 0)), (120, header_y))
        screen.blit(self.font_header.render("PLAYER NAME", True, (0, 0, 0)), (250, header_y))
        screen.blit(self.font_header.render("SCORE", True, (0, 0, 0)), (580, header_y))

    def draw_rank_rows(self, screen):
        """
        Iterate through the ranking data and render each row.
        """
        start_y = 210
        row_height = 50
        
        for i, entry in enumerate(self.rank_data):
            current_y = start_y + (i * row_height)
            
            # Draw row background for alternating colors
            if i % 2 == 0:
                row_rect = pygame.Rect(100, current_y - 5, 600, 40)
                pygame.draw.rect(screen, (245, 245, 245), row_rect, border_radius=5)

            # Render row text
            screen.blit(self.font_row.render(str(entry["rank"]), True, (50, 50, 50)), (130, current_y))
            screen.blit(self.font_row.render(entry["name"], True, (0, 0, 0)), (250, current_y))
            screen.blit(self.font_row.render(f"{entry['score']:,}", True, (0, 0, 0)), (580, current_y))

    def draw(self, screen):
        """
        Main draw loop: Background -> Grid -> Title -> Table Components.
        """
        screen.fill(self.bg_color)
        self.draw_grid(screen)

        # Draw main title
        title_surf = self.font_title.render("TOP SURVIVORS", True, (0, 0, 0))
        screen.blit(title_surf, (280, 80))

        # Draw UI
        self.draw_table_headers(screen)
        self.draw_rank_rows(screen)
        self.back_btn.draw(screen)