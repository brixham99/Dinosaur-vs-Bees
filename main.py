import pygame
import sys
import math
import random

WIDTH, HEIGHT = 256, 224
SCALE = 4
FPS = 60

PALETTE = [
    (0,0,0),       # 0 sky / background
    (40,40,40),    # 1 distant peaks
    (60,100,60),   # 2 dark green
    (90,130,90),   # 3 mid green
    (120,80,40),   # 4 brown base
    (150,100,60),  # 5 light brown lumps
    (220,220,255), # 6 very dim white (stars base)
    (200,200,220), # 7 old mid-bright (unused now)
    (255,255,255), # 8 full bright white – new stronger twinkle peak
]

pygame.init()
pygame.display.set_caption("Dinosaur vs Bees – Parallax v23: Stronger Twinkling Stars")
low_res = pygame.Surface((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.SCALED)
clock = pygame.time.Clock()

frame_count = 0
mountains_offset = 0
hills_offset = 0
ground_offset = 0
scroll_direction = 0

# Static starfield with stronger twinkling
stars = []
random.seed(42)
for i in range(120):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, 100)
    base_bright = 6  # PALETTE[6] dim
    size = random.choice([1, 1, 2])
    # 30% chance to twinkle
    phase = random.uniform(0, 2 * math.pi) if random.random() < 0.3 else None
    stars.append((x, y, base_bright, size, phase))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_LEFT:
                scroll_direction = -1
            elif event.key == pygame.K_RIGHT:
                scroll_direction = 1
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                keys = pygame.key.get_pressed()
                scroll_direction = -1 if keys[pygame.K_LEFT] else (1 if keys[pygame.K_RIGHT] else 0)

    frame_count += 1

    # Integer parallax updates (unchanged from v21)
    if scroll_direction != 0:
        if frame_count % 8 == 0:
            mountains_offset += scroll_direction
        if frame_count % 4 == 0:
            hills_offset += scroll_direction
        if frame_count % 2 == 0:
            ground_offset += scroll_direction

    low_res.fill(PALETTE[0])

    # Draw stars with stronger twinkle
    current_time = pygame.time.get_ticks() * 0.001  # seconds
    for x, y, base_bright, size, phase in stars:
        if phase is not None:  # Twinkler
            # Faster and stronger pulse: 0.0 → 1.0 → 0.0
            flicker = 0.5 + 0.5 * math.sin(current_time * 3 + phase)  # *3 = quicker cycle
            bright_idx = 8 if flicker > 0.4 else 6  # clear jump to full white
        else:
            bright_idx = base_bright
        pygame.draw.rect(low_res, PALETTE[bright_idx], (x, y, size, size))

    # Distant mountains
    for px in range(-80, WIDTH + 80):
        world_x = px + mountains_offset
        h1 = 50 * math.sin(world_x * 0.008)
        h2 = 35 * math.sin(world_x * 0.022 + 1.2)
        h3 = 18 * math.sin(world_x * 0.045 + 3.0)
        mountain_y = 55 + int(h1 + h2 + h3)
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[1], (screen_x, mountain_y, 1, HEIGHT - mountain_y))

    # Green hills
    for px in range(-80, WIDTH + 80):
        world_x = px + hills_offset
        h = 32 * math.sin(world_x * 0.04) + 24 * math.sin(world_x * 0.075 + 1.8)
        y = 138 + int(h)
        col_idx = 2 if h > -8 else 3
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 50))

    # Brown lumpy ground
    for px in range(-80, WIDTH + 80):
        world_x = px + ground_offset
        lump = 7 * math.sin(world_x * 0.09) + 5 * math.cos(world_x * 0.16)
        y = 200 + int(lump)
        col_idx = 5 if lump > 0 else 4
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 10))

    pygame.transform.scale(low_res, win.get_size(), win)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
