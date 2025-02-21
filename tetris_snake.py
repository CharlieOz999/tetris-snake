import pygame
import random
import sys
from enum import Enum
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 400
GRID_SIZE = 20
GRID_DIMENSION = WINDOW_SIZE // GRID_SIZE
FPS = 15
WARNING_TIME = 1.0
BLOCK_FALL_RATE = 2
SNAKE_MOVE_RATE = 1
MAX_BLOCKS = 3
NEW_BLOCK_CHANCE = 0.2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Tetris shapes (each shape is a list of relative coordinates)
SHAPES = {
    'I': [(0,0), (0,1), (0,2), (0,3)],
    'O': [(0,0), (1,0), (0,1), (1,1)],
    'T': [(0,0), (1,0), (2,0), (1,1)],
    'L': [(0,0), (0,1), (0,2), (1,2)],
    'J': [(1,0), (1,1), (1,2), (0,2)],
    'S': [(1,0), (2,0), (0,1), (1,1)],
    'Z': [(0,0), (1,0), (1,1), (2,1)]
}

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class TetrisBlock:
    def __init__(self):
        self.color = random.choice(COLORS)
        self.shape_name = random.choice(list(SHAPES.keys()))
        self.shape = SHAPES[self.shape_name]
        self.position = [random.randint(0, GRID_DIMENSION-3), -1]
        self.is_stone = False
        self.next_position = random.randint(0, GRID_DIMENSION-3)
        self.warning_start = time.time()
        self.is_resting = False
        self.is_falling = False

    def should_show_warning(self):
        return not self.is_falling and time.time() - self.warning_start < WARNING_TIME

    def get_positions(self):
        return [(self.position[0] + dx, self.position[1] + dy) for dx, dy in self.shape]

    def can_move_down(self, stacked_blocks, snake_body):
        # Check if any part of the block would go out of bounds
        for dx, dy in self.shape:
            next_y = self.position[1] + dy + 1
            if next_y >= GRID_DIMENSION:
                return False
            
            # Check if would hit a stacked block
            next_x = self.position[0] + dx
            if 0 <= next_y < GRID_DIMENSION and 0 <= next_x < GRID_DIMENSION:
                if stacked_blocks[next_y][next_x] is not None:
                    return False
                
        # Check if block would hit snake
        next_positions = [(self.position[0] + dx, self.position[1] + dy + 1) 
                         for dx, dy in self.shape]
        return not any(pos in snake_body for pos in next_positions)

    def will_hit_bottom(self):
        # Check if any part of the block would hit bottom after moving
        return any(self.position[1] + dy + 1 >= GRID_DIMENSION for dx, dy in self.shape)

    def will_hit_stacked_blocks(self, stacked_blocks):
        # Check if any part of the block would hit stacked blocks after moving
        for dx, dy in self.shape:
            next_y = self.position[1] + dy + 1
            next_x = self.position[0] + dx
            if 0 <= next_y < GRID_DIMENSION and 0 <= next_x < GRID_DIMENSION:
                if stacked_blocks[next_y][next_x] is not None:
                    return True
        return False

class Snake:
    def __init__(self):
        self.body = [(GRID_DIMENSION//2, GRID_DIMENSION//2)]
        self.direction = Direction.RIGHT
        self.grow = False

    def move(self):
        head = self.body[0]
        dx, dy = self.direction.value
        new_head = (head[0] + dx, head[1] + dy)
        
        if (new_head[0] < 0 or new_head[0] >= GRID_DIMENSION or 
            new_head[1] < 0 or new_head[1] >= GRID_DIMENSION):
            return False

        check_body = self.body[:-1] if not self.grow else self.body
        if new_head in check_body:
            return False
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False
        return True

    def check_collision(self, block):
        if block.is_stone:
            return False
        
        head = self.body[0]
        block_positions = block.get_positions()
        return head in block_positions

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Tetris Snake")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.blocks = [TetrisBlock()]
        self.score = 0
        self.game_over = False
        self.frame_count = 0
        self.stacked_blocks = [[None for _ in range(GRID_DIMENSION)] for _ in range(GRID_DIMENSION)]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_UP and self.snake.direction != Direction.DOWN:
                        self.snake.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.snake.direction != Direction.UP:
                        self.snake.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.snake.direction != Direction.RIGHT:
                        self.snake.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.snake.direction != Direction.LEFT:
                        self.snake.direction = Direction.RIGHT
                elif event.key == pygame.K_SPACE:
                    self.reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(WINDOW_SIZE//2 - 60, WINDOW_SIZE//2 + 50, 120, 40)
                if button_rect.collidepoint(mouse_pos):
                    self.reset_game()

    def update(self):
        if self.game_over:
            return

        self.frame_count += 1

        # Move snake more frequently than blocks
        if self.frame_count % SNAKE_MOVE_RATE == 0:
            if not self.snake.move():
                self.game_over = True
                return

            # Check collision with stacked blocks first
            head_x, head_y = self.snake.body[0]
            if 0 <= head_y < GRID_DIMENSION and 0 <= head_x < GRID_DIMENSION:
                if self.stacked_blocks[head_y][head_x] is not None:
                    self.game_over = True
                    return

            # Then check for collisions with any block
            for block in self.blocks[:]:
                if not block.is_stone and self.snake.check_collision(block):
                    self.score += len(block.shape) * 10
                    self.snake.grow = True
                    self.blocks.remove(block)
                    continue

        # Add new block if we're below maximum
        if len(self.blocks) < MAX_BLOCKS and random.random() < NEW_BLOCK_CHANCE:
            new_block = TetrisBlock()
            new_block.position[0] = new_block.next_position
            self.blocks.append(new_block)

        # Handle block movement
        for block in self.blocks[:]:
            if not block.is_stone:
                if not block.is_falling and time.time() - block.warning_start >= WARNING_TIME:
                    block.is_falling = True
                    block.position[1] = 0

                if block.is_falling and self.frame_count % BLOCK_FALL_RATE == 0:
                    # Check if block will hit bottom
                    if block.will_hit_bottom() or block.will_hit_stacked_blocks(self.stacked_blocks):
                        # Turn to stone
                        for dx, dy in block.shape:
                            x = block.position[0] + dx
                            y = block.position[1] + dy
                            if 0 <= y < GRID_DIMENSION and 0 <= x < GRID_DIMENSION:
                                self.stacked_blocks[y][x] = GRAY
                        self.blocks.remove(block)
                    elif not any((block.position[0] + dx, block.position[1] + dy + 1) in self.snake.body 
                               for dx, dy in block.shape):
                        # Only move down if not blocked by snake
                        block.position[1] += 1

    def draw(self):
        self.screen.fill(BLACK)

        # Draw stacked blocks first
        for y in range(GRID_DIMENSION):
            for x in range(GRID_DIMENSION):
                if self.stacked_blocks[y][x] is not None:
                    pygame.draw.rect(self.screen, self.stacked_blocks[y][x],
                                   (x * GRID_SIZE,
                                    y * GRID_SIZE,
                                    GRID_SIZE-2, GRID_SIZE-2))

        # Draw snake
        for segment in self.snake.body:
            pygame.draw.rect(self.screen, GREEN,
                           (segment[0] * GRID_SIZE,
                            segment[1] * GRID_SIZE,
                            GRID_SIZE-2, GRID_SIZE-2))

        # Draw falling blocks
        for block in self.blocks:
            # Draw warning indicator
            if block.should_show_warning():
                pygame.draw.rect(self.screen, GRAY,
                               (block.next_position * GRID_SIZE,
                                0,
                                GRID_SIZE-2, GRID_SIZE-2))

            # Draw actual block
            if block.is_falling:
                for dx, dy in block.shape:
                    x = (block.position[0] + dx) * GRID_SIZE
                    y = (block.position[1] + dy) * GRID_SIZE
                    if y >= 0:  # Only draw if visible
                        pygame.draw.rect(self.screen, block.color,
                                       (x, y, GRID_SIZE-2, GRID_SIZE-2))

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over!', True, WHITE)
            self.screen.blit(text, (WINDOW_SIZE//4, WINDOW_SIZE//2))
            
            # Draw restart button
            button_rect = pygame.Rect(WINDOW_SIZE//2 - 60, WINDOW_SIZE//2 + 50, 120, 40)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render('Restart', True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()