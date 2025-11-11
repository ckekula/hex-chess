from hex_board import HexBoard

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
HEX_RADIUS = 40
BOARD_SIZE = 6  # Hexagons per side

# Colors
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
GREY = (170, 170, 170)
BACKGROUND = (238, 238,210)
OUTLINE = (30, 30, 30)
HIGHLIGHT = (255, 253, 208)
LEGAL_MOVE_HIGHLIGHT = (144, 238, 144, 100)  # Light green with transparency

def setup_initial_board(board: HexBoard):
    """Set up the initial chess piece positions."""
    # Clear the board first
    for tile in board.tiles.values():
        tile.remove_piece()
    
    # Reset turn to white
    board.current_turn = "white"
    
    # WHITE pieces
    board.place_piece(1, 4, "white", "king")
    board.place_piece(-1, 5, "white", "queen")
    board.place_piece(3, 2, "white", "rook")
    board.place_piece(-3, 5, "white", "rook")
    board.place_piece(2, 3, "white", "knight")
    board.place_piece(-2, 5, "white", "knight")
    board.place_piece(0, 5, "white", "bishop")
    board.place_piece(0, 4, "white", "bishop")
    board.place_piece(0, 3, "white", "bishop")
    board.place_piece(-4, 5, "white", "pawn")
    board.place_piece(-3, 4, "white", "pawn")
    board.place_piece(-2, 3, "white", "pawn")
    board.place_piece(-1, 2, "white", "pawn")
    board.place_piece(0, 1, "white", "pawn")
    board.place_piece(1, 1, "white", "pawn")
    board.place_piece(2, 1, "white", "pawn")
    board.place_piece(3, 1, "white", "pawn")
    board.place_piece(4, 1, "white", "pawn")
    
    # BLACK pieces
    board.place_piece(1, -5, "black", "king")
    board.place_piece(-1, -4, "black", "queen")
    board.place_piece(3, -5, "black", "rook")
    board.place_piece(-3, -2, "black", "rook")
    board.place_piece(2, -5, "black", "knight")
    board.place_piece(-2, -3, "black", "knight")
    board.place_piece(0, -5, "black", "bishop")
    board.place_piece(0, -4, "black", "bishop")
    board.place_piece(0, -3, "black", "bishop")
    board.place_piece(4, -5, "black", "pawn")
    board.place_piece(3, -4, "black", "pawn")
    board.place_piece(2, -3, "black", "pawn")
    board.place_piece(1, -2, "black", "pawn")
    board.place_piece(0, -1, "black", "pawn")
    board.place_piece(-1, -1, "black", "pawn")
    board.place_piece(-2, -1, "black", "pawn")
    board.place_piece(-3, -1, "black", "pawn")
    board.place_piece(-4, -1, "black", "pawn")