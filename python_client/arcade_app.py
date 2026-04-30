import pygame
import sys
from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.profile_screen import ProfileScreen
from screens.catalog_screen import CatalogScreen
from screens.in_game_chat_screen import InGameChatScreen
from network_manager import NetworkManager
from chat_moderation import ChatModerator

LOGIN_SUCCESS = pygame.USEREVENT + 1

class ArcadeApp:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Team Resonance - Game Hub")
        self.clock = pygame.time.Clock()
        
        # 1. 공통 자원(Shared Data)을 가장 먼저 초기화!
        # 스크린들이 생성되자마자 이 가방을 뒤져보기 때문에 순서가 중요해.
        self.shared_data = {
            "username": "Guest",
            "faction": "blue",
            "authenticated": False,
            "games_info": {},
            "current_game_process": None
        }

        # 2. 검열기 및 네트워크 매니저 생성
        self.moderator = ChatModerator()
        self.network = NetworkManager(self, port=50085)
        self.network.start_connection()
        
        # 3. 화면 관리 시스템 (중복 정의 제거!)
        # 이제 각 스크린 객체들은 self.app.network를 통해 서버에 검색을 요청할 수 있어.
        self.screens = {
            "LOGIN": LoginScreen(self),
            "MENU": MenuScreen(self),
            "LEADERBOARD": LeaderboardScreen(self),
            "PROFILE": ProfileScreen(self),
            "CATALOG": CatalogScreen(self),
            "CHAT": InGameChatScreen(self)
        }
        
        self.current_screen = None
        self.running = True
        
        # 4. 시작 화면 설정
        self.switch_screen("LOGIN")

    def switch_screen(self, screen_name):
        """화면 전환 및 창 크기 최적화 로직"""
        if screen_name not in self.screens:
            print(f"Error: Screen '{screen_name}' not found!")
            return

        target_screen = self.screens[screen_name]
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        # 리사이징 설정 처리
        if getattr(target_screen, 'resizable', False):
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags | pygame.RESIZABLE)
        else:
            # 고정 크기 화면으로 돌아갈 때 해상도 복구
            self.WIDTH, self.HEIGHT = 1280, 720 
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)
            
            if hasattr(target_screen, 'scale'):
                target_screen.scale = 1.0
                if hasattr(target_screen, 'refresh_layout'):
                    target_screen.refresh_layout()
                    
        self.current_screen = target_screen

    def run(self):
        """메인 게임 루프"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                # 네트워크 매니저가 던진 로그인 성공 이벤트를 여기서 처리!
                elif event.type == LOGIN_SUCCESS:
                    self.switch_screen("MENU")

            if self.current_screen:
                self.current_screen.handle_events(events)
                self.current_screen.update()
                self.current_screen.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = ArcadeApp()
    app.run()