"""
dialog_ui.py - In-game dialog box UI

This file is PROVIDED. Do not modify it.

Renders the NPC dialog box at the bottom of the screen.
Controls:
    ↑ / ↓      — navigate choices
    Enter/Space — confirm choice  (or close if conversation ended)
    Esc        — close dialog
"""

import threading
import pygame


DIALOG_BG     = (20,  20,  40,  220)   # RGBA (semi-transparent)
DIALOG_BORDER = (180, 160, 100)
CHOICE_HL     = (70,  70,  150)
TEXT_COLOR    = (240, 240, 240)
CHOICE_COLOR  = (200, 200, 255)
DONE_COLOR    = (150, 150, 150)
NAME_COLOR    = (255, 220,  80)

DIALOG_H = 230
PADDING  = 20


class DialogUI:
    """
    Drives and renders an active NPC conversation.

    Parameters
    ----------
    npc_name     : Displayed at the top of the dialog box.
    dialog_graph : DialogGraph to traverse.
    ai_handler   : Optional AIHandler for Gemini responses.
                   Pass None to skip AI for this conversation.
    """

    def __init__(self, npc_name, dialog_graph, ai_handler=None):
        self.npc_name    = npc_name
        self.dg          = dialog_graph
        self.ai_handler  = ai_handler
        self._done       = False
        self._selected   = 0
        self._ai_text    = None
        self._ai_loading = False

        self._name_font   = pygame.font.Font(None, 28)
        self._text_font   = pygame.font.Font(None, 26)
        self._choice_font = pygame.font.Font(None, 24)
        self._hint_font   = pygame.font.Font(None, 20)

        self.dg.reset()
        self._maybe_generate_ai()

    # ------------------------------------------------------------------
    # AI helpers
    # ------------------------------------------------------------------

    def _maybe_generate_ai(self):
         
        if self._ai_loading:
            return
            
        if self.dg.get_current_type() == "ai" and self.ai_handler:
            self._ai_loading = True
            self._ai_text    = None
            
            threading.Thread(target=self._fetch_ai, daemon=True).start()

    def _fetch_ai(self):
        try:
            
            self._ai_text = self.ai_handler.generate(self.npc_name)
        except Exception as exc:
            self._ai_text = f"(AI unavailable: {exc})"
        finally:
            self._ai_loading = False
            

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self._done = True
                return

            if self._ai_loading:
                continue   # wait for the AI response

            if self.dg.is_ended():
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._done = True
                return

            choices = self.dg.get_choices()
            n = max(1, len(choices))
            if event.key == pygame.K_UP:
                self._selected = (self._selected - 1) % n
            elif event.key == pygame.K_DOWN:
                self._selected = (self._selected + 1) % n
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.dg.choose(self._selected):
                    self._selected = 0
                    self._maybe_generate_ai()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface):
        sw, sh = surface.get_size()
        box = pygame.Rect(PADDING, sh - DIALOG_H - PADDING,
                          sw - PADDING * 2, DIALOG_H)

        # Semi-transparent background
        bg = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        bg.fill(DIALOG_BG)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, DIALOG_BORDER, box, 2)

        x, y = box.x + PADDING, box.y + PADDING

        # NPC name header
        surface.blit(self._name_font.render(self.npc_name, True, NAME_COLOR), (x, y))
        y += 34

        # Dialog text
        if self._ai_loading:
            text = "..."
        elif self.dg.get_current_type() == "ai" and self._ai_text:
            text = self._ai_text
        else:
            text = self.dg.get_current_text()

        for line in self._wrap(text, self._text_font, box.width - PADDING * 2):
            surface.blit(self._text_font.render(line, True, TEXT_COLOR), (x, y))
            y += 26
        y += 8

        # Choices or close hint
        if self.dg.is_ended() and not self._ai_loading:
            surface.blit(
                self._hint_font.render("[Enter] Close", True, DONE_COLOR), (x, y)
            )
        else:
            for i, (choice_text, _) in enumerate(self.dg.get_choices()):
                if i == self._selected:
                    hl = pygame.Rect(x - 4, y - 2,
                                     box.width - PADDING * 2, 24)
                    pygame.draw.rect(surface, CHOICE_HL, hl)
                arrow = "▶" if i == self._selected else " "
                label = f"{arrow} {i + 1}. {choice_text}"
                surface.blit(
                    self._choice_font.render(label, True, CHOICE_COLOR), (x, y)
                )
                y += 24

        # Bottom hint bar
        surface.blit(
            self._hint_font.render(
                "↑↓: Select   Enter: Confirm   Esc: Close",
                True, (100, 100, 100)
            ),
            (x, box.bottom - 22)
        )

    def is_done(self):
        return self._done

    # ------------------------------------------------------------------

    @staticmethod
    def _wrap(text, font, max_width):
        words, lines, current = text.split(), [], []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines or [""]
