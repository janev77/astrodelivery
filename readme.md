# AstroDelivery 2D Game in PyGame
### Subject: Programming of video games
### Faculty of Computer Science and Engineering - Skopje


Spaceship controlled by the player needs to avoid rotating asteroids and
deliver stars to the space-station for which gets points. 
Also the player needs to keep an eye on the fuel level and collect gas tanks 
in order to keep delivering and complete the level.

<hr>

## Requirements
 - Python 3.8+
 - Pygame
```bash
pip install pygame
```

## Executing
```bash
python main.py
```

## Project Structure

```
astro-delivery/
├── game.py
└── images/
    ├── spaceship.png
    ├── star.png
    ├── star_collected.png
    ├── asteroid.png
    ├── space_station.png
    ├── fuel_tank.png
    ├── background.png
    ├── bullet.png        
    └── boss.png          
```

## Controls

| Key              | Action |
|------------------|--------|
| `LEFT` / `RIGHT` | Rotate ship |
| `UP`             | Thrust forward |
| `DOWN`           | Thrust backward |
| `SPACE`          | Shoot (Level 3 only) |
| `R`              | Restart |
| `ESC`            | Quit |


## Levels

**Level 1** — Deliver 3 stars to the station. 3 asteroids, 3 fuel packs.

**Level 2** — Deliver 5 stars. Asteroids are faster, only 2 fuel packs.

**Level 3** — No station. Pick up the star and shoot it at the boss 
with `SPACE`. Hit the boss 5 times to win because it chases you and shoots back.



## Fuel

Fuel is shown as a green bar at the top of the screen. Thrusting drains it. Forward thrust costs more than backward. Fuel packs are scattered around the map. If you run out and your ship stops completely, it's game over.

## Scoring

1 point per delivery in levels 1 and 2. Final score shown on the end screen.

## Debug

To start at a specific level, set `DEBUG_START_LEVEL` near the top of `game.py`:

```python
DEBUG_START_LEVEL = None  # change to 1, 2, or 3
```

## Notes

- Resolution: 1400x800
- The world wraps — fly off one edge and you come out the other side
- Collision is rectangle-based for all entities



<br>

<hr>
Project by:

Aleksandar Janev 221258<br>
Ilija Chamevski 222125


