import pygame
import sys
from pygame.locals import *

class GoGame:
    def __init__(self, board_size=19):
        # Initialize pygame
        pygame.init()
        
        # Game constants
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BOARD_COLOR = (219, 171, 85)  # Wooden board color
        self.LINE_COLOR = (0, 0, 0)
        self.HIGHLIGHT_COLOR = (255, 0, 0, 150)
        
        self.BOARD_SIZE = board_size  # Standard Go board is 19x19
        self.CELL_SIZE = 30
        self.STONE_RADIUS = 12
        self.MARGIN = 40
        
        # Calculate window size
        self.WINDOW_WIDTH = self.MARGIN * 2 + (self.BOARD_SIZE - 1) * self.CELL_SIZE
        self.WINDOW_HEIGHT = self.MARGIN * 2 + (self.BOARD_SIZE - 1) * self.CELL_SIZE
        
        # Create game window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Go Game")
        
        # Game state
        self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_player = "B"  # B for black, W for white
        self.captures = {"B": 0, "W": 0}
        self.ko_point = None
        self.game_over = False
        self.passes = 0
        
        # Render once initially
        self.render()

    def render(self):
        # Fill background
        self.screen.fill(self.BOARD_COLOR)
        
        # Draw grid lines
        for i in range(self.BOARD_SIZE):
            # Vertical lines
            start_pos = (self.MARGIN + i * self.CELL_SIZE, self.MARGIN)
            end_pos = (self.MARGIN + i * self.CELL_SIZE, self.WINDOW_HEIGHT - self.MARGIN)
            pygame.draw.line(self.screen, self.LINE_COLOR, start_pos, end_pos, 1)
            
            # Horizontal lines
            start_pos = (self.MARGIN, self.MARGIN + i * self.CELL_SIZE)
            end_pos = (self.WINDOW_WIDTH - self.MARGIN, self.MARGIN + i * self.CELL_SIZE)
            pygame.draw.line(self.screen, self.LINE_COLOR, start_pos, end_pos, 1)
        
        # Draw star points (hoshi)
        hoshi_points = self.get_hoshi_points()
        for point in hoshi_points:
            x, y = self.get_pixel_coordinates(point[0], point[1])
            pygame.draw.circle(self.screen, self.BLACK, (x, y), 4)
        
        # Draw stones
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self.board[y][x]:
                    color = self.BLACK if self.board[y][x] == "B" else self.WHITE
                    pos_x, pos_y = self.get_pixel_coordinates(x, y)
                    pygame.draw.circle(self.screen, color, (pos_x, pos_y), self.STONE_RADIUS)
                    
                    # Add a black outline to white stones for better visibility
                    if self.board[y][x] == "W":
                        pygame.draw.circle(self.screen, self.BLACK, (pos_x, pos_y), self.STONE_RADIUS, 1)
                    
        # Draw captures and current player
        self.render_game_info()
        
        # Update the display
        pygame.display.flip()

    def render_game_info(self):
        # Create a font
        font = pygame.font.Font(None, 24)
        
        # Render text for captures
        black_text = f"Black captures: {self.captures['W']}"
        white_text = f"White captures: {self.captures['B']}"
        turn_text = f"Current player: {'Black' if self.current_player == 'B' else 'White'}"
        
        # Create text surfaces
        black_surface = font.render(black_text, True, self.BLACK)
        white_surface = font.render(white_text, True, self.BLACK)
        turn_surface = font.render(turn_text, True, self.BLACK)
        
        # Position text
        self.screen.blit(black_surface, (10, 10))
        self.screen.blit(white_surface, (self.WINDOW_WIDTH - white_surface.get_width() - 10, 10))
        self.screen.blit(turn_surface, (10, self.WINDOW_HEIGHT - 30))

    def get_hoshi_points(self):
        # Return star points (hoshi) positions based on board size
        if self.BOARD_SIZE == 19:
            return [(3, 3), (9, 3), (15, 3), 
                    (3, 9), (9, 9), (15, 9), 
                    (3, 15), (9, 15), (15, 15)]
        elif self.BOARD_SIZE == 13:
            return [(3, 3), (9, 3), (3, 9), (9, 9), (6, 6)]
        elif self.BOARD_SIZE == 9:
            return [(2, 2), (6, 2), (2, 6), (6, 6), (4, 4)]
        else:
            return []

    def get_board_coordinates(self, pixel_x, pixel_y):
        # Convert pixel coordinates to board coordinates
        x = round((pixel_x - self.MARGIN) / self.CELL_SIZE)
        y = round((pixel_y - self.MARGIN) / self.CELL_SIZE)
        
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            return x, y
        return None

    def get_pixel_coordinates(self, board_x, board_y):
        # Convert board coordinates to pixel coordinates
        pixel_x = self.MARGIN + board_x * self.CELL_SIZE
        pixel_y = self.MARGIN + board_y * self.CELL_SIZE
        return pixel_x, pixel_y

    def place_stone(self, x, y):
        # Check if the move is valid
        if not self.is_valid_move(x, y):
            return False
        
        # Place the stone
        self.board[y][x] = self.current_player
        
        # Capture stones
        captured = self.check_captures(x, y)
        
        # Remove captured stones
        for cx, cy in captured:
            opponent = "W" if self.current_player == "B" else "B"
            if self.board[cy][cx] == opponent:
                self.board[cy][cx] = None
                self.captures[self.current_player] += 1
        
        # Check for ko rule
        if len(captured) == 1 and not self.has_liberties(x, y):
            self.ko_point = captured[0]
        else:
            self.ko_point = None
            
        # Switch player
        self.current_player = "W" if self.current_player == "B" else "B"
        self.passes = 0
        
        return True

    def is_valid_move(self, x, y):
        # Check if the position is on the board
        if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
            return False
        
        # Check if the position is empty
        if self.board[y][x] is not None:
            return False
        
        # Check ko rule
        if self.ko_point and (x, y) == self.ko_point:
            return False
        
        # Place stone temporarily to check suicide rule
        self.board[y][x] = self.current_player
        
        # Check if this move would be suicide
        has_liberties = self.has_liberties(x, y)
        
        # Check if captures would prevent suicide
        captures = self.check_captures(x, y)
        
        # Remove the temporary stone
        self.board[y][x] = None
        
        return has_liberties or captures

    def has_liberties(self, x, y):
        # Check if a stone or group at (x, y) has liberties
        if self.board[y][x] is None:
            return False
        
        color = self.board[y][x]
        visited = set()
        
        def has_liberty(x, y, color, visited):
            if (x, y) in visited:
                return False
            
            if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
                return False
                
            if self.board[y][x] is None:
                return True
                
            if self.board[y][x] != color:
                return False
                
            visited.add((x, y))
            
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if has_liberty(nx, ny, color, visited):
                    return True
                    
            return False
        
        return has_liberty(x, y, color, visited)

    def check_captures(self, x, y):
        captured = []
        color = self.board[y][x]
        opponent = "W" if color == "B" else "B"
        
        # Check all four adjacent positions
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if position is on the board
            if not (0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE):
                continue
                
            # Check if there's an opponent's stone
            if self.board[ny][nx] != opponent:
                continue
                
            # Check if the opponent's group has no liberties
            if not self.has_liberties(nx, ny):
                # Add all stones in the group to captured list
                group = self.get_group(nx, ny)
                captured.extend(group)
                
        return captured

    def get_group(self, x, y):
        # Get all stones in the group containing (x, y)
        if self.board[y][x] is None:
            return []
            
        color = self.board[y][x]
        visited = set()
        group = []
        
        def visit(x, y, color, visited, group):
            if (x, y) in visited:
                return
                
            if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
                return
                
            if self.board[y][x] != color:
                return
                
            visited.add((x, y))
            group.append((x, y))
            
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in directions:
                visit(x + dx, y + dy, color, visited, group)
        
        visit(x, y, color, visited, group)
        return group

    def pass_turn(self):
        # Pass the turn
        self.current_player = "W" if self.current_player == "B" else "B"
        self.passes += 1
        
        # Check if the game is over (two consecutive passes)
        if self.passes >= 2:
            self.game_over = True
            
    def calculate_score(self):
        # Calculate the score at the end of the game
        territory = {"B": 0, "W": 0}
        
        # Create a copy of the board for territory calculation
        territory_board = [row[:] for row in self.board]
        
        # Mark territory
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if territory_board[y][x] is None:
                    # Check which player owns this territory
                    owner = self.find_territory_owner(x, y, territory_board)
                    if owner:
                        territory[owner] += 1
        
        # Final score: territory + captures - komi
        komi = 6.5  # Standard komi for white
        
        score = {
            "B": territory["B"] + self.captures["B"],
            "W": territory["W"] + self.captures["W"] + komi
        }
        
        return score

    def find_territory_owner(self, x, y, territory_board):
        # Find which player owns the territory at (x, y)
        if territory_board[y][x] is not None:
            return None
            
        visited = set()
        borders = set()
        
        def visit(x, y, visited, borders):
            if (x, y) in visited:
                return
                
            if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
                return
                
            if territory_board[y][x] is not None:
                borders.add(territory_board[y][x])
                return
                
            visited.add((x, y))
            
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in directions:
                visit(x + dx, y + dy, visited, borders)
        
        visit(x, y, visited, borders)
        
        # If only one player's stones border this area, it's their territory
        if len(borders) == 1:
            return list(borders)[0]
        
        # If both players' stones border this area, it's neutral
        return None
    
    def run(self):
        # Main game loop
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # Get board coordinates from mouse click
                    mouse_x, mouse_y = event.pos
                    board_pos = self.get_board_coordinates(mouse_x, mouse_y)
                    
                    if board_pos:
                        x, y = board_pos
                        self.place_stone(x, y)
                        
                elif event.type == KEYDOWN:
                    if event.key == K_p:
                        # Pass turn
                        self.pass_turn()
                    elif event.key == K_r:
                        # Resign/reset game
                        self.__init__(self.BOARD_SIZE)
                        
            # Render the game
            self.render()
            
            # Limit frame rate
            pygame.time.Clock().tick(30)
            
        # Game is over, calculate score
        score = self.calculate_score()
        
        # Display the final score
        font = pygame.font.Font(None, 36)
        
        text = f"Game Over! Black: {score['B']}, White: {score['W']}"
        winner = "Black" if score["B"] > score["W"] else "White"
        winner_text = f"{winner} wins by {abs(score['B'] - score['W'])} points"
        
        text_surface = font.render(text, True, self.BLACK)
        winner_surface = font.render(winner_text, True, self.BLACK)
        
        self.screen.fill(self.BOARD_COLOR)
        self.screen.blit(text_surface, (self.WINDOW_WIDTH // 2 - text_surface.get_width() // 2, self.WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(winner_surface, (self.WINDOW_WIDTH // 2 - winner_surface.get_width() // 2, self.WINDOW_HEIGHT // 2 + 20))
        
        pygame.display.flip()
        
        # Wait for quit event
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == KEYDOWN:
                    waiting = False

# Run the game
if __name__ == "__main__":
    # You can change the board size to 9, 13, or 19
    game = GoGame(board_size=19)
    game.run()