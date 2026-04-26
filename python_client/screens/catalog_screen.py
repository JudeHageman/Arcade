# client/screens/catalog_screen.py
import pygame
from screens.base_screen import BaseScreen
from ui.button import Button

class CatalogScreen(BaseScreen):
    def __init__(self, app):
        """
        Initialize the Catalog Screen where players select which mini-game to play.
        """
        super().__init__(app)
        
        # Design settings
        self.bg_color = (250, 250, 250)
        self.grid_color = (235, 235, 235)
        self.font_title = pygame.font.SysFont("arial", 36, bold=True)
        self.font_desc = pygame.font.SysFont("arial", 16)

        # Button Layout Settings
        btn_w, btn_h = 240, 180
        spacing = 30
        start_x = (800 - (btn_w * 3 + spacing * 2)) // 2
        y_pos = 220

        # Game Selection Buttons
        self.buttons = [
            # Game 1: Lumberjack
            Button(start_x, y_pos, btn_w, btn_h, "LUMBERJACK", 
                   action=lambda: self.select_game("LUMBERJACK")),
            
            # Game 2: Ashes
            Button(start_x + (btn_w + spacing), y_pos, btn_w, btn_h, "ASHES", 
                   action=lambda: self.select_game("ASHES")),
            
            # Game 3: Gardener
            Button(start_x + (btn_w + spacing) * 2, y_pos, btn_w, btn_h, "GARDENER", 
                   action=lambda: self.select_game("GARDENER")),
            
            # Navigation
            Button(50, 40, 90, 35, "BACK", action=lambda: self.app.switch_screen("MENU"))
        ]

    def select_game(self, game_name):
        """
        Save the selected game to shared_data and move to the Game Play screen.
        """
        print(f"DEBUG: Selected Game -> {game_name}")
        self.app.shared_data["selected_game"] = game_name
        
        # Switch to the screen where the actual game logic will live
        self.app.switch_screen("GAME_PLAY")

    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def draw_grid(self, screen):
        """Standard grid background for consistency."""
        for x in range(0, 800, 40):
            pygame.draw.line(screen, self.grid_color, (x, 0), (x, 600))
        for y in range(0, 600, 40):
            pygame.draw.line(screen, self.grid_color, (0, y), (800, y))

    def draw(self, screen):
        self.draw_grid(screen)
        screen.fill(self.bg_color)

        # Header Text
        title_surf = self.font_title.render("SELECT YOUR MISSION", True, (0, 0, 0))
        screen.blit(title_surf, (220, 100))

        # Game Descriptions (Optional, adds a professional touch)
        descriptions = [
            "Chop wood fast!",
            "Avoid the rising fire.",
            "Plant flowers carefully."
        ]
        
        # Draw all buttons
        for i, btn in enumerate(self.buttons):
            btn.draw(screen)
            
            # Draw description text under the main 3 buttons
            if i < 3: 
                desc_surf = self.font_desc.render(descriptions[i], True, (100, 100, 100))
                screen.blit(desc_surf, (btn.rect.x + 60, btn.rect.y + btn.rect.height + 10))