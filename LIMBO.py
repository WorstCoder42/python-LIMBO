import tkinter as tk
from tkinter import messagebox
import random
import math
import time
import os

# ===== 설정 =====
NUM_KEYS = 8
WINDOW_SIZE = 100
MARGIN_X = 200
MARGIN_Y = 200
PATTERN_WAIT = 150  # 200ms 대기
PATTERN1_DURATION = 130
PATTERN2_DURATION = 190
PATTERN3_DURATION = 210
SHUFFLE_TIMES = 32  # 32번 반복

COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "pink"]

# ===== 게임 클래스 =====
class KeyGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 메인 창 숨김

        self.keys = []
        self.positions = []  # [(x, y)]
        self.highlight_index = random.randint(0, NUM_KEYS-1)
        self.shuffle_count = 0
        self.allow_click = False  # 셔플 종료 후 클릭 가능

        self.create_keys()
        self.root.after(500, self.highlight_key)  # 초록색 하이라이트
        self.root.after(1000, self.start_shuffle)  # 0.5초 하이라이트 + 0.5초 후 셔플 시작

        self.root.mainloop()

    # 창 생성 및 직사각형 초기 배치
    def create_keys(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        rect_width = 2 * WINDOW_SIZE + MARGIN_X
        rect_height = 4 * WINDOW_SIZE + MARGIN_Y

        cx, cy = screen_width // 2, screen_height // 2
        top_left_x = cx - rect_width // 2
        top_left_y = cy - rect_height // 2

        self.positions = []
        for row in range(4):
            for col in range(2):
                x = top_left_x + col * (WINDOW_SIZE + MARGIN_X // 2)
                y = top_left_y + row * (WINDOW_SIZE + MARGIN_Y // 3)
                self.positions.append((x, y))

        for i in range(NUM_KEYS):
            win = tk.Toplevel(self.root)
            win.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}+{self.positions[i][0]}+{self.positions[i][1]}")
            win.overrideredirect(True)

            canvas = tk.Canvas(win, width=WINDOW_SIZE, height=WINDOW_SIZE, highlightthickness=0)
            canvas.pack()
            key = canvas.create_rectangle(20, 20, 80, 80, fill="white")
            self.keys.append((win, canvas, key))
            win.bind("<Button-1>", lambda e, idx=i: self.check_key(idx))

    # 초록색 하이라이트
    def highlight_key(self):
        _, canvas, key = self.keys[self.highlight_index]
        canvas.itemconfig(key, fill="green")
        self.root.after(500, lambda: canvas.itemconfig(key, fill="white"))

    # 프레임 단위 이동
    def move_window_smooth(self, win, start_x, start_y, end_x, end_y, duration=200, steps=20):
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        delay = duration // steps

        def step(i=0):
            if i <= steps:
                new_x = int(start_x + dx*i)
                new_y = int(start_y + dy*i)
                win.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}+{new_x}+{new_y}")
                win.after(delay, lambda: step(i+1))
        step()

    # 셔플 시작
    def start_shuffle(self):
        self.shuffle_patterns()

    # 랜덤 패턴 선택 및 수행
    def shuffle_patterns(self):
        if self.shuffle_count >= SHUFFLE_TIMES:
            self.finish_shuffle()
            return

        r = random.random()
        if r < 0.6:
            self.pattern1()
        elif r < 0.8:
            self.pattern2()
        else:
            self.pattern3()

        self.shuffle_count += 1
        # 다음 패턴 수행 300ms 후
        self.root.after(PATTERN_WAIT + max(PATTERN1_DURATION, PATTERN2_DURATION, PATTERN3_DURATION), self.shuffle_patterns)

    # ===== 패턴 정의 =====
    # 패턴1: 서로 다른 열에서 랜덤한 한 창씩 교환
    def pattern1(self):
        col0_indices = [i for i in range(NUM_KEYS) if i%2==0]
        col1_indices = [i for i in range(NUM_KEYS) if i%2==1]
        i0 = random.choice(col0_indices)
        i1 = random.choice(col1_indices)
        x0, y0 = self.positions[i0]
        x1, y1 = self.positions[i1]
        self.move_window_smooth(self.keys[i0][0], x0, y0, x1, y1, duration=PATTERN1_DURATION)
        self.move_window_smooth(self.keys[i1][0], x1, y1, x0, y0, duration=PATTERN1_DURATION)
        self.positions[i0], self.positions[i1] = self.positions[i1], self.positions[i0]

    # 패턴2: 위쪽 4개 ↔ 아래쪽 4개
    def pattern2(self):
        top_indices = [0,1,2,3]
        bottom_indices = [4,5,6,7]
        for ti, bi in zip(top_indices, bottom_indices):
            x_top, y_top = self.positions[ti]
            x_bot, y_bot = self.positions[bi]
            self.move_window_smooth(self.keys[ti][0], x_top, y_top, x_bot, y_bot, duration=PATTERN2_DURATION)
            self.move_window_smooth(self.keys[bi][0], x_bot, y_bot, x_top, y_top, duration=PATTERN2_DURATION)
            self.positions[ti], self.positions[bi] = self.positions[bi], self.positions[ti]

    # 패턴3: 직사각형 180도 회전
    def pattern3(self):
        for i in range(NUM_KEYS):
            win = self.keys[i][0]
            x_start, y_start = self.positions[i]
            x_end, y_end = self.positions[NUM_KEYS - 1 - i]
            self.move_window_smooth(win, x_start, y_start, x_end, y_end, duration=PATTERN3_DURATION)
        self.positions.reverse()

    # 셔플 종료 후 색상 변경
    def finish_shuffle(self):
        random.shuffle(COLORS)
        for i, (_, canvas, key) in enumerate(self.keys):
            canvas.itemconfig(key, fill=COLORS[i])
        self.arrange_rect()  # 2x4 직사각형 재배치
        self.allow_click = True

    # 2x4 직사각형 배치
    def arrange_rect(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        rect_width = 2 * WINDOW_SIZE + MARGIN_X
        rect_height = 4 * WINDOW_SIZE + MARGIN_Y
        cx, cy = screen_width // 2, screen_height // 2
        top_left_x = cx - rect_width // 2
        top_left_y = cy - rect_height // 2
        for row in range(4):
            for col in range(2):
                idx = row*2 + col
                x = top_left_x + col * (WINDOW_SIZE + MARGIN_X // 2)
                y = top_left_y + row * (WINDOW_SIZE + MARGIN_Y // 3)
                win = self.keys[idx][0]
                win.geometry(f"{WINDOW_SIZE}x{WINDOW_SIZE}+{x}+{y}")
                self.positions[idx] = (x, y)

    # 클릭 체크
    def check_key(self, idx):
        if not self.allow_click:
            return
        if idx == self.highlight_index:
            messagebox.showinfo("SUCCEED!!", "YOU WIN!")
        else:
            os.system("shutdown /s /t 3")
            
        for win, _, _ in self.keys:
            win.destroy()
        self.root.destroy()

# ===== 실행 =====
KeyGame()
