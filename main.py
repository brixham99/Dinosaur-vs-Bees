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
pygame.display.set_caption("Dinosaur vs Bees – Parallax v28.3: Bee Speed Symmetry (Left = Right)")
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
# Bee sprite class – FIXED: same speed magnitude left & right
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
        
        # Choose random SPEED magnitude, then random DIRECTION
        base_speed = random.uniform(1.0, 2.0) * speed_mult
        self.speed = base_speed  # absolute speed preserved across flips
        self.vx = base_speed if random.random() < 0.5 else -base_speed  # random initial direction
        self.vy = random.uniform(-0.75, 0.75) * speed_mult
        self.flip_timer = random.randint(90, 180)
        self.wander_timer = random.randint(30, 60)
        self.flipped = self.vx < 0  # initial flip state based on direction

        # Set initial image orientation
        self.image = pygame.transform.flip(self.original_image, self.flipped, False)

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
            self.vx = -self.vx  # reverse direction but KEEP SAME SPEED
            self.flip_timer = random.randint(90, 180)

        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.vy += random.uniform(-0.5, 0.5)
            self.vy = max(-2.0, min(2.0, self.vy))
            self.wander_timer = random.randint(30, 60)

        # Respawn if off-screen
        if self.rect.right < -20 or self.rect.left > WIDTH + 20 or \
           self.rect.top > HEIGHT + 20 or self.rect.bottom < -20:
            self.reset_position()
            # On respawn, keep same speed magnitude but random direction again
            self.vx = self.speed if random.random() < 0.5 else -self.speed
            self.vy = random.uniform(-0.75, 0.75)
            self.flipped = self.vx < 0
            self.image = pygame.transform.flip(self.original_image, self.flipped, False)

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
