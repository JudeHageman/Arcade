import pygame
import math
import sys
from pathlib import Path
from screens.base_screen import BaseScreen
from ui.button import Button

# --- [Minju Style] 진짜 루트 폴더(Arcade)까지 올라가서 경로 등록 ---
base_path = Path(__file__).parent.parent.parent

# 1. 자료구조 경로 (Arcade/data_structures)
ds_path = str(base_path / "data_structures")
if ds_path not in sys.path:
    sys.path.insert(0, ds_path)

# 2. 알고리즘 경로 (Arcade/algorithms/sorting)
sorting_path = str(base_path / "algorithms" / "sorting")
if sorting_path not in sys.path:
    sys.path.insert(0, sorting_path)

# 임포트 시도
try:
    from dynamic_array import ArrayList
    from merge_sort import mergesort
    print("✅ Successfully imported ArrayList and MergeSort")
except ImportError as e:
    print(f"❌ Import failed: {e}")

class LeaderboardScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.resizable = True
        self.base_w, self.base_h = 1280, 720
        
        # 1. 컬러 팔레트
        self.colors = {
            "blue": (100, 200, 255),
            "pink": (255, 120, 180),
            "green": (120, 230, 120),
            "black": (30, 30, 30),
            "white": (255, 255, 255),
            "staff": (235, 235, 235)
        }

        # 실제 서버 데이터를 담을 ArrayList
        self.rank_data = ArrayList() 
        
        self.back_btn = None
        self.time = 0
        self.refresh_layout()

    def refresh_layout(self):
        """창 크기에 맞춰 테이블 위치와 폰트 크기 재계산"""
        self.scale = max(self.app.WIDTH / self.base_w, 0.6)
        s = self.scale
        cx = self.app.WIDTH // 2

        # 폰트 업데이트
        self.font_title = pygame.font.SysFont("Arial", max(int(54 * s), 32), bold=True)
        self.font_header = pygame.font.SysFont("Arial", max(int(22 * s), 16), bold=True)
        self.font_row = pygame.font.SysFont("Arial", max(int(20 * s), 14))

        # 뒤로가기 버튼 (디자인 복구!)
        self.back_btn = Button(int(40 * s), int(40 * s), int(120 * s), int(45 * s), 
                               "< BACK", color=self.colors["staff"], action=lambda: self.app.switch_screen("MENU"))

        # 테이블 레이아웃
        self.table_w = int(850 * s)
        self.table_x = cx - self.table_w // 2
        self.header_y = int(180 * s)
        self.row_height = int(55 * s)

    # LeaderboardScreen.py 의 update_leaderboard 함수 수정
    def update_leaderboard(self, raw_data):
        """서버에서 받은 데이터를 안전하게 정렬해서 화면용 데이터로 저장"""
        # 1. [에러 방지] ArrayList나 서버 데이터를 파이썬 기본 리스트로 복사
        # 이렇게 해야 머지소트 내부의 슬라이싱([:mid])이 에러 없이 돌아가!
        python_list = []
        for i in range(len(raw_data)):
            python_list.append(raw_data[i])

        try:
            # 2. [핵심] mergesort에게 "딕셔너리 안에 있는 'score'로 비교해!"라고 알려주기
            # 민주가 짠 머지소트 코드의 파라미터(key, reverse)를 100% 활용하는 거야.
            self.rank_data = mergesort(
                python_list, 
                key=lambda x: x.get('score', 0), # 점수를 비교 대상으로 지정
                reverse=True                    # 높은 점수가 위로 오게 정렬
            )
            print(f"--- UI DEBUG: Leaderboard sorted ({len(self.rank_data)} players) ---")
            
        except Exception as e:
            print(f"--- 여전히 SORT ERROR 발생: {e} ---")
            # 정렬 에러가 나면 일단 데이터라도 보여주기 위해 내장 정렬 사용
            python_list.sort(key=lambda x: x.get('score', 0), reverse=True)
            self.rank_data = python_list
                
        except Exception as e:
            print(f"--- 여전히 에러가 난다면: {e} ---")
            # 정렬에 실패해도 화면이 멈추지 않게 방어 로직
            python_list.sort(key=lambda x: x.get('score', 0), reverse=True)
            self.rank_data = python_list

    def draw(self, screen):
        faction = self.app.shared_data.get("team", "blue")
        theme_color = self.colors.get(faction, self.colors["blue"])
        
        screen.fill(self.colors["white"])
        self.draw_decorations(screen, theme_color)

        title_surf = self.font_title.render("TOP RESONANCE", True, self.colors["black"])
        screen.blit(title_surf, (self.app.WIDTH // 2 - title_surf.get_width() // 2, int(80 * self.scale)))

        s = self.scale
        # 헤더 선 그리기
        pygame.draw.line(screen, theme_color, (self.table_x, self.header_y + int(40 * s)), 
                         (self.table_x + self.table_w, self.header_y + int(40 * s)), int(3 * s))
        
        # 로우 데이터 그리기 (팀 이름 제외 버전)
        start_y = self.header_y + int(60 * s)
        for i in range(min(len(self.rank_data), 10)):
            entry = self.rank_data[i]
            curr_y = start_y + (i * self.row_height)
            
            u_name = entry.get("username", "Unknown")
            u_score = entry.get("score", 0)
            u_team = entry.get("team", "blue") # 색상 참조용으로만 사용
            
            # 팀에 맞는 색상 가져오기 (순위 숫자에 적용)
            row_color = self.colors.get(u_team, (100, 100, 100))
            
            # 텍스트 렌더링 (팀 이름 t_text는 삭제!)
            r_text = self.font_row.render(str(i + 1), True, row_color if i < 3 else (100, 100, 100))
            n_text = self.font_row.render(u_name, True, self.colors["black"])
            s_text = self.font_row.render(f"{u_score:,} pts", True, self.colors["black"])
            
            # 화면에 배치 (간격 조정)
            screen.blit(r_text, (self.table_x + int(50 * s), curr_y))       # 순위
            screen.blit(n_text, (self.table_x + int(180 * s), curr_y))      # 이름 (팀이 빠진 만큼 넓게 배치)
            screen.blit(s_text, (self.table_x + self.table_w - int(180 * s), curr_y)) # 점수
            
            # 가로 구분선 (선택 사항: 더 깔끔하게 보이려면 추가)
            # pygame.draw.line(screen, (240, 240, 240), (self.table_x, curr_y + int(40 * s)), 
            #                  (self.table_x + self.table_w, curr_y + int(40 * s)), 1)

        self.back_btn.draw(screen)

    def draw_decorations(self, screen, theme_color):
        """민주만의 음악 테마 디자인 복구"""
        self.time += 0.02
        s = self.scale
        
        # 1. 배경 오선
        for i in range(5):
            y = int(400 * s) + (i * int(30 * s))
            pygame.draw.line(screen, self.colors["staff"], (0, y), (self.app.WIDTH, y - int(100 * s)), 2)

        # 2. 팀 공명 원
        res_pos = [(150*s, 150*s, 60*s), (self.app.WIDTH - 150*s, 150*s, 70*s)]
        for x, y, r in res_pos:
            pulse = math.sin(self.time * 1.5 + x) * (5 * s)
            pygame.draw.circle(screen, theme_color, (int(x), int(y)), int(r + pulse), 3)

        # 3. 알록달록 음표
        note_colors = [self.colors["blue"], self.colors["pink"], self.colors["green"]]
        for i in range(3):
            nx = (300 + i * 350) * s
            ny = (100 + (i % 2) * 50) * s
            self.draw_music_note(screen, (nx, ny + math.sin(self.time * 3 + i) * 12), note_colors[i % 3])

    def draw_music_note(self, screen, pos, color):
        s = self.scale
        x, y = int(pos[0]), int(pos[1])
        r = 10 * s
        pygame.draw.circle(screen, color, (x, y), int(r))
        pygame.draw.line(screen, color, (x + r - 2, y), (x + r - 2, y - 28 * s), int(3 * s))
        pygame.draw.line(screen, color, (x + r - 2, y - 28 * s), (x + r + 10 * s, y - 18 * s), int(3 * s))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.app.WIDTH, self.app.HEIGHT = event.w, event.h
                self.refresh_layout()
            self.back_btn.handle_event(event)

    def update(self): pass

     