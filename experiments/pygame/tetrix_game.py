import pygame
import random
import time

# Initialize PyGame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Tetromino shapes (I, J, L, O, S, T, Z)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyGame Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

class Tetromino:
    def __init__(self):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        
    def rotate(self):
        # Rotate the shape (transpose and reverse each row)
        rotated = [[self.shape[y][x] for y in range(len(self.shape) - 1, -1, -1)]
                  for x in range(len(self.shape[0]))]
        
        # Check if rotation is valid
        old_shape = self.shape
        self.shape = rotated
        if self.collision(self.x, self.y, grid):
            self.shape = old_shape
            
    def collision(self, x, y, grid):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j]:
                    # Check if out of bounds
                    if (y + i >= GRID_HEIGHT or
                        x + j < 0 or
                        x + j >= GRID_WIDTH):
                        return True
                    # Check if collision with placed blocks
                    if y + i >= 0 and grid[y + i][x + j]:
                        return True
        return False

def create_grid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def merge_tetromino(tetromino, grid):
    for i in range(len(tetromino.shape)):
        for j in range(len(tetromino.shape[i])):
            if tetromino.shape[i][j]:
                grid[tetromino.y + i][tetromino.x + j] = tetromino.color
    return grid

def clear_rows(grid):
    full_rows = []
    for i in range(GRID_HEIGHT):
        if all(grid[i]):
            full_rows.append(i)
    
    for row in full_rows:
        del grid[row]
        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    
    return len(full_rows)

def draw_grid(screen, grid):
    # Draw background and grid
    screen.fill(BLACK)
    
    # Draw grid border
    pygame.draw.rect(screen, WHITE, 
                    (GRID_OFFSET_X - 1, GRID_OFFSET_Y - 1, 
                     GRID_WIDTH * GRID_SIZE + 2, GRID_HEIGHT * GRID_SIZE + 2), 
                    1)
    
    # Draw grid cells
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if grid[i][j]:
                pygame.draw.rect(screen, grid[i][j], 
                                (GRID_OFFSET_X + j * GRID_SIZE, 
                                 GRID_OFFSET_Y + i * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                (GRID_OFFSET_X + j * GRID_SIZE, 
                                 GRID_OFFSET_Y + i * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE), 
                                1)

def draw_tetromino(screen, tetromino):
    for i in range(len(tetromino.shape)):
        for j in range(len(tetromino.shape[i])):
            if tetromino.shape[i][j]:
                pygame.draw.rect(screen, tetromino.color, 
                                (GRID_OFFSET_X + (tetromino.x + j) * GRID_SIZE, 
                                 GRID_OFFSET_Y + (tetromino.y + i) * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                (GRID_OFFSET_X + (tetromino.x + j) * GRID_SIZE, 
                                 GRID_OFFSET_Y + (tetromino.y + i) * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE), 
                                1)

def draw_next_tetromino(screen, next_tetromino):
    # Draw "Next" text
    next_text = font.render("Next:", True, WHITE)
    screen.blit(next_text, (GRID_OFFSET_X + GRID_WIDTH * GRID_SIZE + 20, GRID_OFFSET_Y))
    
    # Calculate position for the next tetromino preview
    next_x = GRID_OFFSET_X + GRID_WIDTH * GRID_SIZE + 50
    next_y = GRID_OFFSET_Y + 40
    
    # Draw the next tetromino
    for i in range(len(next_tetromino.shape)):
        for j in range(len(next_tetromino.shape[i])):
            if next_tetromino.shape[i][j]:
                pygame.draw.rect(screen, next_tetromino.color, 
                                (next_x + j * GRID_SIZE, 
                                 next_y + i * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                (next_x + j * GRID_SIZE, 
                                 next_y + i * GRID_SIZE, 
                                 GRID_SIZE, GRID_SIZE), 
                                1)

def main():
    global grid
    grid = create_grid()
    
    current_tetromino = Tetromino()
    next_tetromino = Tetromino()
    
    fall_time = 0
    fall_speed = 0.5  # seconds
    level_time = 0
    score = 0
    level = 1
    
    running = True
    game_over = False
    paused = False
    
    while running:
        # Timing
        dt = clock.tick(60) / 1000  # Convert to seconds
        
        if not game_over and not paused:
            fall_time += dt
            level_time += dt
            
            # Increase speed every 60 seconds
            if level_time > 60:
                level_time = 0
                level += 1
                fall_speed *= 0.8
            
            # Move tetromino down
            if fall_time >= fall_speed:
                fall_time = 0
                current_tetromino.y += 1
                
                # If collision, place tetromino and create new one
                if current_tetromino.collision(current_tetromino.x, current_tetromino.y, grid):
                    current_tetromino.y -= 1
                    grid = merge_tetromino(current_tetromino, grid)
                    rows_cleared = clear_rows(grid)
                    score += rows_cleared * 100 * level
                    
                    current_tetromino = next_tetromino
                    next_tetromino = Tetromino()
                    
                    # Check if game over (collision at spawn)
                    if current_tetromino.collision(current_tetromino.x, current_tetromino.y, grid):
                        game_over = True
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_p:
                        paused = not paused
                        
                    if not paused:
                        if event.key == pygame.K_LEFT:
                            current_tetromino.x -= 1
                            if current_tetromino.collision(current_tetromino.x, current_tetromino.y, grid):
                                current_tetromino.x += 1
                                
                        elif event.key == pygame.K_RIGHT:
                            current_tetromino.x += 1
                            if current_tetromino.collision(current_tetromino.x, current_tetromino.y, grid):
                                current_tetromino.x -= 1
                                
                        elif event.key == pygame.K_DOWN:
                            current_tetromino.y += 1
                            if current_tetromino.collision(current_tetromino.x, current_tetromino.y, grid):
                                current_tetromino.y -= 1
                                
                        elif event.key == pygame.K_UP:
                            current_tetromino.rotate()
                            
                        elif event.key == pygame.K_SPACE:
                            # Hard drop
                            while not current_tetromino.collision(current_tetromino.x, current_tetromino.y + 1, grid):
                                current_tetromino.y += 1
                                score += 1
                else:
                    if event.key == pygame.K_r:
                        # Restart game
                        grid = create_grid()
                        current_tetromino = Tetromino()
                        next_tetromino = Tetromino()
                        fall_time = 0
                        fall_speed = 0.5
                        level_time = 0
                        score = 0
                        level = 1
                        game_over = False
        
        # Draw everything
        draw_grid(screen, grid)
        
        if not game_over:
            draw_tetromino(screen, current_tetromino)
            draw_next_tetromino(screen, next_tetromino)
            
            # Display score and level
            score_text = font.render(f"Score: {score}", True, WHITE)
            level_text = font.render(f"Level: {level}", True, WHITE)
            screen.blit(score_text, (20, 20))
            screen.blit(level_text, (20, 50))
            
            if paused:
                paused_text = font.render("PAUSED", True, WHITE)
                screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - paused_text.get_height() // 2))
        else:
            game_over_text = font.render("GAME OVER", True, WHITE)
            restart_text = font.render("Press R to restart", True, WHITE)
            
            screen.blit(game_over_text, 
                      (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                       SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(restart_text, 
                      (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                       SCREEN_HEIGHT // 2 + 30))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()