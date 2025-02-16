# game_state.py
import pygame, sys, random, math
from settings import WIDTH, HEIGHT, GAME_STATE_INSTRUCTIONS, GAME_STATE_PLAYING, GAME_STATE_WIN, GAME_STATE_LOSE, SWITCH_TIMER_DURATION, PINK_DIAMETER, PINK_SPEED, BLUE_SIZE, RED_WIDTH, RED_HEIGHT
from level import generate_candidate_level, get_cell_barriers, bfs_path_length
from collisions import resolve_red_collision, circle_rect_collision
from input_handler import get_blue_movement

class Game:
    def __init__(self, screen, sprite_frames):
        self.screen = screen
        self.sprite_frames = sprite_frames
        self.num_frames = len(sprite_frames)
        self.current_frame_index = 0
        self.frame_duration = 50  # milliseconds per frame
        self.last_frame_update_time = pygame.time.get_ticks()

        # Initialize joystick if available
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        if self.joysticks:
            self.joystick = self.joysticks[0]
            self.joystick.init()
        else:
            self.joystick = None

        # Load fonts
        self.font = pygame.font.Font(None, 80)
        self.instruction_font = pygame.font.Font(None, 30)

        # Initialize game state
        self.reset()

    def reset(self, start_state=GAME_STATE_INSTRUCTIONS):
        """Resets the game to the initial state.
        The start_state parameter lets you choose whether to start at the instructions
        screen (default) or directly in the PLAYING state.
        """
        self.game_state = start_state

        # Initialize red block
        self.red_x = 100
        self.red_y = 100
        self.red_speed_x = 1.7
        self.red_speed_y = 1.7
        self.red_rect = pygame.Rect(self.red_x, self.red_y, RED_WIDTH, RED_HEIGHT)

        # Generate level obstacles and the green block using level functions
        self.obstacles, self.green_rect = generate_candidate_level(self.red_rect, candidate_attempts=10)

        # Generate the switch for deactivating barriers
        self.switch_rect = self.generate_switch()

        # Initialize blue block at a valid position
        self.blue_x, self.blue_y, self.blue_rect = self.generate_blue_block()

        # Flags for game progression
        self.barriers_disabled = False
        self.switch_triggered = False
        self.switch_activation_time = None

        # Initialize pink hazard circles and spawn timer
        self.pink_circles = []
        self.next_pink_spawn_time = None

    def generate_blue_block(self):
        """Generates a valid blue block position that does not overlap obstacles or barriers."""
        from level import get_cell_barriers
        while True:
            blue_x = random.randint(0, WIDTH - BLUE_SIZE)
            blue_y = random.randint(0, HEIGHT - BLUE_SIZE)
            blue_rect = pygame.Rect(blue_x, blue_y, BLUE_SIZE, BLUE_SIZE)
            conflict = False
            # Check collision with obstacles
            for obs in self.obstacles:
                if blue_rect.colliderect(obs):
                    conflict = True
                    break
            # Check collision with barriers around the green block
            for barrier in get_cell_barriers(self.green_rect, pad=10, thick=10):
                if blue_rect.colliderect(barrier):
                    conflict = True
                    break
            if not conflict:
                return blue_x, blue_y, blue_rect

    def generate_switch(self):
        """Finds a valid location for the orange switch."""
        while True:
            switch_x = random.randint(0, WIDTH - BLUE_SIZE)  # Using SWITCH_SIZE; assumed same as blue block here
            switch_y = random.randint(0, HEIGHT - BLUE_SIZE)
            switch_rect = pygame.Rect(switch_x, switch_y, BLUE_SIZE, BLUE_SIZE)
            conflict = switch_rect.colliderect(self.green_rect)
            for obs in self.obstacles:
                if switch_rect.colliderect(obs):
                    conflict = True
                    break
            if not conflict:
                # Also ensure it doesn't conflict with cell barriers around green_rect
                for barrier in get_cell_barriers(self.green_rect, pad=10, thick=10):
                    if switch_rect.colliderect(barrier):
                        conflict = True
                        break
            if not conflict:
                # Verify a valid path exists from red to switch
                barriers = self.obstacles + get_cell_barriers(self.green_rect, pad=10, thick=10)
                if bfs_path_length(self.red_rect.center, switch_rect.center, barriers) is not None:
                    return switch_rect

    def update(self, events):
        current_time = pygame.time.get_ticks()

        if self.game_state == GAME_STATE_INSTRUCTIONS:
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    self.game_state = GAME_STATE_PLAYING
                    print("Game state changed to PLAYING")
                    return
            if pygame.mouse.get_pressed()[0]:
                self.game_state = GAME_STATE_PLAYING
                print("Game state changed to PLAYING via mouse")
            return

        if self.game_state == GAME_STATE_PLAYING:
            # Update blue block movement
            dx, dy = get_blue_movement(blue_speed=4)  # Blue block speed is set to 4
            candidate_blue_rect = pygame.Rect(self.blue_x + dx, self.blue_y, BLUE_SIZE, BLUE_SIZE)
            if not any(candidate_blue_rect.colliderect(obs) for obs in self.obstacles):
                self.blue_x += dx
            candidate_blue_rect = pygame.Rect(self.blue_x, self.blue_y + dy, BLUE_SIZE, BLUE_SIZE)
            if not any(candidate_blue_rect.colliderect(obs) for obs in self.obstacles):
                self.blue_y += dy
            self.blue_x = max(0, min(self.blue_x, WIDTH - BLUE_SIZE))
            self.blue_y = max(0, min(self.blue_y, HEIGHT - BLUE_SIZE))
            self.blue_rect.topleft = (self.blue_x, self.blue_y)

            # Check if red collides with the switch to disable barriers
            if not self.switch_triggered and self.red_rect.colliderect(self.switch_rect):
                self.switch_triggered = True
                self.barriers_disabled = True
                self.switch_activation_time = current_time
                self.next_pink_spawn_time = current_time + 5000  # 5000ms interval
                for _ in range(2):
                    self.spawn_pink_circle()

            # Win condition: red touches green block
            if self.red_rect.colliderect(self.green_rect):
                self.game_state = GAME_STATE_WIN

            # Check switch timer for lose condition
            if self.barriers_disabled and (current_time - self.switch_activation_time > SWITCH_TIMER_DURATION):
                self.game_state = GAME_STATE_LOSE

            # Spawn new pink circles periodically
            if self.barriers_disabled and (self.next_pink_spawn_time is None or current_time >= self.next_pink_spawn_time):
                self.spawn_pink_circle()
                self.next_pink_spawn_time = current_time + 5000

            # Update pink hazards movement
            self.update_pink_circles()

            # Update red block's autonomous movement
            self.update_red_block()

            # Handle red and blue block collisions
            if self.red_rect.colliderect(self.blue_rect):
                self.handle_red_blue_collision()

            # Resolve any residual collisions for red block
            barriers = self.obstacles.copy()
            if not self.barriers_disabled:
                barriers += get_cell_barriers(self.green_rect, pad=10, thick=10)
            self.red_rect = resolve_red_collision(self.red_rect, barriers)
            self.red_x, self.red_y = self.red_rect.topleft

            # Clamp red block to screen edges and adjust speed accordingly
            if self.red_rect.left < 0:
                self.red_rect.left = 0
                self.red_speed_x = abs(self.red_speed_x)
            if self.red_rect.right > WIDTH:
                self.red_rect.right = WIDTH
                self.red_speed_x = -abs(self.red_speed_x)
            if self.red_rect.top < 0:
                self.red_rect.top = 0
                self.red_speed_y = abs(self.red_speed_y)
            if self.red_rect.bottom > HEIGHT:
                self.red_rect.bottom = HEIGHT
                self.red_speed_y = -abs(self.red_speed_y)
            self.red_x, self.red_y = self.red_rect.topleft

        # Update sprite animation
        if current_time - self.last_frame_update_time > self.frame_duration:
            self.current_frame_index = (self.current_frame_index + 1) % self.num_frames
            self.last_frame_update_time = current_time

    def spawn_pink_circle(self):
        """Spawns a pink hazard circle at a random valid location."""
        while True:
            pink_x = random.randint(0, WIDTH - PINK_DIAMETER)
            pink_y = random.randint(0, HEIGHT - PINK_DIAMETER)
            pink_rect = pygame.Rect(pink_x, pink_y, PINK_DIAMETER, PINK_DIAMETER)
            conflict = any(pink_rect.colliderect(obs) for obs in self.obstacles)
            if not conflict:
                distance = math.hypot(pink_rect.centerx - self.red_rect.centerx,
                                      pink_rect.centery - self.red_rect.centery)
                if distance < 150:
                    conflict = True
            if not conflict:
                break
        dir_x = random.choice([PINK_SPEED, -PINK_SPEED])
        dir_y = random.choice([PINK_SPEED, -PINK_SPEED])
        self.pink_circles.append({'rect': pink_rect, 'speed_x': dir_x, 'speed_y': dir_y})

    def update_pink_circles(self):
        """Updates the movement of pink hazard circles and checks for collisions with the red block."""
        for circle in self.pink_circles:
            new_x = circle['rect'].x + circle['speed_x']
            temp_rect = pygame.Rect(new_x, circle['rect'].y, circle['rect'].width, circle['rect'].height)
            barriers = self.obstacles.copy()
            if not self.barriers_disabled:
                barriers += get_cell_barriers(self.green_rect, pad=10, thick=10)
            if any(temp_rect.colliderect(obs) for obs in barriers):
                circle['speed_x'] = -circle['speed_x']
            else:
                circle['rect'].x = new_x
            new_y = circle['rect'].y + circle['speed_y']
            temp_rect = pygame.Rect(circle['rect'].x, new_y, circle['rect'].width, circle['rect'].height)
            if any(temp_rect.colliderect(obs) for obs in barriers):
                circle['speed_y'] = -circle['speed_y']
            else:
                circle['rect'].y = new_y
            # Clamp to screen edges
            if circle['rect'].left < 0:
                circle['rect'].left = 0
                circle['speed_x'] = abs(circle['speed_x'])
            if circle['rect'].right > WIDTH:
                circle['rect'].right = WIDTH
                circle['speed_x'] = -abs(circle['speed_x'])
            if circle['rect'].top < 0:
                circle['rect'].top = 0
                circle['speed_y'] = abs(circle['speed_y'])
            if circle['rect'].bottom > HEIGHT:
                circle['rect'].bottom = HEIGHT
                circle['speed_y'] = -abs(circle['speed_y'])
            # Check collision with red block
            if circle_rect_collision(circle['rect'].center, circle['rect'].width // 2, self.red_rect):
                self.game_state = GAME_STATE_LOSE

    def update_red_block(self):
        """Updates the red block's autonomous movement."""
        new_red_x = self.red_x + self.red_speed_x
        barriers = self.obstacles.copy()
        if not self.barriers_disabled:
            barriers += get_cell_barriers(self.green_rect, pad=10, thick=10)
        temp_rect = pygame.Rect(new_red_x, self.red_y, RED_WIDTH, RED_HEIGHT)
        if any(temp_rect.colliderect(obs) for obs in barriers):
            self.red_speed_x = -self.red_speed_x
        else:
            self.red_x = new_red_x

        new_red_y = self.red_y + self.red_speed_y
        temp_rect = pygame.Rect(self.red_x, new_red_y, RED_WIDTH, RED_HEIGHT)
        if any(temp_rect.colliderect(obs) for obs in barriers):
            self.red_speed_y = -self.red_speed_y
        else:
            self.red_y = new_red_y

        self.red_rect.topleft = (self.red_x, self.red_y)

    def handle_red_blue_collision(self):
        """Adjusts red block's position when colliding with the blue block."""
        red_center = self.red_rect.center
        blue_center = self.blue_rect.center
        diff_x = red_center[0] - blue_center[0]
        diff_y = red_center[1] - blue_center[1]
        distance = max(math.hypot(diff_x, diff_y), 1)
        norm_x, norm_y = diff_x / distance, diff_y / distance
        current_speed = math.hypot(self.red_speed_x, self.red_speed_y)
        self.red_speed_x = current_speed * norm_x
        self.red_speed_y = current_speed * norm_y
        candidate_red_x = self.blue_rect.right if norm_x >= 0 else self.blue_rect.left - RED_WIDTH
        candidate_red_y = self.blue_rect.bottom if norm_y >= 0 else self.blue_rect.top - RED_HEIGHT
        candidate_red_rect = pygame.Rect(candidate_red_x, candidate_red_y, RED_WIDTH, RED_HEIGHT)
        barriers = self.obstacles.copy()
        if not self.barriers_disabled:
            barriers += get_cell_barriers(self.green_rect, pad=10, thick=10)
        if not any(candidate_red_rect.colliderect(obs) for obs in barriers):
            self.red_x = candidate_red_x
            self.red_y = candidate_red_y
            self.red_rect.topleft = candidate_red_rect.topleft

    def render(self):
        """Renders the current game state using UI functions."""
        from ui import draw_instructions, draw_gameplay, draw_end_screen
        if self.game_state == GAME_STATE_INSTRUCTIONS:
            draw_instructions(self.screen, self.instruction_font,
                              "Help the red block reunite with the green block!\n\n"
                              "Control the blue block using your joystick or arrow keys.\n"
                              "Avoid pink hazards and follow the instructions.\n\n"
                              "Click 'Start Game' or press A to begin.")
        elif self.game_state == GAME_STATE_PLAYING:
            # Calculate remaining timer if switch activated
            timer_value = None
            if self.barriers_disabled and self.switch_activation_time is not None:
                elapsed = pygame.time.get_ticks() - self.switch_activation_time
                timer_value = max(0, (SWITCH_TIMER_DURATION - elapsed) // 1000)
            # Get the current red sprite frame and determine if it should be flipped
            red_frame = self.sprite_frames[self.current_frame_index]
            sprite_flip = self.red_speed_x < 0

            # Call the gameplay drawing function with all parameters
            draw_gameplay(
                self.screen,
                self.obstacles,
                self.green_rect,
                self.barriers_disabled,
                self.switch_rect,
                self.switch_triggered,
                self.blue_rect,
                self.red_rect,
                red_frame,
                self.pink_circles,
                timer_value,
                self.font,
                sprite_flip=sprite_flip,
                get_cell_barriers_func=get_cell_barriers
            )
        else:
            # Win or lose state: use a smaller font for the end screen.
            small_font = pygame.font.Font(None, 40)
            button_rect = draw_end_screen(self.screen, small_font, self.game_state)
            # Check for mouse click on the "Play again" button.
            if pygame.mouse.get_pressed()[0]:
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    self.reset(start_state=GAME_STATE_PLAYING)
            # Also check if joystick "A" button (button 0) is pressed to restart.
            if self.joystick and self.joystick.get_button(0):
                self.reset(start_state=GAME_STATE_PLAYING)