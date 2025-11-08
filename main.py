import pygame
import math
from typing import Tuple
from constants import *
from hex_board import HexBoard
from asset_manager import PieceImageManager

def draw_hexagon(surface: pygame.Surface, center: Tuple[float, float], 
                 radius: float, color: Tuple[int, int, int], 
                 outline_color: Tuple[int, int, int], highlight: bool = False):
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
    
    # Draw outline
    outline_width = 3 if highlight else 2
    pygame.draw.polygon(surface, outline_color, corners, outline_width)


def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hexagonal Chess Board")
    clock = pygame.time.Clock()
    
    # Create the hex board and piece manager
    board = HexBoard(BOARD_SIZE, HEX_RADIUS)
    piece_manager = PieceImageManager()
    
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
                        selected_tile = hovered_coord
                        dragging = True
                        drag_piece = tile.get_piece()
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and selected_tile and hovered_coord:
                    # Move piece
                    board.move_piece(selected_tile[0], selected_tile[1], 
                                   hovered_coord[0], hovered_coord[1])
                dragging = False
                selected_tile = None
                drag_piece = None
        
        # Clear screen
        screen.fill(BACKGROUND)
        
        # Draw all hexagons and pieces
        for (q, r), tile in board.tiles.items():
            x, y = board.axial_to_pixel(q, r, center_x, center_y)
            tile.pixel_pos = (x, y)
            
            # Highlight if selected or hovered
            highlight = (q, r) == selected_tile or (q, r) == hovered_coord
            draw_hexagon(screen, (x, y), board.radius, tile.color, OUTLINE, highlight)
            
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
        text = font.render(f"Hexagonal Board: {BOARD_SIZE} per side", True, (0, 0, 0))
        screen.blit(text, (10, 10))
        
        info_text = small_font.render("Click and drag pieces to move them", True, (0, 0, 0))
        screen.blit(info_text, (10, 35))
        
        if hovered_coord:
            coord_text = small_font.render(f"Hex: ({hovered_coord[0]}, {hovered_coord[1]})", True, (0, 0, 0))
            screen.blit(coord_text, (10, 55))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()