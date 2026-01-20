import pygame
import sys
import os

# ==================== CONFIG ====================
# Local path – assumes you're running from the project root folder
SPRITE_PATH = os.path.join("assets", "dino-sprite-sheet.png")

# ← You MUST update these based on your actual sprite sheet!
FRAME_WIDTH   = 96     # width of ONE frame in pixels (example – measure yours)
FRAME_HEIGHT  = 96     # height of ONE frame in pixels
NUM_FRAMES    = 8      # total number of frames in the horizontal strip

FPS           = 12     # animation speed (frames per second when moving)

WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
BG_COLOR      = (0, 0, 0)          # black placeholder for now

MOVE_SPEED    = 4                      # pixels per frame when holding arrow key
# ================================================

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur vs Bees – Animation Test")
clock = pygame.time.Clock()

# Load sprite sheet locally
try:
    sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
    print(f"Successfully loaded: {SPRITE_PATH}")
except pygame.error as e:
    print(f"Error loading sprite sheet: {e}")
    print("Check that:")
    print("  - You're running from the project root folder")
    print("  - assets/dino-sprite-sheet.png exists")
    sys.exit(1)

# Extract frames (assuming horizontal strip: frames side-by-side from left to right)
frames_right = []
for i in range(NUM_FRAMES):
    rect = pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
    frame = sheet.subsurface(rect)
    frames_right.append(frame)

# Create left-facing versions by flipping horizontally
frames_left = [pygame.transform.flip(f, True, False) for f in frames_right]

# Starting position & animation state
current_frame = 0
frame_timer   = 0
facing_right  = True
x_pos         = WINDOW_WIDTH // 2 - FRAME_WIDTH // 2
y_pos         = WINDOW_HEIGHT - FRAME_HEIGHT - 40   # near bottom – adjust if needed

running = True
while running:
    dt = clock.tick(60) / 1000.0   # ~60 FPS loop

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

    # Advance animation only when moving
    if moving:
        frame_timer += dt
        if frame_timer >= 1 / FPS:
            frame_timer -= 1 / FPS
            current_frame = (current_frame + 1) % NUM_FRAMES

    # Draw everything
    screen.fill(BG_COLOR)

    current_sprite = frames_right[current_frame] if facing_right else frames_left[current_frame]
    screen.blit(current_sprite, (x_pos, y_pos))

    pygame.display.flip()

pygame.quit()
sys.exit()
