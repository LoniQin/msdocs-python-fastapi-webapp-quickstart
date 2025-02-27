import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 5
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
FLOOR_HEIGHT = 100
BIRD_START_X = 80
BIRD_START_Y = 250

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 32)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(BIRD_START_X, BIRD_START_Y))
        self.velocity = 0
        
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        
        # Keep the bird on screen
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity = 0
            
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def reset(self):
        self.rect.center = (BIRD_START_X, BIRD_START_Y)
        self.velocity = 0

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.Surface((60, SCREEN_HEIGHT))
        self.image.fill(GREEN)
        
        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.rect = self.image.get_rect(midtop=(x, y))
        else:
            self.rect = self.image.get_rect(midbottom=(x, y))
            
    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()

class Floor(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, FLOOR_HEIGHT))
        self.image.fill((139, 69, 19))  # Brown color
        self.rect = self.image.get_rect(topleft=(x, SCREEN_HEIGHT - FLOOR_HEIGHT))
        
    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right <= 0:
            self.rect.left = SCREEN_WIDTH

def create_floor():
    floor_sprites = pygame.sprite.Group()
    for i in range(2):
        floor = Floor(i * SCREEN_WIDTH)
        floor_sprites.add(floor)
    return floor_sprites

def create_pipe():
    random_height = random.randint(100, 350)
    top_pipe = Pipe(SCREEN_WIDTH + 100, random_height - PIPE_GAP // 2, -1)
    bottom_pipe = Pipe(SCREEN_WIDTH + 100, random_height + PIPE_GAP // 2, 1)
    return top_pipe, bottom_pipe

def check_collision(bird, pipes, floor):
    # Check if the bird hit the floor
    if bird.rect.bottom >= SCREEN_HEIGHT - FLOOR_HEIGHT:
        return True
    
    # Check pipe collisions
    if pygame.sprite.spritecollide(bird, pipes, False):
        return True
    
    return False

def display_score(score):
    score_surface = font.render(f'Score: {score}', True, BLACK)
    score_rect = score_surface.get_rect(topleft=(10, 10))
    screen.blit(score_surface, score_rect)

def display_game_over():
    game_over_surface = font.render('Game Over! Press R to restart', True, BLACK)
    game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(game_over_surface, game_over_rect)

def main():
    # Set up bird and pipe groups
    bird = Bird()
    bird_group = pygame.sprite.GroupSingle()
    bird_group.add(bird)
    
    pipe_group = pygame.sprite.Group()
    floor_group = create_floor()
    
    # Game variables
    score = 0
    game_active = True
    last_pipe = pygame.time.get_ticks()
    passed_pipes = []
    
    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird.flap()
                if event.key == pygame.K_SPACE and not game_active:
                    # Restart the game
                    game_active = True
                    pipe_group.empty()
                    bird.reset()
                    score = 0
                    passed_pipes = []
                if event.key == pygame.K_r and not game_active:
                    # Restart the game
                    game_active = True
                    pipe_group.empty()
                    bird.reset()
                    score = 0
                    passed_pipes = []
        
        screen.fill(SKY_BLUE)
        
        # Update game objects when game is active
        if game_active:
            # Bird
            bird_group.update()
            bird_group.draw(screen)
            
            # Pipes
            pipe_group.update()
            pipe_group.draw(screen)
            
            # Generate new pipes
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe > PIPE_FREQUENCY:
                top_pipe, bottom_pipe = create_pipe()
                pipe_group.add(top_pipe, bottom_pipe)
                last_pipe = current_time
            
            # Check for score
            for pipe in pipe_group:
                if pipe.rect.right < bird.rect.left and pipe not in passed_pipes:
                    passed_pipes.append(pipe)
                    if len(passed_pipes) % 2 == 0:  # Count pairs of pipes
                        score += 1
            
            # Floor
            floor_group.update()
            floor_group.draw(screen)
            
            # Check for collisions
            game_active = not check_collision(bird, pipe_group, floor_group)
            
        else:
            # Display game over screen
            display_game_over()
            floor_group.draw(screen)
        
        # Always display the score
        display_score(score)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()