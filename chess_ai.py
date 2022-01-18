from random import randint
import pygame as p
import chess
import pygame_menu

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}     # usage: IMAGES['R']
level = 0       # level of AI


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    start_menu(screen)


def start_menu(screen):
    if screen is None:
        return
    menu = pygame_menu.Menu('Chess AI', WIDTH, HEIGHT,
                            theme=pygame_menu.themes.THEME_DARK)
    menu.add.selector('Difficulty:', [('Easy', 0), ('Medium', 1), ('Hard', 2)], onchange=set_difficulty)
    menu.add.button('Play', start_the_game, screen)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    how_to_play = '\n HOW TO PLAY'
    how_to_play_text = '- Use mouse left click to move piece\n- Press Z to undo move\n- Click X to back to menu in-game'
    menu.add.label(how_to_play, max_char=-1, font_size=20)
    menu.add.label(how_to_play_text, max_char=-1, font_size=14)
    menu.mainloop(surface=screen)


def set_difficulty(value, difficulty):
    global level
    level = difficulty


def start_the_game(screen):
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
                if e.key == p.K_z:
                    if len(board.move_stack) > 1:
                        board.pop()
                        board.pop()
            elif e.type == p.MOUSEBUTTONDOWN and not game_over:
                # handle mouse click
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col) or board.turn == chess.BLACK:
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = chess.Move(
                        from_square=get_sq_id(player_clicks[0][0], player_clicks[0][1]),
                        to_square=get_sq_id(player_clicks[1][0], player_clicks[1][1])
                    )
                    move_promotion = chess.Move(
                        from_square=get_sq_id(player_clicks[0][0], player_clicks[0][1]),
                        to_square=get_sq_id(player_clicks[1][0], player_clicks[1][1]),
                        promotion=chess.QUEEN
                    )
                    if board.is_legal(move):
                        board.push(move)
                    elif board.is_legal(move_promotion):
                        board.push(move_promotion)
                    sq_selected = ()
                    player_clicks = []
                    print(board)
            elif e.type == p.MOUSEBUTTONDOWN and game_over:
                running = False

        if board.outcome() is not None:
            game_over = True
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


def draw_game_state(screen, board, sq_selected):
    draw_board(screen, sq_selected, board)
    draw_pieces(screen, board)


def draw_board(screen, sq_selected, board):
    colors = [p.Color('#FFCE9E'), p.Color('#D18B47')]
    color_selected = [p.Color('#CDD16A'), p.Color('#AAA23B')]
    last_move = None
    if len(board.move_stack) > 0:
        last_move = board.move_stack[-1]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            if (r, c) == sq_selected:
                color = color_selected[((r + c) % 2)]
            if last_move is not None and get_sq_id(r, c) in [last_move.from_square, last_move.to_square]:
                color = color_selected[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            sq_id = get_sq_id(r, c)
            piece = board.piece_map().get(sq_id) #{(63: 'King')}
            if piece is not None:
                screen.blit(IMAGES[piece.symbol()], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_game_over_screen(screen, winner):
    myfont = p.font.SysFont('arialblack', 40)
    text_winner = "DRAW!"
    if winner == chess.WHITE:
        text_winner = "You win!"
    elif winner == chess.BLACK:
        text_winner = "You lose!"
    text = myfont.render(f'Game Over! {text_winner}', True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rect)
    # p.draw_text(screen, "GAME OVER", 64, WIDTH/2, HEIGHT/2)


def make_black_ai_move(board):
    if level == 0:
        board.push(calculate_best_move(board))
    elif level == 1:
        board.push(calculate_best_move_minimax(1, board, True))
    elif level == 2:
        board.push(calculate_best_move_minimax(3, board, True))
    # else:
    # calculate_rand_move(board)


def calculate_rand_move(board):
    legal_moves = list(board.legal_moves)
    if len(legal_moves) == 0:
        print("Black has no move.")
    return legal_moves[randint(0, len(legal_moves) - 1)]


def calculate_best_move(board):
    new_game_moves = board.legal_moves
    best_value = -9999
    list_value = []
    for newGameMove in new_game_moves:
        board.push(newGameMove)
        # take the negative as AI plays as black
        board_value = -evaluate_board_easy_mode(board)
        board.pop()
        if board_value > best_value:
            best_value = board_value
            best_move = newGameMove
            list_value = [(best_value, best_move)]
        elif board_value == best_value:
            list_value.append((board_value, newGameMove))
    return list_value[randint(0, len(list_value) - 1)][1]


def evaluate_board_easy_mode(board):
    total_evaluation = 0
    piece_map = board.piece_map()
    for index in piece_map:
        total_evaluation = total_evaluation + get_piece_value_easy_mode(piece_map.get(index))
    return total_evaluation


def get_piece_value_easy_mode(piece):
    if piece is None:
        return 0
    piece_value = {
        chess.PAWN: 10,
        chess.ROOK: 50,
        chess.KNIGHT: 30,
        chess.BISHOP: 30,
        chess.QUEEN: 90,
        chess.KING: 900
    }
    value = piece_value[piece.piece_type]
    if piece.color == chess.BLACK:
        value = -value
    return value


def calculate_best_move_minimax(depth, board, is_maximising_player):
    new_game_moves = board.legal_moves
    best_move = -9999
    list_value = []

    for newGameMove in new_game_moves:
        board.push(newGameMove)
        value = minimax(depth - 1, board, -10000, 10000, not is_maximising_player)
        board.pop()
        if value > best_move:
            best_move = value
            best_move_found = newGameMove
            list_value = [(best_move, best_move_found)]
        elif value == best_move:
            list_value.append((value, newGameMove))
    return list_value[randint(0, len(list_value) - 1)][1]


def minimax(depth, board, alpha, beta, is_maximising_player):
    if depth == 0:
        return -evaluate_board_hard_mode(board)

    new_game_moves = board.legal_moves

    if is_maximising_player:
        best_move = -9999
        for newGameMove in new_game_moves:
            board.push(newGameMove)
            best_move = max(best_move, minimax(depth - 1, board, alpha, beta, not is_maximising_player))
            board.pop()
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = 9999
        for newGameMove in new_game_moves:
            board.push(newGameMove)
            best_move = min(best_move, minimax(depth - 1, board, alpha, beta, not is_maximising_player))
            board.pop()
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move


def evaluate_board_hard_mode(board):
    total_evaluation = 0
    piece_map = board.piece_map()
    for index in piece_map:
        r, c = get_row_col(index)
        total_evaluation = total_evaluation + get_piece_value_hard_mode(piece_map.get(index), r, c)
    return total_evaluation


pawnEvalWhite = [
    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
    [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
    [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
    [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
    [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
    [0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5],
    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
]

pawnEvalBlack = pawnEvalWhite[::-1]

knightEval = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
    [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
    [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
    [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
    [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
    [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]

bishopEvalWhite = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
    [-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
    [-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
    [-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
    [-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]

bishopEvalBlack = bishopEvalWhite[::-1]

rookEvalWhite = [
    [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [ 0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
    [ 0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
]

rookEvalBlack = rookEvalWhite[::-1]

evalQueen = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [ 0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
    [-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
    [-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]

kingEvalWhite = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [ 2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0],
    [ 2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0]
]

kingEvalBlack = kingEvalWhite[::-1]


def get_piece_value_hard_mode(piece, x, y):
    if piece is None:
        return 0
    absolute_value = 0
    if piece.piece_type == chess.PAWN:
        absolute_value = 10 + (pawnEvalWhite[y][x] if piece.color == chess.WHITE else pawnEvalBlack[y][x])
    elif piece.piece_type == chess.ROOK:
        absolute_value = 50 + (rookEvalWhite[y][x] if piece.color == chess.WHITE else rookEvalBlack[y][x])
    elif piece.piece_type == chess.KNIGHT:
        absolute_value = 30 + knightEval[y][x]
    elif piece.piece_type == chess.BISHOP:
        absolute_value = 30 + (bishopEvalWhite[y][x] if piece.color == chess.WHITE else bishopEvalBlack[y][x])
    elif piece.piece_type == chess.QUEEN:
        absolute_value = 90 + evalQueen[y][x]
    elif piece.piece_type == chess.KING:
        absolute_value = 900 + (kingEvalWhite[y][x] if piece.color == chess.WHITE else kingEvalBlack[y][x])
    else:
        print("Error: Dont know piece type!")
        exit()

    return absolute_value if piece.color == chess.WHITE else -absolute_value


if __name__ == '__main__':
    main()
