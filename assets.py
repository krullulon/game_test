# assets.py
import pygame
from settings import RED_WIDTH, RED_HEIGHT


import os
import pygame

def load_sprite_frames(sprite_sheet_path, rows=11, cols=10):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, sprite_sheet_path)
    sprite_sheet = pygame.image.load(full_path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_width(), sprite_sheet.get_height()
    frame_width = sheet_width // cols
    frame_height = sheet_height // rows
    frames = []
    for r in range(rows):
        col_limit = cols if r < rows - 1 else 2
        for c in range(col_limit):
            rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
            frame = sprite_sheet.subsurface(rect)
            frames.append(frame)
    return frames


def load_image(image_path):
    """
    Loads an image with alpha transparency.

    Parameters:
        image_path (str): Path to the image file.

    Returns:
        pygame.Surface: The loaded image.
    """
    return pygame.image.load(image_path).convert_alpha()


def load_font(font_path, size):
    """
    Loads a font at a given size.

    Parameters:
        font_path (str): Path to the .ttf font file. Use None for the default font.
        size (int): Font size.

    Returns:
        pygame.font.Font: The loaded font object.
    """
    return pygame.font.Font(font_path, size)