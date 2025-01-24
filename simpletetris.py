import pygame
import random

# Constants
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * BOARD_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * BOARD_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),    # Cyan (I)
    (255, 255, 0),    # Yellow (O)
    (128, 0, 128),    # Purple (T)
    (255, 165, 0),    # Orange (L)
    (0, 0, 255),      # Blue (J)
    (0, 255, 0),      # Green (S)
    (255, 0, 0)       # Red (Z)
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# Initialize pygame mixer for sound (uncomment to include clearline sound)
# pygame.mixer.init()
# Load the sound
# clearline_sound = pygame.mixer.Sound("tetrisclearline.mp3")


def rotate(shape):
    """Rotate a shape 90 degrees clockwise"""
    return [[shape[y][x] for y in range(len(shape))] 
            for x in range(len(shape[0])-1, -1, -1)]

def new_piece():
    """Create a new random piece"""
    shape = random.choice(SHAPES)
    color = COLORS[SHAPES.index(shape)]
    return {
        'shape': shape,
        'color': color,
        'x': BOARD_WIDTH // 2 - len(shape[0]) // 2,
        'y': 0
    }

def valid(board, piece, px, py):
    """Check if piece at position (px, py) is valid"""
    shape = piece['shape']
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                if not (0 <= x + px < BOARD_WIDTH and 0 <= y + py < BOARD_HEIGHT):
                    return False
                if board[y + py][x + px]:
                    return False
    return True

def merge_piece(board, piece):
    """Merge piece into the board"""
    shape = piece['shape']
    px = piece['x']
    py = piece['y']
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                board[py + y][px + x] = piece['color']

def clear_lines(board):
    """Clear completed lines and return number of cleared lines"""
    full_lines = []
    for y in range(BOARD_HEIGHT):
        if all(board[y]):
            full_lines.append(y)
    
    for y in full_lines:
        del board[y]
        board.insert(0, [0] * BOARD_WIDTH)

    # Play the sound when lines are cleared (uncomment to add sound)
    #  if full_lines:
    #    clearline_sound.play()  # Play the sound
    
    return len(full_lines)

def draw_board(screen, board):
    """Draw the board"""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x]:
                pygame.draw.rect(screen, board[y][x], 
                               (x*BLOCK_SIZE, y*BLOCK_SIZE,
                                BLOCK_SIZE-1, BLOCK_SIZE-1))

def draw_piece(screen, piece):
    """Draw the current piece"""
    shape = piece['shape']
    color = piece['color']
    px = piece['x']
    py = piece['y']
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                pygame.draw.rect(screen, color,
                               ((px + x) * BLOCK_SIZE,
                                (py + y) * BLOCK_SIZE,
                                BLOCK_SIZE-1, BLOCK_SIZE-1))

def draw_score(screen, score):
    """Draw the score on the screen"""
    font = pygame.font.SysFont("comicsans", 30)
    text = font.render(f"Score: {score}", True, WHITE)
    
    # Calculate the position for top-right corner
    text_width = text.get_width()
    text_height = text.get_height()
    x_position = SCREEN_WIDTH - text_width - 10  # 10 pixels padding from the right edge
    y_position = 10  # 10 pixels padding from the top edge
    
    screen.blit(text, (x_position, y_position))

def hard_drop(board, piece):
    """Instantly drop the piece to the bottom"""
    while valid(board, piece, piece['x'], piece['y'] + 1):
        piece['y'] += 1
    merge_piece(board, piece)
    return clear_lines(board)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    current_piece = new_piece()
    score = 0
    fall_time = 0
    fall_speed = 200  # milliseconds (normal fall speed)
    fast_fall_speed = 50  # milliseconds (accelerated fall speed when down arrow is pressed)
    
    # Hard drop logic
    hard_drop_ready = False  # Track if the first down arrow press has occurred
    hard_drop_duration = 500  # milliseconds (time to hold down arrow to trigger hard drop)
    hard_drop_start_time = 0  # Track when the down arrow is first held
    
    # Grace time logic
    grace_time_duration = 500  # milliseconds (time to adjust the piece after landing)
    grace_time_start = None  # Track when the piece lands
    
    running = True
    while running:
        screen.fill(BLACK)
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if valid(board, current_piece, current_piece['x'] - 1, current_piece['y']):
                        current_piece['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid(board, current_piece, current_piece['x'] + 1, current_piece['y']):
                        current_piece['x'] += 1
                elif event.key == pygame.K_DOWN:
                    if not hard_drop_ready:
                        # First press: move down once and prepare for hard drop
                        if valid(board, current_piece, current_piece['x'], current_piece['y'] + 1):
                            current_piece['y'] += 1
                        hard_drop_ready = True
                        hard_drop_start_time = pygame.time.get_ticks()
                elif event.key == pygame.K_UP:
                    rotated = rotate(current_piece['shape'])
                    original = current_piece['shape']
                    current_piece['shape'] = rotated
                    if not valid(board, current_piece, current_piece['x'], current_piece['y']):
                        current_piece['shape'] = original
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    # Reset hard drop logic when down arrow is released
                    hard_drop_ready = False
        
        # Check if down arrow is held for hard drop
        if hard_drop_ready and pygame.key.get_pressed()[pygame.K_DOWN]:
            hold_duration = pygame.time.get_ticks() - hard_drop_start_time
            if hold_duration >= hard_drop_duration:
                # Hard drop triggered
                lines = hard_drop(board, current_piece)
                score += lines * 100
                current_piece = new_piece()
                if not valid(board, current_piece, current_piece['x'], current_piece['y']):
                    # Game over
                    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
                    score = 0
                hard_drop_ready = False
        
        # Automatic falling (with acceleration if down arrow is pressed)
        delta_time = clock.get_rawtime()
        fall_time += delta_time
        current_fall_speed = fast_fall_speed if pygame.key.get_pressed()[pygame.K_DOWN] else fall_speed
        if fall_time >= current_fall_speed:
            fall_time = 0
            if valid(board, current_piece, current_piece['x'], current_piece['y'] + 1):
                current_piece['y'] += 1
            else:
                # Start grace time when the piece lands
                if grace_time_start is None:
                    grace_time_start = pygame.time.get_ticks()
        
        # Grace time logic
        if grace_time_start is not None:
            grace_time_elapsed = pygame.time.get_ticks() - grace_time_start
            if grace_time_elapsed >= grace_time_duration:
                # Grace time expired, lock the piece
                merge_piece(board, current_piece)
                lines = clear_lines(board)
                score += lines * 100
                current_piece = new_piece()
                if not valid(board, current_piece, current_piece['x'], current_piece['y']):
                    # Game over
                    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
                    score = 0
                grace_time_start = None  # Reset grace time
        
        # Draw everything
        draw_board(screen, board)
        draw_piece(screen, current_piece)
        draw_score(screen, score)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
