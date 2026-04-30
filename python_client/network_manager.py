# py_client/network_manager.py
import asyncio
import websockets
import json
import threading
import pygame

# Define a custom event for login success
LOGIN_SUCCESS = pygame.USEREVENT + 1

class NetworkManager:
    def __init__(self, app, port=50085):
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

        # 1. 신규 유저 팀 선택 요청
        if msg_type == "select_team":
            selected_team = self.app.shared_data.get("faction", "blue")
            print(f"--- NETWORK DEBUG: Sending team choice: {selected_team} ---")
            self.send_action("select_team", team=selected_team)

        # 2. 로그인 최종 성공 (기존 유저 & 팀 선택 완료한 신규 유저)
        elif msg_type == "initial":
            print("--- NETWORK DEBUG: Login Final Success! ---")
            
            # 데이터 저장
            self.app.shared_data.update({
                "username": data.get("username"),
                "team": data.get("team"),
                "authenticated": True
            })
            
            # 과거 채팅 기록 전달
            chat_history = data.get("chat_history", {})
            # 현재 화면뿐만 아니라 대시보드 화면 객체 자체에 데이터를 넘겨주는 게 안전해
            dashboard = self.app.screens.get("DASHBOARD") # ArcadeApp에 등록한 이름 확인!
            if dashboard and hasattr(dashboard, "load_history"):
                dashboard.load_history(chat_history)
            
            # [중요] 메인 스레드에 화면 전환 신호 전송 (딱 한 번만!)
            pygame.event.post(pygame.event.Event(LOGIN_SUCCESS))

        # 3. 실시간 데이터 업데이트 (채팅, 점수 등)
        elif msg_type == "initial":
        # 1. 과거 기록 배달
            chat_history = data.get("chat_history", {})
            # [수정] "DASHBOARD"가 아니라 "CHAT"으로 이름을 맞춰야 해!
            chat_screen = self.app.screens.get("CHAT") 
            if chat_screen and hasattr(chat_screen, "load_history"):
                chat_screen.load_history(chat_history)
            
            pygame.event.post(pygame.event.Event(LOGIN_SUCCESS))

        elif msg_type == "global":
            # 2. 실시간 채팅 배달
            recent_chats = data.get("recent_chats", {})
            chat_screen = self.app.screens.get("CHAT") # 여기서도 "CHAT"!
            if chat_screen and hasattr(chat_screen, "append_message"):
                for game_name, messages in recent_chats.items():
                    for m in messages:
                        chat_type = "team" if game_name == "TeamChannel" else "global"
                        chat_screen.append_message(chat_type, m['sender'], m['message'])
        
   
    def send_action(self, action_type, **kwargs):
        print(f"--- NETWORK DEBUG: send_action called with {action_type} ---") # 3번 확인
        if not self.is_connected or not self.ws:
            print("--- NETWORK DEBUG: ERROR - Not connected! ---")
            return

        payload = json.dumps({"type": "user", "action": action_type, **kwargs})
        asyncio.run_coroutine_threadsafe(self.ws.send(payload), self.loop)