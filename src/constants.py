COMPUTATION_DEPTH = 2 # higher means more difficult

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
HEX_RADIUS = 40
BOARD_SIZE = 6

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

LIGHT_SQUARE = (255, 217, 181)
DARK_SQUARE = (181, 136, 99)
NEUTRAL_SQUARE = (210, 180, 145)

BACKGROUND = (38, 42, 47)
OUTLINE = (30, 30, 30)

HIGHLIGHT = (246, 230, 120, 150)
LEGAL_MOVE_HIGHLIGHT = (100, 180, 105, 120)

ENGINE_MOVE_START = (255, 140, 0, 120)
ENGINE_MOVE_END = (255, 215, 0, 140)

BUTTON_BG = (200, 200, 200)
BUTTON_DISABLED = (150, 150, 150)
RESET_COLOR = (210, 75, 70)
UNDO_COLOR = (110, 180, 210)
FLIP_COLOR = BLACK

# Piece values in centipawns
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}

# Phase calculation
MAX_PHASE = 26  # 4*Knight + 6*Bishop + 4*Rook + 2*Queen

PHASE_VALUES = {
    'knight': 1,
    'bishop': 1,
    'rook': 2,
    'queen': 4,
    'pawn': 0,
    'king': 0
}
