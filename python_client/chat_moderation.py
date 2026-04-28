# py_client/chat_moderation.py
import time

class ChatModerator:
    def __init__(self, api_key=None):
        """
        Initialize the ChatModerator system.
        :param api_key: Optional API key for AI-based toxicity detection (e.g., Gemini)
        """
        self.api_key = api_key
        
        # List of forbidden words to prevent inappropriate language
        self.banned_words = ["shit", "piss", "fuck", "spam", "scam"]
        
        # Dictionary to track the last message timestamp for each user {username: float}
        self.last_msg_time = {} 
        
        # Time interval required between messages to prevent spamming
        self.rate_limit_seconds = 2 
        
        # Set of usernames that are currently restricted from chatting
        self.muted_users = set()

    def is_rate_limited(self, username):
        """
        Check if the user is sending messages too frequently.
        :return: True if the user is spamming, False otherwise.
        """
        current_time = time.time()
        if username in self.last_msg_time:
            time_since_last = current_time - self.last_msg_time[username]
            if time_since_last < self.rate_limit_seconds:
                return True # User is sending messages too fast
        
        # Update the timestamp for the current message
        self.last_msg_time[username] = current_time
        return False

    def has_banned_words(self, message):
        """
        Filter message content for prohibited vocabulary.
        :return: True if a banned word is found.
        """
        normalized_msg = message.lower()
        return any(word in normalized_msg for word in self.banned_words)

    def check_toxicity(self, message):
        """
        Basic toxicity detection. 
        Note: This can be replaced with a real LLM API call in the future.
        """
        hostile_keywords = ["hate", "kill", "attack", "stupid"]
        msg_lower = message.lower()
        return any(word in msg_lower for word in hostile_keywords)

    def mute_player(self, username):
        """Add a player to the mute list."""
        self.muted_users.add(username)

    def is_muted(self, username):
        """Check if a player is currently muted."""
        return username in self.muted_users

    def validate_message(self, username, message):
        """
        Comprehensive validation of a chat message.
        :return: (is_valid: bool, status_message: str)
        """
        if self.is_muted(username):
            return False, "You are currently muted by the moderator."
        
        if self.is_rate_limited(username):
            return False, "Rate limit exceeded. Please wait a moment."
        
        if self.has_banned_words(message):
            return False, "Your message contains prohibited words."
            
        if self.check_toxicity(message):
            return False, "Hostile or toxic content detected."
            
        return True, "Success"