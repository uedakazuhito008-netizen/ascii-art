#!/usr/bin/env python3
"""
Snake — ターミナル スネーク ゲーム
矢印キー / WASD で操作、Q で終了
"""
import sys, os, time, random, shutil, json
from collections import deque

# ── Windows ANSI 有効化 ───────────────────────────────────────────────────────
def enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass

# ── カラー ────────────────────────────────────────────────────────────────────
R    = "\033[0m"
BOLD = "\033[1m"

def rgb(r, g, b): return f"\033[38;2;{r};{g};{b}m"

RAINBOW = [
    rgb(255, 80,  80), rgb(255, 180,   0), rgb(255, 255,  60),
    rgb( 60, 255,  60), rgb( 60, 160, 255), rgb(200,  60, 255),
]
NAMED = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m", "white": "\033[97m",
}
def col(text, name): return NAMED.get(name, "") + text + R

# ── キー入力 ─────────────────────────────────────────────────────────────────
if sys.platform == "win32":
    import msvcrt
    def key_ready(): return msvcrt.kbhit()
    def get_key():
        ch = msvcrt.getch()
        if ch in (b'\xe0', b'\x00'):
            a = msvcrt.getch()
            return {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}.get(a)
        d = ch.decode('utf-8', errors='ignore').upper()
        return d if d else None
else:
    import tty, termios, select
    def key_ready(): return bool(select.select([sys.stdin], [], [], 0)[0])
    def get_key():
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            rest = sys.stdin.read(2)
            return {'[A': 'UP', '[B': 'DOWN', '[D': 'LEFT', '[C': 'RIGHT'}.get(rest)
        return ch.upper() if ch else None

# ── 端末ユーティリティ ────────────────────────────────────────────────────────
def clear():     sys.stdout.write("\033[2J\033[H")
def goto(r, c):  return f"\033[{r};{c}H"
def hide_cur():  sys.stdout.write("\033[?25l")
def show_cur():  sys.stdout.write("\033[?25h")
def term_size():
    s = shutil.get_terminal_size((80, 24))
    return s.columns, s.lines

# ── ハイスコア ────────────────────────────────────────────────────────────────
_SF = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".snake_score")
def load_high():
    try:
        with open(_SF) as f: return json.load(f).get("high", 0)
    except Exception: return 0
def save_high(s):
    try:
        with open(_SF, 'w') as f: json.dump({"high": s}, f)
    except Exception: pass

# ── 定数 ─────────────────────────────────────────────────────────────────────
BW, BH = 42, 22          # ボーダーサイズ
IW, IH = BW - 2, BH - 2  # 内側プレイエリア
FOOD_CHARS = ["●", "★", "♥", "◆", "▲"]
FOOD_COLS  = ["red", "magenta", "yellow", "cyan", "green"]

# ── タイトルアート ────────────────────────────────────────────────────────────
def title_art():
    try:
        import pyfiglet
        lines = pyfiglet.figlet_format("SNAKE", font="big").splitlines()
        return [l for l in lines if l.strip()]
    except Exception:
        return [
            r" ____  _  _   _   _  _  _____",
            r"/ ___|| \| | /_\ | |/ /| ____|",
            r"\___ \| .` |/ _ \|   < | _|   ",
            r" ___/ | |\  / ___ \ |\ \| |___ ",
            r"|____/|_| \_/_/   \_\_| \_\_____|",
        ]

# ── ゲームプレイ ──────────────────────────────────────────────────────────────
def play():
    tw, th = term_size()
    high   = load_high()
    or_    = max(3, (th - BH) // 2)
    oc     = max(1, (tw - BW) // 2)

    # スネーク初期化 (中央から右向き 3 マス)
    r0, c0 = IH // 2, IW // 2
    snake     = deque([(r0, c0), (r0, c0 - 1), (r0, c0 - 2)])
    snake_set = set(snake)
    dr, dc    = 0, 1
    ndr, ndc  = 0, 1

    def rand_food():
        while True:
            p = (random.randint(0, IH - 1), random.randint(0, IW - 1))
            if p not in snake_set:
                return p, random.choice(FOOD_CHARS), random.choice(FOOD_COLS)

    fp, fc, fcl = rand_food()
    score, frame, speed = 0, 0, 0.13

    # ── 描画ヘルパー ──────────────────────────────────────────────────────────
    def at(row, c_): return goto(or_ + 1 + row, oc + 1 + c_)

    def draw_header():
        if or_ >= 2:
            t = (f"  SCORE:{col(str(score).zfill(4), 'yellow')}"
                 f"  BEST:{col(str(high).zfill(4), 'cyan')}"
                 f"  {col('↑←↓→/WASD', 'white')}  {col('Q=Quit', 'magenta')}")
            sys.stdout.write(goto(or_ - 1, oc) + t + "          ")

    def draw_border():
        buf = [goto(or_, oc) + col("╔" + "═" * IW + "╗", "cyan")]
        for i in range(1, BH - 1):
            buf.append(goto(or_ + i, oc) + col("║", "cyan") + " " * IW + col("║", "cyan"))
        buf.append(goto(or_ + BH - 1, oc) + col("╚" + "═" * IW + "╝", "cyan"))
        sys.stdout.write("".join(buf))

    def draw_food():
        sys.stdout.write(at(fp[0], fp[1]) + col(BOLD + fc, fcl))

    def draw_head(p):
        sys.stdout.write(at(p[0], p[1]) + RAINBOW[frame % 6] + "█" + R)

    def draw_body(p, idx):
        sys.stdout.write(at(p[0], p[1]) + RAINBOW[idx % 6] + "▓" + R)

    def erase(p):
        sys.stdout.write(at(p[0], p[1]) + " ")

    # ── 初期描画 ──────────────────────────────────────────────────────────────
    clear()
    hide_cur()
    draw_border()
    draw_header()
    for i, seg in enumerate(snake):
        if i == 0:
            draw_head(seg)
        else:
            draw_body(seg, i)
    draw_food()
    sys.stdout.flush()

    last = time.perf_counter()
    died = False

    while True:
        # 入力処理
        while key_ready():
            k = get_key()
            if k in ('Q', '\x03', '\x1b'):
                return score, high, False
            nd = {
                'UP': (-1, 0), 'W': (-1, 0),
                'DOWN': (1, 0), 'S': (1, 0),
                'LEFT': (0, -1), 'A': (0, -1),
                'RIGHT': (0, 1), 'D': (0, 1),
            }.get(k)
            if nd and (nd[0] + dr, nd[1] + dc) != (0, 0):
                ndr, ndc = nd

        now = time.perf_counter()
        if now - last < speed:
            time.sleep(0.005)
            continue

        last   = now
        dr, dc = ndr, ndc
        frame += 1

        head = snake[0]
        nh   = (head[0] + dr, head[1] + dc)

        if not (0 <= nh[0] < IH and 0 <= nh[1] < IW):
            died = True
            break
        if nh in snake_set:
            died = True
            break

        ate = (nh == fp)
        snake.appendleft(nh)
        snake_set.add(nh)

        draw_body(head, frame + 1)
        draw_head(nh)

        if ate:
            score += 10
            if score > high:
                high = score
                save_high(high)
            fp, fc, fcl = rand_food()
            draw_food()
            speed = max(0.04, speed - 0.005)
            draw_header()
        else:
            tail = snake.pop()
            snake_set.discard(tail)
            erase(tail)

        sys.stdout.flush()

    return score, high, died

# ── ゲームオーバー画面 ────────────────────────────────────────────────────────
def game_over(score, high):
    tw, th = term_size()
    box = [
        ("╔══════════════════════════════╗", "red"),
        ("║      G A M E   O V E R      ║", "red"),
        (f"║  SCORE: {str(score).zfill(4)}   BEST: {str(high).zfill(4)}    ║", "yellow"),
        ("║    [R] Retry    [Q] Quit     ║", "cyan"),
        ("╚══════════════════════════════╝", "red"),
    ]
    r  = th // 2 - len(box) // 2
    c_ = max(0, (tw - 32) // 2)
    for i, (line, color) in enumerate(box):
        sys.stdout.write(goto(r + i, c_) + col(line, color))
    sys.stdout.flush()

# ── タイトル画面 ──────────────────────────────────────────────────────────────
def title():
    tw, th = term_size()
    high   = load_high()
    clear()

    art = title_art()
    aw  = max(len(l) for l in art)
    ar  = max(2, (th - len(art) - 6) // 2)
    ac  = max(1, (tw - aw) // 2)

    for i, line in enumerate(art):
        out = ""
        for j, ch in enumerate(line):
            out += (RAINBOW[(i * 6 + j) % 6] + ch + R) if ch != ' ' else ch
        sys.stdout.write(goto(ar + i, ac) + out)

    ir = ar + len(art) + 2
    msgs = [
        col("矢印キー / WASD で移動   Q で終了", "white"),
        col("ENTER または SPACE でスタート!", "cyan"),
    ]
    if high:
        msgs.insert(0, f"  Best: {col(str(high).zfill(4), 'yellow')}")
    for i, m in enumerate(msgs):
        sys.stdout.write(goto(ir + i, max(1, (tw - 34) // 2)) + m)
    sys.stdout.flush()

    while True:
        if key_ready():
            k = get_key()
            if k in ('\r', '\n', ' '):
                return True
            if k in ('Q', '\x03', '\x1b'):
                return False
        time.sleep(0.05)

# ── メイン ────────────────────────────────────────────────────────────────────
def main():
    enable_ansi()
    _old = None
    if sys.platform != "win32":
        import tty, termios
        fd   = sys.stdin.fileno()
        _old = termios.tcgetattr(fd)
        tty.setraw(fd)
    try:
        while True:
            if not title():
                break
            score, high, died = play()
            if died:
                game_over(score, high)
                while True:
                    if key_ready():
                        k = get_key()
                        if k and k.upper() == 'R':
                            break
                        if k in ('Q', '\x03', '\x1b'):
                            raise SystemExit
                    time.sleep(0.05)
    except (SystemExit, KeyboardInterrupt):
        pass
    finally:
        if _old is not None:
            import termios
            try: termios.tcsetattr(fd, termios.TCSADRAIN, _old)
            except Exception: pass
        show_cur()
        clear()
        print(RAINBOW[3] + "  またね！ See you next time! 🐍" + R)
        print()

if __name__ == "__main__":
    main()
