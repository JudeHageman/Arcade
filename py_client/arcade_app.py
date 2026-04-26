# client/arcade_app.py
import pygame
import sys

from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.chat_screen import ChatScreen
from screens.profile_screen import ProfileScreen
from trie import PlayerTrie
from screens.catalog_screen import CatalogScreen
from screens.signup_screen import SignupScreen


 

class ArcadeApp:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Team Resonance - Game Hub")
        self.clock = pygame.time.Clock()
        
        
        
        # 공통 자원 관리 (나중에 여기에 Network, Trie 인스턴스 추가)
        self.shared_data = {}
        self.player_trie = PlayerTrie() # This is our member database
        # 화면 관리 시스템
        self.screens = {} # {"LOGIN": LoginScreen(self), "MENU": MenuScreen(self)} 식의 구조
        self.current_screen = None
        self.running = True
        # 화면 인스턴스 생성 및 등록
        self.screens = {
            "LOGIN": LoginScreen(self),
            "MENU": MenuScreen(self),
            "LEADERBOARD": LeaderboardScreen(self),
            "CHAT": ChatScreen(self),
            "PROFILE": ProfileScreen(self),
            "CATALOG": CatalogScreen(self),
            "SIGNUP": SignupScreen(self)
            # "MENU": MenuScreen(self)
        }
        
        # 시작 화면 설정
        self.switch_screen("LOGIN")

    def switch_screen(self, screen_name):
         
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
        else:
            print(f"Error: Screen '{screen_name}' not found.")

    def run(self):
        """메인 루프: 이벤트 -> 업데이트 -> 그리기"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            if self.current_screen:
                self.current_screen.handle_events(events)
                self.current_screen.update()
                self.current_screen.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60) # 60 FPS 고정

        pygame.quit()
        sys.exit()