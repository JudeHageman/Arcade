# py_client/network_manager.py
import asyncio
import websockets
import json
import threading
import pygame

# Define a custom event for login success
LOGIN_SUCCESS = pygame.USEREVENT + 1

class NetworkManager:
    def __init__(self, app, port=8000):
        self.app = app
        self.url = f"ws://127.0.0.1:{port}"
        self.ws = None
        self.loop = None
        self.is_connected = False

    def start_connection(self):
        """Start the background thread for websocket communication."""
        threading.Thread(target=self._run_async_loop, daemon=True).start()

    def _run_async_loop(self):
        """Internal thread to run the asyncio loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._listen())

    async def _listen(self):
        """Maintain persistent connection and listen for server messages."""
        try:
            async with websockets.connect(self.url) as websocket:
                self.ws = websocket
                self.is_connected = True
                print(f"Connected to server at {self.url}")

                async for message in websocket:
                    data = json.loads(message)
                    self._handle_server_payload(data)
        except Exception as e:
            print(f"Connection Error: {e}")
            self.is_connected = False

    def _handle_server_payload(self, data):
         
        print(f"DEBUG: Received from server -> {data}")
        msg_type = data.get("type")
        
         
        chat_screen = self.app.screens.get("CHAT")
        catalog_screen = self.app.screens.get("CATALOG")

         
        if msg_type == "select_team":
            selected_team = self.app.shared_data.get("faction", "blue")
            print(f"--- NETWORK DEBUG: Server asked for team. Sending: {selected_team} ---")
            self.send_action("select_team", team=selected_team)

         
        elif msg_type == "initial":
            print("--- NETWORK DEBUG: Login Final Success! ---")
            
             
            username = data.get("username")
            team = data.get("team")
            self.app.shared_data.update({
                "username": username,
                "team": team,
                "authenticated": True
            })
            
             
            history = data.get("team_chat_history", [])
            if chat_screen:
                 
                for msg in history:
                    chat_screen.append_message(msg)
            
             
            pygame.event.post(pygame.event.Event(LOGIN_SUCCESS))

         
        elif msg_type == "team_chat_update":
            messages = data.get("messages", [])
            if chat_screen:
                 
                for msg in messages:
                    chat_screen.append_message(msg)

         
        elif msg_type == "games_catalog":
            rows = data.get("rows", [])
            print(f"--- NETWORK DEBUG: Received Catalog Rows ({len(rows)}) ---")
            if catalog_screen:
                catalog_screen.load_rows(rows)

         
        elif msg_type == "global":
            self.app.shared_data["games_info"] = data.get("games", {})
            recent = data.get("recent_chats", {})
            game_screen = self.app.screens.get("GAMES")
            
            if game_screen:
                for s_name, msgs in recent.items():
                     
                    # 예: "Game 2" -> "Island Gardener"
                    target_ui_name = s_name
                    if s_name == "Game 2": target_ui_name = "Island Gardener"
                    elif s_name == "Game 3": target_ui_name = "MELODY DASH"
                    
                    for m in msgs:
                        game_screen.add_message(target_ui_name, m['sender'], m['message'])
        elif msg_type == "leaderboard":
            # data: {"type": "leaderboard", "rows": [...], "own_rank": ...}
            lb_screen = self.app.screens.get("LEADERBOARD")
            if lb_screen:
                lb_screen.load_data(data)
        elif msg_type == "player_search":
            # data: {"results": [{"username": "...", "team": "..."}, ...]}
            search_screen = self.app.screens.get("SEARCH") # 스크린 이름 확인!
            if search_screen:
                search_screen.load_results(data.get("results", []))

        elif msg_type == "player_profile":
            # data: {"data": {"username": "...", "total_games": ...}}
            search_screen = self.app.screens.get("SEARCH")
            if search_screen:
                search_screen.load_profile(data.get("data", {}))
        elif msg_type == "match_history":
            # data: {"type": "match_history", "data": [...]}
            mh_screen = self.app.screens.get("HISTORY")
            if mh_screen:
                mh_screen.load_data(data.get("data", []))
        elif msg_type == "profile":
            profile_screen = self.app.screens.get("PROFILE")
            if profile_screen:
                 
                profile_screen.load_data(data.get("data", {}))

     

    def logout(self):
        """로그아웃 처리: 인증 해제 및 로그인 화면으로 이동"""
        print("--- NETWORK: Logging out... ---")
         
        self.app.shared_data["authenticated"] = False
        self.app.shared_data["username"] = None
        
         
        self.app.switch_screen("LOGIN")
        
         
    def send_action(self, action_type, **kwargs):
        print(f"--- NETWORK DEBUG: send_action called with {action_type} ---")  
        if not self.is_connected or not self.ws:
            print("--- NETWORK DEBUG: ERROR - Not connected! ---")
            return

        payload = json.dumps({"type": "user", "action": action_type, **kwargs})
        asyncio.run_coroutine_threadsafe(self.ws.send(payload), self.loop)
     
    def send_score(self, game_name, score, team, team_score=0, game_time=0):
        """서버가 로그에 찍을 수 있도록 점수 데이터를 JSON으로 전송"""
        if not self.connected:
            return

         
        payload = {
            "type": "user",
            "action": "score",
            "username": self.player_name,
            "game": game_name,
            "individual_score": score,
            "team": team,
            "team_score": team_score,
            "game_time": game_time
        }

        try:
             
            message = json.dumps(payload) + "\n"
            self.sock.sendall(message.encode('utf-8'))
            print(f"📡 [NETWORK] Score data sent to server: {score}")
        except Exception as e:
            print(f"❌ [NETWORK] Failed to send score: {e}")