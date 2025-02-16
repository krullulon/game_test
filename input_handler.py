# input_handler.py
import pygame


def get_blue_movement(blue_speed, deadzone=0.1):
    """
    Computes movement deltas (dx, dy) for the blue block based on joystick and keyboard input.

    Parameters:
        blue_speed (float): Base speed multiplier for movement.
        deadzone (float): Minimum threshold for joystick input to avoid drift.

    Returns:
        tuple: (dx, dy) movement deltas.
    """
    dx, dy = 0, 0

    # Process joystick input if available.
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        if not joystick.get_init():
            joystick.init()
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)
        if abs(axis_x) > deadzone:
            dx += axis_x * blue_speed
        if abs(axis_y) > deadzone:
            dy += axis_y * blue_speed

    # Process keyboard input.
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        dx -= blue_speed
    if keys[pygame.K_RIGHT]:
        dx += blue_speed
    if keys[pygame.K_UP]:
        dy -= blue_speed
    if keys[pygame.K_DOWN]:
        dy += blue_speed

    return dx, dy