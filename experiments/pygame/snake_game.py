import pygame
import random
import sys
# Prompt: Create a snake game with PyGame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Direction constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.score = 0
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # Game over check - snake collides with itself
        if new_head in self.positions[1:]:
            return False
        
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            self.score += 1
        
        return True
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow_snake(self):
        self.grow = True
    
    def draw(self, surface):
        for i, position in enumerate(self.positions):
            color = GREEN if i == 0 else (0, 200, 0)  # Head is lighter green
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self, snake_positions):
        self.position = self.generate_position(snake_positions)
    
    def generate_position(self, snake_positions):
        while True:
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if position not in snake_positions:
                return position
    
    def update(self, snake_positions):
        self.position = self.generate_position(snake_positions)
    
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, BLACK, rect, 1)

def main():
    # Set up the game
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 25)
    
    # Game objects
    snake = Snake()
    food = Food(snake.positions)
    game_over = False
    
    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # Restart game
                        snake = Snake()
                        food = Food(snake.positions)
                        game_over = False
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
        
        if not game_over:
            # Update game state
            if not snake.update():
                game_over = True
            
            # Check for food collision
            if snake.get_head_position() == food.position:
                snake.grow_snake()
                food.update(snake.positions)
        
        # Draw everything
        screen.fill(WHITE)
        draw_grid(screen)
        snake.draw(screen)
        food.draw(screen)
        
        # Display score
        score_text = font.render(f'Score: {snake.score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        
        # Display game over message
        if game_over:
            game_over_text = font.render('Game Over! Press R to restart', True, BLACK)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(game_over_text, text_rect)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()