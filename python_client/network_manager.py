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
        # 서버에서 오는 모든 데이터를 터미널에 찍어서 확인 (디버깅용)
        print(f"DEBUG: Received from server -> {data}")
        msg_type = data.get("type")
        
        # 화면 객체 미리 가져오기
        chat_screen = self.app.screens.get("CHAT")
        catalog_screen = self.app.screens.get("CATALOG")

        # 1. 신규 유저 팀 선택 요청
        if msg_type == "select_team":
            selected_team = self.app.shared_data.get("faction", "blue")
            print(f"--- NETWORK DEBUG: Server asked for team. Sending: {selected_team} ---")
            self.send_action("select_team", team=selected_team)

        # 2. 로그인 최종 성공 (기존 유저 & 팀 선택 완료한 신규 유저)
        elif msg_type == "initial":
            print("--- NETWORK DEBUG: Login Final Success! ---")
            
            # 사용자 정보 업데이트
            username = data.get("username")
            team = data.get("team")
            self.app.shared_data.update({
                "username": username,
                "team": team,
                "authenticated": True
            })
            
            # [중요] 과거 팀 채팅 기록(리스트) 로드
            history = data.get("team_chat_history", [])
            if chat_screen:
                # 서버가 주는 리스트를 하나씩 꺼내서 채팅창에 추가
                for msg in history:
                    chat_screen.append_message(msg)
            
            # 메인 스레드에 화면 전환 신호 전송
            pygame.event.post(pygame.event.Event(LOGIN_SUCCESS))

        # 3. 실시간 팀 채팅 업데이트 (서버가 2초마다 묶어서 보냄)
        elif msg_type == "team_chat_update":
            messages = data.get("messages", [])
            if chat_screen:
                # 🚨 서버는 메시지 '리스트'를 보내므로 반드시 루프를 돌아야 해!
                for msg in messages:
                    chat_screen.append_message(msg)

        # 4. 게임 카탈로그(통계) 데이터 수신
        elif msg_type == "games_catalog":
            rows = data.get("rows", [])
            print(f"--- NETWORK DEBUG: Received Catalog Rows ({len(rows)}) ---")
            if catalog_screen:
                catalog_screen.load_rows(rows)

        # 5. 글로벌 데이터 (게임 서버 상태 및 글로벌 채팅)
       # NetworkManager 내의 "global" 처리 부분 보강 팁
        elif msg_type == "global":
            self.app.shared_data["games_info"] = data.get("games", {})
            recent = data.get("recent_chats", {})
            game_screen = self.app.screens.get("GAMES")
            
            if game_screen:
                for s_name, msgs in recent.items():
                    # [팁] 서버 이름(s_name)을 UI 이름(u_name)으로 변환하는 과정이 필요할 수 있습니다.
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
                # 서버가 {"type": "profile", "data": {...}} 형태로 보내니까 data.get("data")를 넘겨줌
                profile_screen.load_data(data.get("data", {}))

    # network_manager.py 파일 안에 추가

    def logout(self):
        """로그아웃 처리: 인증 해제 및 로그인 화면으로 이동"""
        print("--- NETWORK: Logging out... ---")
        # 1. 인증 정보 초기화
        self.app.shared_data["authenticated"] = False
        self.app.shared_data["username"] = None
        
        # 2. 화면을 로그인으로 돌려보냄
        self.app.switch_screen("LOGIN")
        
        # 3. (선택사항) 서버에 로그아웃 알림을 보내고 싶다면?
        # self.send_action("logout")
    def send_action(self, action_type, **kwargs):
        print(f"--- NETWORK DEBUG: send_action called with {action_type} ---") # 3번 확인
        if not self.is_connected or not self.ws:
            print("--- NETWORK DEBUG: ERROR - Not connected! ---")
            return

        payload = json.dumps({"type": "user", "action": action_type, **kwargs})
        asyncio.run_coroutine_threadsafe(self.ws.send(payload), self.loop)
    def send_score(self, game_name, score):
        """
        게임이 끝났을 때 서버에 점수를 전송합니다.
        :param game_name: 플레이한 게임 이름 (예: 'lumberjack')
        :param score: 획득한 점수 (정수)
        """
        if not self.is_connected:
            print("--- NETWORK ERROR: Cannot send score, not connected! ---")
            return

        print(f"--- NETWORK: Submitting score [{score}] for game [{game_name}] ---")
        
        # 기존의 send_action 기능을 활용해 서버에 전달
        # 서버에서 action: "submit_score"를 처리하도록 약속되어 있어야 합니다.
        
    # 서버 로그에서 "action": "score"를 쓰고 있다면 이름을 맞춰야 합니다.
        self.send_action(
            "score",  # "submit_score"에서 "score"로 변경 (로그 기반)
            game=game_name, 
            individual_score=score,
            team=self.app.shared_data.get("team", "blue"),
            team_score=0, # 필요시 추가
            game_time=10  # 필요시 추가
        )