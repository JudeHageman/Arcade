# client/arcade_app.py
import pygame
import sys
LOGIN_SUCCESS = pygame.USEREVENT + 1
from screens.login_screen import LoginScreen
from screens.menu_screen import MenuScreen
from screens.leaderboard_screen import LeaderboardScreen
from screens.profile_screen import ProfileScreen
 
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
        
         
        self.shared_data = {}
         
        self.screens = {}  
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
         
        self.switch_screen("LOGIN")

    def switch_screen(self, screen_name):
        if screen_name not in self.screens:
            print(f"❌ Error: Screen '{screen_name}' not found!")
            return

        target_screen = self.screens[screen_name]
         
        self.current_screen = target_screen

         
        if screen_name == "PROFILE" and hasattr(target_screen, "fetch_profile"):
            target_screen.fetch_profile()
        elif screen_name == "RANKING" and hasattr(target_screen, "fetch_leaderboard"):
            target_screen.fetch_leaderboard()
        elif screen_name == "HISTORY" and hasattr(target_screen, "fetch_history"):
            target_screen.fetch_history()

    def draw_navigation_bar(self):
         
         
        menu = self.screens.get("MENU")
        if menu:
            menu.draw_header(self.screen)
            for btn in menu.nav_buttons:
                btn.draw(self.screen)
    def handle_navigation_events(self, events):
        """어느 화면에 있든 상단 네비게이션 클릭을 감지"""
        menu = self.screens.get("MENU")
        if menu and hasattr(menu, 'nav_buttons'):
             
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

             
            if self.shared_data.get("authenticated"):
                self.handle_navigation_events(events) 

             
            if self.current_screen:
                self.current_screen.handle_events(events)
                self.current_screen.update()
             
            if self.current_screen:
                self.current_screen.draw(self.screen)
            
             
            if self.shared_data.get("authenticated"):
                self.draw_navigation_bar() 
                
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

   