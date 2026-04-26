# client/ui/button.py
import pygame

class Button:
    def __init__(self, x, y, width, height, text, action=None, color=(160, 160, 160), hover_color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action  # 클릭 시 실행할 함수 (Callback)
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("arial", 24, bold=True)

    def draw(self, screen):
        # 마우스 위치 확인하여 Hover 효과 적용
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        # 버튼 배경과 테두리 그리기
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # 텍스트 중앙 정렬
        text_surf = self.font.render(self.text, True, (30, 30, 30))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action() # 버튼이 가진 액션 실행!