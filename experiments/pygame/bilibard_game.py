import pygame
import sys
import math
import random
def main():
    # Initialize pygame
    pygame.init()

    # Constants
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 100, 0)
    BROWN = (139, 69, 19)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    FRICTION = 0.99

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Billiards Game")
    clock = pygame.time.Clock()

    class Ball:
        def __init__(self, x, y, radius, color, is_cue=False):
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.is_cue = is_cue
            self.vx = 0
            self.vy = 0
            self.potted = False
        
        def update(self):
            # Apply friction
            self.vx *= FRICTION
            self.vy *= FRICTION
            
            # Update position
            self.x += self.vx
            self.y += self.vy
            
            # Stop if very slow
            if abs(self.vx) < 0.1 and abs(self.vy) < 0.1:
                self.vx = 0
                self.vy = 0
            
            # Boundary collision
            if self.x - self.radius < 100:
                self.x = 100 + self.radius
                self.vx = -self.vx * 0.8
            elif self.x + self.radius > WIDTH - 100:
                self.x = WIDTH - 100 - self.radius
                self.vx = -self.vx * 0.8
                
            if self.y - self.radius < 100:
                self.y = 100 + self.radius
                self.vy = -self.vy * 0.8
            elif self.y + self.radius > HEIGHT - 100:
                self.y = HEIGHT - 100 - self.radius
                self.vy = -self.vy * 0.8
        
        def draw(self, screen):
            if not self.potted:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
                if self.is_cue:
                    pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 5)
        
        def distance(self, other):
            return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
        def collide(self, other):
            if self.potted or other.potted:
                return False
                
            # Check if the balls are close enough to collide
            dist = self.distance(other)
            if dist < self.radius + other.radius:
                # Normal vector
                nx = (other.x - self.x) / dist
                ny = (other.y - self.y) / dist
                
                # Relative velocity
                dvx = other.vx - self.vx
                dvy = other.vy - self.vy
                
                # Dot product (impulse)
                dp = dvx * nx + dvy * ny
                
                # If the balls are moving away from each other, no collision response
                if dp > 0:
                    return False
                    
                # Collision response
                impulse = 1.8 * dp  # Slightly bouncy
                
                # Apply impulse
                self.vx += impulse * nx
                self.vy += impulse * ny
                other.vx -= impulse * nx
                other.vy -= impulse * ny
                
                # Move balls apart to prevent sticking
                overlap = (self.radius + other.radius - dist) / 2
                self.x -= overlap * nx
                self.y -= overlap * ny
                other.x += overlap * nx
                other.y += overlap * ny
                
                return True
            return False
        
        def check_pocket(self, pockets):
            if self.potted:
                return False
                
            for pocket in pockets:
                dist = math.sqrt((self.x - pocket[0])**2 + (self.y - pocket[1])**2)
                if dist < 20:  # Pocket radius
                    self.potted = True
                    return True
            return False

    class Cue:
        def __init__(self, ball):
            self.ball = ball
            self.power = 0
            self.max_power = 20
            self.angle = 0
            self.pulling = False
            self.length = 150
        
        def update(self, mouse_pos):
            if not self.ball.potted and (self.ball.vx == 0 and self.ball.vy == 0):
                dx = mouse_pos[0] - self.ball.x
                dy = mouse_pos[1] - self.ball.y
                self.angle = math.atan2(dy, dx)
                
                if self.pulling:
                    # Calculate distance for power
                    dist = math.sqrt(dx**2 + dy**2)
                    self.power = min(dist / 10, self.max_power)
        
        def draw(self, screen):
            if not self.ball.potted and (self.ball.vx == 0 and self.ball.vy == 0) and not self.pulling:
                # Draw cue line
                end_x = self.ball.x - math.cos(self.angle) * self.length
                end_y = self.ball.y - math.sin(self.angle) * self.length
                pygame.draw.line(screen, BROWN, (self.ball.x, self.ball.y), (end_x, end_y), 5)
            
            elif self.pulling:
                # Draw power line
                power_line_length = self.power * 10
                end_x = self.ball.x - math.cos(self.angle) * power_line_length
                end_y = self.ball.y - math.sin(self.angle) * power_line_length
                pygame.draw.line(screen, RED, (self.ball.x, self.ball.y), (end_x, end_y), 2)
        
        def shoot(self):
            if self.pulling and not self.ball.potted:
                self.ball.vx = math.cos(self.angle) * -self.power
                self.ball.vy = math.sin(self.angle) * -self.power
                self.pulling = False
                self.power = 0
                return True
            return False

    # Create balls
    balls = []
    cue_ball = Ball(600, HEIGHT/2, 15, WHITE, is_cue=True)
    balls.append(cue_ball)

    # Create a triangle formation for the colored balls
    start_x = 200
    start_y = HEIGHT/2
    colors = [RED, YELLOW, BLUE, RED, YELLOW, BLUE, RED, YELLOW, BLUE]
    row_sizes = [1, 2, 3, 4]
    idx = 0

    for row, size in enumerate(row_sizes):
        for col in range(size):
            if idx < len(colors):
                x = start_x + row * 30 * math.sqrt(3)/2
                y = start_y - (size-1) * 15 + col * 30
                balls.append(Ball(x, y, 15, colors[idx]))
                idx += 1

    # Create cue
    cue = Cue(cue_ball)

    # Create pockets
    pockets = [
        (100, 100), (WIDTH-100, 100),
        (100, HEIGHT/2), (WIDTH-100, HEIGHT/2),
        (100, HEIGHT-100), (WIDTH-100, HEIGHT-100)
    ]

    # Game state
    game_over = False
    all_stopped = True
    score = 0

    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and all_stopped:
                cue.pulling = True
            
            if event.type == pygame.MOUSEBUTTONUP and cue.pulling:
                if cue.shoot():
                    all_stopped = False
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update
        all_stopped = True
        for ball in balls:
            if not ball.potted:
                ball.update()
                if abs(ball.vx) > 0.1 or abs(ball.vy) > 0.1:
                    all_stopped = False
        
        # Update cue
        cue.update(mouse_pos)
        
        # Check for collisions
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                balls[i].collide(balls[j])
        
        # Check for pocketing
        for ball in balls:
            if ball.check_pocket(pockets):
                if not ball.is_cue:
                    score += 1
                else:
                    game_over = True
        
        # Check if all colored balls are potted
        if all(ball.potted or ball.is_cue for ball in balls):
            game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw table
        pygame.draw.rect(screen, GREEN, (90, 90, WIDTH-180, HEIGHT-180))
        pygame.draw.rect(screen, BROWN, (90, 90, WIDTH-180, HEIGHT-180), 10)
        
        # Draw pockets
        for pocket in pockets:
            pygame.draw.circle(screen, BLACK, pocket, 20)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        # Draw cue
        if all_stopped:
            cue.draw(screen)
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Game over
        if game_over:
            game_over_text = font.render("Game Over! Press Q to quit or R to restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH/2 - 200, 20))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                running = False
            if keys[pygame.K_r]:
                # Reset game
                balls = []
                cue_ball = Ball(600, HEIGHT/2, 15, WHITE, is_cue=True)
                balls.append(cue_ball)
                
                # Recreate triangle formation
                idx = 0
                for row, size in enumerate(row_sizes):
                    for col in range(size):
                        if idx < len(colors):
                            x = start_x + row * 30 * math.sqrt(3)/2
                            y = start_y - (size-1) * 15 + col * 30
                            balls.append(Ball(x, y, 15, colors[idx]))
                            idx += 1
                
                cue = Cue(cue_ball)
                game_over = False
                all_stopped = True
                score = 0
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()