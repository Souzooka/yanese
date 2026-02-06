# TEMPORARY CODE

import sys

import numpy as np
import pygame

from src.NES import NES

SCALE = 4
H = 256
V = 240

pygame.init()

screen = pygame.display.set_mode((H * SCALE, V * SCALE), depth=32)

frame_buffer = np.ndarray((H, V), dtype=np.uint32)

clock = pygame.time.Clock()

surface = pygame.Surface((H, V), depth=32)

pygame.display.set_caption("yaNESe")


def rainbow(tick, array):
    import colorsys

    s = 0xC0
    v = 0xC0
    h = int(tick * (100.0 / 255.0) / 20) & 0xFF
    h = h / 255.0
    v = v / 255.0
    s = s / 255.0
    r, g, b = (int(c * 255.0) for c in colorsys.hsv_to_rgb(h, s, v))
    a = 0xFF
    color = (a << 24) | (b << 16) | (g << 8) | (r << 0)

    array.fill(color)


def on_frame(frame_buffer):
    pygame.surfarray.blit_array(surface, frame_buffer)
    screen.blit(pygame.transform.scale(surface, (H * SCALE, V * SCALE)), (0, 0))
    pygame.display.flip()


def do_nes(file_path: str):
    nes = NES()
    with open(file_path, "rb") as cart:
        nes.load_cartridge(cart)

    while True:
        clock.tick(60.0)
        nes.run(on_frame)

        if any(event.type == pygame.QUIT for event in pygame.event.get()):
            return


while True:
    clock.tick(60.0)
    rainbow(pygame.time.get_ticks(), frame_buffer)
    frame_buffer[245][10] = 0xFF0000FF  # Should plot blue near the top right
    pygame.surfarray.blit_array(surface, frame_buffer)
    screen.blit(pygame.transform.scale(surface, (H * SCALE, V * SCALE)), (0, 0))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.DROPFILE:
            do_nes(event.file)
            sys.exit()

sys.exit()

# /TEMPORARY CODE
