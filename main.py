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
pygame.display.set_caption("Dinosaur vs Bees – v30.0: Dinosaur refinements")
low_res = pygame.Surface((WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), pygame.SCALED)
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 16, bold=True)

# ────────────────────────────────────────────────────────────────
# Load and prepare dinosaur frames (scaled 75%)
# ────────────────────────────────────────────────────────────────
sprite_sheet = pygame.image.load("assets/dino-sprite-sheet.png").convert_alpha()
dino_frames_original = []
frame_width, frame_height = 212, 160
for row in range(3):
    cols = 5 if row < 2 else 3
    for col in range(cols):
        frame = sprite_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
        dino_frames_original.append(frame)

scale_factor = 0.75
dino_frames = []
for frame in dino_frames_original:
    w, h = frame.get_size()
    scaled = pygame.transform.scale(frame, (int(w * scale_factor), int(h * scale_factor)))
    dino_frames.append(scaled)

scaled_width  = dino_frames[0].get_width()   # ≈159
scaled_height = dino_frames[0].get_height()  # ≈120

# Dinosaur state
dino_frame_idx = 0
dino_anim_timer = 0
anim_delay = 6                  # frame every 6 ticks (~10 FPS when moving)
dino_screen_x = WIDTH // 2
facing_right = True
last_scroll_direction = 1

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
        self.speed_mult = speed_mult
        self.reset_position()
        self.vx = random.uniform(-2, -1) * speed_mult
        self.vy = random.uniform(-0.75, 0.75) * speed_mult
        self.flip_timer = random.randint(90, 180)
        self.wander_timer = random.randint(30, 60)
        self.flipped = False

    def reset_position(self):
        self.world_x = ground_offset + WIDTH + random.randint(20, 100)
        self.world_y = random.randint(80, 180)
        self.rect.x = int(self.world_x - ground_offset)
        self.rect.y = int(self.world_y)

    def update(self):
        self.world_x += self.vx
        self.world_y += self.vy
        self.rect.x = int(self.world_x - ground_offset)
        self.rect.y = int(self.world_y)

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
            self.vx = random.uniform(-2, -1) * self.speed_mult
            self.vy = random.uniform(-0.75, 0.75) * self.speed_mult
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

# ────────────────────────────────────────────────────────────────
# Global variables
# ────────────────────────────────────────────────────────────────
frame_count = 0
mountains_offset = 0.0
hills_offset = 0.0
ground_offset = 0.0
scroll_direction = 0
current_level = 1
bees = create_bees_for_level(current_level)

# Starfield (only used in level 2)
stars = []
random.seed(42)
for i in range(120):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, 100)
    base_bright = 7
    size = random.choice([1, 1, 2])
    phase = random.uniform(0, 2 * math.pi) if random.random() < 0.3 else None
    stars.append((x, y, base_bright, size, phase))

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

    # Update scrolling offsets
    if scroll_direction != 0:
        if frame_count % 8 == 0:
            mountains_offset += scroll_direction
        if frame_count % 4 == 0:
            hills_offset += scroll_direction
        ground_offset += scroll_direction   # doubled speed

    low_res.fill((0,0,0))

    # ── Sky & special elements per level ───────────────────────────
    if current_level == 1:
        for y in range(HEIGHT):
            t = y / HEIGHT
            col = (
                int(135 + (255-135)*t),
                int(206 + (255-206)*t),
                int(235 + (255-235)*t)
            )
            pygame.draw.line(low_res, col, (0,y), (WIDTH,y))
        sun_center = (40, 40)
        pygame.draw.circle(low_res, (255,255,0), sun_center, 24)
        pygame.draw.circle(low_res, (255,220,80), sun_center, 18)

    elif current_level == 2:
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
        low_res.fill((211,211,211))

    elif current_level == 4:
        for y in range(HEIGHT):
            t = y / HEIGHT
            col = (
                int(200 + (255-200)*t),
                int(0 + (100-0)*t),
                int(0 + (50-0)*t)
            )
            pygame.draw.line(low_res, col, (0,y), (WIDTH,y))
        moon_center = (WIDTH - 50, 50)
        pygame.draw.circle(low_res, (240,240,240), moon_center, 28)
        pygame.draw.circle(low_res, (220,220,220), moon_center, 22)

    # ── Parallax layers ────────────────────────────────────────────
    # Mountains (slow)
    for px in range(-80, WIDTH + 80):
        world_x = px + mountains_offset
        h1 = 50 * math.sin(world_x * 0.008)
        h2 = 35 * math.sin(world_x * 0.022 + 1.2)
        h3 = 18 * math.sin(world_x * 0.045 + 3.0)
        mountain_y = 55 + int(h1 + h2 + h3)
        screen_x = int(px)
        if 0 <= screen_x < WIDTH and mountain_y < HEIGHT:
            pygame.draw.rect(low_res, PALETTE[1], (screen_x, mountain_y, 1, HEIGHT - mountain_y))

    # Hills (medium)
    for px in range(-80, WIDTH + 80):
        world_x = px + hills_offset
        h = 19.2 * math.sin(world_x * 0.04) + 14.4 * math.sin(world_x * 0.075 + 1.8)
        y = 138 + int(h)
        col_idx = 2 if h > -8 else 3
        screen_x = int(px)
        if 0 <= screen_x < WIDTH:
            pygame.draw.rect(low_res, PALETTE[col_idx], (screen_x, y, 1, HEIGHT - y + 50))

    # Ground (fast)
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

    # ── Dinosaur ────────────────────────────────────────────────────
    # Update facing when moving
    if scroll_direction != 0:
        facing_right = (scroll_direction == 1)
        last_scroll_direction = scroll_direction

    # Animate only when moving
    if scroll_direction != 0:
        dino_anim_timer += 1
        if dino_anim_timer >= anim_delay:
            dino_anim_timer = 0
            dino_frame_idx = (dino_frame_idx + 1) % len(dino_frames)
    else:
        dino_anim_timer = 0  # reset timer when stopped

    # Get current frame and flip if necessary
    current_frame = dino_frames[dino_frame_idx]
    if not facing_right:
        current_frame = pygame.transform.flip(current_frame, True, False)

    # Calculate ground height under dinosaur
    dino_world_x = ground_offset + dino_screen_x
    lump = 4.2 * math.sin(dino_world_x * 0.09) + 3.0 * math.cos(dino_world_x * 0.16)
    ground_y = 200 + int(lump)

    # Position so feet rest on ground
    dino_screen_y = ground_y - scaled_height

    # Draw dinosaur centered horizontally
    low_res.blit(current_frame, (dino_screen_x - scaled_width // 2, dino_screen_y))

    # ── Level indicator ─────────────────────────────────────────────
    level_text = font.render(f"Level {current_level}", True, (255,255,255))
    low_res.blit(level_text, (WIDTH - level_text.get_width() - 8, HEIGHT - level_text.get_height() - 4))

    # Final blit & flip
    pygame.transform.scale(low_res, win.get_size(), win)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
