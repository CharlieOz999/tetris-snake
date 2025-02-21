# Tetris Snake Game

A unique fusion of classic Snake and Tetris gameplay mechanics. Navigate your snake to eat falling Tetris blocks while avoiding collisions with walls, stone blocks, and your own tail.

## Features

- Classic Snake movement with arrow key controls
- Tetris-style falling blocks with all 7 classic shapes (I, O, T, L, J, S, Z)
- Multiple blocks falling simultaneously
- Warning indicators for upcoming blocks
- Blocks can rest on the snake's tail
- Score system based on block sizes
- Game over on wall collision or self-collision
- Spacebar to restart after game over

## Requirements

- Python 3.9+
- Pygame 2.5.2

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/tetris-snake.git
cd tetris-snake
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python tetris_snake.py
```

2. Controls:
- Arrow keys to move the snake
- Spacebar to restart after game over

3. Gameplay:
- Guide your snake to eat the falling colored blocks
- Blocks turn to stone (gray) when they hit the bottom
- Game ends if you hit a wall, stone block, or your own tail
- Watch for the red warning indicators showing where blocks will fall

## License

MIT License