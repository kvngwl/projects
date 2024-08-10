import tkinter as tk
from tkinter import messagebox

class ChessPiece:
    def __init__(self, color, symbol, position):
        self.color = color
        self.symbol = symbol
        self.position = position
        self.has_moved = False

    def is_valid_move(self, board, end_pos):
        raise NotImplementedError("This method should be implemented by subclasses")

class Pawn(ChessPiece):
    def is_valid_move(self, board, end_pos):
        start_row, start_col = self.position
        end_row, end_col = end_pos
        
        direction = 1 if self.color == 'white' else -1
        
        # 전진
        if start_col == end_col and board.is_empty(end_pos):
            if end_row == start_row + direction:
                return True
            if not self.has_moved and end_row == start_row + 2 * direction and board.is_empty((start_row + direction, start_col)):
                return True
        
        # 공격
        if abs(start_col - end_col) == 1 and end_row == start_row + direction:
            if board.get_piece(end_pos) and board.get_piece(end_pos).color != self.color:
                return True
        
        return False

class Rook(ChessPiece):
    def is_valid_move(self, board, end_pos):
        return board.is_clear_path(self.position, end_pos, ['horizontal', 'vertical'])

class Knight(ChessPiece):
    def is_valid_move(self, board, end_pos):
        start_row, start_col = self.position
        end_row, end_col = end_pos
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class Bishop(ChessPiece):
    def is_valid_move(self, board, end_pos):
        return board.is_clear_path(self.position, end_pos, ['diagonal'])

class Queen(ChessPiece):
    def is_valid_move(self, board, end_pos):
        return board.is_clear_path(self.position, end_pos, ['horizontal', 'vertical', 'diagonal'])

class King(ChessPiece):
    def is_valid_move(self, board, end_pos):
        start_row, start_col = self.position
        end_row, end_col = end_pos
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)
        return max(row_diff, col_diff) == 1

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

    def setup_board(self):
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i in range(8):
            self.board[1][i] = Pawn('white', '♙', (1, i))
            self.board[6][i] = Pawn('black', '♟', (6, i))
            self.board[0][i] = piece_order[i]('white', '♖♘♗♕♔♗♘♖'[i], (0, i))
            self.board[7][i] = piece_order[i]('black', '♜♞♝♛♚♝♞♜'[i], (7, i))

    def get_piece(self, position):
        row, col = position
        return self.board[row][col]

    def set_piece(self, position, piece):
        row, col = position
        self.board[row][col] = piece
        if piece:
            piece.position = position

    def is_empty(self, position):
        return self.get_piece(position) is None

    def is_clear_path(self, start, end, allowed_directions):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = end_row - start_row
        col_diff = end_col - start_col

        if 'horizontal' in allowed_directions and row_diff == 0:
            step = 1 if col_diff > 0 else -1
            for col in range(start_col + step, end_col, step):
                if not self.is_empty((start_row, col)):
                    return False
            return True

        if 'vertical' in allowed_directions and col_diff == 0:
            step = 1 if row_diff > 0 else -1
            for row in range(start_row + step, end_row, step):
                if not self.is_empty((row, start_col)):
                    return False
            return True

        if 'diagonal' in allowed_directions and abs(row_diff) == abs(col_diff):
            row_step = 1 if row_diff > 0 else -1
            col_step = 1 if col_diff > 0 else -1
            for i in range(1, abs(row_diff)):
                if not self.is_empty((start_row + i*row_step, start_col + i*col_step)):
                    return False
            return True

        return False

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.board = ChessBoard()
        self.current_player = 'white'
        self.selected_piece = None
        self.create_board_gui()
        self.status_label = tk.Label(master, text="흰색 차례", font=('Helvetica', 16))
        self.status_label.grid(row=8, column=0, columnspan=8)

    def create_board_gui(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                button = tk.Button(self.master, width=5, height=2, bg=color, font=('Helvetica', 20), command=lambda r=row, c=col: self.on_square_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button
        self.update_board_gui()

    def update_board_gui(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                text = piece.symbol if piece else ""
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.buttons[row][col].config(text=text, bg=color)

    def on_square_click(self, row, col):
        if self.selected_piece is None:
            piece = self.board.get_piece((row, col))
            if piece and piece.color == self.current_player:
                self.selected_piece = (row, col)
                self.buttons[row][col].config(bg="yellow")
        else:
            start = self.selected_piece
            end = (row, col)
            if self.is_valid_move(start, end):
                self.make_move(start, end)
                if self.is_checkmate():
                    messagebox.showinfo("게임 종료", f"체크메이트! {self.current_player}의 승리!")
                    self.master.quit()
                elif self.is_check():
                    messagebox.showinfo("체크", "체크!")
                self.switch_player()
            self.selected_piece = None
            self.update_board_gui()

    def is_valid_move(self, start, end):
        piece = self.board.get_piece(start)
        if not piece or piece.color != self.current_player:
            return False
        
        if not piece.is_valid_move(self.board, end):
            return False
        
        end_piece = self.board.get_piece(end)
        if end_piece and end_piece.color == self.current_player:
            return False
        
        temp_board = ChessBoard()
        temp_board.board = [row[:] for row in self.board.board]
        temp_board.set_piece(end, temp_board.get_piece(start))
        temp_board.set_piece(start, None)
        if self.is_in_check(self.current_player, temp_board):
            return False
        
        return True

    def make_move(self, start, end):
        piece = self.board.get_piece(start)
        self.board.set_piece(end, piece)
        self.board.set_piece(start, None)
        piece.has_moved = True

    def switch_player(self):
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.status_label.config(text=f"{'흑' if self.current_player == 'black' else '백'}색 차례")

    def is_in_check(self, color, board=None):
        if board is None:
            board = self.board
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.color != color:
                    if piece.is_valid_move(board, king_pos):
                        return True
        return False

    def is_check(self):
        return self.is_in_check(self.current_player)

    def is_checkmate(self):
        if not self.is_in_check(self.current_player):
            return False
        
        for start_row in range(8):
            for start_col in range(8):
                start = (start_row, start_col)
                piece = self.board.get_piece(start)
                if piece and piece.color == self.current_player:
                    for end_row in range(8):
                        for end_col in range(8):
                            end = (end_row, end_col)
                            if self.is_valid_move(start, end):
                                return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess Game")
    game = ChessGame(root)
    root.mainloop()