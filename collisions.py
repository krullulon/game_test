# collisions.py
import pygame
import math


def circle_rect_collision(circle_center, radius, rect):
    """
    Check if a circle collides with a rectangle.

    Parameters:
        circle_center (tuple): (x, y) coordinates of the circle's center.
        radius (float): Radius of the circle.
        rect (pygame.Rect): The rectangle.

    Returns:
        bool: True if the circle collides with the rectangle, False otherwise.
    """
    closest_x = max(rect.left, min(circle_center[0], rect.right))
    closest_y = max(rect.top, min(circle_center[1], rect.bottom))
    distance = math.hypot(circle_center[0] - closest_x, circle_center[1] - closest_y)
    return distance < radius


def resolve_red_collision(rect, obstacles):
    """
    Adjust the position of a rectangle to resolve collisions with any obstacles.

    The function iteratively moves the rectangle out of any overlapping obstacles.

    Parameters:
        rect (pygame.Rect): The rectangle (red block) to adjust.
        obstacles (list of pygame.Rect): List of obstacle rectangles.

    Returns:
        pygame.Rect: The adjusted rectangle with collisions resolved.
    """
    collision_found = True
    iterations = 0
    max_iterations = 10  # Prevent infinite loops
    while collision_found and iterations < max_iterations:
        collision_found = False
        for obs in obstacles:
            if rect.colliderect(obs):
                # Calculate overlap in both x and y directions.
                overlap_x = min(rect.right, obs.right) - max(rect.left, obs.left)
                overlap_y = min(rect.bottom, obs.bottom) - max(rect.top, obs.top)
                # Move in the direction of the smallest overlap.
                if overlap_x < overlap_y:
                    if rect.centerx < obs.centerx:
                        rect.x -= overlap_x
                    else:
                        rect.x += overlap_x
                else:
                    if rect.centery < obs.centery:
                        rect.y -= overlap_y
                    else:
                        rect.y += overlap_y
                collision_found = True
                break  # Check again after adjustment
        iterations += 1
    return rect