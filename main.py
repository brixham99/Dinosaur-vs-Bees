import pygame
import sys
import math
import random

WIDTH, HEIGHT = 256, 224
SCALE = 4
FPS = 60

PALETTE = [
    (0,0,0),          # 0 sky / background
    (40,40,40),       # 1 distant peaks
    (60,100,60),      # 2 dark green
    (90,130,90),      # 3 mid green
    (120,80,40),      # 4 brown base
    (150,100,60),     # 5 light brown lumps
    (30,30,40),       # 6 very dark gray – dull twinklers
    (180,180,220),    # 7 brighter non-twinklers
    (255,255,255),    # 8 full white twinkle peak
]

pygame.init()
pygame.display.set_caption("Dinosaur vs Bees – Parallax v27: Bee Sprites + Random Flight/Flips")
low_res = pygame.Surface((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.SCALED)
clock = pygame.time.Clock()

frame_count = 0
mountains_offset = 0
hills_offset = 0
ground_offset = 0
scroll
