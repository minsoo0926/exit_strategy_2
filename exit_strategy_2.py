import numpy as np
import tkinter as tk
from tkinter import messagebox

class Piece:
    def __init__(self, player, number, x, y):
        self.player = player
        self.number = number
        self.x = x
        self.y = y

class BoardGame:
    def __init__(self):
        self.board = np.zeros((7, 7), dtype=int)  # 7x7 board
        self.green_zone = (3, 3)  # Green center zone
        self.forbidden_rows = [3]  # Forbidden rows for placement
        self.forbidden_cols = [3]  # Forbidden columns for placement
        self.obstacles = [(3, 0), (3, 6)]  # Obstacles positions
        self.player_pieces = {1: [], 2: []}  # Player pieces will be placed later
        self.current_player = 1
        self.placement_phase = True
        self.piece_counter = {1: 0, 2: 0}  # Track number of pieces placed per player
        self.column_counts = {1: [0] * 7, 2: [0] * 7}  # Track pieces placed per column
        self.scores = {1: 0, 2: 0}  # Track scores for each player
        self.winner = None
        self.selected_piece = None
        self.history = []  # History for undo functionality
        self.init_board()

    def init_board(self):
        for x in range(7):
            for y in range(7):
                if not self.is_valid_placement(x, y):
                    self.board[x, y] = -1
        for ox, oy in self.obstacles:
            self.board[ox, oy] = -2  # Obstacles marked as -2

    def is_valid_placement(self, x, y):
        if (x, y) in self.obstacles or (x == 3 or y == 3):
            return False  # Column and row 3 should remain unchanged
        if self.current_player == 1 and (y < 0 or y > 2):
            return False  # Player 1 can only use columns 0 to 2
        if self.current_player == 2 and (y < 4 or y > 6):
            return False  # Player 2 can only use columns 4 to 6
        if self.column_counts[self.current_player][y] >= 2:
            return False  # Limit of 2 pieces per column
        return self.board[x, y] == 0

    def place_piece(self, x, y):
        if self.is_valid_placement(x, y):
            piece_number = len(self.player_pieces[self.current_player]) + 1
            piece = Piece(self.current_player, piece_number, x, y)
            self.player_pieces[self.current_player].append(piece)
            self.board[x, y] = self.current_player
            self.piece_counter[self.current_player] += 1
            self.column_counts[self.current_player][y] += 1
            self.history.append((np.copy(self.board), self.current_player, self.scores.copy(), self.piece_counter.copy(), self.winner, [[Piece(p.player, p.number, p.x, p.y) for p in pieces] for pieces in self.player_pieces.values()]))

            if self.piece_counter[1] == 6 and self.piece_counter[2] == 6:
                self.placement_phase = False  # End placement phase
                self.reset_board_after_placement()  # Reset tiles after placement phase
                self.current_player = 1  # Set first turn to Player 1
            else:
                self.current_player = 3 - self.current_player  # Switch players
                self.reset_placement_tiles()

    def reset_board_after_placement(self):
        for x in range(7):
            for y in range(7):
                if (x, y) == self.green_zone or (x, y) in self.obstacles or (x == 3 or y == 3):
                    continue  # Keep special zones, obstacles, and row/column 3 unchanged
                if self.board[x, y] not in [1, 2]:
                    self.board[x, y] = 0  # Reset other tiles to 0

    def reset_placement_tiles(self):
        for x in range(7):
            for y in range(7):
                if (x, y) in self.obstacles or (x == 3 or y == 3):
                    continue  # Column and row 3 should remain unchanged
                if any(piece.x == x and piece.y == y for pieces in self.player_pieces.values() for piece in pieces):
                    continue  # Tiles with pieces should remain the same
                self.board[x, y] = 0 if self.board[x, y] == -1 else self.board[x, y]
                if self.is_valid_placement(x, y):
                    self.board[x, y] = 0
                else:
                    self.board[x, y] = -1

    def move_piece(self, start, direction):
        if self.winner:
            return "Game over!"

        x, y = start
        player = self.board[x, y]

        if player != self.current_player:
            return "Not your turn!"

        dx, dy = direction

        self.history.append((np.copy(self.board), self.current_player, self.scores.copy(), self.piece_counter.copy(), self.winner, [[Piece(p.player, p.number, p.x, p.y) for p in pieces] for pieces in self.player_pieces.values()]))

        while 0 <= x + dx < 7 and 0 <= y + dy < 7:
            nx, ny = x + dx, y + dy
            if self.board[nx, ny] in [-2, 1, 2]:  # Stop before obstacle or another piece
                break
            x, y = nx, ny

        self.board[start[0], start[1]] = -1 if start[0] == 3 or start[1] == 3 else 0
        if (x, y) == self.green_zone:
            self.scores[self.current_player] += 1
            self.check_winner()
            self.player_pieces[self.current_player] = [piece for piece in self.player_pieces[self.current_player] if not (piece.x == start[0] and piece.y == start[1])]
        else:
            self.board[x, y] = player
            for piece in self.player_pieces[self.current_player]:
                if piece.x == start[0] and piece.y == start[1]:
                    piece.x, piece.y = x, y

        self.current_player = 3 - self.current_player  # Switch players

    def check_winner(self):
        if self.scores[1] == 2:
            self.winner = 1
            messagebox.showinfo("Game Over", "Player 1 wins!")
        elif self.scores[2] == 2:
            self.winner = 2
            messagebox.showinfo("Game Over", "Player 2 wins!")

    def get_possible_moves(self, position):
        x, y = position
        directions = []
        potential_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in potential_directions:
            nx, ny = x, y
            while 0 <= nx + dx < 7 and 0 <= ny + dy < 7:
                nx, ny = nx + dx, ny + dy
                if self.board[nx, ny] in [-2, 1, 2]:  # Stop before obstacle or piece
                    break
                else:
                    directions.append(((dx, dy), (nx, ny)))
        return directions

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.board, self.current_player, self.scores, self.piece_counter, self.winner, restored_pieces = state
            self.player_pieces = {1: restored_pieces[0], 2: restored_pieces[1]}
            self.selected_piece = None  # Clear selected piece

class GameApp:
    def __init__(self, root):
        self.root = root
        self.game = BoardGame()
        self.canvas = tk.Canvas(root, width=350, height=350, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.score_label = [tk.Label(root, font=("Arial", 14)), tk.Label(root, font=("Arial", 14)), tk.Label(root, font=("Arial", 14))]
        self.score_label[0].grid(row=0, column=0)
        self.score_label[1].grid(row=0, column=1)
        self.score_label[2].grid(row=0, column=2)
        self.update_score_label()
        self.status_label = tk.Label(root, text="Player 1: Place your pieces", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, columnspan=3)
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=3, column=1)
        self.undo_button = tk.Button(root, text="Undo", command=self.undo, state=tk.DISABLED)
        self.undo_button.grid(row=3, column=2)  # Move to the bottom-right
        self.canvas.bind("<Button-1>", self.click_board)
        self.creator_label = tk.Label(root, text="제작자: 대학전쟁2 포항공대팀 하민수", font=("Arial", 10))
        self.creator_label.grid(row=4, column=0, columnspan=3)
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for x in range(7):
            for y in range(7):
                color = "white"
                if (x, y) == self.game.green_zone:
                    color = "green"
                elif self.game.board[x, y] == -1:
                    color = "gray"
                elif self.game.board[x, y] == -2:
                    color = "black"  # Obstacles are black
                elif self.game.board[x, y] == 1:
                    color = "blue"
                elif self.game.board[x, y] == 2:
                    color = "red"
                
                self.canvas.create_rectangle(
                    y * 50, x * 50, y * 50 + 50, x * 50 + 50, fill=color, outline="black"
                )

        for pieces in self.game.player_pieces.values():
            for piece in pieces:
                self.canvas.create_text(
                    piece.y * 50 + 25, piece.x * 50 + 25, text=str(piece.number), fill="white"
                )

        if self.game.selected_piece:
            x, y = self.game.selected_piece
            self.canvas.create_rectangle(
                y * 50 + 5, x * 50 + 5, y * 50 + 45, x * 50 + 45, outline="yellow", width=3
            )

    def draw_arrows(self, position, directions):
        x, y = position
        for (dx, dy), (nx, ny) in directions:
            self.canvas.create_line(
                y * 50 + 25, x * 50 + 25, ny * 50 + 25, nx * 50 + 25, fill="yellow", arrow=tk.LAST
            )

    def click_board(self, event):
        x, y = event.y // 50, event.x // 50

        if self.game.winner:
            messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            return

        if self.game.placement_phase:
            if self.game.is_valid_placement(x, y) and self.game.board[x, y] == 0:
                self.game.place_piece(x, y)
                self.update_score_label()
                self.status_label.config(text=f"Player {self.game.current_player}: Place your pieces")
                self.draw_board()
                if not self.game.placement_phase:
                    self.undo_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text=f"Player {self.game.current_player}: Invalid place")

        else:
            if self.game.selected_piece is None:
                if self.game.board[x, y] == self.game.current_player:
                    self.game.selected_piece = (x, y)
                    possible_directions = self.game.get_possible_moves((x, y))
                    self.draw_board()
                    self.draw_arrows((x, y), possible_directions)
            else:
                possible_directions = self.game.get_possible_moves(self.game.selected_piece)
                for (dx, dy), (end_x, end_y) in possible_directions:
                    if (x, y) == (end_x, end_y):
                        self.game.move_piece(self.game.selected_piece, (dx, dy))
                        self.game.selected_piece = None
                        self.update_score_label()
                        self.status_label.config(text=f"Player {self.game.current_player}'s turn")
                        self.draw_board()
                        return
                    
    def reset_game(self):
        self.game = BoardGame()
        self.status_label.config(text="Player 1: Place your pieces")
        self.update_score_label()
        self.undo_button.config(state=tk.DISABLED)
        self.draw_board()

    def update_score_label(self):
        self.score_label[0].config(text=f"Player 1: {self.game.scores[1]}", fg="blue")
        self.score_label[1].config(text=f" | ", fg="black")
        self.score_label[2].config(text=f"Player 2: {self.game.scores[2]}", fg="red")

    def undo(self):
        self.game.undo()
        self.update_score_label()
        self.status_label.config(text=f"Player {self.game.current_player}'s turn")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Exit Strategy 2")
    app = GameApp(root)
    root.mainloop()
