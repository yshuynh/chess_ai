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
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    board = chess.Board()
    load_images()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        clock.tick(MAX_FPS)
        p.display.flip()


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


if __name__ == '__main__':
    main()
