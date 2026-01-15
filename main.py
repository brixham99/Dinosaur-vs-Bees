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
    (180,180,220),    # 7 brighter non-twinkling stars
    (255,255,255),    # 8 full bright white – twinkle peak
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
scroll_direction = 0

# Static starfield
stars = []
random.seed(42)
for i in range(120):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, 100)
    base_bright = 7
    size = random.choice([1, 1, 2])
    phase = random.uniform(0, 2 * math.pi) if random.random() < 0.3 else None
    stars.append((x, y, base_bright, size, phase))

# Bee sprite class
class Bee(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("assets/bee.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.reset_position()
        self.vx = random.uniform(-4, -2)  # mostly leftward
        self.vy = random.uniform(-1.5, 1.5)
        self.flip_timer = random.randint(90, 180)   # frames until flip
        self.wander_timer = random.randint(30, 60)  # frames until y nudge
        self.flipped = False

    def reset_position(self):
        self.rect.x = WIDTH + random.randint(20, 100)  # start off right
        self.rect.y = random.randint(80, 180)          # mid-high on screen

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Periodic flip & direction reverse
        self.flip_timer -= 1
        if self.flip_timer <= 0:
            self.flipped = not self.flipped
            self.image = pygame.transform.flip(self.original_image, self.flipped, False)
            self.vx = -self.vx  # reverse horizontal direction
            self.flip_timer = random.randint(90, 180)

        # Periodic small y wander
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.vy += random.uniform(-0.5, 0.5)
            self.vy = max(-2.0, min(2.0, self.vy))  # clamp speed
            self.wander_timer = random.randint(30, 60)

        # Respawn if off-screen
        if self.rect.right < -20 or self.rect.left > WIDTH + 20 or \
           self.rect.top > HEIGHT + 20 or self.rect.bottom < -20:
            self.reset_position()
            self.vx = random.uniform(-4, -2)
            self.vy = random.uniform(-1.5, 1.5)
            self.flipped = False
            self.image = self.original_image

# Create bee group
bees = pygame.sprite.Group()
for _ in range(4):
    bees.add(Bee())

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

    if scroll_direction != 0:
        if frame_count % 8 == 0:
            mountains_offset += scroll_direction
        if frame_count % 4 == 0:
            hills_offset += scroll_direction
        if frame_count % 2 == 0:
            ground_offset += scroll_direction

    low_res.fill(PALETTE[0])

    # Stars
    current_time = pygame.time.get_ticks() * 0.001
    for x, y, base_bright, size, phase in stars:
        if phase is not None:
            flicker = 0.5 + 0.5 * math.sin(current_time * 2.8 + phase)
            bright_idx = 8 if flicker > 0.35 else 6
        else:
            bright_idx = base_bright
        pygame.draw.rect(low_res, PALETTE[bright_idx], (x, y, size, size))

    # Mountains
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
        h = 19.2 * math.sin(world_x * 0.04) + 14.4 * math.sin(world_x * 0.075 + 1.8)
        y = 138 + int(h)
        col_idx = 2 if h > -8 else 3
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 50))

    # Brown ground
    for px in range(-80, WIDTH + 80):
        world_x = px + ground_offset
        lump = 4.2 * math.sin(world_x * 0.09) + 3.0 * math.cos(world_x * 0.16)
        y = 200 + int(lump)
        col_idx = 5 if lump > 0 else 4
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 10))

    # Update & draw bees
    bees.update()
    bees.draw(low_res)

    pygame.transform.scale(low_res, win.get_size(), win)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
