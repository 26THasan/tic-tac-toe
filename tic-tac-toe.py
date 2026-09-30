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


def play_tic_tac_toe():
    playing_rounds = True

    try:
        with open("history.txt", "r") as f:
            has_content = f.read().strip() != ""
    except FileNotFoundError:
        has_content = False

    if not has_content:
        with open("history.txt", "a") as f:
            f.write("=== Tic-Tac-Toe Game History ===\n")

    print("=== Welcome to Tic-Tac-Toe! ===")
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
                game_over = True
            elif check_draw(board):
                print("It's a draw! The board is full.")
                log_move("Result: Draw match.")
                game_over = True
            else:
                current_player = "O" if current_player == "X" else "X"

        rematch = input("Would you like to play another round? (Y/N): ").strip().lower()
        if rematch not in ['y', 'yes']:
            playing_rounds = False
            print("\nThanks for playing! Goodbye.")
        else:
            print("\nStarting a fresh match...")


play_tic_tac_toe()
