# main.py
import pygame, sys
from settings import WIDTH, HEIGHT, FPS
from assets import load_sprite_frames
from level import generate_candidate_level
from collisions import resolve_red_collision, circle_rect_collision
from input_handler import get_blue_movement
from ui import draw_instructions, draw_gameplay, draw_end_screen
from game_state import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    sprite_frames = load_sprite_frames("assets/images/sprite_sheet2.png")
    game = Game(screen, sprite_frames)

    while True:
        events = pygame.event.get()  # Gather events here
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        game.update(events)  # Pass events to your update() method
        game.render()
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()