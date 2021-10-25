import pygame as p
import chess

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}     # usage: IMAGES['R']
level = 0       # level of AI


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    start_the_game(screen)


def start_the_game(screen):
    print("start game")
    print("start game")
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    board = chess.Board()
    load_images()
    running = True
    game_over = False
    winner = None
    sq_selected = ()  # last click [(1,2)]
    player_clicks = []  # two last clicks [(1,2), (2,3)]
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN and not game_over:
                # handle undo
                pass
            elif e.type == p.MOUSEBUTTONDOWN and not game_over:
                # handle mouse click
                pass

        if board.is_checkmate():
            game_over = True
            # print("winner: ", board.outcome().winner)
            print("Game Over! Winner: ", "WHITE" if board.turn == chess.WHITE else "BLACK")
            winner = not board.turn
        draw_game_state(screen, board, sq_selected)
        if game_over:
            draw_game_over_screen(screen, winner)
        clock.tick(MAX_FPS)
        p.display.flip()
        if board.turn == chess.BLACK and not game_over:
            make_black_ai_move(board)


def get_sq_id(r, c):
    return (DIMENSION - r - 1) * DIMENSION + c


def get_row_col(sq_id):
    r = int(sq_id / DIMENSION)
    r = int(DIMENSION - r - 1)
    c = int(sq_id % DIMENSION)
    return r, c


def load_images():
    pieces = ['p', 'r', 'n', 'b', 'k', 'q', 'P', 'R', 'N', 'B', 'K', 'Q']
    for piece in pieces:
        file_path = 'images/' + 'b' + piece + '.png'
        if piece.isupper():
            file_path = 'images/' + 'w' + piece + '.png'
        # f = open(file_path, "w")
        # f.write(chess.svg.piece(chess.Piece.from_symbol(piece), size=SQ_SIZE)
        # f.close()
        IMAGES[piece] = p.image.load(file_path)


# luong
def draw_game_state(screen, board, sq_selected):
    pass


# luong
def draw_game_over_screen(screen, winner):
    pass


def make_black_ai_move(board):
    if level == 0:
        board.push(calculate_best_move(board))
    elif level == 1:
        board.push(calculate_best_move_minimax(1, board, True))
    elif level == 2:
        board.push(calculate_best_move_minimax(3, board, True))
    else:
        calculate_rand_move(board)


# minh
def calculate_rand_move(board):
    pass


# minh
def calculate_best_move(board):
    pass


# ys
def calculate_best_move_minimax(depth, board, is_maximising_player):
    pass


if __name__ == '__main__':
    main()
