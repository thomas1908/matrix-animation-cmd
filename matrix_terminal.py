#!/usr/bin/env python3
import os, sys, random, time, shutil, signal

# caractères utilisés
CHARS = ['ｦ', 'ｱ', 'ｳ', 'ｴ', 'ｵ', 'ｶ', 'ｷ', 'ｹ', 'ｺ', 'ｻ', 'ｼ', 'ｽ', 'ｾ', 'ｿ', 'ﾀ', 'ﾂ', 'ﾃ', 'ﾅ', 'ﾆ', 'ﾇ', 'ﾈ', 'ﾊ', 'ﾋ', 'ﾎ', 'ﾏ', 'ﾐ', 'ﾑ', 'ﾒ', 'ﾓ', 'ﾔ', 'ﾕ', 'ﾗ', 'ﾘ', 'ﾜ', '9', '8', '7', '5', '2', '1', ':', '.', '"', '=', '*', '+', '-', '¦', '|', '_', '╌', '日']

def color_step(i, total):
    g = int(80 + (175 * i / total))
    return f"\033[38;2;0;{g};0m"

def set_terminal_bg(r, g, b):
    sys.stdout.write(f"\033]11;rgb:{r:02x}/{g:02x}/{b:02x}\007")  # séquence OSC 11
    sys.stdout.flush()

def reset_terminal_bg():
    """Restaure la couleur de fond par défaut."""
    sys.stdout.write("\033]111;\007")
    sys.stdout.flush()

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def get_size():
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

class Matrix:
    def __init__(self):
        self.cols, self.rows = get_size()
        self.fade = 20
        self.trails = [[0]*self.rows for _ in range(self.cols)]
        self.drops = [random.randint(0, self.rows) for _ in range(self.cols)]
        self.speeds = [random.uniform(0.02, 0.08) for _ in range(self.cols)]
        self.last_update = [time.time()] * self.cols
        self.resize_pending = False
        clear_screen()

    def resize(self, *_):
        self.resize_pending = True

    def apply_resize(self):
        self.cols, self.rows = get_size()
        self.trails = [[0]*self.rows for _ in range(self.cols)]
        self.drops = [random.randint(0, self.rows) for _ in range(self.cols)]
        self.speeds = [random.uniform(0.02, 0.08) for _ in range(self.cols)]
        self.last_update = [time.time()] * self.cols
        clear_screen()

    def step(self):
        if self.resize_pending:
            self.resize_pending = False
            self.apply_resize()

        cols, rows = self.cols, self.rows
        now = time.time()

        for x in range(cols):
            if now - self.last_update[x] > self.speeds[x]:
                self.last_update[x] = now
                head_y = self.drops[x]
                if 0 <= head_y < rows:
                    self.trails[x][head_y] = self.fade
                    if head_y > 0:
                        self.trails[x][head_y - 1] = max(self.trails[x][head_y - 1], self.fade - 1)
                    if head_y > 1:
                        self.trails[x][head_y - 2] = max(self.trails[x][head_y - 2], self.fade - 2)
                self.drops[x] = (self.drops[x] + 1) % rows

            trail = self.trails[x]
            for y in range(rows):
                val = trail[y]
                if val > 0:
                    color = "\033[1;37m" if val >= self.fade - 1 else color_step(val, self.fade)
                    char = random.choice(CHARS)
                    sys.stdout.write(f"\033[{y+1};{x+1}H{color}{char}")
                    trail[y] = val - 1
                elif val == 0:
                    # ne laisse pas de trainé
                    sys.stdout.write(f"\033[{y+1};{x+1}H ")
        sys.stdout.flush()

def main():
    set_terminal_bg(0, 15, 0)
    sys.stdout.write("\033[?25l") # pour faire disparaitre le curseur
    sys.stdout.flush()

    matrix = Matrix()
    signal.signal(signal.SIGWINCH, matrix.resize)

    try:
        while True:
            matrix.step()
            time.sleep(0.025)
    except KeyboardInterrupt:
        reset_terminal_bg()
        sys.stdout.write("\033[0m\033[?25h\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
