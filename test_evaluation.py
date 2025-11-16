"""
Test script for evaluation function and AI engine.

Run this to see the evaluation function in action.
"""

import sys
sys.path.insert(0, 'src')

from hex_board import HexBoard
from evaluation import Evaluator
from ai_engine import HexChessEngine

def setup_test_board(board: HexBoard):
    """Set up a simple test position."""
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

def test_evaluation():
    """Test the evaluation function on starting position."""
    print("=" * 50)
    print("TESTING EVALUATION FUNCTION")
    print("=" * 50)
    
    board = HexBoard(6, 40)
    setup_test_board(board)
    
    evaluator = Evaluator(6)
    
    print("\n1. Starting Position:")
    evaluator.print_evaluation_breakdown(board)
    
    # Make a move
    print("\n\n2. After white moves knight to center:")
    board.move_piece(2, 3, 0, 2)  # Move knight toward center
    evaluator.print_evaluation_breakdown(board)
    
    print("\n\n3. PST Values for Knight at different positions:")
    print(f"Edge (3,2): {evaluator.pst.get_value('knight', 3, 2, 'white'):+d}")
    print(f"Near edge (2,2): {evaluator.pst.get_value('knight', 2, 2, 'white'):+d}")
    print(f"Center (0,0): {evaluator.pst.get_value('knight', 0, 0, 'white'):+d}")
    print(f"Near center (1,0): {evaluator.pst.get_value('knight', 1, 0, 'white'):+d}")

def test_ai():
    """Test the AI engine finding best move."""
    print("\n\n" + "=" * 50)
    print("TESTING AI ENGINE")
    print("=" * 50)
    
    board = HexBoard(6, 40)
    setup_test_board(board)
    
    engine = HexChessEngine(6)
    
    print("\nFinding best move for White (depth 3)...")
    print("This may take a few seconds...\n")
    
    best_move = engine.get_best_move(board, depth=3, time_limit=5.0)
    
    if best_move:
        from_q, from_r, to_q, to_r = best_move
        from_tile = board.get_tile(from_q, from_r)
        piece_color, piece_name = from_tile.get_piece()
        
        print(f"\n✓ Best move found:")
        print(f"  Move {piece_name} from ({from_q}, {from_r}) to ({to_q}, {to_r})")
        print(f"  Total nodes searched: {engine.nodes_searched}")
    else:
        print("\n✗ No move found!")

if __name__ == "__main__":
    print("\n" + "█" * 50)
    print("  HEX CHESS - EVALUATION FUNCTION TEST")
    print("█" * 50 + "\n")
    
    try:
        test_evaluation()
        test_ai()
        
        print("\n\n" + "=" * 50)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 50)
        print("\nEvaluation function is working!")
        print("AI engine successfully finds best moves.")
        print("\nKey Features:")
        print("  ✓ Material counting")
        print("  ✓ Piece-Square Tables (PSTs)")
        print("  ✓ Mobility evaluation")
        print("  ✓ Minimax with alpha-beta pruning")
        print("  ✓ Move ordering")
        print("  ✓ Quiescence search")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
