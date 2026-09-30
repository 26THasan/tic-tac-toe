import re
from datetime import datetime


def display_board(board):
    print("\n")
    for i in range(3):
        row_display = [cell if cell != "" else " " for cell in board[i]]
        print(f" {row_display[0]} | {row_display[1]} | {row_display[2]} ")
        if i < 2:
            print("---|---|---")
    print("\n")


def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    return None


def check_draw(board):
    for row in board:
        if "" in row:
            return False
    return True


def log_move(move_str):
    with open("history.txt", "a") as f:
        f.write(move_str + "\n")


def ensure_history_file():
    """Write the title line only if the history file is new or empty."""
    try:
        with open("history.txt", "r") as f:
            has_content = f.read().strip() != ""
    except FileNotFoundError:
        has_content = False

    if not has_content:
        with open("history.txt", "a") as f:
            f.write("=== Tic-Tac-Toe Game History ===\n")


def score_line(scores, mode):
    """Build a one-line summary of the current scores."""
    if mode == "1":
        x_name, o_name = "You (X)", "Computer (O)"
    else:
        x_name, o_name = "Player X", "Player O"
    return f"{x_name}: {scores['X']} | {o_name}: {scores['O']} | Draws: {scores['Draws']}"


def display_scores(scores, mode):
    print("\n=== SCOREBOARD ===")
    print(score_line(scores, mode))
    print("==================\n")


def minimax(board, is_maximizing, ai, human, depth):
    """Score a position: positive is good for the AI, negative is good for the human."""
    winner = check_winner(board)
    if winner == ai:
        return 10 - depth
    if winner == human:
        return depth - 10
    if check_draw(board):
        return 0

    if is_maximizing:
        best_score = -100
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = ai
                    score = minimax(board, False, ai, human, depth + 1)
                    board[r][c] = ""
                    best_score = max(best_score, score)
        return best_score
    else:
        best_score = 100
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = human
                    score = minimax(board, True, ai, human, depth + 1)
                    board[r][c] = ""
                    best_score = min(best_score, score)
        return best_score


def best_move(board, ai, human):
    """Try every empty square and return the (row, col) with the best minimax score."""
    best_score = -100
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = ai
                score = minimax(board, False, ai, human, 1)
                board[r][c] = ""
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move


# ---------- Replay mode ----------

def load_matches():
    """Read history.txt and return a list of matches.
    Each match is a dict: {"header": str, "moves": [(player, row, col), ...], "result": str}
    """
    matches = []
    current = None

    try:
        with open("history.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return matches

    move_pattern = re.compile(r"Player (\w) placed at row (\d), col (\d)")

    for line in lines:
        line = line.strip()

        if line.startswith("--- New Match Started"):
            current = {
                "header": line.strip("- ").strip(),
                "moves": [],
                "result": "No result recorded",
            }
            matches.append(current)
        elif current is not None:
            match = move_pattern.match(line)
            if match:
                player, row, col = match.groups()
                current["moves"].append((player, int(row), int(col)))
            elif line.startswith("Result:"):
                current["result"] = line[len("Result:"):].strip()

    return matches


def replay_match(match):
    board = [["", "", ""], ["", "", ""], ["", "", ""]]
    total = len(match["moves"])

    print(f"\n=== Replaying: {match['header']} ===")
    display_board(board)

    for number, (player, row, col) in enumerate(match["moves"], 1):
        choice = input(f"Press Enter for move {number}/{total} (or type Q to stop): ").strip().lower()
        if choice == "q":
            print("Replay stopped.")
            return

        board[row][col] = player
        print(f"Move {number}: Player {player} placed at row {row}, col {col}")
        display_board(board)

    print(f"Result: {match['result']}")
    print("End of replay.\n")


def replay_mode():
    matches = load_matches()

    if not matches:
        print("\nNo saved matches found yet. Play a game first!\n")
        return

    while True:
        print("\n=== Past Matches (most recent 10) ===")
        start = max(0, len(matches) - 10)
        for i in range(start, len(matches)):
            m = matches[i]
            print(f"{i + 1}. {m['header']} - {len(m['moves'])} moves - {m['result']}")

        choice = input("\nEnter a match number to replay (or B to go back): ").strip().lower()
        if choice == "b":
            return

        try:
            index = int(choice) - 1
        except ValueError:
            print("Please enter a match number or B.")
            continue

        if not (0 <= index < len(matches)):
            print("That match number doesn't exist.")
            continue

        replay_match(matches[index])



def play_tic_tac_toe():
    playing_rounds = True
    scores = {"X": 0, "O": 0, "Draws": 0}

    mode = ""
    while mode not in ["1", "2"]:
        mode = input("Choose mode - 1: Play vs Computer, 2: Two players: ").strip()

    while playing_rounds:
        board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]

        current_player = "X"
        game_over = False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode_name = "vs Computer" if mode == "1" else "Two players"
        log_move(f"\n--- New Match Started ({mode_name}): {timestamp} ---")
        display_board(board)

        while not game_over:
            print(f"Player {current_player}'s turn.")

            if mode == "1" and current_player == "O":
                print("Computer is thinking...")
                row, col = best_move(board, "O", "X")
            else:
                try:
                    row = int(input("Enter row index (0, 1, or 2): "))
                    col = int(input("Enter column index (0, 1, or 2): "))
                except ValueError:
                    print("Please enter whole numbers (0, 1, or 2) only.")
                    continue

                if not (0 <= row <= 2 and 0 <= col <= 2):
                    print("Invalid index! Choice must be between 0 and 2. Try again.")
                    continue

                if board[row][col] != "":
                    print("That position is already taken! Try a different one.")
                    continue

            board[row][col] = current_player

            log_move(f"Player {current_player} placed at row {row}, col {col}")
            display_board(board)

            winner = check_winner(board)
            if winner:
                print(f"Player {winner} wins this round!")
                log_move(f"Result: Player {winner} won this round.")
                scores[winner] += 1
                game_over = True
            elif check_draw(board):
                print("It's a draw! The board is full.")
                log_move("Result: Draw match.")
                scores["Draws"] += 1
                game_over = True
            else:
                current_player = "O" if current_player == "X" else "X"

        display_scores(scores, mode)
        log_move(f"Score after this round - {score_line(scores, mode)}")

        rematch = input("Would you like to play another round? (Y/N): ").strip().lower()
        if rematch not in ['y', 'yes']:
            playing_rounds = False
            print("\nFinal scores:")
            print(score_line(scores, mode))
            log_move(f"Final score - {score_line(scores, mode)}")
        else:
            print("\nStarting a fresh match...")


def main():
    ensure_history_file()
    print("=== Welcome to Tic-Tac-Toe! ===")

    while True:
        print("\n--- Main Menu ---")
        print("1. Play a game")
        print("2. Replay a past match")
        print("3. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            play_tic_tac_toe()
        elif choice == "2":
            replay_mode()
        elif choice == "3":
            print("\nThanks for playing! Goodbye.")
            break
        else:
            print("Please enter 1, 2, or 3.")


main()
