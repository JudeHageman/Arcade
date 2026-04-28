# client/screens/base_screen.py
import pygame

class BaseScreen:
    def __init__(self, app):
        self.app = app    

    def handle_events(self, events):
         pass

    def update(self):
         pass

    def draw(self, screen):
         pass