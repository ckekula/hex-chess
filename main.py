import pygame
import math
import os
from typing import Tuple, Optional, Dict

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


class HexTile:
    """Represents a single hexagonal tile."""
    
    def __init__(self, q: int, r: int, color: Tuple[int, int, int]):
        self.q = q
        self.r = r
        self.color = color
        self.piece = None  # Will hold (color, piece_name) tuple
        self.pixel_pos = None  # Will be set during rendering
        
    def set_piece(self, color: str, piece_name: str):
        """Place a piece on this tile."""
        self.piece = (color, piece_name)
        
    def remove_piece(self):
        """Remove piece from this tile."""
        self.piece = None
        
    def has_piece(self) -> bool:
        """Check if tile has a piece."""
        return self.piece is not None
    
    def get_piece(self) -> Optional[Tuple[str, str]]:
        """Get the piece on this tile."""
        return self.piece


class HexBoard:
    """Represents a hexagonal chess board using axial coordinates."""
    
    def __init__(self, size: int, hex_radius: float):
        self.size = size
        self.radius = hex_radius
        self.tiles: Dict[Tuple[int, int], HexTile] = {}
        self._generate_tiles()
        
    def _generate_tiles(self):
        """Generate hex tiles using axial coordinates (q, r)."""
        for q in range(-self.size + 1, self.size):
            r1 = max(-self.size + 1, -q - self.size + 1)
            r2 = min(self.size - 1, -q + self.size - 1)
            for r in range(r1, r2 + 1):
                color = self._get_hex_color(q, r)
                self.tiles[(q, r)] = HexTile(q, r, color)
    
    def _get_hex_color(self, q: int, r: int) -> Tuple[int, int, int]:
        """
        Determine hex color using 3-coloring algorithm.
        For hexagonal grids, we can use: (q - r) mod 3
        This ensures no two adjacent hexagons have the same color.
        """
        color_index = (q - r) % 3
        colors = [GREY, WHITE, BLACK]
        return colors[color_index]
    
    def axial_to_pixel(self, q: int, r: int, center_x: float, center_y: float) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates."""
        x = center_x + self.radius * (3/2 * q)
        y = center_y + self.radius * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x, y
    
    def pixel_to_axial(self, x: float, y: float, center_x: float, center_y: float) -> Optional[Tuple[int, int]]:
        """Convert pixel coordinates to axial coordinates."""
        # Convert to fractional axial coordinates
        x_rel = x - center_x
        y_rel = y - center_y
        
        q = (2.0/3.0 * x_rel) / self.radius
        r = (-1.0/3.0 * x_rel + math.sqrt(3)/3 * y_rel) / self.radius
        
        # Round to nearest hex
        return self._axial_round(q, r)
    
    def _axial_round(self, q: float, r: float) -> Optional[Tuple[int, int]]:
        """Round fractional axial coordinates to nearest hex."""
        s = -q - r
        
        q_int = round(q)
        r_int = round(r)
        s_int = round(s)
        
        q_diff = abs(q_int - q)
        r_diff = abs(r_int - r)
        s_diff = abs(s_int - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            q_int = -r_int - s_int
        elif r_diff > s_diff:
            r_int = -q_int - s_int
        
        # Check if this coordinate is on the board
        if (q_int, r_int) in self.tiles:
            return (q_int, r_int)
        return None
    
    def get_tile(self, q: int, r: int) -> Optional[HexTile]:
        """Get tile at given axial coordinates."""
        return self.tiles.get((q, r))
    
    def place_piece(self, q: int, r: int, color: str, piece_name: str) -> bool:
        """Place a piece on the board."""
        tile = self.get_tile(q, r)
        if tile:
            tile.set_piece(color, piece_name)
            return True
        return False
    
    def move_piece(self, from_q: int, from_r: int, to_q: int, to_r: int) -> bool:
        """Move a piece from one tile to another."""
        from_tile = self.get_tile(from_q, from_r)
        to_tile = self.get_tile(to_q, to_r)
        
        if from_tile and to_tile and from_tile.has_piece() and from_tile != to_tile:
            to_tile.piece = from_tile.piece
            from_tile.remove_piece()
            return True
        return False
    
    def get_hex_corners(self, center_x: float, center_y: float) -> list:
        """Calculate the six corner points of a hexagon."""
        corners = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + self.radius * math.cos(angle_rad)
            y = center_y + self.radius * math.sin(angle_rad)
            corners.append((x, y))
        return corners


class PieceImageManager:
    """Manages loading and caching of piece images."""
    
    def __init__(self, assets_folder: str = "assets"):
        self.assets_folder = assets_folder
        self.images: Dict[Tuple[str, str], pygame.Surface] = {}
        self._load_images()
    
    def _load_images(self):
        """Load all piece images from assets folder."""
        if not os.path.exists(self.assets_folder):
            print(f"Warning: Assets folder '{self.assets_folder}' not found.")
            return
        
        # Expected piece names
        piece_names = ["king", "queen", "rook", "bishop", "knight", "pawn"]
        colors = ["white", "black"]
        
        for color in colors:
            for piece in piece_names:
                filename = f"{color}-{piece}.svg.png"
                filepath = os.path.join(self.assets_folder, filename)
                
                if os.path.exists(filepath):
                    try:
                        image = pygame.image.load(filepath)
                        # Scale image to fit hex (slightly smaller than hex radius)
                        target_size = int(HEX_RADIUS * 1.4)
                        image = pygame.transform.smoothscale(image, (target_size, target_size))
                        self.images[(color, piece)] = image
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                else:
                    print(f"Warning: Image not found: {filename}")
    
    def get_image(self, color: str, piece_name: str) -> Optional[pygame.Surface]:
        """Get the image for a specific piece."""
        return self.images.get((color, piece_name))


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