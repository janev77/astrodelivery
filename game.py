import random
import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1400, 800
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 13)
BLUE = (0, 0, 255)

GRAY = (129, 133, 137)
YELLOW = (255, 234, 5)

SAFE_SPAWN_DISTANCE = 320

# 1, 2, 3, None(default) for debugging purposes
DEBUG_START_LEVEL = None


def wrap(x, y):
    return x % WIDTH, y % HEIGHT


def dist(x1, y1, x2, y2):
    dx, dy = x1 - x2, y1 - y2
    return (dx * dx + dy * dy) ** 0.5


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def rand_pos(pad=100):
    return random.randint(pad, WIDTH - pad), random.randint(pad, HEIGHT - pad)


def safe_rand_pos(avoid_x, avoid_y, min_d=SAFE_SPAWN_DISTANCE, pad=100, tries=120):
    for _ in range(tries):
        x, y = rand_pos(pad)
        if dist(x, y, avoid_x, avoid_y) >= min_d:
            return x, y
    return rand_pos(pad)


def rand_asteroid_size():
    size = random.randint(80, 200)
    return size, size


def level_config(level):
    if level == 1:
        return {
            "deliveries_needed": 3,
            "asteroids_count": 3,
            "asteroids_speed": (0.7, 1.3),
            "fuel_packs": 3
        }
    if level == 2:
        return {
            "deliveries_needed": 5,
            "asteroids_count": 5,
            "asteroids_speed": (1.0, 1.8),
            "fuel_packs": 2
        }
    return {
        "deliveries_needed": 0,
        "asteroids_count": 4,
        "asteroids_speed": (1.0, 2.0),
        "fuel_packs": 2,

        "boss_hp": 5,
        "boss_speed": 1.0,
        "boss_shoot_cd": 120,
        "boss_bullet_speed": 6.0
    }


def draw_center_text(screen, font, text, y, color=WHITE):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def draw_overlay(screen, alpha=220):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))


def get_bullet_angle(vx, vy):
    return -math.degrees(math.atan2(vy, vx)) - 90


NEXT_LEVEL_INSTRUCTIONS = {
    #Between level 1 and level 2
    1: [
        ("LEVEL 2 - MORE STARS, MORE ASTEROIDS!", YELLOW),
        ("Deliver  5  stars  to  the  station  to  complete  the  level.", WHITE),
        ("Watch out — asteroids are faster and there are more of them.", WHITE),
        ("Only  2  fuel  packs  available,  so  fly  efficiently!", WHITE),
    ],
    # Between level 2 and level 3
    2: [
        ("LEVEL 3 - BOSS BATTLE!", YELLOW),
        ("There is no station.  Pick up the STAR to load your weapon.", WHITE),
        ("Press  SPACE  to  fire  the  star  at  the  boss.", WHITE),
        ("Hit the boss  5  times  to  defeat  it.  Don't get hit!", WHITE),
        ("The boss chases you and shoots — keep moving!", WHITE),
    ],
}


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 80)
    pygame.display.set_caption("Astro Delivery")

    try:
        spaceship_img = pygame.image.load("images/spaceship.png").convert_alpha()
        star_img = pygame.image.load("images/star.png").convert_alpha()
        asteroid_img = pygame.image.load("images/asteroid.png").convert_alpha()
        station_img = pygame.image.load("images/space_station.png").convert_alpha()
        fuel_tank_img = pygame.image.load("images/fuel_tank.png").convert_alpha()
        background = pygame.image.load("images/background.png").convert_alpha()

        spaceship_img = pygame.transform.smoothscale(spaceship_img, (100, 100))
        star_img = pygame.transform.smoothscale(star_img, (40, 40))
        asteroid_img = pygame.transform.smoothscale(asteroid_img, (200, 200))
        station_img = pygame.transform.smoothscale(station_img, (150, 150))
        fuel_tank_img = pygame.transform.smoothscale(fuel_tank_img, (60, 60))
        background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
    except:
        print("Error loading images. Make sure all images are in the images folder.")
        return

    player_bullet_img_base = pygame.transform.smoothscale(star_img, (30, 30))

    try:
        bullet_img_base = pygame.image.load("images/bullet.png").convert_alpha()
        bullet_img_base = pygame.transform.smoothscale(bullet_img_base, (50, 50))
        boss_bullet_img_base = pygame.transform.smoothscale(bullet_img_base, (50, 50))
        use_bullet_img = True
    except:
        use_bullet_img = False

    try:
        boss_img = pygame.image.load("images/boss.png").convert_alpha()
        boss_img = pygame.transform.smoothscale(boss_img, (230, 230))
    except:
        boss_img = pygame.transform.smoothscale(asteroid_img, (230, 230))

    state = "MENU"
    level = 1
    score = 0
    menu_option = 0
    MENU_OPTIONS = ["Start Game", "Quit"]

    ship_x, ship_y = WIDTH // 2, HEIGHT // 2
    ship_vx, ship_vy = 0.0, 0.0
    ship_angle = 0
    fuel = 100.0
    carrying = False

    star_x, star_y = rand_pos()
    station_x, station_y = rand_pos()
    asteroids = []
    fuel_packs = []

    deliveries_done = 0
    deliveries_needed = 3

    boss_active = False
    boss_x, boss_y = WIDTH // 2, 120
    boss_vx, boss_vy = 0.0, 0.0
    boss_hp = 0
    boss_shoot_timer = 0
    boss_bullets = []

    player_bullets = []
    shoot_cd = 0

    def reset_ship(full=True):
        nonlocal ship_x, ship_y, ship_vx, ship_vy, ship_angle, fuel, carrying
        ship_x, ship_y = WIDTH // 2, HEIGHT // 2
        ship_vx, ship_vy = 0.0, 0.0
        ship_angle = 0
        carrying = False
        if full:
            fuel = 100.0

    def setup_level(lvl):
        nonlocal star_x, star_y, station_x, station_y, asteroids, fuel_packs
        nonlocal deliveries_done, deliveries_needed, boss_active
        nonlocal boss_x, boss_y, boss_vx, boss_vy, boss_hp
        nonlocal boss_shoot_timer, boss_bullets
        nonlocal player_bullets, shoot_cd
        nonlocal carrying

        cfg = level_config(lvl)

        reset_ship(full=True)
        player_bullets = []
        shoot_cd = 0
        carrying = False

        deliveries_done = 0
        deliveries_needed = cfg.get("deliveries_needed", 0)

        star_x, star_y = safe_rand_pos(ship_x, ship_y, min_d=SAFE_SPAWN_DISTANCE + 40)

        if lvl in (1, 2):
            station_x, station_y = safe_rand_pos(ship_x, ship_y, min_d=SAFE_SPAWN_DISTANCE + 40)
        else:
            station_x, station_y = -9999, -9999

        asteroids = []
        for _ in range(cfg["asteroids_count"]):
            ax, ay = safe_rand_pos(ship_x, ship_y, min_d=360)
            sx = random.uniform(cfg["asteroids_speed"][0], cfg["asteroids_speed"][1])
            sy = random.uniform(cfg["asteroids_speed"][0], cfg["asteroids_speed"][1])
            vx = random.choice([-1, 1]) * sx
            vy = random.choice([-1, 1]) * sy
            w, h = rand_asteroid_size()
            asteroids.append([ax, ay, vx, vy, w, h])

        fuel_packs = []
        for _ in range(cfg["fuel_packs"]):
            fx, fy = safe_rand_pos(ship_x, ship_y, min_d=260)
            fuel_packs.append([fx, fy])

        boss_active = (lvl == 3)
        boss_bullets = []
        boss_shoot_timer = 0

        if boss_active:
            boss_x, boss_y = safe_rand_pos(ship_x, ship_y, min_d=480)
            boss_vx, boss_vy = 0.0, 0.0
            boss_hp = cfg["boss_hp"]

            star_x, star_y = safe_rand_pos(boss_x, boss_y, min_d=420)

    if DEBUG_START_LEVEL in (1, 2, 3):
        level = DEBUG_START_LEVEL
        score = 0
        state = "PLAY"
        setup_level(level)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if state == "MENU":
                    if event.key == pygame.K_UP:
                        menu_option = (menu_option - 1) % len(MENU_OPTIONS)
                    if event.key == pygame.K_DOWN:
                        menu_option = (menu_option + 1) % len(MENU_OPTIONS)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if menu_option == 0:
                            state = "PLAY"
                            setup_level(level)
                        elif menu_option == 1:
                            return

                if event.key == pygame.K_r and state in ("GAME_OVER", "WIN"):
                    level = 1
                    score = 0
                    state = "PLAY"
                    setup_level(level)

                if event.key == pygame.K_SPACE and state == "LEVEL_COMPLETE":
                    level += 1
                    if level > 3:
                        level = 3
                    state = "PLAY"
                    setup_level(level)

                if event.key == pygame.K_SPACE and state == "PLAY" and level == 3 and carrying and shoot_cd == 0:
                    angle_rad = math.radians(-ship_angle + 90)

                    fx = -math.cos(angle_rad)
                    fy = -math.sin(angle_rad)

                    bullet_speed = 12
                    nose_offset = 55

                    bx = ship_x + fx * nose_offset
                    by = ship_y + fy * nose_offset
                    bvx = fx * bullet_speed + ship_vx
                    bvy = fy * bullet_speed + ship_vy

                    player_bullets.append([bx, by, bvx, bvy, 180, False])
                    carrying = False
                    star_x, star_y = safe_rand_pos(boss_x, boss_y, min_d=420)
                    shoot_cd = 12

        keys = pygame.key.get_pressed()

        if state == "PLAY":
            if shoot_cd > 0:
                shoot_cd -= 1

            if keys[pygame.K_LEFT]:
                ship_angle += 3

            if keys[pygame.K_RIGHT]:
                ship_angle -= 3

            if keys[pygame.K_DOWN] and fuel > 0:
                angle_rad = math.radians(-ship_angle + 90)
                ship_vx += math.cos(angle_rad) * 0.3
                ship_vy += math.sin(angle_rad) * 0.3
                fuel -= 0.2

            if keys[pygame.K_UP] and fuel > 0:
                angle_rad = math.radians(-ship_angle + 90)
                ship_vx -= math.cos(angle_rad) * 0.15
                ship_vy -= math.sin(angle_rad) * 0.15
                fuel -= 0.1

            ship_vx *= 0.98
            ship_vy *= 0.98

            speed = (ship_vx * ship_vx + ship_vy * ship_vy) ** 0.5
            if speed > 6:
                ship_vx = ship_vx / speed * 6
                ship_vy = ship_vy / speed * 6

            ship_x += ship_vx
            ship_y += ship_vy
            ship_x, ship_y = wrap(ship_x, ship_y)

            for ast in asteroids:
                ast[0] += ast[2]
                ast[1] += ast[3]
                ast[0], ast[1] = wrap(ast[0], ast[1])

            ship_rect = pygame.Rect(ship_x - 30, ship_y - 30, 60, 60)

            for ast in asteroids:
                ast_rect = pygame.Rect(ast[0] - ast[4]//2, ast[1] - ast[5]//2, ast[4], ast[5])
                if ship_rect.colliderect(ast_rect):
                    state = "GAME_OVER"

            for fp in fuel_packs:
                fp_rect = pygame.Rect(fp[0] - 30, fp[1] - 30, 60, 60)
                if ship_rect.colliderect(fp_rect):
                    fuel = min(fuel + 30, 100)
                    fp[0], fp[1] = rand_pos(100)

            star_rect = pygame.Rect(star_x - 25, star_y - 25, 50, 50)
            if not carrying and ship_rect.colliderect(star_rect):
                carrying = True

            cfg = level_config(level)

            if level in (1, 2):
                station_rect = pygame.Rect(station_x - 55, station_y - 55, 110, 110)
                if carrying and ship_rect.colliderect(station_rect):
                    carrying = False
                    deliveries_done += 1
                    score += 1

                    star_x, star_y = safe_rand_pos(station_x, station_y, min_d=320)
                    station_x, station_y = safe_rand_pos(ship_x, ship_y, min_d=320)

                    if deliveries_done >= deliveries_needed:
                        state = "LEVEL_COMPLETE"

            if boss_active:
                dx = ship_x - boss_x
                dy = ship_y - boss_y
                d = (dx * dx + dy * dy) ** 0.5 + 1e-6
                boss_speed = cfg["boss_speed"]

                boss_vx = (dx / d) * boss_speed
                boss_vy = (dy / d) * boss_speed
                boss_x += boss_vx
                boss_y += boss_vy
                boss_x, boss_y = wrap(boss_x, boss_y)

                boss_shoot_timer += 1
                if boss_shoot_timer >= cfg["boss_shoot_cd"]:
                    boss_shoot_timer = 0
                    bdx = ship_x - boss_x
                    bdy = ship_y - boss_y
                    bd = (bdx * bdx + bdy * bdy) ** 0.5 + 1e-6
                    bvx = (bdx / bd) * cfg["boss_bullet_speed"]
                    bvy = (bdy / bd) * cfg["boss_bullet_speed"]
                    boss_bullets.append([boss_x, boss_y, bvx, bvy])

                new_bullets = []
                for b in boss_bullets:
                    b[0] += b[2]
                    b[1] += b[3]

                    if b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                        continue

                    bullet_rect = pygame.Rect(b[0] - 6, b[1] - 6, 12, 12)
                    if ship_rect.colliderect(bullet_rect):
                        state = "GAME_OVER"
                        break

                    new_bullets.append(b)
                boss_bullets = new_bullets

                boss_rect = pygame.Rect(boss_x - 110, boss_y - 110, 220, 220)
                if ship_rect.colliderect(boss_rect):
                    state = "GAME_OVER"

            new_player_bullets = []

            for pb in player_bullets:
                x, y, vx, vy, life, stuck = pb

                if not stuck:
                    x += vx
                    y += vy
                    life -= 1

                    if boss_active:
                        boss_rect = pygame.Rect(boss_x - 110, boss_y - 110, 220, 220)
                        bullet_rect = pygame.Rect(x - 6, y - 6, 12, 12)
                        if bullet_rect.colliderect(boss_rect):
                            boss_hp -= 1
                            if boss_hp <= 0:
                                state = "WIN"
                            continue

                    if (x < 0 or x > WIDTH or y < 0 or y > HEIGHT) or (life <= 0):
                        stuck = True
                        vx = 0
                        vy = 0
                        x = clamp(x, 0, WIDTH)
                        y = clamp(y, 0, HEIGHT)

                new_player_bullets.append([x, y, vx, vy, life, stuck])

            player_bullets = new_player_bullets

            speed = (ship_vx * ship_vx + ship_vy * ship_vy) ** 0.5
            if fuel <= 0 and speed < 0.1 and state == "PLAY":
                state = "GAME_OVER"

            fuel = clamp(fuel, 0, 100)

        screen.blit(background, (0, 0))

        if level in (1, 2):
            screen.blit(station_img, (station_x - 75, station_y - 75))

        if not carrying:
            screen.blit(star_img, (int(star_x) - 40, int(star_y) - 40))

        for fp in fuel_packs:
            screen.blit(fuel_tank_img, (fp[0] - 30, fp[1] - 30))

        for ast in asteroids:
            scaled_ast = pygame.transform.smoothscale(asteroid_img, (ast[4], ast[5]))
            screen.blit(scaled_ast, (int(ast[0]) - ast[4]//2, int(ast[1]) - ast[5]//2))

        if boss_active:
            screen.blit(boss_img, (int(boss_x) - 130, int(boss_y) - 130))
            for b in boss_bullets:
                if use_bullet_img:
                    angle = get_bullet_angle(b[2], b[3])
                    rotated = pygame.transform.rotate(boss_bullet_img_base, angle)
                    rect = rotated.get_rect(center=(int(b[0]), int(b[1])))
                    screen.blit(rotated, rect.topleft)
                else:
                    pygame.draw.circle(screen, RED, (int(b[0]), int(b[1])), 6)

        for pb in player_bullets:
            rotated = pygame.transform.rotate(player_bullet_img_base, get_bullet_angle(pb[2], pb[3]))
            rect = rotated.get_rect(center=(int(pb[0]), int(pb[1])))
            screen.blit(rotated, rect.topleft)

        rotated_ship = pygame.transform.rotate(spaceship_img, ship_angle)
        rotated_rect = rotated_ship.get_rect(center=(ship_x, ship_y))
        screen.blit(rotated_ship, rotated_rect.topleft)

        if carrying:
            screen.blit(star_img, (int(ship_x) - 20, int(ship_y) - 75))

        bar_w = int((fuel / 100) * 150)
        bar_x = WIDTH // 2 - 75
        pygame.draw.rect(screen, GREEN, (bar_x, 20, bar_w, 15))
        pygame.draw.rect(screen, WHITE, (bar_x, 20, 150, 15), 2)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH - 160, 20))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 160, 55))
        screen.blit(font.render("Astro Delivery", True, WHITE), (20, 20))

        if level in (1, 2):
            screen.blit(font.render(f"Deliveries: {deliveries_done}/{deliveries_needed}", True, WHITE), (20, 55))
        else:
            if boss_active:
                screen.blit(font.render(f"BOSS HP: {boss_hp}", True, RED), (20, 55))
                screen.blit(font.render("Level 3: Pick STAR -> SPACE to shoot", True, WHITE), (20, 85))

        if state == "MENU":
            screen.blit(background, (0, 0))
            draw_overlay(screen, alpha=200)

            draw_center_text(screen, big_font, "ASTRO DELIVERY", HEIGHT // 2 - 230, YELLOW)

            draw_center_text(screen, font, "CONTROLS:", HEIGHT // 2 - 155, WHITE)
            draw_center_text(screen, font, "LEFT / RIGHT - Rotate ship", HEIGHT // 2 - 125, WHITE)
            draw_center_text(screen, font, "UP / DOWN - Thrust", HEIGHT // 2 - 95, WHITE)
            draw_center_text(screen, font, "SPACE - Shoot (Level 3)", HEIGHT // 2 - 65, WHITE)

            draw_center_text(screen, font, "LEVEL 1-2: Pick up the STAR and deliver to the STATION", HEIGHT // 2 - 20, WHITE)
            draw_center_text(screen, font, "LEVEL 3: Pick STAR -> SPACE to shoot the boss", HEIGHT // 2 + 10, WHITE)

            option_start_y = HEIGHT // 2 + 80
            option_gap = 75
            for i, option in enumerate(MENU_OPTIONS):
                if i == menu_option:
                    opt_surf = big_font.render(option, True, WHITE)
                    opt_x = WIDTH // 2 - opt_surf.get_width() // 2
                    opt_y = option_start_y + i * option_gap

                    glow = pygame.Surface((opt_surf.get_width() + 40, opt_surf.get_height() + 10), pygame.SRCALPHA)
                    glow.fill(GRAY)
                    screen.blit(glow, (opt_x - 20, opt_y - 5))
                    screen.blit(opt_surf, (opt_x, opt_y))

                else:
                    opt_surf = big_font.render(option, True, GRAY)
                    opt_x = WIDTH // 2 - opt_surf.get_width() // 2
                    screen.blit(opt_surf, (opt_x, option_start_y + i * option_gap))

            pygame.display.flip()
            continue

        if state == "LEVEL_COMPLETE":
            draw_overlay(screen, alpha=200)
            draw_center_text(screen, big_font, f"LEVEL {level} COMPLETE!", HEIGHT // 2 - 180, YELLOW)

            instructions = NEXT_LEVEL_INSTRUCTIONS.get(level)
            if instructions:
                inst_y = HEIGHT // 2 - 95
                line_gap = 38
                for line_text, line_color in instructions:
                    draw_center_text(screen, font, line_text, inst_y, line_color)
                    inst_y += line_gap
            else:
                draw_center_text(screen, font, "Get ready for the next challenge!", HEIGHT // 2 - 10, WHITE)

            draw_center_text(screen, font, "Press SPACE to continue", HEIGHT // 2 + 105, WHITE)
            draw_center_text(screen, font, "ESC to quit", HEIGHT // 2 + 140, WHITE)

        if state == "GAME_OVER":
            draw_overlay(screen, alpha=200)
            draw_center_text(screen, big_font, "GAME OVER", HEIGHT // 2 - 90, RED)
            draw_center_text(screen, font, f"Score: {score}", HEIGHT // 2 - 10, WHITE)
            draw_center_text(screen, font, "Press R to restart", HEIGHT // 2 + 30, WHITE)
            draw_center_text(screen, font, "ESC to quit", HEIGHT // 2 + 65, WHITE)

        if state == "WIN":
            draw_overlay(screen, alpha=200)
            draw_center_text(screen, big_font, "YOU WIN!", HEIGHT // 2 - 110, GREEN)
            draw_center_text(screen, font, "Final Boss defeated", HEIGHT // 2 - 30, WHITE)
            draw_center_text(screen, font, f"Score: {score}", HEIGHT // 2 + 10, WHITE)
            draw_center_text(screen, font, "Press R to play again", HEIGHT // 2 + 45, WHITE)
            draw_center_text(screen, font, "ESC to quit", HEIGHT // 2 + 80, WHITE)

        pygame.display.flip()


if __name__ == "__main__":
    main()