# ui.py
import pygame
from settings import WIDTH, HEIGHT


def draw_multiline_text(surface, text, font, color, rect, line_spacing=5):
    """
    Draws multiline text on a surface within a given rectangle.
    Returns the total height used by the rendered text.
    """
    words = [line.split(' ') for line in text.splitlines()]
    x, y = rect.topleft
    total_height = 0
    for line in words:
        current_line = ""
        for word in line:
            test_line = current_line + word + " "
            if font.size(test_line)[0] > rect.width and current_line:
                line_surface = font.render(current_line, True, color)
                surface.blit(line_surface, (x, y))
                y += line_surface.get_height() + line_spacing
                total_height += line_surface.get_height() + line_spacing
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            line_surface = font.render(current_line, True, color)
            surface.blit(line_surface, (x, y))
            y += line_surface.get_height() + line_spacing
            total_height += line_surface.get_height() + line_spacing
    return total_height


def measure_multiline_text(text, font, max_width, line_spacing=5):
    """
    Calculates the total height required to render the given multiline text.
    """
    total_height = 0
    for line in text.splitlines():
        current_line = ""
        for word in line.split(' '):
            test_line = current_line + word + " "
            if font.size(test_line)[0] > max_width and current_line:
                total_height += font.get_linesize() + line_spacing
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            total_height += font.get_linesize() + line_spacing
    return total_height


def draw_button(surface, text, font, center, padding=(20, 10), bg_color=(200, 200, 200), text_color=(0, 0, 0)):
    """
    Draws a button with the specified text at the given center position.
    Returns the button's rect.
    """
    text_surface = font.render(text, True, text_color)
    button_rect = text_surface.get_rect(center=center)
    # Inflate for padding
    button_rect = button_rect.inflate(padding[0] * 2, padding[1] * 2)
    pygame.draw.rect(surface, bg_color, button_rect)
    text_rect = text_surface.get_rect(center=button_rect.center)
    surface.blit(text_surface, text_rect)
    return button_rect


def draw_instructions(surface, font, instructions_text):
    """
    Renders the instructions screen. The text is wrapped and left‐justified,
    but the entire block is horizontally centered on the screen.
    Draws the "Start Game" button and the "A" button.
    Returns the rectangle for the "Start Game" button.
    """
    from settings import WIDTH, HEIGHT
    surface.fill((0, 0, 0))

    # Wrap text manually into lines that do not exceed a max width.
    max_text_width = int(WIDTH * 0.8)  # initial wrapping width (80% of screen)
    wrapped_lines = []
    for line in instructions_text.splitlines():
        words = line.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] > max_text_width and current_line:
                wrapped_lines.append(current_line.rstrip())
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            wrapped_lines.append(current_line.rstrip())

    # Compute the maximum rendered width of the wrapped lines.
    max_rendered_width = 0
    for line in wrapped_lines:
        line_width, _ = font.size(line)
        if line_width > max_rendered_width:
            max_rendered_width = line_width

    # Determine the left coordinate so that the text block is centered.
    text_x = (WIDTH - max_rendered_width) // 2

    # Calculate total height of the text block.
    line_height = font.get_linesize() + 5  # including line spacing
    total_text_height = len(wrapped_lines) * line_height

    gap = 40
    button_height = font.get_linesize()
    total_block_height = total_text_height + gap + button_height
    text_y = (HEIGHT - total_block_height) // 2

    # Draw each line at (text_x, text_y)
    y = text_y
    for line in wrapped_lines:
        line_surface = font.render(line, True, (255, 255, 255))
        surface.blit(line_surface, (text_x, y))
        y += line_height

    # Draw "Start Game" button centered below the text block.
    from ui import draw_button
    button_center = (WIDTH // 2, y + gap + button_height // 2)
    button_rect = draw_button(surface, "Start Game", font, button_center)

    # Draw the "A" button as a green circle with "A" next to it.
    a_button_radius = 20
    a_button_x = button_rect.right + a_button_radius + 25
    a_button_y = button_rect.centery
    pygame.draw.circle(surface, (0, 200, 0), (a_button_x, a_button_y), a_button_radius)
    a_text_surface = font.render("A", True, (255, 255, 255))
    a_text_rect = a_text_surface.get_rect(center=(a_button_x, a_button_y))
    surface.blit(a_text_surface, a_text_rect)

    return button_rect


def draw_end_screen(surface, font, game_state):
    """
    Renders the win/lose screen with a "Play again" button and the "A" button.
    Returns the rectangle for the "Play again" button.
    """
    from settings import WIDTH, HEIGHT
    surface.fill((0, 0, 0))
    message = "You win!" if game_state == "win" else "You lose!"
    text_surface = font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(text_surface, text_rect)

    button_text = "Play again"
    button_surface = font.render(button_text, True, (0, 0, 0))
    button_rect = button_surface.get_rect(center=(WIDTH // 2, text_rect.bottom + 60))
    pygame.draw.rect(surface, (200, 200, 200), button_rect.inflate(20, 10))
    surface.blit(button_surface, button_rect)

    # Draw the "A" button as a green circle with the letter "A"
    a_button_radius = 20
    a_button_x = button_rect.right + a_button_radius + 25
    a_button_y = button_rect.centery
    pygame.draw.circle(surface, (0, 200, 0), (a_button_x, a_button_y), a_button_radius)
    a_text_surface = font.render("A", True, (255, 255, 255))
    a_text_rect = a_text_surface.get_rect(center=(a_button_x, a_button_y))
    surface.blit(a_text_surface, a_text_rect)

    return button_rect


def draw_gameplay(surface, obstacles, green_rect, barriers_disabled, switch_rect, switch_triggered,
                  blue_rect, red_rect, red_frame, pink_circles, timer_value, font, sprite_flip=False,
                  get_cell_barriers_func=None):
    """
    Renders the gameplay screen with all game elements.

    Parameters:
        surface (pygame.Surface): The main display surface.
        obstacles (list): List of obstacle rectangles.
        green_rect (pygame.Rect): The green block's rectangle.
        barriers_disabled (bool): Whether barriers are disabled.
        switch_rect (pygame.Rect): The switch's rectangle.
        switch_triggered (bool): Whether the switch has been triggered.
        blue_rect (pygame.Rect): The blue block's rectangle.
        red_rect (pygame.Rect): The red block's rectangle.
        red_frame (pygame.Surface): Current sprite frame for the red block.
        pink_circles (list): List of dicts for pink hazards.
        timer_value (int or None): Remaining time value to display.
        font (pygame.font.Font): Font for drawing timer text.
        sprite_flip (bool): Whether to flip the red sprite horizontally.
        get_cell_barriers_func (callable): Function to get cell barriers (if needed).
    """
    surface.fill((0, 0, 0))
    # Draw obstacles
    for obs in obstacles:
        pygame.draw.rect(surface, (128, 128, 128), obs)
    # Draw green block
    pygame.draw.rect(surface, (0, 255, 0), green_rect)
    # Draw barriers if applicable
    if not barriers_disabled and get_cell_barriers_func is not None:
        barriers = get_cell_barriers_func(green_rect, pad=10, thick=10)
        for barrier in barriers:
            pygame.draw.rect(surface, (128, 128, 128), barrier)
    # Draw switch if not triggered
    if not switch_triggered:
        pygame.draw.rect(surface, (255, 165, 0), switch_rect)
    # Draw blue block
    pygame.draw.rect(surface, (0, 0, 255), blue_rect)
    # Draw red block: flip sprite if needed, then blit at red_rect position
    frame = red_frame
    if sprite_flip:
        frame = pygame.transform.flip(red_frame, True, False)
    surface.blit(frame, red_rect)
    # Draw timer if available
    if timer_value is not None:
        timer_text = font.render(f"{timer_value}", True, (255, 255, 255))
        surface.blit(timer_text, (WIDTH - 100, 50))
    # Draw pink circles (hazards)
    for circle in pink_circles:
        pygame.draw.circle(surface, (255, 105, 180), circle['rect'].center, circle['rect'].width // 2)