"""
Evaluation function for Glinski's Hex Chess with Piece-Square Tables.

This module provides position evaluation using:
1. Material counting
2. Piece-Square Tables (PSTs) for positional bonuses
3. Additional heuristics for hex chess strategy
"""

from typing import Dict, Tuple
from hex_board import HexBoard
from game import MoveGenerator, MoveValidator

# Material values (in centipawns)
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}

class HexPieceSquareTables:
    """
    Piece-Square Tables for hexagonal chess board.
    
    Values are assigned based on hex distance from center and strategic importance.
    Positive values encourage pieces to occupy those squares.
    """
    
    def __init__(self, board_size: int = 6):
        self.board_size = board_size
        self.tables = {}
        self._initialize_tables()
    
    def _distance_from_center(self, q: int, r: int) -> float:
        """Calculate hex distance from center (0,0)."""
        # Hex distance formula
        return (abs(q) + abs(r) + abs(-q - r)) / 2
    
    def _initialize_tables(self):
        """Initialize piece-square tables for hex board."""
        
        # PAWN PST: Encourage forward movement, center files
        self.tables['pawn'] = {}
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Pawns prefer:
                # - Not too far forward (vulnerable)
                # - Center files slightly
                # - Advance bonus based on color handled in get_value
                base_value = 0
                
                # Center file bonus (q near 0)
                if abs(q) <= 1:
                    base_value += 10
                elif abs(q) <= 2:
                    base_value += 5
                
                # Slight penalty for edges
                if dist >= self.board_size - 1:
                    base_value -= 10
                
                self.tables['pawn'][(q, r)] = base_value
        
        # KNIGHT PST: Strongly prefer center, avoid edges
        self.tables['knight'] = {}
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Knights are strongest in center
                if dist <= 1:
                    value = 40  # Center hexes
                elif dist <= 2:
                    value = 20  # Near center
                elif dist <= 3:
                    value = 0   # Mid-range
                elif dist <= 4:
                    value = -20 # Approaching edge
                else:
                    value = -40 # Edge hexes (bad for knights)
                
                self.tables['knight'][(q, r)] = value
        
        # BISHOP PST: Prefer center, long diagonals
        self.tables['bishop'] = {}
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Bishops prefer center for mobility
                if dist <= 1:
                    value = 25
                elif dist <= 2:
                    value = 15
                elif dist <= 3:
                    value = 5
                else:
                    value = -5
                
                # Bonus for diagonals (same color lines)
                # Bishops on q-r constant lines have more reach
                if abs(q - r) <= 1:
                    value += 10
                
                self.tables['bishop'][(q, r)] = value
        
        # ROOK PST: Prefer center ranks/files, back rank in early game
        self.tables['rook'] = {}
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Rooks prefer center files for mobility
                if dist <= 2:
                    value = 10
                else:
                    value = 0
                
                # Bonus for center files (q axis)
                if abs(q) <= 1:
                    value += 10
                # Bonus for center ranks (r axis)
                if abs(r) <= 1:
                    value += 10
                
                self.tables['rook'][(q, r)] = value
        
        # QUEEN PST: Prefer center, avoid early development to edge
        self.tables['queen'] = {}
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Queen prefers center but not too exposed
                if dist <= 1:
                    value = 15
                elif dist <= 2:
                    value = 10
                elif dist <= 3:
                    value = 5
                else:
                    value = -10  # Penalty for edge
                
                self.tables['queen'][(q, r)] = value
        
        # KING PST: Safety first - varies by game phase
        # Endgame: King should be active (center)
        # Opening/Middlegame: King should be safe (castled position)
        self.tables['king_opening'] = {}
        self.tables['king_endgame'] = {}
        
        for q in range(-self.board_size + 1, self.board_size):
            r1 = max(-self.board_size + 1, -q - self.board_size + 1)
            r2 = min(self.board_size - 1, -q + self.board_size - 1)
            for r in range(r1, r2 + 1):
                dist = self._distance_from_center(q, r)
                
                # Opening/Middlegame: King prefers back ranks, corner safety
                if dist >= 4:
                    opening_value = 30  # Back rank safety
                elif dist >= 3:
                    opening_value = 10
                else:
                    opening_value = -20  # Exposed in center
                
                # Endgame: King should be active (center)
                if dist <= 1:
                    endgame_value = 40
                elif dist <= 2:
                    endgame_value = 20
                elif dist <= 3:
                    endgame_value = 0
                else:
                    endgame_value = -20
                
                self.tables['king_opening'][(q, r)] = opening_value
                self.tables['king_endgame'][(q, r)] = endgame_value
    
    def get_value(self, piece_name: str, q: int, r: int, piece_color: str, is_endgame: bool = False) -> int:
        """
        Get PST value for a piece at a given position.
        
        Args:
            piece_name: Type of piece
            q, r: Axial coordinates
            piece_color: 'white' or 'black'
            is_endgame: Whether to use endgame king table
        
        Returns:
            PST bonus value in centipawns
        """
        # Handle king's special tables
        if piece_name == 'king':
            table_key = 'king_endgame' if is_endgame else 'king_opening'
            base_value = self.tables[table_key].get((q, r), 0)
        else:
            base_value = self.tables[piece_name].get((q, r), 0)
        
        # For pawns, add advancement bonus
        if piece_name == 'pawn':
            if piece_color == 'white':
                # White pawns advance toward negative r
                advancement_bonus = -r * 5  # Closer to r=-5 is better
            else:
                # Black pawns advance toward positive r
                advancement_bonus = r * 5   # Closer to r=5 is better
            base_value += max(0, advancement_bonus)
        
        # Flip values for black (black wants negative scores from white's perspective)
        if piece_color == 'black':
            return -base_value
        return base_value


class Evaluator:
    """
    Position evaluator combining material and PST evaluation.
    """
    
    def __init__(self, board_size: int = 6):
        self.pst = HexPieceSquareTables(board_size)
        self.move_gen = None  # Will be set when evaluating
        self.move_validator = None  # Will be set when evaluating
    
    def count_material(self, board: HexBoard) -> Dict[str, int]:
        """Count material for both sides."""
        material = {'white': 0, 'black': 0}
        piece_count = {'white': {}, 'black': {}}
        
        for tile in board.tiles.values():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                value = PIECE_VALUES.get(piece_name, 0)
                material[color] += value
                piece_count[color][piece_name] = piece_count[color].get(piece_name, 0) + 1
        
        return material, piece_count
    
    def is_endgame(self, piece_count: Dict[str, Dict[str, int]]) -> bool:
        """
        Determine if position is in endgame phase.
        Simple heuristic: Queens traded or total pieces < threshold
        """
        total_pieces = sum(
            sum(pieces.values()) for pieces in piece_count.values()
        )
        
        # Endgame if:
        # - Both queens off the board, OR
        # - Very few pieces remain
        white_queens = piece_count.get('white', {}).get('queen', 0)
        black_queens = piece_count.get('black', {}).get('queen', 0)
        
        return (white_queens == 0 and black_queens == 0) or total_pieces < 12
    
    def evaluate_position(self, board: HexBoard) -> int:
        """
        Evaluate the current board position.
        
        Returns score from white's perspective (positive = white advantage)
        
        Score components:
        1. Material balance
        2. Piece-square table bonuses
        3. Game phase adjustments
        """
        # Initialize move generator and validator
        self.move_gen = MoveGenerator(board)
        self.move_validator = MoveValidator(board)
        
        # Check for terminal positions
        game_status = self.move_validator.get_game_status()
        if game_status == 'checkmate':
            # Current player is checkmated
            if board.current_turn == 'white':
                return -100000  # Black wins
            else:
                return 100000   # White wins
        elif game_status == 'stalemate':
            return 0  # Draw
        
        # Material counting
        material, piece_count = self.count_material(board)
        material_score = material['white'] - material['black']
        
        # PST bonuses
        is_endgame = self.is_endgame(piece_count)
        pst_score = 0
        
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                pst_value = self.pst.get_value(piece_name, q, r, color, is_endgame)
                pst_score += pst_value
        
        # Mobility bonus (simplified - count legal moves)
        white_mobility = self._count_mobility(board, 'white')
        black_mobility = self._count_mobility(board, 'black')
        mobility_score = (white_mobility - black_mobility) * 2
        
        # Check penalty/bonus
        check_score = 0
        if self.move_validator.is_in_check('white'):
            check_score -= 50
        if self.move_validator.is_in_check('black'):
            check_score += 50
        
        # Total evaluation
        total_score = material_score + pst_score + mobility_score + check_score
        
        return total_score
    
    def _count_mobility(self, board: HexBoard, color: str) -> int:
        """Count total legal moves for a color (simplified mobility metric)."""
        if self.move_gen is None:
            self.move_gen = MoveGenerator(board)
        
        mobility = 0
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                piece_color, _ = tile.get_piece()
                if piece_color == color:
                    # Count legal moves for this piece
                    moves = self.move_gen.get_legal_moves(q, r)
                    mobility += len(moves)
        return mobility
    
    def print_evaluation_breakdown(self, board: HexBoard):
        """Print detailed evaluation breakdown for debugging."""
        material, piece_count = self.count_material(board)
        is_endgame = self.is_endgame(piece_count)
        
        print("\n=== Position Evaluation ===")
        print(f"Game Phase: {'Endgame' if is_endgame else 'Opening/Middlegame'}")
        print(f"\nMaterial:")
        print(f"  White: {material['white']} centipawns")
        print(f"  Black: {material['black']} centipawns")
        print(f"  Balance: {material['white'] - material['black']:+d}")
        
        # PST breakdown
        pst_white = 0
        pst_black = 0
        for (q, r), tile in board.tiles.items():
            if tile.has_piece():
                color, piece_name = tile.get_piece()
                pst_value = self.pst.get_value(piece_name, q, r, color, is_endgame)
                if color == 'white':
                    pst_white += pst_value
                else:
                    pst_black -= pst_value  # Convert to white's perspective
        
        print(f"\nPST Scores:")
        print(f"  White: {pst_white:+d}")
        print(f"  Black: {pst_black:+d}")
        print(f"  Balance: {pst_white - pst_black:+d}")
        
        # Mobility
        white_mobility = self._count_mobility(board, 'white')
        black_mobility = self._count_mobility(board, 'black')
        print(f"\nMobility:")
        print(f"  White: {white_mobility} moves")
        print(f"  Black: {black_mobility} moves")
        
        print(f"\nTotal Evaluation: {self.evaluate_position(board):+d} centipawns")
        print("=" * 30)
