# level.py
import random
import math
import pygame
from settings import WIDTH, HEIGHT, LEVEL_CELL_SIZE, MIN_PATH_CELLS


def get_cell_barriers(g_rect, pad=10, thick=10):
    left_barrier = pygame.Rect(g_rect.left - pad - thick, g_rect.top - pad, thick, g_rect.height + 2 * pad)
    right_barrier = pygame.Rect(g_rect.right + pad, g_rect.top - pad, thick, g_rect.height + 2 * pad)
    top_barrier = pygame.Rect(g_rect.left - pad, g_rect.top - pad - thick, g_rect.width + 2 * pad, thick)
    bottom_barrier = pygame.Rect(g_rect.left - pad, g_rect.bottom + pad, g_rect.width + 2 * pad, thick)
    return [left_barrier, right_barrier, top_barrier, bottom_barrier]


def generate_level(red_rect):
    """
    Generates a level by creating a list of obstacles and a green target rectangle.
    The obstacles are randomly placed, ensuring they don't overlap with an inflated red_rect
    and that the green block (50x50) can be placed without conflicts.

    Returns:
        obstacles (list of pygame.Rect): The list of obstacle rectangles.
        green_rect (pygame.Rect): The rectangle for the green block.
    """
    max_attempts = 30
    # Inflate red_rect to create a clearance area around the red block.
    red_clearance = red_rect.inflate(10, 10)

    for _ in range(max_attempts):
        num_obstacles = random.randint(20, 35)
        obstacles = []
        while len(obstacles) < num_obstacles:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                obs_WIDTH = random.randint(80, 250)
                obs_HEIGHT = 30
            else:
                obs_WIDTH = 30
                obs_HEIGHT = random.randint(80, 250)
            obs_x = random.randint(0, WIDTH - obs_WIDTH)
            obs_y = random.randint(0, HEIGHT - obs_HEIGHT)
            new_obs = pygame.Rect(obs_x, obs_y, obs_WIDTH, obs_HEIGHT)
            if not new_obs.colliderect(red_clearance) and not any(new_obs.colliderect(obs) for obs in obstacles):
                obstacles.append(new_obs)

        # Attempt to place the green block (50x50) within safe boundaries.
        green_size = 50
        barrier_padding = 10
        barrier_thickness = 10
        min_green_x = barrier_padding + barrier_thickness
        max_green_x = WIDTH - green_size - (barrier_padding + barrier_thickness)
        min_green_y = barrier_padding + barrier_thickness
        max_green_y = HEIGHT - green_size - (barrier_padding + barrier_thickness)
        green_rect = None
        for _ in range(300):
            candidate_green = pygame.Rect(
                random.randint(min_green_x, max_green_x),
                random.randint(min_green_y, max_green_y),
                green_size, green_size
            )
            cell_barriers = get_cell_barriers(candidate_green, pad=barrier_padding, thick=barrier_thickness)
            conflict = any(candidate_green.colliderect(obs) for obs in obstacles) or \
                       any(candidate_green.colliderect(barrier) for barrier in cell_barriers)
            if not conflict:
                green_rect = candidate_green
                break
        if green_rect:
            return obstacles, green_rect
    raise RuntimeError("Couldn't generate a valid level.")


def bfs_path_length(start, goal, obstacles, cell_size=LEVEL_CELL_SIZE):
    """
    Estimates the path length from 'start' to 'goal' using BFS on a grid.
    The grid is defined by 'cell_size' and obstacles are taken into account.

    Returns:
        int: The number of steps from start to goal, or None if no path exists.
    """
    cols = WIDTH // cell_size
    rows = HEIGHT // cell_size
    start_cell = (start[0] // cell_size, start[1] // cell_size)
    goal_cell = (goal[0] // cell_size, goal[1] // cell_size)
    from collections import deque
    queue = deque()
    queue.append((start_cell, 0))
    visited = {start_cell}
    while queue:
        (c, r), dist = queue.popleft()
        if (c, r) == goal_cell:
            return dist
        for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nc, nr = c + dc, r + dr
            if 0 <= nc < cols and 0 <= nr < rows and (nc, nr) not in visited:
                center_x = nc * cell_size + cell_size // 2
                center_y = nr * cell_size + cell_size // 2
                if not any(obs.collidepoint(center_x, center_y) for obs in obstacles):
                    visited.add((nc, nr))
                    queue.append(((nc, nr), dist + 1))
    return None


def generate_candidate_level(red_rect, candidate_attempts=10):
    """
    Attempts to generate multiple candidate levels and selects the one with the shortest
    valid path from the red block to the green block.

    Returns:
        tuple: (obstacles, green_rect) of the best candidate.
    """
    candidates = []
    for _ in range(candidate_attempts):
        try:
            obstacles_candidate, green_rect_candidate = generate_level(red_rect)
        except RuntimeError:
            continue
        start = red_rect.center
        goal = green_rect_candidate.center
        path_length = bfs_path_length(start, goal, obstacles_candidate)
        if path_length is None:
            continue
        candidates.append((obstacles_candidate, green_rect_candidate, path_length))
    if not candidates:
        raise RuntimeError("Couldn't generate any valid candidate levels.")
    best_candidate = min(candidates, key=lambda x: x[2])
    print("Selected candidate with path length:", best_candidate[2])
    return best_candidate[0], best_candidate[1]