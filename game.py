import random
import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1600, 800
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 13)
BLUE = (0, 0, 255)

GRAY = (129, 133, 137)
YELLOW = (255, 234, 5)


# Da izleze od stranite
def wrap(x, y):
    return x % WIDTH, y % HEIGHT


def dist(x1, y1, x2, y2):
    dx, dy = x1 - x2, y1 - y2
    return (dx * dx + dy * dy) ** 0.5


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
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
        print(
            "Error loading images. Make sure all images are in the images folder.")
        return

    ship_x, ship_y = WIDTH // 2, HEIGHT // 2
    ship_vx, ship_vy = 0, 0
    ship_angle = 0  # Rotation angle
    fuel = 100
    score = 0
    carrying = False
    game_over = False

    star_x, star_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
    station_x, station_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
    asteroids = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(-1, 1), random.uniform(-1, 1)] for
                 _ in range(3)]
    fuel_packs = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(3)]

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_r and game_over:
                    return main()

        keys = pygame.key.get_pressed()

        if not game_over:
            # Rotation controls
            if keys[pygame.K_LEFT]:
                ship_angle += 3  # Rotate counterclockwise
            if keys[pygame.K_RIGHT]:
                ship_angle -= 3  # Rotate clockwise

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

            # Gravitacija
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
                ast_rect = pygame.Rect(ast[0] - 70, ast[1] - 70, 140, 140)
                if ship_rect.colliderect(ast_rect):
                    game_over = True

            for fp in fuel_packs:
                fp_rect = pygame.Rect(fp[0] - 30, fp[1] - 30, 60, 60)
                if ship_rect.colliderect(fp_rect):
                    fuel = min(fuel + 30, 100)
                    fp[0], fp[1] = random.randint(0, WIDTH), random.randint(0, HEIGHT)

            star_rect = pygame.Rect(star_x - 25, star_y - 25, 50, 50)
            if not carrying and ship_rect.colliderect(star_rect):
                carrying = True

            station_rect = pygame.Rect(station_x - 55, station_y - 55, 110, 110)
            if carrying and ship_rect.colliderect(station_rect):
                carrying = False
                score += 1
                star_x, star_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
                station_x, station_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)

            if fuel <= 0 and speed < 0.1:
                game_over = True

        screen.blit(background, (0, 0))

        screen.blit(station_img, (station_x - 75, station_y - 75))

        if not carrying:
            screen.blit(star_img, (int(star_x) - 40, int(star_y) - 40))

        for fp in fuel_packs:
            screen.blit(fuel_tank_img, (fp[0] - 30, fp[1] - 30))

        for ast in asteroids:
            screen.blit(asteroid_img, (int(ast[0]) - 100, int(ast[1]) - 100))

        rotated_ship = pygame.transform.rotate(spaceship_img, ship_angle)
        rotated_rect = rotated_ship.get_rect(center=(ship_x, ship_y))
        screen.blit(rotated_ship, rotated_rect.topleft)

        if carrying:
            pygame.draw.circle(screen, YELLOW, (int(ship_x), int(ship_y - 60)), 8)
            pygame.draw.circle(screen, (255, 255, 150), (int(ship_x), int(ship_y - 60)), 5)

        # Gorivo
        bar_w = int((fuel / 100) * 150)
        bar_x = WIDTH // 2 - 75
        pygame.draw.rect(screen, GREEN, (bar_x, 20, bar_w, 15))
        pygame.draw.rect(screen, WHITE, (bar_x, 20, 150, 15), 2)

        txt = font.render(f"Score: {score}", True, WHITE)
        screen.blit(txt, (WIDTH - 150, 20))
        game_txt = font.render("Astro Delivery", True, WHITE)
        screen.blit(game_txt, (20, 20))

        if game_over:
            msg = font.render(f"GAME OVER", True, RED)
            msg2 = font.render(f"Score: {score}", True, WHITE)
            msg3 = font.render("Press R to restart", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 50))

            # sredi kometi, dzvezdi i gorivo so sliki                    #SREDENO
            # sredi podobar UI za zavrshuvanje i pochnuvanje na igra
            # sredi sredi pozadina, dodadi 3 nivoa, i final boss
            # zapazi ist stil da se slikite shto ke se koristat.

        pygame.display.flip()


if __name__ == "__main__":
    main()