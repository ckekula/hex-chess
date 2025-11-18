"""
Simple Evaluation function for Glinski's Hex Chess.
"""

from hex_board import HexBoard
from game import MoveGenerator

# Material values
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}

"""
Simple Evaluation function for Glinski's Hex Chess.
"""

from hex_board import HexBoard
from game import MoveGenerator

# Material values
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}

class Evaluator:
    """Simple position evaluator."""
    
    def __init__(self, board_size: int = 6):
        self.board_size = board_size
    
    def evaluate_position(self, board: HexBoard) -> int:
        """
        Evaluate position (positive = white advantage).
        
        Score = Material + Center Control + Mobility
        """
        score = 0
        
        # 1. Material counting
        for tile in board.tiles.values():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                value = PIECE_VALUES.get(piece_name, 0)
                score += value if color == 'white' else -value
        
        # 2. Center control bonus (pieces near center get +10)
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                if piece_name != 'king':  # Not for king
                    dist = (abs(q) + abs(r) + abs(-q - r)) / 2
                    if dist <= 2:  # Central hexes
                        bonus = 10
                        score += bonus if color == 'white' else -bonus
        
        # 3. Simple mobility (count available moves)
        move_gen = MoveGenerator(board)
        
        white_moves = 0
        black_moves = 0
        
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                color, _ = tile.get_piece()
                moves = move_gen.get_legal_moves(q, r)
                if color == 'white':
                    white_moves += len(moves)
                else:
                    black_moves += len(moves)
        
        score += (white_moves - black_moves) * 2
        
        return score
    
    def print_evaluation_breakdown(self, board: HexBoard):
        """Print simple breakdown."""
        material_white = 0
        material_black = 0
        
        for tile in board.tiles.values():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                value = PIECE_VALUES.get(piece_name, 0)
                if color == 'white':
                    material_white += value
                else:
                    material_black += value
        
        print(f"\n=== Evaluation ===")
        print(f"Material: White {material_white} | Black {material_black}")
        print(f"Total Score: {self.evaluate_position(board):+d} centipawns")
        print("=" * 20)

