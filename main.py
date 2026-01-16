import pygame
import sys
import math
import random

WIDTH, HEIGHT = 256, 224
SCALE = 4
FPS = 60

PALETTE = [
    (0,0,0),          # 0 sky fallback
    (40,40,40),       # 1 distant peaks
    (60,100,60),      # 2 dark green
    (90,130,90),      # 3 mid green
    (120,80,40),      # 4 brown base
    (150,100,60),     # 5 light brown lumps
    (30,30,40),       # 6 very dark gray – dull twinklers
    (180,180,220),    # 7 brighter non-twinkling stars
    (255,255,255),    # 8 full bright white – twinkle peak
    (135,206,235),    # 9 bright blue sky (level 1)
    (211,211,211),    # 10 light grey sky (level 3)
    (200,0,0),        # 11 red sky base (level 4)
    (255,255,0),      # 12 yellow sun
    (240,240,240),    # 13 white moon
]

pygame.init()
pygame.display.set_caption("Dinosaur vs Bees – Parallax v28.1: 4 Levels (Level 2 Fixed)")
low_res = pygame.Surface((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.SCALED)
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 16, bold=True)

# Global starfield (only used in level 2)
stars = []
random.seed(42)
for i in range(120):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, 100)
    base_bright = 7
    size = random.choice([1, 1, 2])
    phase = random.uniform(0, 2 * math.pi) if random.random() < 0.3 else None
    stars.append((x, y, base_bright, size, phase))

frame_count = 0
mountains_offset = 0.0
hills_offset = 0.0
ground_offset = 0.0
scroll_direction = 0
current_level = 1

# ────────────────────────────────────────────────────────────────
# Bee sprite class
# ────────────────────────────────────────────────────────────────
class Bee(pygame.sprite.Sprite):
    def __init__(self, scale=1.0, speed_mult=1.0):
        super().__init__()
        img = pygame.image.load("assets/bee.png").convert_alpha()
        w, h = img.get_size()
        self.original_image = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.reset_position()
        self.vx = random.uniform(-4, -2) * speed_mult
        self.vy = random.uniform(-1.5, 1.5) * speed_mult
        self.flip_timer = random.randint(90, 180)
        self.wander_timer = random.randint(30, 60)
        self.flipped = False

    def reset_position(self):
        self.rect.x = WIDTH + random.randint(20, 100)
        self.rect.y = random.randint(80, 180)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        self.flip_timer -= 1
        if self.flip_timer <= 0:
            self.flipped = not self.flipped
            self.image = pygame.transform.flip(self.original_image, self.flipped, False)
            self.vx = -self.vx
            self.flip_timer = random.randint(90, 180)

        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.vy += random.uniform(-0.5, 0.5)
            self.vy = max(-2.0, min(2.0, self.vy))
            self.wander_timer = random.randint(30, 60)

        if self.rect.right < -20 or self.rect.left > WIDTH + 20 or \
           self.rect.top > HEIGHT + 20 or self.rect.bottom < -20:
            self.reset_position()
            self.vx = random.uniform(-4, -2)
            self.vy = random.uniform(-1.5, 1.5)
            self.flipped = False
            self.image = self.original_image

# ────────────────────────────────────────────────────────────────
# Create bees for current level
# ────────────────────────────────────────────────────────────────
def create_bees_for_level(level):
    bees = pygame.sprite.Group()
    if level == 1:
        count, scale, speed_mult = 2, 0.5, 0.7
    elif level == 2:
        count, scale, speed_mult = 3, 0.5, 0.7
    elif level == 3:
        count, scale, speed_mult = 3, 1.0, 1.4
    elif level == 4:
        count, scale, speed_mult = 4, 1.0, 1.4
    else:
        count, scale, speed_mult = 4, 1.0, 1.0

    for _ in range(count):
        bee = Bee(scale=scale, speed_mult=speed_mult)
        bees.add(bee)
    return bees

bees = create_bees_for_level(current_level)

# ────────────────────────────────────────────────────────────────
# Main loop
# ────────────────────────────────────────────────────────────────
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
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                new_level = int(pygame.key.name(event.key))
                if new_level != current_level:
                    current_level = new_level
                    bees = create_bees_for_level(current_level)
                    mountains_offset = hills_offset = ground_offset = 0.0
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

    low_res.fill((0,0,0))

    # ── Sky & special elements per level ───────────────────────────
    if current_level == 1:
        # Bright blue sky gradient
        for y in range(HEIGHT):
            t = y / HEIGHT
            col = (
                int(135 + (255-135)*t),
                int(206 + (255-206)*t),
                int(235 + (255-235)*t)
            )
            pygame.draw.line(low_res, col, (0,y), (WIDTH,y))
        # Yellow sun top-left
        sun_center = (40, 40)
        pygame.draw.circle(low_res, (255,255,0), sun_center, 24)
        pygame.draw.circle(low_res, (255,220,80), sun_center, 18)

    elif current_level == 2:
        # Black sky + twinkling stars
        low_res.fill((0,0,0))
        current_time = pygame.time.get_ticks() * 0.001
        for x, y, base_bright, size, phase in stars:
            if phase is not None:
                flicker = 0.5 + 0.5 * math.sin(current_time * 2.8 + phase)
                bright_idx = 8 if flicker > 0.35 else 6
            else:
                bright_idx = base_bright
            pygame.draw.rect(low_res, PALETTE[bright_idx], (x, y, size, size))

    elif current_level == 3:
        # Solid light grey sky
        low_res.fill((211,211,211))

    elif current_level == 4:
        # Red sky gradient
        for y in range(HEIGHT):
            t = y / HEIGHT
            col = (
                int(200 + (255-200)*t),
                int(0 + (100-0)*t),
                int(0 + (50-0)*t)
            )
            pygame.draw.line(low_res, col, (0,y), (WIDTH,y))
        # White moon top-right
        moon_center = (WIDTH - 50, 50)
        pygame.draw.circle(low_res, (240,240,240), moon_center, 28)
        pygame.draw.circle(low_res, (220,220,220), moon_center, 22)

    # ── Parallax layers (drawn on top of sky) ──────────────────────
    for px in range(-80, WIDTH + 80):
        world_x = px + mountains_offset
        h1 = 50 * math.sin(world_x * 0.008)
        h2 = 35 * math.sin(world_x * 0.022 + 1.2)
        h3 = 18 * math.sin(world_x * 0.045 + 3.0)
        mountain_y = 55 + int(h1 + h2 + h3)
        screen_x = int(px)
        if 0 <= screen_x < WIDTH and mountain_y < HEIGHT:
            pygame.draw.rect(low_res, PALETTE[1], (screen_x, mountain_y, 1, HEIGHT - mountain_y))

    for px in range(-80, WIDTH + 80):
        world_x = px + hills_offset
        h = 19.2 * math.sin(world_x * 0.04) + 14.4 * math.sin(world_x * 0.075 + 1.8)
        y = 138 + int(h)
        col_idx = 2 if h > -8 else 3
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 50))

    for px in range(-80, WIDTH + 80):
        world_x = px + ground_offset
        lump = 4.2 * math.sin(world_x * 0.09) + 3.0 * math.cos(world_x * 0.16)
        y = 200 + int(lump)
        col_idx = 5 if lump > 0 else 4
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 10))

    # ── Bees ────────────────────────────────────────────────────────
    bees.update()
    bees.draw(low_res)

    # ── Level indicator ─────────────────────────────────────────────
    level_text = font.render(f"Level {current_level}", True, (255,255,255))
    low_res.blit(level_text, (WIDTH - level_text.get_width() - 8, HEIGHT - level_text.get_height() - 4))

    pygame.transform.scale(low_res, win.get_size(), win)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
