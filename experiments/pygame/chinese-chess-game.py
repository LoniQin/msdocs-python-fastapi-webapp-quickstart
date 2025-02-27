import pygame
import sys
import os

# Initialize pygame
pygame.init()
pygame.font.init()

# Game constants
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 750
BOARD_MARGIN_X = 50
BOARD_MARGIN_Y = 50
BOARD_WIDTH = 9  # 9 columns in Xiangqi
BOARD_HEIGHT = 10  # 10 rows in Xiangqi
GRID_SIZE = 64
INFO_PANEL_HEIGHT = 50

# Colors
BACKGROUND_COLOR = (240, 217, 181)
GRID_COLOR = (0, 0, 0)
RED_PIECE_COLOR = (200, 30, 30)
BLACK_PIECE_COLOR = (50, 50, 50)
SELECTED_COLOR = (0, 255, 0, 100)
HIGHLIGHT_COLOR = (0, 0, 255, 70)
TEXT_COLOR = (10, 10, 10)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chinese Chess (Xiangqi)")

# Load font
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

class ChessPiece:
    def __init__(self, name, side, pos_x, pos_y, symbol):
        self.name = name
        self.side = side  # "red" or "black"
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.symbol = symbol
        self.selected = False
    
    def draw(self, surface):
        # Calculate position on the screen
        screen_x = BOARD_MARGIN_X + self.pos_x * GRID_SIZE
        screen_y = BOARD_MARGIN_Y + self.pos_y * GRID_SIZE
        
        # Draw circle background
        color = RED_PIECE_COLOR if self.side == "red" else BLACK_PIECE_COLOR
        pygame.draw.circle(surface, color, (screen_x, screen_y), GRID_SIZE // 2 - 5)
        pygame.draw.circle(surface, BACKGROUND_COLOR, (screen_x, screen_y), GRID_SIZE // 2 - 7)
        pygame.draw.circle(surface, color, (screen_x, screen_y), GRID_SIZE // 2 - 10)
        
        # Draw text
        text_color = RED_PIECE_COLOR if self.side == "red" else BLACK_PIECE_COLOR
        text = small_font.render(self.symbol, True, text_color)
        text_rect = text.get_rect(center=(screen_x, screen_y))
        surface.blit(text, text_rect)
        
        # Draw selection highlight
        if self.selected:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            s.fill(SELECTED_COLOR)
            surface.blit(s, (screen_x - GRID_SIZE // 2, screen_y - GRID_SIZE // 2))

class XiangqiGame:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.pieces = []
        self.selected_piece = None
        self.current_player = "red"  # Red starts first
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        
        # Initialize pieces
        self.initialize_pieces()
    
    def initialize_pieces(self):
        # Red pieces (bottom side)
        # Chariot (Rook)
        self.add_piece("chariot", "red", 0, 9, "車")
        self.add_piece("chariot", "red", 8, 9, "車")
        # Horse (Knight)
        self.add_piece("horse", "red", 1, 9, "馬")
        self.add_piece("horse", "red", 7, 9, "馬")
        # Elephant
        self.add_piece("elephant", "red", 2, 9, "相")
        self.add_piece("elephant", "red", 6, 9, "相")
        # Advisor
        self.add_piece("advisor", "red", 3, 9, "仕")
        self.add_piece("advisor", "red", 5, 9, "仕")
        # General (King)
        self.add_piece("general", "red", 4, 9, "帥")
        # Cannon
        self.add_piece("cannon", "red", 1, 7, "炮")
        self.add_piece("cannon", "red", 7, 7, "炮")
        # Soldier (Pawn)
        for i in range(5):
            self.add_piece("soldier", "red", i*2, 6, "兵")
        
        # Black pieces (top side)
        # Chariot (Rook)
        self.add_piece("chariot", "black", 0, 0, "車")
        self.add_piece("chariot", "black", 8, 0, "車")
        # Horse (Knight)
        self.add_piece("horse", "black", 1, 0, "馬")
        self.add_piece("horse", "black", 7, 0, "馬")
        # Elephant
        self.add_piece("elephant", "black", 2, 0, "象")
        self.add_piece("elephant", "black", 6, 0, "象")
        # Advisor
        self.add_piece("advisor", "black", 3, 0, "士")
        self.add_piece("advisor", "black", 5, 0, "士")
        # General (King)
        self.add_piece("general", "black", 4, 0, "將")
        # Cannon
        self.add_piece("cannon", "black", 1, 2, "炮")
        self.add_piece("cannon", "black", 7, 2, "炮")
        # Soldier (Pawn)
        for i in range(5):
            self.add_piece("soldier", "black", i*2, 3, "卒")
    
    def add_piece(self, name, side, x, y, symbol):
        piece = ChessPiece(name, side, x, y, symbol)
        self.pieces.append(piece)
        self.board[y][x] = piece
    
    def select_piece(self, x, y):
        # First, clear all selections
        for piece in self.pieces:
            piece.selected = False
        
        # Reset valid moves
        self.valid_moves = []
        
        # If there's a piece at the position
        if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH and self.board[y][x] is not None:
            piece = self.board[y][x]
            
            # Can only select your own pieces
            if piece.side == self.current_player:
                piece.selected = True
                self.selected_piece = piece
                
                # Get valid moves for this piece
                self.valid_moves = self.get_valid_moves(piece)
                return True
        
        self.selected_piece = None
        return False
    
    def move_piece(self, x, y):
        if self.selected_piece and (x, y) in self.valid_moves:
            # Check if there's a piece at the destination
            captured = None
            if self.board[y][x] is not None:
                captured = self.board[y][x]
                
                # Remove captured piece
                self.pieces.remove(captured)
                
                # Check if it's a general/king
                if captured.name == "general":
                    self.game_over = True
                    self.winner = self.current_player
            
            # Update board
            self.board[self.selected_piece.pos_y][self.selected_piece.pos_x] = None
            
            # Update piece position
            self.selected_piece.pos_x = x
            self.selected_piece.pos_y = y
            
            # Place piece on new position on board
            self.board[y][x] = self.selected_piece
            
            # Deselect piece
            self.selected_piece.selected = False
            self.selected_piece = None
            self.valid_moves = []
            
            # Change player turn
            self.current_player = "black" if self.current_player == "red" else "red"
            
            return True
        return False
    
    def get_valid_moves(self, piece):
        valid_moves = []
        
        # Different movement patterns for each piece type
        if piece.name == "chariot":  # Rook movement
            # Can move horizontally and vertically
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            for dx, dy in directions:
                x, y = piece.pos_x, piece.pos_y
                
                while True:
                    x += dx
                    y += dy
                    
                    if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
                        break
                    
                    if self.board[y][x] is None:
                        valid_moves.append((x, y))
                    else:
                        if self.board[y][x].side != piece.side:
                            valid_moves.append((x, y))
                        break
        
        elif piece.name == "horse":  # Knight movement
            # Move in L-pattern but blocked by adjacent pieces
            jumps = [
                (1, 2), (2, 1), (2, -1), (1, -2),
                (-1, -2), (-2, -1), (-2, 1), (-1, 2)
            ]
            
            for dx, dy in jumps:
                x, y = piece.pos_x + dx, piece.pos_y + dy
                
                # Check if within bounds
                if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
                    # Check for blocking piece
                    block_x = piece.pos_x + (1 if dx > 0 else -1 if dx < 0 else 0)
                    block_y = piece.pos_y + (1 if dy > 0 else -1 if dy < 0 else 0)
                    
                    # Determine blocking piece based on direction
                    if abs(dx) > abs(dy):  # Horizontal longer, so block is horizontal
                        block_y = piece.pos_y
                    else:  # Vertical longer, so block is vertical
                        block_x = piece.pos_x
                    
                    # Add move if not blocked and destination is empty or has enemy piece
                    if self.board[block_y][block_x] is None:
                        if self.board[y][x] is None or self.board[y][x].side != piece.side:
                            valid_moves.append((x, y))
        
        elif piece.name == "elephant":  # Elephant movement
            # Moves diagonally 2 spaces but can't cross the river
            jumps = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            
            for dx, dy in jumps:
                x, y = piece.pos_x + dx, piece.pos_y + dy
                
                # Check if within bounds and on correct side of the river
                if 0 <= x < BOARD_WIDTH:
                    if piece.side == "red" and 5 <= y < BOARD_HEIGHT:
                        # Check for blocking piece (elephant eye)
                        block_x = piece.pos_x + dx // 2
                        block_y = piece.pos_y + dy // 2
                        
                        if self.board[block_y][block_x] is None:
                            if self.board[y][x] is None or self.board[y][x].side != piece.side:
                                valid_moves.append((x, y))
                    
                    elif piece.side == "black" and 0 <= y < 5:
                        # Check for blocking piece (elephant eye)
                        block_x = piece.pos_x + dx // 2
                        block_y = piece.pos_y + dy // 2
                        
                        if self.board[block_y][block_x] is None:
                            if self.board[y][x] is None or self.board[y][x].side != piece.side:
                                valid_moves.append((x, y))
        
        elif piece.name == "advisor":  # Advisor movement
            # Moves diagonally 1 space within palace
            jumps = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            
            for dx, dy in jumps:
                x, y = piece.pos_x + dx, piece.pos_y + dy
                
                # Check if within palace
                if 3 <= x <= 5:
                    if (piece.side == "red" and 7 <= y <= 9) or (piece.side == "black" and 0 <= y <= 2):
                        if self.board[y][x] is None or self.board[y][x].side != piece.side:
                            valid_moves.append((x, y))
        
        elif piece.name == "general":  # General movement
            # Moves 1 space horizontally or vertically within palace
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            for dx, dy in directions:
                x, y = piece.pos_x + dx, piece.pos_y + dy
                
                # Check if within palace
                if 3 <= x <= 5:
                    if (piece.side == "red" and 7 <= y <= 9) or (piece.side == "black" and 0 <= y <= 2):
                        if self.board[y][x] is None or self.board[y][x].side != piece.side:
                            valid_moves.append((x, y))
            
            # Special case: flying general
            # Check if this general can see the enemy general directly
            enemy_general = None
            for p in self.pieces:
                if p.name == "general" and p.side != piece.side:
                    enemy_general = p
                    break
            
            if enemy_general and piece.pos_x == enemy_general.pos_x:
                # Check if there are any pieces between the two generals
                y_min = min(piece.pos_y, enemy_general.pos_y)
                y_max = max(piece.pos_y, enemy_general.pos_y)
                
                has_piece_between = False
                for y in range(y_min + 1, y_max):
                    if self.board[y][piece.pos_x] is not None:
                        has_piece_between = True
                        break
                
                if not has_piece_between:
                    valid_moves.append((enemy_general.pos_x, enemy_general.pos_y))
        
        elif piece.name == "cannon":  # Cannon movement
            # Moves like chariot but needs exactly one piece to jump over for captures
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            for dx, dy in directions:
                x, y = piece.pos_x, piece.pos_y
                jump_count = 0
                
                while True:
                    x += dx
                    y += dy
                    
                    if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
                        break
                    
                    if self.board[y][x] is None:
                        if jump_count == 0:  # Can move to empty spaces with no jumps
                            valid_moves.append((x, y))
                    else:
                        if jump_count == 0:
                            jump_count = 1
                        else:
                            if self.board[y][x].side != piece.side:
                                valid_moves.append((x, y))
                            break
        
        elif piece.name == "soldier":  # Soldier/Pawn movement
            # Moves 1 step forward before crossing river
            # After crossing, can move horizontally as well
            
            if piece.side == "red":
                # Can always move up
                if piece.pos_y > 0:
                    if self.board[piece.pos_y - 1][piece.pos_x] is None or self.board[piece.pos_y - 1][piece.pos_x].side != piece.side:
                        valid_moves.append((piece.pos_x, piece.pos_y - 1))
                
                # If crossed the river, can move horizontally
                if piece.pos_y < 5:
                    # Move right
                    if piece.pos_x < BOARD_WIDTH - 1:
                        if self.board[piece.pos_y][piece.pos_x + 1] is None or self.board[piece.pos_y][piece.pos_x + 1].side != piece.side:
                            valid_moves.append((piece.pos_x + 1, piece.pos_y))
                    
                    # Move left
                    if piece.pos_x > 0:
                        if self.board[piece.pos_y][piece.pos_x - 1] is None or self.board[piece.pos_y][piece.pos_x - 1].side != piece.side:
                            valid_moves.append((piece.pos_x - 1, piece.pos_y))
            
            else:  # Black
                # Can always move down
                if piece.pos_y < BOARD_HEIGHT - 1:
                    if self.board[piece.pos_y + 1][piece.pos_x] is None or self.board[piece.pos_y + 1][piece.pos_x].side != piece.side:
                        valid_moves.append((piece.pos_x, piece.pos_y + 1))
                
                # If crossed the river, can move horizontally
                if piece.pos_y >= 5:
                    # Move right
                    if piece.pos_x < BOARD_WIDTH - 1:
                        if self.board[piece.pos_y][piece.pos_x + 1] is None or self.board[piece.pos_y][piece.pos_x + 1].side != piece.side:
                            valid_moves.append((piece.pos_x + 1, piece.pos_y))
                    
                    # Move left
                    if piece.pos_x > 0:
                        if self.board[piece.pos_y][piece.pos_x - 1] is None or self.board[piece.pos_y][piece.pos_x - 1].side != piece.side:
                            valid_moves.append((piece.pos_x - 1, piece.pos_y))
        
        return valid_moves
    
    def draw(self, surface):
        # Draw board background
        surface.fill(BACKGROUND_COLOR)
        
        # Draw grid
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                rect_x = BOARD_MARGIN_X + x * GRID_SIZE - GRID_SIZE // 2
                rect_y = BOARD_MARGIN_Y + y * GRID_SIZE - GRID_SIZE // 2
                
                # Draw grid lines
                if x < BOARD_WIDTH - 1:
                    pygame.draw.line(surface, GRID_COLOR, 
                                    (BOARD_MARGIN_X + x * GRID_SIZE, BOARD_MARGIN_Y + y * GRID_SIZE),
                                    (BOARD_MARGIN_X + (x + 1) * GRID_SIZE, BOARD_MARGIN_Y + y * GRID_SIZE))
                
                if y < BOARD_HEIGHT - 1:
                    pygame.draw.line(surface, GRID_COLOR, 
                                    (BOARD_MARGIN_X + x * GRID_SIZE, BOARD_MARGIN_Y + y * GRID_SIZE),
                                    (BOARD_MARGIN_X + x * GRID_SIZE, BOARD_MARGIN_Y + (y + 1) * GRID_SIZE))
        
        # Draw the river
        river_rect = pygame.Rect(
            BOARD_MARGIN_X - GRID_SIZE // 2,
            BOARD_MARGIN_Y + 4 * GRID_SIZE - GRID_SIZE // 2,
            BOARD_WIDTH * GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, (190, 210, 230), river_rect)
        
        # Draw palace diagonal lines
        # Top palace
        pygame.draw.line(surface, GRID_COLOR,
                         (BOARD_MARGIN_X + 3 * GRID_SIZE, BOARD_MARGIN_Y + 0 * GRID_SIZE),
                         (BOARD_MARGIN_X + 5 * GRID_SIZE, BOARD_MARGIN_Y + 2 * GRID_SIZE))
        pygame.draw.line(surface, GRID_COLOR,
                         (BOARD_MARGIN_X + 5 * GRID_SIZE, BOARD_MARGIN_Y + 0 * GRID_SIZE),
                         (BOARD_MARGIN_X + 3 * GRID_SIZE, BOARD_MARGIN_Y + 2 * GRID_SIZE))
        
        # Bottom palace
        pygame.draw.line(surface, GRID_COLOR,
                         (BOARD_MARGIN_X + 3 * GRID_SIZE, BOARD_MARGIN_Y + 7 * GRID_SIZE),
                         (BOARD_MARGIN_X + 5 * GRID_SIZE, BOARD_MARGIN_Y + 9 * GRID_SIZE))
        pygame.draw.line(surface, GRID_COLOR,
                         (BOARD_MARGIN_X + 5 * GRID_SIZE, BOARD_MARGIN_Y + 7 * GRID_SIZE),
                         (BOARD_MARGIN_X + 3 * GRID_SIZE, BOARD_MARGIN_Y + 9 * GRID_SIZE))
        
        # Draw valid moves
        for x, y in self.valid_moves:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT_COLOR)
            surface.blit(s, (BOARD_MARGIN_X + x * GRID_SIZE - GRID_SIZE // 2, 
                            BOARD_MARGIN_Y + y * GRID_SIZE - GRID_SIZE // 2))
        
        # Draw pieces
        for piece in self.pieces:
            piece.draw(surface)
        
        # Draw info panel
        pygame.draw.rect(surface, (200, 200, 200), (0, SCREEN_HEIGHT - INFO_PANEL_HEIGHT, SCREEN_WIDTH, INFO_PANEL_HEIGHT))
        
        # Show current player
        current_text = f"Current Player: {'Red' if self.current_player == 'red' else 'Black'}"
        text_surf = font.render(current_text, True, TEXT_COLOR)
        surface.blit(text_surf, (20, SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 15))
        
        # Show game over message if applicable
        if self.game_over:
            winner_text = f"Game Over! {'Red' if self.winner == 'red' else 'Black'} Wins!"
            text_surf = font.render(winner_text, True, RED_PIECE_COLOR if self.winner == "red" else BLACK_PIECE_COLOR)
            surface.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 15))

def main():
    game = XiangqiGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Get board coordinates from mouse position
                mouse_x, mouse_y = event.pos
                board_x = round((mouse_x - BOARD_MARGIN_X) / GRID_SIZE)
                board_y = round((mouse_y - BOARD_MARGIN_Y) / GRID_SIZE)
                
                # If within board bounds
                if 0 <= board_x < BOARD_WIDTH and 0 <= board_y < BOARD_HEIGHT:
                    # If a piece is already selected, try to move it
                    if game.selected_piece:
                        if not game.move_piece(board_x, board_y):
                            # If move failed, try to select a new piece
                            game.select_piece(board_x, board_y)
                    else:
                        # No piece selected, try to select one
                        game.select_piece(board_x, board_y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset game
                    game.reset_game()
        
        # Draw the game
        game.draw(screen)
        
        # Update the display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()