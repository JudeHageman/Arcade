"""
time_travel.py - Time travel system using stacks

Implements rewind/replay functionality for single-player mode.
Disabled when multiple players are connected.

Author: Minju Seo
Date: 2026-02-19
Lab: Lab 4 - Time Travel with Stacks
"""

from datastructures.stack import Stack


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
        """
        self.history = Stack()
        self.future = Stack()
        self.max_history = max_history
        self.sample_rate = sample_rate
        
        self.frame_counter = 0
        self.frames_since_last_record = 0
        self.rewinding = False
    
    def record_state(self, player_x, player_y):
        """
        Record the current game state (sampled based on sample_rate).
        """
        self.frames_since_last_record += 1
        
        # Check if it's time to record based on sample_rate
        if self.frames_since_last_record >= self.sample_rate:
            # 1. Create a GameState snapshot
            state = GameState(player_x, player_y, self.frame_counter)
            
            # 2. Push to history
            self.history.push(state)
            
            # 3. Handle max_history overflow (Remove oldest from BOTTOM)
            if self.history.size() > self.max_history:
                # Using a temporary stack to reach the bottom element
                temp_stack = Stack()
                while self.history.size() > 1:
                    temp_stack.push(self.history.pop())
                
                # The remaining item in history is the oldest one; pop and discard it
                self.history.pop()
                
                # Push everything back into history
                while not temp_stack.is_empty():
                    self.history.push(temp_stack.pop())
            
            # 4. Clear future (New movement invalidates redo/replay)
            if not self.future.is_empty():
                self.future.clear()
            
            # 5. Reset internal counter
            self.frames_since_last_record = 0
            
        # Always increment the total frame counter
        self.frame_counter += 1
    
    def can_rewind(self):
        """Returns True if history has at least 2 states."""
        return self.history.size() >= 2
    
    def can_replay(self):
        """Returns True if future stack is not empty."""
        return not self.future.is_empty()
    
    def rewind(self):
        """Go back one frame in time."""
        if not self.can_rewind():
            return None
            
        # Move current state to future
        current_state = self.history.pop()
        self.future.push(current_state)
        
        # New current state is the top of history
        return self.history.peek()
    
    def replay(self):
        """Go forward one frame in time (after rewinding)."""
        if not self.can_replay():
            return None
            
        # Move state from future back to history
        next_state = self.future.pop()
        self.history.push(next_state)
        
        return next_state
    
    def get_history_size(self):
        """Get number of states in history."""
        return self.history.size()
    
    def get_future_size(self):
        """Get number of states in future."""
        return self.future.size()
    
    def clear(self):
        """Clear all history and future states."""
        self.history.clear()
        self.future.clear()
        self.frame_counter = 0
        self.frames_since_last_record = 0