import pygame
import sys

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 19
STONE_SIZE = 28
GRID_MARGIN = 30
LINE_COLOR = (0, 0, 0)
BOARD_COLOR = (200, 150, 80)
BLACK_STONE = (0, 0, 0)
WHITE_STONE = (255, 255, 255)

def grid_to_screen(grid_x, grid_y):
    """Converts grid coordinates to screen coordinates."""
    screen_x = GRID_MARGIN + grid_x * (WIDTH - 2 * GRID_MARGIN) / (GRID_SIZE - 1)
    screen_y = GRID_MARGIN + grid_y * (HEIGHT - 2 * GRID_MARGIN) / (GRID_SIZE - 1)
    return screen_x, screen_y

def screen_to_grid(screen_x, screen_y):
    """Converts screen coordinates to grid coordinates."""
    grid_x = round((screen_x - GRID_MARGIN) * (GRID_SIZE - 1) / (WIDTH - 2 * GRID_MARGIN))
    grid_y = round((screen_y - GRID_MARGIN) * (GRID_SIZE - 1) / (HEIGHT - 2 * GRID_MARGIN))
    return grid_x, grid_y

def draw_board(screen):
    """Draws the Go board."""
    screen.fill(BOARD_COLOR)
    for i in range(GRID_SIZE):
        start_x, start_y = grid_to_screen(i, 0)
        end_x, end_y = grid_to_screen(i, GRID_SIZE - 1)
        pygame.draw.line(screen, LINE_COLOR, (start_x, start_y), (end_x, end_y))

        start_x, start_y = grid_to_screen(0, i)
        end_x, end_y = grid_to_screen(GRID_SIZE - 1, i)
        pygame.draw.line(screen, LINE_COLOR, (start_x, start_y), (end_x, end_y))

def draw_stones(screen, board_state):
    """Draws the stones on the board."""
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if board_state[y][x] == 1:  # Black stone
                screen_x, screen_y = grid_to_screen(x, y)
                pygame.draw.circle(screen, BLACK_STONE, (screen_x, screen_y), STONE_SIZE // 2)
            elif board_state[y][x] == 2:  # White stone
                screen_x, screen_y = grid_to_screen(x, y)
                pygame.draw.circle(screen, WHITE_STONE, (screen_x, screen_y), STONE_SIZE // 2)

def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Go Game")

    board_state = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # 0: empty, 1: black, 2: white
    current_player = 1  # 1: black, 2: white

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = screen_to_grid(mouse_x, mouse_y)

                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and board_state[grid_y][grid_x] == 0:
                    board_state[grid_y][grid_x] = current_player
                    current_player = 3 - current_player  # Switch players (1 -> 2, 2 -> 1)

        draw_board(screen)
        draw_stones(screen, board_state)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()