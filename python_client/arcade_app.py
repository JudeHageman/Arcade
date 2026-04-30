# client/arcade_app.py
import pygame
import sys
LOGIN_SUCCESS = pygame.USEREVENT + 1
from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.profile_screen import ProfileScreen
from Trie import PlayerTrie
from screens.catalog_screen import CatalogScreen
from screens.in_game_chat_screen import InGameChatScreen
from network_manager import NetworkManager
from chat_moderation import ChatModerator

class ArcadeApp:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Team Resonance - Game Hub")
        self.clock = pygame.time.Clock()
        
        self.network = NetworkManager(self, port=50085)
        self.network.start_connection()
        
        # 공통 자원 관리 (나중에 여기에 Network, Trie 인스턴스 추가)
        self.shared_data = {}
        self.player_trie = PlayerTrie() # This is our member database
        # 화면 관리 시스템
        self.screens = {} # {"LOGIN": LoginScreen(self), "MENU": MenuScreen(self)} 식의 구조
        self.current_screen = None
        self.running = True
         
        self.screens = {
            "LOGIN": LoginScreen(self),
            "MENU": MenuScreen(self),
            "LEADERBOARD": LeaderboardScreen(self),
            "PROFILE": ProfileScreen(self),
            "CATALOG": CatalogScreen(self),
            "CHAT": InGameChatScreen(self)
             
        }
        self.moderator = ChatModerator()
        # 시작 화면 설정
        self.switch_screen("LOGIN")

    def switch_screen(self, screen_name):
    # 1. 대상 스크린 가져오기
        target_screen = self.screens[screen_name]
        
        # 2. 기본 플래그 설정
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        # 3. 스크린의 resizable 속성에 따라 창 모드 변경
        if getattr(target_screen, 'resizable', False):
            # 리사이징 활성화
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags | pygame.RESIZABLE)
        else:
            # 리사이징 비활성화 (고정 크기로 강제 복구)
            # 만약 창이 커진 상태였다면, 다시 기본 해상도로 되돌려야 디자인이 안 깨집니다.
            self.WIDTH, self.HEIGHT = 1280, 720 
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)
            
            # 비활성화된 스크린들이 배율 때문에 깨지지 않게 scale을 1.0으로 초기화할 수도 있습니다.
            if hasattr(target_screen, 'scale'):
                target_screen.scale = 1.0
                if hasattr(target_screen, 'refresh_layout'):
                    target_screen.refresh_layout()
        self.current_screen = target_screen

    def run(self):
        """메인 루프: 이벤트 -> 업데이트 -> 그리기"""
        
        while self.running:
            events = pygame.event.get()
            for event in events:
                # 1. 시스템 종료 이벤트
                if event.type == pygame.QUIT:
                    self.running = False
                
                # 2. 네트워크 성공 이벤트 (메인 스레드에서 안전하게 화면 전환)
                elif event.type == LOGIN_SUCCESS:
                    print("--- APP DEBUG: Login Success Event Received. Switching to MENU ---")
                    self.switch_screen("MENU")

            # 3. 현재 화면 업데이트 및 그리기
            if self.current_screen:
                # handle_events에 events 리스트 전체를 넘겨줍니다.
                self.current_screen.handle_events(events)
                self.current_screen.update()
                self.current_screen.draw(self.screen)
            
            # 4. 화면 업데이트 및 프레임 고정
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

   