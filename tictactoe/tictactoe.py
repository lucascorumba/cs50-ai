"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    moves = counter(board)
    if moves[0] == moves[1]:
        return X
    if moves[0] > moves[1]:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board) == True:
        return None
    free = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                free.add((i, j))
    return free


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    mark = player(board)
    board_copy = copy.deepcopy(board)
    if board_copy[action[0]][action[1]] != EMPTY:
        raise Exception("Invalid move")
    board_copy[action[0]][action[1]] = mark
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for item in board:
        if item.count('X') == 3 or item.count('O') == 3:
            return item[0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[1][1] != EMPTY:
        return board[1][1]
    if board[0][2] == board[1][1] == board[2][0] and board[1][1] != EMPTY:
        return board[1][1]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    win = winner(board)
    if win == X or win == O:
        return True
    if win == None:
        for row in board:
            if EMPTY in row:
                return False
        return True
    

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    if win == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action (i, j) for the current player on the board.
    """
    if terminal(board) == True:
        return None
    if player(board) == X:
        v, best_move = max_value(board)
        return best_move
    v, best_move = min_value(board)
    return best_move


def counter(board):
    """
    Returns a tuple (i, j), where 'i' stands for the number of 'X' moves 
    and 'j' for 'O' moves.
    """
    i, j = 0, 0
    for el in board:
        i += el.count(X)
        j += el.count(O)
    return i, j


def max_value(board):
    """
    Picks action in actions that produces the highest value of min_value().
    """
    if terminal(board) == True:
        return utility(board), None
    v = float('-inf')
    current_best = None
    for action in actions(board):
        current_value, current_move = min_value(result(board, action))
        if current_value > v:
            v = current_value
            current_best = action
            if v == 1:
                return v, current_best
    return v, current_best


def min_value(board):
    """
    Picks action in actions that produces the lowest value of max_value().
    """
    if terminal(board) == True:
        return utility(board), None
    v = float('inf')
    current_best = None
    for action in actions(board):
        current_value, current_move = max_value(result(board, action))
        if current_value < v:
            v = current_value
            current_best = action
            if v == -1:
                return v, current_best
    return v, current_best