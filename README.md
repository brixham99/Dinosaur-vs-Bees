# Dinosaur vs Bees

Retro-style arcade game built with Python & Pygame.  
A long-necked dinosaur defends against swarms of bees in a scrolling volcanic landscape.

## Current State (January 2026)
- 256×224 resolution, 60 fps
- 3-layer parallax scrolling (mountains, hills, ground)
- Static starfield sky
- Arrow keys: left/right to scroll direction
- Q to quit
- Very gentle pace (eighth original speed)

## Tech
- Python 3 + Pygame
- No external assets yet (placeholders procedural)

## To Do
- Load dinosaur sprite (fixed position, neck movement)
- Bee enemies (various sizes, directions)
- Collision & scoring
- Lava glow effects
- Multiple levels / landscapes

Run with:
```bash
pip install pygame
python main.py
