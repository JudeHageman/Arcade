import pygame
import sys
import argparse
from settings import *
from level import Level


class Game:
    def __init__(self, player_name, team, server_host='localhost', server_port=8080, serializer='text'):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        
        try:
            self.font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.SysFont('arial', 48)
            self.button_font = pygame.font.SysFont('arial', 32)
            self.small_font = pygame.font.SysFont('arial', 20)
        
        pygame.display.set_caption(GAME_NAME + f' - {player_name} ({serializer.upper()})')
        self.clock = pygame.time.Clock()

        # Network settings
        self.player_name = player_name
        self.team = team
        self.server_host = server_host
        self.server_port = server_port
        self.serializer = serializer

        self.level = None
        self.running = True
    
    def run(self):
        """Main game loop"""
        # Create level with the single fixed player character
        self.level = Level(
            self.player_name,
            self.team,
            self.server_host, 
            self.server_port, 
            self.serializer
        )
        
        # Game loop
        while self.running:
            events = []
            for event in pygame.event.get():
                events.append(event)
                if event.type == pygame.QUIT:
                    self.level.network.disconnect()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.level.network.disconnect()
                        pygame.quit()
                        sys.exit()

            self.screen.fill('black')
            self.level.run(events)
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Multiplayer Game Client')
    parser.add_argument('name', help='Your player name')
    parser.add_argument('--server', default='localhost', 
                       help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Server port (default: 8080)')
    parser.add_argument('--serializer', choices=['text', 'json', 'binary'], 
                       default='text',
                       help='Serialization format: text (default), json, or binary')
    parser.add_argument('--team', choices=['blue', 'pink', 'green', 'default'], 
                       default='default',
                       help='Team: blue, pink, green, or default (default)')
    
    args = parser.parse_args()
    
    print("="*50)
    print(f"Starting game as '{args.name}'")
    print(f"Team: {args.team.upper()}")
    print(f"Connecting to {args.server}:{args.port}")
    print(f"Using {args.serializer.upper()} serialization")
    print("="*50)
    print()
    
    game = Game(args.name, args.team, args.server, args.port, args.serializer)
    game.run()
