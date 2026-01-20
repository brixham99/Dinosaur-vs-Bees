import pygame
import sys
import os
import urllib.request

# ==================== CONFIG ====================
# Once you push the sprite sheet to assets/, update this filename if needed
SPRITE_FILENAME = "dino-sprite-sheet.png"
RAW_URL = f"https://raw.githubusercontent.com/brixham99/Dinosaur-vs-Bees/main/assets/{SPRITE_FILENAME}"

# If testing locally before push, you can temporarily switch to local path:
# SPRITE_PATH = os.path.join("assets", SPRITE_FILENAME)

FRAME_WIDTH   = 96     # ← UPDATE: width of ONE frame in pixels
FRAME_HEIGHT  = 96     # ← UPDATE: height of ONE frame in pixels
NUM_FRAMES    = 8      # ← UPDATE: total frames in the horizontal strip
FPS           = 12     # animation speed

WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
BG_COLOR      = (0, 0, 0)  # black placeholder — we'll add parallax later

MOVE_SPEED    = 4
# ================================================

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur vs Bees – Animation Test")
clock = pygame.time.Clock()

# Load sprite sheet from GitHub raw (downloads once)
try:
    with urllib.request.urlopen(RAW_URL) as response:
        sprite_data = response.read()
    # Save temporarily or load directly from bytes
    from io import BytesIO
    sheet = pygame.image.load(BytesIO(sprite_data)).convert_alpha()
    print(f"Loaded sprite sheet from: {RAW_URL}")
except Exception as e:
    print(f"Error loading from GitHub: {e}")
    print("Falling back — place the file locally in assets/ and uncomment local path above")
    sys.exit(1)

# Extract frames (horizontal strip assumed: frame 0 to NUM_FRAMES-1 left-to-right)
frames_right = []
for i in range(NUM_FRAMES):
    rect = pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    frame = sheet.subsurface(rect)
    frames_right.append(frame)

# Left-facing versions (horizontal flip)
frames_left = [pygame.transform.flip(f, True, False) for f in frames_right]

# Starting state
current_frame = 0
frame_timer   = 0
facing_right  = True
x_pos         = WINDOW_WIDTH // 2 - FRAME_WIDTH // 2
y_pos         = WINDOW_HEIGHT - FRAME_HEIGHT - 40  # near bottom, adjust as needed

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

    # Animate when moving
    if moving:
        frame_timer += dt
        if frame_timer >= 1 / FPS:
            frame_timer -= 1 / FPS
            current_frame = (current_frame + 1) % NUM_FRAMES

    # Render
    screen.fill(BG_COLOR)

    current_sprite = frames_right[current_frame] if facing_right else frames_left[current_frame]
    screen.blit(current_sprite, (x_pos, y_pos))

    pygame.display.flip()

pygame.quit()
sys.exit()
