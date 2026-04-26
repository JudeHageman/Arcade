# client/screens/base_screen.py
import pygame

class BaseScreen:
    def __init__(self, app):
        self.app = app  # ArcadeApp 인스턴스에 접근하여 화면 전환이나 공유 데이터 사용 가능

    def handle_events(self, events):
        """마우스 클릭, 키보드 입력 등 이벤트 처리"""
        pass

    def update(self):
        """데이터 업데이트 (애니메이션, 논리 로직)"""
        pass

    def draw(self, screen):
        """화면에 그리기"""
        pass