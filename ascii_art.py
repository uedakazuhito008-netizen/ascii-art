#!/usr/bin/env python3
"""
ASCII Art Generator — インタラクティブなターミナルおもちゃ
依存: pyfiglet (初回実行時に自動インストール)
"""
import sys
import os
import time
import random
import shutil

# ── Windows ANSI 有効化 ───────────────────────────────────────────────────────
def enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

# ── カラー ────────────────────────────────────────────────────────────────────
R    = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

NAMED = {
    "red":     "\033[91m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "blue":    "\033[94m",
    "magenta": "\033[95m",
    "cyan":    "\033[96m",
    "white":   "\033[97m",
}

RAINBOW = [
    rgb(255, 80,  80),
    rgb(255, 180, 0),
    rgb(255, 255, 60),
    rgb(60,  255, 60),
    rgb(60,  160, 255),
    rgb(200, 60,  255),
]

def c(text, name):
    return NAMED.get(name, "") + text + R

def rainbow(text, offset=0):
    out = ""
    i = offset
    for ch in text:
        if ch not in " \t\n":
            out += RAINBOW[i % len(RAINBOW)] + ch + R
            i += 1
        else:
            out += ch
    return out

# ── pyfiglet 自動インストール ─────────────────────────────────────────────────
def get_figlet():
    try:
        import pyfiglet
        return pyfiglet
    except ImportError:
        print(c("  pyfiglet をインストール中...", "yellow"), flush=True)
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyfiglet", "-q"],
            stdout=subprocess.DEVNULL,
        )
        import pyfiglet
        return pyfiglet

# ── ユーティリティ ────────────────────────────────────────────────────────────
def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def goto(row, col):
    return f"\033[{row};{col}H"

def term_size():
    s = shutil.get_terminal_size((80, 24))
    return s.columns, s.lines

# ── メニューヘッダー ──────────────────────────────────────────────────────────
HEADER_LINES = [
    r"   _   ___  ___ ___ ___   _   ___ _____",
    r"  /_\ / __|/ __|_ _|_ _| /_\ | _ \_   _|",
    r" / _ \\__ \ (__ | | | | / _ \|   / | |  ",
    r"/_/ \_\___/\___|___|___/_/ \_\_|_\ |_|  ",
]

def print_header():
    clear()
    for i, line in enumerate(HEADER_LINES):
        print(rainbow(line, offset=i * 4))
    print()
    cols, _ = term_size()
    print(c("  " + "─" * min(cols - 4, 50), "cyan"))
    print()

# ── モード 1: テキスト → ASCII アート ────────────────────────────────────────
FONTS = [
    ("big",        "クラシック大文字"),
    ("banner3",    "ボールドバナー"),
    ("slant",      "スラント斜体"),
    ("doom",       "Doom スタイル"),
    ("isometric1", "3D 等角投影"),
    ("block",      "ブロック体"),
]

def ascii_art_mode():
    pyfiglet = get_figlet()
    print_header()
    print(c("  ▶ テキスト → ASCII アート\n", "cyan"))

    text = input(c("  テキストを入力 ▶ ", "yellow")).strip()
    if not text:
        return

    print()
    print(c("  フォント:", "cyan"))
    for i, (font, name) in enumerate(FONTS, 1):
        print(f"    {c(str(i), 'yellow')}. {name:<16} {c(f'({font})', 'white')}")
    print(f"    {c('7', 'yellow')}. ランダム")

    print()
    choice = input(c("  番号を選択 [1-7] ▶ ", "yellow")).strip()
    if choice == "7":
        font, fname = random.choice(FONTS)
        print(c(f"  → {fname} ({font})", "green"))
    elif choice.isdigit() and 1 <= int(choice) <= 6:
        font, _ = FONTS[int(choice) - 1]
    else:
        font = "big"

    print()
    print(c("  カラー:", "cyan"))
    color_opts = [
        ("1", "レインボー 🌈",  "rainbow"),
        ("2", "シアン",         "cyan"),
        ("3", "グリーン",       "green"),
        ("4", "イエロー",       "yellow"),
        ("5", "マゼンタ",       "magenta"),
        ("6", "ホワイト",       "white"),
    ]
    for num, name, _ in color_opts:
        print(f"    {c(num, 'yellow')}. {name}")

    print()
    col_choice = input(c("  番号を選択 [1-6] ▶ ", "yellow")).strip()

    try:
        art = pyfiglet.figlet_format(text, font=font)
    except Exception:
        art = pyfiglet.figlet_format(text, font="big")

    print()
    cols, _ = term_size()
    print(c("  " + "─" * min(cols - 4, 60), "cyan"))
    print()

    for i, line in enumerate(art.split("\n")):
        if col_choice == "1":
            print(rainbow(line, offset=i * 3))
        elif col_choice == "2":
            print(c(line, "cyan"))
        elif col_choice == "3":
            print(c(line, "green"))
        elif col_choice == "4":
            print(c(line, "yellow"))
        elif col_choice == "5":
            print(c(line, "magenta"))
        else:
            print(c(line, "white"))
        time.sleep(0.025)

    print(c("  " + "─" * min(cols - 4, 60), "cyan"))
    print()
    input(c("  [Enter] でメニューへ戻る", "cyan"))

# ── モード 2: マトリックス雨 ──────────────────────────────────────────────────
MATRIX_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789@#$%&*ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ"
)

def matrix_rain():
    clear()
    cols, rows = term_size()
    rows -= 1

    drops = []
    for col in range(1, cols + 1):
        if random.random() < 0.75:
            drops.append({
                "col":    col,
                "pos":    random.uniform(-rows, 0),
                "speed":  random.uniform(0.4, 2.2),
                "length": random.randint(6, 22),
                "trail":  [random.choice(MATRIX_CHARS) for _ in range(60)],
            })

    print("\033[?25l", end="")  # カーソル非表示
    sys.stdout.write(goto(rows + 1, 1) + c("  Ctrl+C でメニューへ戻る", "green") + " " * 10)

    try:
        frame = 0
        while True:
            buf = []
            for drop in drops:
                col    = drop["col"]
                head   = int(drop["pos"])
                length = drop["length"]
                trail  = drop["trail"]

                # 先頭 (白く光る)
                if 1 <= head <= rows:
                    ch = random.choice(MATRIX_CHARS)
                    buf.append(goto(head, col) + "\033[97m" + ch + R)

                # トレイル
                for i in range(1, length + 1):
                    r = head - i
                    if 1 <= r <= rows:
                        ch = trail[(frame + i) % len(trail)]
                        if i == 1:
                            color = "\033[92m"       # 明るい緑
                        elif i < length // 2:
                            color = "\033[32m"       # 緑
                        else:
                            color = DIM + "\033[32m" # 暗い緑
                        buf.append(goto(r, col) + color + ch + R)

                # 末尾を消す
                erase = head - length - 1
                if 1 <= erase <= rows:
                    buf.append(goto(erase, col) + " ")

                # 位置更新
                drop["pos"] += drop["speed"]
                if drop["pos"] - length > rows:
                    drop["pos"]    = random.uniform(-rows // 2, 0)
                    drop["speed"]  = random.uniform(0.4, 2.2)
                    drop["length"] = random.randint(6, 22)

            sys.stdout.write("".join(buf))
            sys.stdout.flush()
            time.sleep(0.05)
            frame += 1

    except KeyboardInterrupt:
        pass
    finally:
        print("\033[?25h", end="")
        clear()

# ── モード 3: レインボーバナー (アニメーション) ───────────────────────────────
def rainbow_banner():
    pyfiglet = get_figlet()
    print_header()
    print(c("  ▶ レインボーバナー\n", "cyan"))

    text = input(c("  テキストを入力 ▶ ", "yellow")).strip()
    if not text:
        text = "HELLO"

    font = "big"
    try:
        art = pyfiglet.figlet_format(text, font=font)
    except Exception:
        art = pyfiglet.figlet_format(text)

    lines = [l for l in art.split("\n") if l.strip()]
    cols, rows = term_size()
    art_h = len(lines)
    start_row = max(3, (rows - art_h) // 2)

    print("\033[?25l", end="")
    clear()

    try:
        cycle = 0
        while True:
            buf = [goto(1, 1) + c("  ✨ Ctrl+C で停止", "cyan") + " " * 20]
            for i, line in enumerate(lines):
                buf.append(goto(start_row + i, 1))
                padding = max(0, (cols - len(line)) // 2)
                out = " " * padding
                for j, ch in enumerate(line):
                    if ch not in " \t":
                        idx = (i * 4 + j + cycle * 2) % len(RAINBOW)
                        out += RAINBOW[idx] + ch + R
                    else:
                        out += ch
                buf.append(out)

            sys.stdout.write("".join(buf))
            sys.stdout.flush()
            time.sleep(0.06)
            cycle += 1

    except KeyboardInterrupt:
        pass
    finally:
        print("\033[?25h", end="")
        clear()

# ── メイン ────────────────────────────────────────────────────────────────────
def main():
    enable_ansi()
    while True:
        print_header()
        print(f"    {c('1', 'yellow')}. テキスト → ASCII アート")
        print(f"    {c('2', 'yellow')}. マトリックス雨 🌧")
        print(f"    {c('3', 'yellow')}. レインボーバナー ✨")
        print(f"    {c('4', 'yellow')}. 終了")
        print()
        cols, _ = term_size()
        print(c("  " + "─" * min(cols - 4, 50), "cyan"))

        choice = input(c("  選択 [1-4] ▶ ", "cyan")).strip()

        if choice == "1":
            ascii_art_mode()
        elif choice == "2":
            matrix_rain()
        elif choice == "3":
            rainbow_banner()
        elif choice == "4":
            clear()
            print(rainbow("  またね！ See you next time! ✨"))
            print()
            break

if __name__ == "__main__":
    main()
