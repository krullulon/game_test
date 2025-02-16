# settings.py
# Global configuration and constants for the game

# Screen dimensions and FPS
WIDTH = 1200
HEIGHT = 1000
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)

# Sprite and object sizes
RED_WIDTH = 55
RED_HEIGHT = 61
BLUE_SIZE = 30
SWITCH_SIZE = 30

# Game state identifiers
GAME_STATE_INSTRUCTIONS = "instructions"
GAME_STATE_PLAYING = "playing"
GAME_STATE_WIN = "win"
GAME_STATE_LOSE = "lose"

# Timer settings (in milliseconds)
SWITCH_TIMER_DURATION = 60000  # 60 seconds for switch timer

# Obstacle and hazard settings
PINK_DIAMETER = 40
PINK_SPEED = 1.7  # Matches red block's speed

# Level generation parameters
LEVEL_CELL_SIZE = 40  # Used for grid-based pathfinding
MIN_PATH_CELLS = 30   # Minimum cells required in path for a valid level

# Other settings can be added here as needed...