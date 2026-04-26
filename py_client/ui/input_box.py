# client/ui/input_box.py
import pygame

class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.is_password = is_password
        self.font = pygame.font.SysFont("arial", 22)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 박스를 클릭하면 활성화
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            
            # 비밀번호일 경우 '*'로 렌더링
            display_text = '*' * len(self.text) if self.is_password else self.text
            self.txt_surface = self.font.render(display_text, True, (0, 0, 0))

    def draw(self, screen):
        # 텍스트와 박스 그리기
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)