import pygame
import math
from typing import Tuple
from constants import *
from hex_board import HexBoard
from asset_manager import PieceImageManager
from move_validator import MoveValidator

def draw_hexagon(surface: pygame.Surface, center: Tuple[float, float], 
                 radius: float, color: Tuple[int, int, int], 
                 outline_color: Tuple[int, int, int], highlight: bool = False,
                 legal_move: bool = False):
    """Draw a single hexagon with outline."""
    corners = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        corners.append((x, y))
    
    # Draw filled hexagon
    pygame.draw.polygon(surface, color, corners)
    
    # Draw highlight if selected
    if highlight:
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        s_corners = [(c[0] - center[0] + radius, c[1] - center[1] + radius) for c in corners]
        pygame.draw.polygon(s, HIGHLIGHT, s_corners)
        surface.blit(s, (center[0] - radius, center[1] - radius))
    
    # Draw legal move indicator (green dot)
    if legal_move:
        pygame.draw.circle(surface, (0, 200, 0, 180), (int(center[0]), int(center[1])), int(radius * 0.3))
    
    # Draw outline
    outline_width = 3 if highlight else 2
    pygame.draw.polygon(surface, outline_color, corners, outline_width)


def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hexagonal Chess - Glinski's Variant")
    clock = pygame.time.Clock()
    
    # Create the hex board and piece manager
    board = HexBoard(BOARD_SIZE, HEX_RADIUS)
    piece_manager = PieceImageManager()
    move_validator = MoveValidator(board)
    
    # Calculate center of screen
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    
    # Initial board positions
    # WHITE
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
    # BLACK
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
    
    # For piece dragging
    selected_tile = None
    dragging = False
    drag_piece = None
    legal_moves = []
    
    # Font for info
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered_coord = board.pixel_to_axial(mouse_pos[0], mouse_pos[1], center_x, center_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hovered_coord:
                    tile = board.get_tile(*hovered_coord)
                    if tile and tile.has_piece():
                        piece_color, _ = tile.get_piece()
                        # Only allow selecting pieces of current turn
                        if piece_color == move_validator.current_turn:
                            selected_tile = hovered_coord
                            dragging = True
                            drag_piece = tile.get_piece()
                            legal_moves = move_validator.get_legal_moves(*hovered_coord)
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and selected_tile and hovered_coord:
                    # Check if move is legal
                    if move_validator.is_legal_move(selected_tile[0], selected_tile[1],
                                                   hovered_coord[0], hovered_coord[1]):
                        # Move piece
                        board.move_piece(selected_tile[0], selected_tile[1], 
                                       hovered_coord[0], hovered_coord[1])
                        # Switch turns
                        move_validator.switch_turn()
                dragging = False
                selected_tile = None
                drag_piece = None
                legal_moves = []
        
        # Clear screen
        screen.fill(BACKGROUND)
        
        # Draw all hexagons and pieces
        for (q, r), tile in board.tiles.items():
            x, y = board.axial_to_pixel(q, r, center_x, center_y)
            tile.pixel_pos = (x, y)
            
            # Highlight if selected or hovered
            highlight = (q, r) == selected_tile or (q, r) == hovered_coord
            is_legal_move = (q, r) in legal_moves
            
            draw_hexagon(screen, (x, y), board.radius, tile.color, OUTLINE, 
                        highlight, is_legal_move)
            
            # Draw piece if present and not being dragged
            if tile.has_piece() and (not dragging or (q, r) != selected_tile):
                piece_color, piece_name = tile.get_piece()
                piece_image = piece_manager.get_image(piece_color, piece_name)
                if piece_image:
                    rect = piece_image.get_rect(center=(x, y))
                    screen.blit(piece_image, rect)
        
        # Draw dragged piece at mouse position
        if dragging and drag_piece:
            piece_color, piece_name = drag_piece
            piece_image = piece_manager.get_image(piece_color, piece_name)
            if piece_image:
                rect = piece_image.get_rect(center=mouse_pos)
                screen.blit(piece_image, rect)
        
        # Draw info text
        text = font.render(f"Hexagonal Chess - Glinski's Variant", True, (0, 0, 0))
        screen.blit(text, (10, 10))
        
        turn_text = font.render(f"Turn: {move_validator.current_turn.upper()}", True, 
                               (255, 255, 255) if move_validator.current_turn == "white" else (0, 0, 0))
        turn_rect = turn_text.get_rect()
        turn_rect.topleft = (10, 40)
        # Draw background for turn indicator
        bg_color = (80, 80, 80) if move_validator.current_turn == "white" else (220, 220, 220)
        pygame.draw.rect(screen, bg_color, turn_rect.inflate(10, 5))
        screen.blit(turn_text, turn_rect)
        
        info_text = small_font.render("Green dots = legal moves", True, (0, 0, 0))
        screen.blit(info_text, (10, 75))
        
        if hovered_coord:
            coord_text = small_font.render(f"Hex: ({hovered_coord[0]}, {hovered_coord[1]})", True, (0, 0, 0))
            screen.blit(coord_text, (10, 95))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()