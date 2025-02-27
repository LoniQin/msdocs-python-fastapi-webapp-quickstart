import pygame
import math
import sys
from collections import deque

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Game state
class GameState:
    def __init__(self):
        self.money = 100
        self.lives = 20
        self.wave = 0
        self.game_over = False
        self.wave_in_progress = False
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.path = []
        self.spawn_timer = 0
        self.enemy_queue = deque()
        
# Tower class
class Tower:
    def __init__(self, x, y, tower_type="basic"):
        self.x = x
        self.y = y
        self.range = 120
        self.attack_speed = 1.0  # Attacks per second
        self.damage = 10
        self.last_shot = 0
        self.tower_type = tower_type
        self.target = None
        self.level = 1
        
        # Set tower properties based on type
        if tower_type == "basic":
            self.cost = 50
            self.color = BLUE
            self.range = 120
        elif tower_type == "sniper":
            self.cost = 100
            self.color = RED
            self.range = 200
            self.attack_speed = 0.5
            self.damage = 25
        elif tower_type == "rapid":
            self.cost = 75
            self.color = GREEN
            self.range = 100
            self.attack_speed = 2.0
            self.damage = 5
    
    def upgrade(self):
        self.level += 1
        self.range *= 1.2
        self.damage *= 1.5
        self.attack_speed *= 1.2
        return self.level * self.cost // 2  # Return upgrade cost
    
    def can_shoot(self, current_time):
        return current_time - self.last_shot > 1000 / self.attack_speed
        
    def find_target(self, enemies, current_time):
        if not self.can_shoot(current_time):
            return None
            
        closest = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if dist <= self.range and dist < min_dist:
                min_dist = dist
                closest = enemy
                
        return closest
    
    def shoot(self, current_time, enemies):
        self.target = self.find_target(enemies, current_time)
        if self.target:
            self.last_shot = current_time
            return Projectile(self.x, self.y, self.target, self.damage)
        return None
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), GRID_SIZE // 2)
        # Draw tower level indicator
        level_text = pygame.font.SysFont(None, 20).render(str(self.level), True, WHITE)
        screen.blit(level_text, (self.x - 5, self.y - 10))
        
        # Draw range circle (transparent)
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (128, 128, 128, 64), (self.range, self.range), self.range)
        screen.blit(range_surface, (self.x - self.range, self.y - self.range))

# Enemy class
class Enemy:
    def __init__(self, path, enemy_type="normal"):
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.speed = 1.0
        self.health = 30
        self.max_health = 30
        self.reward = 10
        self.enemy_type = enemy_type
        
        # Set enemy properties based on type
        if enemy_type == "normal":
            self.color = RED
            self.speed = 1.0
            self.health = 30
            self.max_health = 30
            self.reward = 10
        elif enemy_type == "fast":
            self.color = GREEN
            self.speed = 2.0
            self.health = 15
            self.max_health = 15
            self.reward = 15
        elif enemy_type == "tank":
            self.color = GRAY
            self.speed = 0.5
            self.health = 100
            self.max_health = 100
            self.reward = 25
        
    def move(self):
        if self.path_index >= len(self.path) - 1:
            return True  # Reached end of path
            
        target_x, target_y = self.path[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
        else:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
            
        return False  # Still on path
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
        
    def draw(self, screen):
        # Draw enemy
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), GRID_SIZE // 3)
        
        # Draw health bar
        bar_width = GRID_SIZE
        bar_height = 5
        health_percentage = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, RED, (int(self.x) - bar_width//2, int(self.y) - 20, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (int(self.x) - bar_width//2, int(self.y) - 20, int(bar_width * health_percentage), bar_height))

# Projectile class
class Projectile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5.0
        self.damage = damage
        self.hit = False
        
    def move(self):
        if self.hit or not self.target:
            return True  # Remove projectile
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            # Hit target
            self.hit = True
            return self.target.take_damage(self.damage)
        else:
            # Move towards target
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
            return False
            
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)

# Game setup
def create_path():
    # Create a simple path from left to right with a few turns
    path = []
    # Start at the left edge
    x, y = 0, SCREEN_HEIGHT // 2
    path.append((x, y))
    
    # Add some waypoints to create a path
    waypoints = [
        (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4),
        (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT * 3 // 4),
        (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH, SCREEN_HEIGHT // 2)
    ]
    
    for waypoint in waypoints:
        path.append(waypoint)
        
    return path

def spawn_wave(game_state):
    game_state.wave += 1
    wave_size = 5 + game_state.wave * 2
    
    # Mix enemy types based on wave number
    for i in range(wave_size):
        if game_state.wave >= 3 and i % 5 == 0:
            enemy_type = "tank"
        elif game_state.wave >= 2 and i % 3 == 0:
            enemy_type = "fast"
        else:
            enemy_type = "normal"
            
        # Add enemies to the queue
        game_state.enemy_queue.append(enemy_type)
    
    game_state.wave_in_progress = True
    game_state.spawn_timer = 0

def update_game(game_state, current_time):
    # Spawn enemies from queue
    if game_state.wave_in_progress and game_state.enemy_queue:
        game_state.spawn_timer += 1
        if game_state.spawn_timer >= 60:  # Spawn enemy every second
            enemy_type = game_state.enemy_queue.popleft()
            game_state.enemies.append(Enemy(game_state.path.copy(), enemy_type))
            game_state.spawn_timer = 0
            
    # If no enemies in queue or on screen, wave is complete
    if not game_state.enemy_queue and not game_state.enemies:
        game_state.wave_in_progress = False
    
    # Update enemies
    enemies_to_remove = []
    for i, enemy in enumerate(game_state.enemies):
        reached_end = enemy.move()
        if reached_end:
            game_state.lives -= 1
            enemies_to_remove.append(i)
            if game_state.lives <= 0:
                game_state.game_over = True
    
    # Remove enemies that reached the end
    for i in sorted(enemies_to_remove, reverse=True):
        game_state.enemies.pop(i)
    
    # Let towers shoot
    for tower in game_state.towers:
        projectile = tower.shoot(current_time, game_state.enemies)
        if projectile:
            game_state.projectiles.append(projectile)
    
    # Update projectiles
    projectiles_to_remove = []
    for i, projectile in enumerate(game_state.projectiles):
        killed = projectile.move()
        if projectile.hit:
            projectiles_to_remove.append(i)
            if killed:
                # Enemy died, remove it and give player money
                enemy_index = game_state.enemies.index(projectile.target)
                reward = game_state.enemies[enemy_index].reward
                game_state.money += reward
                game_state.enemies.pop(enemy_index)
    
    # Remove projectiles that hit
    for i in sorted(projectiles_to_remove, reverse=True):
        game_state.projectiles.pop(i)

def draw_game(screen, game_state, tower_option, mouse_pos):
    # Draw background
    screen.fill(WHITE)
    
    # Draw path
    for i in range(len(game_state.path) - 1):
        pygame.draw.line(screen, BROWN, game_state.path[i], game_state.path[i+1], 5)
    
    # Draw grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.rect(screen, LIGHT_GRAY, (x, y, GRID_SIZE, GRID_SIZE), 1)
    
    # Draw enemies
    for enemy in game_state.enemies:
        enemy.draw(screen)
    
    # Draw towers
    for tower in game_state.towers:
        tower.draw(screen)
    
    # Draw projectiles
    for projectile in game_state.projectiles:
        projectile.draw(screen)
    
    # Draw tower placement preview
    if tower_option:
        mouse_x, mouse_y = mouse_pos
        grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        
        # Check if position is valid for tower placement
        valid_pos = True
        for tower in game_state.towers:
            if tower.x == grid_x and tower.y == grid_y:
                valid_pos = False
                break
                
        # Check if too close to path
        for i in range(len(game_state.path) - 1):
            x1, y1 = game_state.path[i]
            x2, y2 = game_state.path[i+1]
            
            # Simple distance check to line segments
            dist = point_to_line_distance(grid_x, grid_y, x1, y1, x2, y2)
            if dist < GRID_SIZE:
                valid_pos = False
                break
        
        color = GREEN if valid_pos else RED
        pygame.draw.circle(screen, color, (grid_x, grid_y), GRID_SIZE // 2, 2)
        
        # Show tower range
        range_val = 120  # Default range
        if tower_option == "sniper":
            range_val = 200
        elif tower_option == "rapid":
            range_val = 100
            
        range_surface = pygame.Surface((range_val * 2, range_val * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (128, 128, 128, 64), (range_val, range_val), range_val)
        screen.blit(range_surface, (grid_x - range_val, grid_y - range_val))
    
    # Draw UI
    font = pygame.font.SysFont(None, 36)
    money_text = font.render(f"Money: ${game_state.money}", True, BLACK)
    lives_text = font.render(f"Lives: {game_state.lives}", True, BLACK)
    wave_text = font.render(f"Wave: {game_state.wave}", True, BLACK)
    
    screen.blit(money_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(wave_text, (10, 90))
    
    # Draw tower selection buttons
    pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 180, 10, 50, 50))
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 120, 10, 50, 50))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 60, 10, 50, 50))
    
    small_font = pygame.font.SysFont(None, 20)
    basic_text = small_font.render("Basic", True, WHITE)
    sniper_text = small_font.render("Sniper", True, WHITE)
    rapid_text = small_font.render("Rapid", True, WHITE)
    
    screen.blit(basic_text, (SCREEN_WIDTH - 180 + 5, 20))
    screen.blit(sniper_text, (SCREEN_WIDTH - 120 + 5, 20))
    screen.blit(rapid_text, (SCREEN_WIDTH - 60 + 5, 20))
    
    cost_basic = small_font.render("$50", True, WHITE)
    cost_sniper = small_font.render("$100", True, WHITE)
    cost_rapid = small_font.render("$75", True, WHITE)
    
    screen.blit(cost_basic, (SCREEN_WIDTH - 180 + 15, 40))
    screen.blit(cost_sniper, (SCREEN_WIDTH - 120 + 10, 40))
    screen.blit(cost_rapid, (SCREEN_WIDTH - 60 + 15, 40))
    
    # Draw next wave button if wave is not in progress
    if not game_state.wave_in_progress:
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40))
        next_wave_text = font.render("Next Wave", True, WHITE)
        screen.blit(next_wave_text, (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 45))
    
    # Draw game over message
    if game_state.game_over:
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 36))
        
        restart_font = pygame.font.SysFont(None, 36)
        restart_text = restart_font.render("Press R to restart", True, BLACK)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 36))

def point_to_line_distance(px, py, x1, y1, x2, y2):
    # Calculate perpendicular distance from point to line segment
    line_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if line_len == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

def main():
    # Game setup
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()
    
    game_state = GameState()
    game_state.path = create_path()
    
    tower_option = None
    selected_tower = None
    
    # Game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state.game_over:
                    # Restart game
                    game_state = GameState()
                    game_state.path = create_path()
                    tower_option = None
                    selected_tower = None
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    # Check if clicked on tower selection
                    if mouse_y <= 60:
                        if SCREEN_WIDTH - 180 <= mouse_x <= SCREEN_WIDTH - 130:
                            tower_option = "basic"
                        elif SCREEN_WIDTH - 120 <= mouse_x <= SCREEN_WIDTH - 70:
                            tower_option = "sniper"
                        elif SCREEN_WIDTH - 60 <= mouse_x <= SCREEN_WIDTH - 10:
                            tower_option = "rapid"
                    
                    # Check if clicked on next wave button
                    if not game_state.wave_in_progress and not game_state.game_over:
                        if SCREEN_WIDTH - 150 <= mouse_x <= SCREEN_WIDTH - 10 and SCREEN_HEIGHT - 50 <= mouse_y <= SCREEN_HEIGHT - 10:
                            spawn_wave(game_state)
                    
                    # Place tower if tower option is selected
                    if tower_option and not game_state.game_over:
                        grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                        grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                        
                        # Check if position is valid
                        valid_pos = True
                        for tower in game_state.towers:
                            if tower.x == grid_x and tower.y == grid_y:
                                valid_pos = False
                                break
                                
                        # Check if too close to path
                        for i in range(len(game_state.path) - 1):
                            x1, y1 = game_state.path[i]
                            x2, y2 = game_state.path[i+1]
                            dist = point_to_line_distance(grid_x, grid_y, x1, y1, x2, y2)
                            if dist < GRID_SIZE:
                                valid_pos = False
                                break
                        
                        # Check if enough money
                        tower_cost = 50
                        if tower_option == "sniper":
                            tower_cost = 100
                        elif tower_option == "rapid":
                            tower_cost = 75
                            
                        if valid_pos and game_state.money >= tower_cost:
                            new_tower = Tower(grid_x, grid_y, tower_option)
                            game_state.towers.append(new_tower)
                            game_state.money -= tower_cost
                            tower_option = None  # Reset tower option after placement
                    
                    # Select tower for upgrade
                    selected_tower = None
                    for tower in game_state.towers:
                        if math.sqrt((tower.x - mouse_x) ** 2 + (tower.y - mouse_y) ** 2) <= GRID_SIZE // 2:
                            selected_tower = tower
                            break
                            
                elif event.button == 3:  # Right click
                    # Upgrade selected tower
                    if selected_tower and not game_state.game_over:
                        upgrade_cost = selected_tower.level * selected_tower.cost // 2
                        if game_state.money >= upgrade_cost:
                            game_state.money -= upgrade_cost
                            selected_tower.upgrade()
                    
                    # Cancel tower selection/placement
                    tower_option = None
                    selected_tower = None
        
        if not game_state.game_over:
            update_game(game_state, current_time)
        
        draw_game(screen, game_state, tower_option, mouse_pos)
        
        # Draw selection highlight for selected tower
        if selected_tower:
            pygame.draw.circle(screen, YELLOW, (selected_tower.x, selected_tower.y), GRID_SIZE // 2 + 2, 2)
            
            # Draw upgrade info
            upgrade_cost = selected_tower.level * selected_tower.cost // 2
            font = pygame.font.SysFont(None, 20)
            upgrade_text = font.render(f"Upgrade: ${upgrade_cost}", True, BLACK)
            screen.blit(upgrade_text, (selected_tower.x - 40, selected_tower.y + 30))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()