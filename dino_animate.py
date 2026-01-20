import pygame
import sys
import os

# ==================== CONFIG ====================
SPRITE_PATH = os.path.join("assets", "dino-sprite-sheet.png")

FRAME_WIDTH   = 212
FRAME_HEIGHT  = 160
NUM_FRAMES    = 13          # total across all rows
FPS           = 10          # adjust as needed (slower/faster walk)

WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
BG_COLOR      = (0, 0, 0)   # placeholder — later sky/gradient

MOVE_SPEED    = 4
# ================================================

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur vs Bees – Animation Test")
clock = pygame.time.Clock()

# Load sprite sheet
try:
    sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
    print(f"Loaded: {SPRITE_PATH} ({sheet.get_width()}×{sheet.get_height()})")
except pygame.error as e:
    print(f"Error: {e}")
    sys.exit(1)

# Extract all 13 frames (row-major order)
frames_right = []

# Row 0: frames 0–4
for col in range(5):
    rect = pygame.Rect(col * FRAME_WIDTH, 0 * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
    frames_right.append(sheet.subsurface(rect))

# Row 1: frames 5–9
for col in range(5):
    rect = pygame.Rect(col * FRAME_WIDTH, 1 * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
    frames_right.append(sheet.subsurface(rect))

# Row 2: frames 10–12
for col in range(3):
    rect = pygame.Rect(col * FRAME_WIDTH, 2 * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)
    frames_right.append(sheet.subsurface(rect))

# Create flipped versions for left-facing
frames_left = [pygame.transform.flip(f, True, False) for f in frames_right]

# Animation & position state
current_frame = 0
frame_timer   = 0
facing_right  = True
x_pos         = WINDOW_WIDTH // 2 - FRAME_WIDTH // 2
y_pos         = WINDOW_HEIGHT - FRAME_HEIGHT - 20   # near bottom, tweak if cut off

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        x_pos -= MOVE_SPEED
        facing_right = False
        moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x_pos += MOVE_SPEED
        facing_right = True
        moving = True

    if moving:
        frame_timer += dt
        if frame_timer >= 1 / FPS:
            frame_timer -= 1 / FPS
            current_frame = (current_frame + 1) % NUM_FRAMES

    screen.fill(BG_COLOR)

    current_sprite = frames_right[current_frame] if facing_right else frames_left[current_frame]
    screen.blit(current_sprite, (x_pos, y_pos))

    pygame.display.flip()

pygame.quit()
sys.exit()
