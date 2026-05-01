"""
main.py - Island Gardener
팀 정보 수신 및 세션 기록 통합 버전
"""

import pygame
import sys
import argparse
import os
from settings import *
from level import Level
from subcharacter import get_all_character_classes
from dotenv import load_dotenv
from session import Session
# from ai_npc import AIHandler # 필요한 경우 주석 해제
import time
load_dotenv()  

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        try:
            self.font = pygame.font.Font(None, fontsize)
        except:
            self.font = pygame.font.SysFont('arial', fontsize)
        
        self.content = content
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fg, self.bg = fg, bg

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
        return False

# ... CharacterCard 클래스는 동일하므로 생략 (그대로 두면 돼!) ...

class Game:
    def __init__(self, player_name, team, server_host='localhost', server_port=8080, serializer='text'):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        
        # 폰트 설정
        try:
            self.font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.SysFont('arial', 48)
            self.button_font = pygame.font.SysFont('arial', 32)
            self.small_font = pygame.font.SysFont('arial', 20)
        
        # 🚨 팀 정보를 제목에 표시
        pygame.display.set_caption(f"{GAME_NAME} - {player_name} [TEAM: {team}]")
        self.clock = pygame.time.Clock()

        self.player_name = player_name
        self.team = team # 🚨 팀 정보 저장
        self.server_host = server_host
        self.server_port = server_port
        self.serializer = serializer

        self.selected_character = None
        self.level = None
        self.running = True

    def character_select(self):
        """캐릭터 선택 화면 (기존 로직 유지)"""
        char_select = True
        # ... (캐릭터 선택 카드 및 버튼 그리기 로직 동일) ...
        # [중략] 
        # 캐릭터가 선택되면 self.selected_character에 저장됨
        
        # 예시로 첫 번째 캐릭터 자동 선택 로직 (테스트용)
        character_classes = get_all_character_classes()
        if character_classes:
            self.selected_character = character_classes[0]
            char_select = False

    def run(self):
        """메인 게임 루프"""
        self.character_select()
        
        if not self.running or self.selected_character is None:
            return
        
        # 1. 레벨 생성 시 팀 정보 전달
        self.level = Level(
            self.player_name, 
            self.selected_character, 
            self.server_host, 
            self.server_port, 
            self.serializer,
            self.team # 🚨 Level 클래스가 이걸 받도록 설계되어 있어야 해!
        )

        # 2. 세션 기록용 스코어 함수
        def get_scores():
            # 서버가 기대하는 (개인점수, 팀점수, 팀이름) 튜플 반환
            # level.player.exp가 개인 점수라고 가정할게
            return (self.level.player.exp, self.level.team_kills, self.team)

        # 🚨 서버가 "Game 2"로 인식하므로 게임 이름을 맞춰줌 (필요시 수정)
        self.session = Session(self.player_name, "Island Gardener", get_scores)
        
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit_game()

            self.screen.fill('black')
            self.level.run(events)
            pygame.display.update()
            self.clock.tick(FPS)

    def exit_game(self):
        """종료 시 세션 전송 및 정리"""
        if hasattr(self, 'session'):
            print("--- SESSION: Sending data to server... ---")
            self.session.print_session() 
            
            # 🚨 [핵심] 데이터를 보내고 서버가 읽을 시간을 줍니다.
            time.sleep(0.3) 
            
        if self.level and hasattr(self.level, 'network'):
            self.level.network.disconnect()
            
        print("--- SYSTEM: Closing game... ---")
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Multiplayer Game Client')
    parser.add_argument('name', help='Your player name')
    parser.add_argument('--server', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8081, help='Server port')
    parser.add_argument('--serializer', default='text', help='Serialization format')
    # 🚨 런처에서 보내는 --team 인자를 여기서 받음!
    parser.add_argument('--team', default='default', help='Team name (e.g. PINK, GREEN)')
    
    args = parser.parse_args()
    
    # 🚨 Game 생성자에 args.team 추가
    game = Game(args.name, args.team, args.server, args.port, args.serializer)
    game.run()