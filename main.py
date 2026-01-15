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
    (220,220,255), # 6 very dim white (stars)
    (200,200,220), # 7 slightly brighter star
]

pygame.init()
pygame.display.set_caption("Dinosaur vs Bees – Parallax v21: Scrolling Halved Again (1/8 Original)")
low_res = pygame.Surface((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.SCALED)
clock = pygame.time.Clock()

frame_count = 0
mountains_offset = 0
hills_offset = 0
ground_offset = 0

# Static starfield
stars = []
random.seed(42)
for _ in range(120):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, 100)
    brightness = random.choice([6, 6, 6, 7])
    size = 1 if brightness == 6 else 2
    stars.append((x, y, brightness, size))

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
                if not (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]):
                    scroll_direction = 0

    frame_count += 1

    # Apply direction only when key held
    if 'scroll_direction' in locals() and scroll_direction != 0:
        # Quarter-speed layering – integer steps only
        if frame_count % 8 == 0:
            mountains_offset += scroll_direction * 1   # ~0.125 px/frame
        if frame_count % 4 == 0:
            hills_offset += scroll_direction * 1       # ~0.25 px/frame
        if frame_count % 2 == 0:
            ground_offset += scroll_direction * 1      # ~0.5 px/frame

    low_res.fill(PALETTE[0])

    # Static stars
    for x, y, pal_idx, sz in stars:
        pygame.draw.rect(low_res, PALETTE[pal_idx], (x, y, sz, sz))

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
        col = PALETTE[2] if h > -8 else PALETTE[3]
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, col, (screen_x, y, 1, HEIGHT - y + 50))

    # Brown lumpy ground – lowered
    for px in range(-80, WIDTH + 80):
        world_x = px + ground_offset
        lump = 7 * math.sin(world_x * 0.09) + 5 * math.cos(world_x * 0.16)
        y = 200 + int(lump)
        col = PALETTE[5] if lump > 0 else PALETTE[4]
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, col, (screen_x, y, 1, HEIGHT - y + 10))

    pygame.transform.scale(low_res, win.get_size(), win)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

