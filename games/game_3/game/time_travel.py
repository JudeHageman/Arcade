"""
time_travel.py - Time travel system using stacks

Implements rewind/replay functionality for single-player mode.
Disabled when multiple players are connected.

Author: Michael Janeczko
Date: 2/20/2026
Lab: Lab 4 - Time Travel with Stacks
"""

import sys
sys.path.insert(0, './datastructures/')
from stack import Stack


class GameState:
    """
    Represents a snapshot of the game state at a single point in time.
    """
    
    def __init__(self, player_x, player_y, timestamp):
        """
        Create a game state snapshot.
        
        Args:
            player_x (float): Player's x position
            player_y (float): Player's y position
            timestamp (int): Frame number when this state was recorded
        """
        self.player_x = player_x
        self.player_y = player_y
        self.timestamp = timestamp
    
    def __repr__(self):
        """String representation for debugging"""
        return f"GameState(x={self.player_x:.1f}, y={self.player_y:.1f}, frame={self.timestamp})"


class TimeTravel:
    """
    Manages game state history for rewind/replay functionality.
    
    Uses two stacks:
    - history: Past states (what we've done)
    - future: Future states (available after rewinding)
    
    Note: Only works in single-player mode!
    """
    
    def __init__(self, max_history=180, sample_rate=10):
        """
        Initialize the time travel system.
        
        Args:
            max_history (int): Maximum number of states to remember 
                              (default: 180 states)
            sample_rate (int): Record every N frames (default: 10)
                              sample_rate=5 means 180 states = 15 seconds at 60 FPS
                              sample_rate=10 means 180 states = 30 seconds at 60 FPS
        """
        # TODO: Create a Stack for history (past states)
        self.history = Stack()
        # TODO: Create a Stack for future (states after rewinding)
        self.future = Stack()
        # TODO: Store max_history
        self.max_history = max_history
        # TODO: Store sample_rate
        self.sample_rate = sample_rate
        # TODO: Initialize frame_counter to 0
        self.frame_counter = 0
        # TODO: Initialize frames_since_last_record to 0
        self.frames_since_last_record = 0
    
    def record_state(self, player_x, player_y):
        """
        Record the current game state (sampled based on sample_rate).
        
        This should be called every frame, but only records every N frames
        based on sample_rate.
        
        Args:
            player_x (float): Current player x position
            player_y (float): Current player y position
        """
        # TODO: Increment frames_since_last_record
        self.frames_since_last_record += 1
        
        # TODO: Check if frames_since_last_record >= sample_rate
        if self.frames_since_last_record >= self.sample_rate:
            # TODO: If yes:
            #   - Create a GameState with the current position and frame counter
            state = GameState(player_x, player_y, self.frame_counter)
            #   - Push the new state onto the history stack
            self.history.push(state)
            
            #   - If history stack size exceeds max_history, remove the oldest state
            #     Hint: You'll need to remove from the BOTTOM of the stack
            #     This is tricky with a stack! Consider using a temporary stack
            if self.history.size() > self.max_history:
                keep = self.max_history - 1
                
                for i in range(self.history.size() - keep):
                    self.history.pop()
            
            #   - Clear the future stack (new actions invalidate redo)
            self.future.clear()
            #   - Reset frames_since_last_record to 0
            self.frames_since_last_record = 0
        
        # TODO: Always increment the frame counter
        self.frame_counter += 1
    
    def can_rewind(self):
        """
        Check if rewinding is possible.
        
        Returns:
            bool: True if we can rewind (history has at least 2 states)
            
        Note: We need at least 2 states because we need to keep the current state
              and go back to the previous one.
        """
        # need at least 2 states to go back
        return self.history.size() > 1
    
    def can_replay(self):
        """
        Check if replaying forward is possible.
        
        Returns:
            bool: True if future stack has states (we've rewound and can go forward)
        """
        # can only replay if future stack has states
        return not self.future.is_empty()
    
    def rewind(self):
        """
        Go back one frame in time.
        
        Returns:
            GameState or None: The previous state to restore to, or None if can't rewind
            
        Algorithm:
            1. Check if we can rewind (need at least 2 states in history)
            2. Pop the current state from history
            3. Push that state onto the future stack (so we can replay later)
            4. Peek at the new top of history (this is where we rewind to)
            5. Return that state
        """
        if not self.can_rewind():
            return None
        
        # move current state to future, return the previous state
        self.future.push(self.history.pop())
        return self.history.peek()
    
    def replay(self):
        """
        Go forward one frame in time (after rewinding).
        
        Returns:
            GameState or None: The next state to restore to, or None if can't replay
            
        Algorithm:
            1. Check if we can replay (future stack must not be empty)
            2. Pop the next state from the future stack
            3. Push it back onto the history stack
            4. Return that state
        """
        if not self.can_replay():
            return None
        
        # move next state back to history and return it
        self.history.push(self.future.pop())
        return self.history.peek()
    
    def get_history_size(self):
        """Get number of states in history"""
        return self.history.size()
    
    def get_future_size(self):
        """Get number of states in future (available for replay)"""
        return self.future.size()
    
    def clear(self):
        """
        Clear all history and future states.
        Call this when switching levels or starting a new game.
        """
        # clear both stacks
        self.history.clear()
        self.future.clear()