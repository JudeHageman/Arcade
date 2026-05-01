# py_client/ui/input_box.py
import pygame

class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        """
        Custom Input Box for the Resonance Theme.
        """
        self.rect = pygame.Rect(x, y, w, h)
        
        # Colors (Matching our New Theme)
        self.color_inactive = (200, 200, 200) # Gray border when not clicked
        self.color_active = (173, 216, 230)   # Sky Blue border when active
        self.bg_color = (255, 255, 255)       # Pure White background
        self.text_color = (30, 30, 30)        # Clean Black
        
        self.color = self.color_inactive
        self.text = text
        self.is_password = is_password
        
        # Font: Source Sans 3 style
        self.font = pygame.font.SysFont("Source Sans 3, Arial", 22)
        
        # Render the initial text
        self.txt_surface = self.font.render(self.get_display_text(), True, self.text_color)
        self.active = False

    def get_display_text(self):
        """Returns asterisks if password mode is on."""
        return "*" * len(self.text) if self.is_password else self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # You could trigger a callback here if needed
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Add character (limit length to prevent overflow)
                    if len(self.text) < 20: 
                        self.text += event.unicode
                
                # Re-render the text.
                self.txt_surface = self.font.render(self.get_display_text(), True, self.text_color)

    def draw(self, screen):
        # 1. Draw the Background (White)
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        
        # 2. Draw the Border (Blue if active, Gray if not)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=8)
        
        # 3. Draw the Text
        # Add a little padding (10px) so the text isn't stuck to the edge
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + (self.rect.height//2 - self.txt_surface.get_height()//2)))
    def update_pos(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)