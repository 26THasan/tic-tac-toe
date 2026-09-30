import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

HISTORY_FILE = "history.txt"
CELL_BG = "#f4f1ea"
WIN_BG = "#b7e4c7"
COLORS = {"X": "#1d6fb8", "O": "#c8372d"}
HINT_FG = "#b5b0a3"  # colour of the 1-9 hints in Numbers style

LINES = (
    [[(r, 0), (r, 1), (r, 2)] for r in range(3)]
    + [[(0, c), (1, c), (2, c)] for c in range(3)]
    + [[(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
)


# ---------- Game logic ----------

def winning_line(board):
    for a, b, c in LINES:
        v = board[a[0]][a[1]]
        if v != "" and v == board[b[0]][b[1]] == board[c[0]][c[1]]:
            return [a, b, c]
    return None


def check_winner(board):
    line = winning_line(board)
    return board[line[0][0]][line[0][1]] if line else None


def check_draw(board):
    return all("" not in row for row in board)


def minimax(board, is_maximizing, ai, human, depth):
    winner = check_winner(board)
    if winner == ai:
        return 10 - depth
    if winner == human:
        return depth - 10
    if check_draw(board):
        return 0

    player = ai if is_maximizing else human
    scores = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = player
                scores.append(minimax(board, not is_maximizing, ai, human, depth + 1))
                board[r][c] = ""
    return max(scores) if is_maximizing else min(scores)


def best_move(board, ai, human):
    best_score, move = -100, None
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = ai
                score = minimax(board, False, ai, human, 1)
                board[r][c] = ""
                if score > best_score:
                    best_score, move = score, (r, c)
    return move


# ---------- History file ----------

def log_move(text):
    with open(HISTORY_FILE, "a") as f:
        f.write(text + "\n")


def ensure_history_file():
    try:
        with open(HISTORY_FILE, "r") as f:
            has_content = f.read().strip() != ""
    except FileNotFoundError:
        has_content = False
    if not has_content:
        with open(HISTORY_FILE, "a") as f:
            f.write("=== Tic-Tac-Toe Game History ===\n")


def load_matches():
    """Parse history.txt into a list of match dicts (same format the console game writes)."""
    try:
        with open(HISTORY_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    header_re = re.compile(r"--- New Match Started(?: \((.+?)\))?: (.+?) ---")
    move_re = re.compile(r"Player (\w) placed at row (\d), col (\d)")
    matches, current = [], None

    for line in lines:
        line = line.strip()
        h = header_re.match(line)
        if h:
            mode, stamp = h.groups()
            current = {"timestamp": stamp, "mode": mode or "Two players",
                       "moves": [], "result": "No result recorded", "outcome": None}
            matches.append(current)
        elif current is not None:
            m = move_re.match(line)
            if m:
                current["moves"].append((m.group(1), int(m.group(2)), int(m.group(3))))
            elif line.startswith("Result:"):
                current["result"] = line[len("Result:"):].strip()
                if "Draw" in line:
                    current["outcome"] = "Draw"
                elif "Player X won" in line:
                    current["outcome"] = "X"
                elif "Player O won" in line:
                    current["outcome"] = "O"
    return matches


def build_stats_text(matches):
    if not matches:
        return "No saved matches yet. Play a game first!"

    done = [m for m in matches if m["outcome"] is not None]
    total = len(done)
    pct = lambda n, t: f"{n / t * 100:.0f}%" if t else "0%"
    count = lambda ms, o: sum(1 for m in ms if m["outcome"] == o)

    out = [f"Matches recorded: {len(matches)}",
           f"Completed: {total}   Unfinished: {len(matches) - total}"]
    if total == 0:
        return "\n".join(out)

    out += ["", "Overall",
            f"  X wins: {count(done, 'X')} ({pct(count(done, 'X'), total)})",
            f"  O wins: {count(done, 'O')} ({pct(count(done, 'O'), total)})",
            f"  Draws:  {count(done, 'Draw')} ({pct(count(done, 'Draw'), total)})"]

    for mode, x_name, o_name in (("vs Computer", "You", "Computer"),
                                 ("Two players", "Player X", "Player O")):
        sub = [m for m in done if m["mode"] == mode]
        if sub:
            n = len(sub)
            out += ["", f"{mode} ({n} games)",
                    f"  {x_name} won: {count(sub, 'X')} ({pct(count(sub, 'X'), n)})",
                    f"  {o_name} won: {count(sub, 'O')} ({pct(count(sub, 'O'), n)})",
                    f"  Draws: {count(sub, 'Draw')} ({pct(count(sub, 'Draw'), n)})"]

    lengths = [len(m["moves"]) for m in done]
    out += ["", "Game length",
            f"  Average: {sum(lengths) / len(lengths):.1f} moves",
            f"  Shortest: {min(lengths)}   Longest: {max(lengths)}",
            "", "Most recent match",
            f"  {matches[-1]['timestamp']} ({matches[-1]['mode']})",
            f"  {matches[-1]['result']}"]
    return "\n".join(out)


# ---------- GUI helpers ----------

def build_grid(parent, font_size, width, height, on_click=None):
    cells = []
    for r in range(3):
        row = []
        for c in range(3):
            lbl = tk.Label(parent, text="", font=("Helvetica", font_size, "bold"),
                           width=width, height=height, bg=CELL_BG, relief="raised", bd=3)
            lbl.grid(row=r, column=c, padx=3, pady=3)
            if on_click:
                lbl.config(cursor="hand2")
                lbl.bind("<Button-1>", lambda e, r=r, c=c: on_click(r, c))
            row.append(lbl)
        cells.append(row)
    return cells


def set_cell(lbl, player):
    lbl.config(text=player, fg=COLORS.get(player, "black"), bg=CELL_BG)


# ---------- Main app ----------

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("Tic-Tac-Toe")
        root.resizable(False, False)
        root.bind("<Key>", self.on_key)

        self.mode = tk.StringVar(value="vs Computer")
        self.style = tk.StringVar(value="Classic")
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.board = [[""] * 3 for _ in range(3)]
        self.current = "X"
        self.game_over = False
        self.busy = False
        self.header_logged = False

        self.score_label = tk.Label(root, font=("Helvetica", 12))
        self.score_label.pack(pady=(12, 4))
        self.status = tk.Label(root, font=("Helvetica", 14, "bold"))
        self.status.pack(pady=4)

        frame = tk.Frame(root)
        frame.pack(padx=16, pady=8)
        self.cells = build_grid(frame, 32, 3, 1, on_click=self.on_click)

        controls = tk.Frame(root)
        controls.pack(pady=(4, 14))
        tk.OptionMenu(controls, self.mode, "vs Computer", "Two players",
                      command=lambda _: self.change_mode()).grid(row=0, column=0, padx=4)
        tk.OptionMenu(controls, self.style, "Classic", "Numbers",
                      command=lambda _: self.refresh_empty_cells()).grid(row=0, column=1, padx=4)
        tk.Button(controls, text="New Game", command=self.new_game).grid(row=0, column=2, padx=4)
        tk.Button(controls, text="Replay", command=self.open_replay).grid(row=0, column=3, padx=4)
        tk.Button(controls, text="Stats", command=self.open_stats).grid(row=0, column=4, padx=4)

        self.new_game()

    # --- names / scores ---
    def names(self):
        if self.mode.get() == "vs Computer":
            return "You (X)", "Computer (O)"
        return "Player X", "Player O"

    def score_text(self):
        x, o = self.names()
        return f"{x}: {self.scores['X']} | {o}: {self.scores['O']} | Draws: {self.scores['Draws']}"

    def refresh_scores(self):
        self.score_label.config(text=self.score_text())

    def change_mode(self):
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.new_game()

    # --- game flow ---
    def new_game(self):
        self.board = [[""] * 3 for _ in range(3)]
        self.current = "X"
        self.game_over = False
        self.busy = False
        self.header_logged = False
        for row in self.cells:
            for lbl in row:
                lbl.config(bg=CELL_BG)
        self.refresh_empty_cells()
        self.refresh_scores()
        self.status.config(text="X's turn")

    def refresh_empty_cells(self):
        """Show 1-9 hints in empty squares (Numbers style) or leave them blank (Classic)."""
        numbers = self.style.get() == "Numbers"
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.cells[r][c].config(text=str(r * 3 + c + 1) if numbers else "",
                                            fg=HINT_FG)

    def on_key(self, event):
        # Number keys only work in Numbers style; on_click already ignores
        # taken squares, finished games and the computer's turn.
        if self.style.get() == "Numbers" and event.char in tuple("123456789"):
            r, c = divmod(int(event.char) - 1, 3)
            self.on_click(r, c)

    def on_click(self, r, c):
        if self.game_over or self.busy or self.board[r][c] != "":
            return
        if self.mode.get() == "vs Computer" and self.current == "O":
            return
        self.place(r, c)

    def place(self, r, c):
        if not self.header_logged:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_move(f"\n--- New Match Started ({self.mode.get()}): {stamp} ---")
            self.header_logged = True

        self.board[r][c] = self.current
        set_cell(self.cells[r][c], self.current)
        log_move(f"Player {self.current} placed at row {r}, col {c}")

        line = winning_line(self.board)
        if line:
            for lr, lc in line:
                self.cells[lr][lc].config(bg=WIN_BG)
            self.finish(self.current)
        elif check_draw(self.board):
            self.finish(None)
        else:
            self.current = "O" if self.current == "X" else "X"
            self.status.config(text=f"{self.current}'s turn")
            if self.mode.get() == "vs Computer" and self.current == "O":
                self.busy = True
                self.status.config(text="Computer is thinking...")
                self.root.after(400, self.computer_move)

    def computer_move(self):
        if self.game_over:
            return
        self.busy = False
        r, c = best_move(self.board, "O", "X")
        self.place(r, c)

    def finish(self, winner):
        self.game_over = True
        if winner:
            self.scores[winner] += 1
            x, o = self.names()
            who = x if winner == "X" else o
            self.status.config(text=f"{who} wins!")
            log_move(f"Result: Player {winner} won this round.")
        else:
            self.scores["Draws"] += 1
            self.status.config(text="It's a draw!")
            log_move("Result: Draw match.")
        log_move(f"Score after this round - {self.score_text()}")
        self.refresh_scores()

    # --- stats window ---
    def open_stats(self):
        win = tk.Toplevel(self.root)
        win.title("Stats")
        tk.Label(win, text=build_stats_text(load_matches()), justify="left",
                 font=("Courier", 11)).pack(padx=20, pady=16)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 14))

    # --- replay window ---
    def open_replay(self):
        matches = load_matches()
        if not matches:
            messagebox.showinfo("Replay", "No saved matches yet. Play a game first!")
            return

        win = tk.Toplevel(self.root)
        win.title("Replay")
        win.resizable(False, False)

        listbox = tk.Listbox(win, width=58, height=8, exportselection=False)
        for i, m in enumerate(matches, 1):
            listbox.insert(tk.END, f"{i}. {m['timestamp']} ({m['mode']}) - {m['result']}")
        listbox.see(tk.END)
        listbox.pack(padx=12, pady=(12, 6))

        info = tk.Label(win, text="Select a match above", font=("Helvetica", 11))
        info.pack(pady=4)

        frame = tk.Frame(win)
        frame.pack(pady=4)
        cells = build_grid(frame, 22, 3, 1)

        state = {"match": None, "step": 0}

        def render():
            for row in cells:
                for lbl in row:
                    lbl.config(text="", bg=CELL_BG)
            m = state["match"]
            if not m:
                return
            for player, r, c in m["moves"][:state["step"]]:
                set_cell(cells[r][c], player)
            total = len(m["moves"])
            text = f"Move {state['step']}/{total}"
            if state["step"] == total:
                text += f"  -  {m['result']}"
            info.config(text=text)

        def on_select(_event=None):
            sel = listbox.curselection()
            if sel:
                state["match"] = matches[sel[0]]
                state["step"] = 0
                render()

        def step(delta):
            m = state["match"]
            if m:
                state["step"] = max(0, min(len(m["moves"]), state["step"] + delta))
                render()

        listbox.bind("<<ListboxSelect>>", on_select)

        buttons = tk.Frame(win)
        buttons.pack(pady=(4, 12))
        tk.Button(buttons, text="< Prev", command=lambda: step(-1)).grid(row=0, column=0, padx=4)
        tk.Button(buttons, text="Next >", command=lambda: step(1)).grid(row=0, column=1, padx=4)
        tk.Button(buttons, text="Close", command=win.destroy).grid(row=0, column=2, padx=4)


def main():
    ensure_history_file()
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
