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
from screens.games_screen import GamesScreen
from screens.PlayerSearchScreen import PlayerSearchScreen
from screens.MatchHistoryScreen import MatchHistoryScreen

class ArcadeApp:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Team Resonance - Game Hub")
        self.clock = pygame.time.Clock()
        
        self.network = NetworkManager(self, port=8000)
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
            "CHAT": InGameChatScreen(self),
            "GAMES": GamesScreen(self),
            "SEARCH": PlayerSearchScreen(self),
            "HISTORY": MatchHistoryScreen(self)
             
        }
        self.moderator = ChatModerator()
        # 시작 화면 설정
        self.switch_screen("LOGIN")

    def switch_screen(self, screen_name):
        if screen_name not in self.screens:
            print(f"❌ Error: Screen '{screen_name}' not found!")
            return

        target_screen = self.screens[screen_name]
        # ... (리사이징 로직 생략) ...
        self.current_screen = target_screen

        # 🚨 [수정] 각 화면에 맞는 데이터 로드 함수 자동 호출
        if screen_name == "PROFILE" and hasattr(target_screen, "fetch_profile"):
            target_screen.fetch_profile()
        elif screen_name == "RANKING" and hasattr(target_screen, "fetch_leaderboard"):
            target_screen.fetch_leaderboard()
        elif screen_name == "HISTORY" and hasattr(target_screen, "fetch_history"):
            target_screen.fetch_history()

    def draw_navigation_bar(self):
        """상단 네비게이션 바를 화면 위에 덧그림"""
        # MenuScreen 객체에 이미 네비게이션 버튼들이 있으니까, 
        # MenuScreen의 draw_header와 버튼 그리기를 재활용하는 게 가장 편해!
        menu = self.screens.get("MENU")
        if menu:
            menu.draw_header(self.screen)
            for btn in menu.nav_buttons:
                btn.draw(self.screen)
    def handle_navigation_events(self, events):
        """어느 화면에 있든 상단 네비게이션 클릭을 감지"""
        menu = self.screens.get("MENU")
        if menu and hasattr(menu, 'nav_buttons'):
            # 🚨 [수정] 리스트가 비어있어도 안전하게 돌아가는 for 문으로 변경!
            for event in events:
                for btn in menu.nav_buttons:
                    btn.handle_event(event)
    def run(self):
        while self.running:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == LOGIN_SUCCESS:
                    self.switch_screen("MENU")

            # 🚨 [수정 포인트] 로그인 상태라면 상단 바 버튼 이벤트를 먼저 처리!
            if self.shared_data.get("authenticated"):
                self.handle_navigation_events(events) # 👈 이 함수를 새로 만들 거야

            # 그 다음 현재 화면의 이벤트를 처리
            if self.current_screen:
                self.current_screen.handle_events(events)
                self.current_screen.update()
            # 2. 화면 그리기
            if self.current_screen:
                self.current_screen.draw(self.screen)
            
            # 3. 로그인 상태일 때 상단 바 그리기
            if self.shared_data.get("authenticated"):
                self.draw_navigation_bar() 
                
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

   