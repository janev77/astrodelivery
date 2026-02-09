import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 13)
BLUE = (0, 0, 255)

GRAY = (129, 133, 137)
YELLOW = (255, 234, 5)


#Da izleze od druga strana
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

    ship_x, ship_y = WIDTH // 2, HEIGHT // 2
    ship_vx, ship_vy = 0, 0
    fuel = 100
    score = 0
    carrying = False
    game_over = False

    star_x, star_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
    station_x, station_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
    asteroids = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(3)]
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

            if keys[pygame.K_LEFT] and fuel > 0:
                ship_vx -= 0.5
                fuel -= 0.2
            if keys[pygame.K_RIGHT] and fuel > 0:
                ship_vx += 0.5
                fuel -= 0.2
            if keys[pygame.K_UP] and fuel > 0:
                ship_vy -= 0.5
                fuel -= 0.2
            if keys[pygame.K_DOWN] and fuel > 0:
                ship_vy += 0.5
                fuel -= 0.2

            #Gravitacija
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

            ship_rect = pygame.Rect(ship_x - 10, ship_y - 10, 20, 20)

            for ast in asteroids:
                ast_rect = pygame.Rect(ast[0] - 30, ast[1] - 30, 60, 60)
                if ship_rect.colliderect(ast_rect):
                    game_over = True

            for fp in fuel_packs:
                fp_rect = pygame.Rect(fp[0] - 8, fp[1] - 10, 16, 20)
                if ship_rect.colliderect(fp_rect):
                    fuel = min(fuel + 30, 100)
                    fp[0], fp[1] = random.randint(0, WIDTH), random.randint(0, HEIGHT)

            star_rect = pygame.Rect(star_x - 12, star_y - 12, 24, 24)
            if not carrying and ship_rect.colliderect(star_rect):
                carrying = True

            station_rect = pygame.Rect(station_x - 25, station_y - 25, 50, 50)
            if carrying and ship_rect.colliderect(station_rect):
                carrying = False
                score += 1
                star_x, star_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)
                station_x, station_y = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)

            if fuel <= 0 and speed < 0.1:
                game_over = True

        screen.fill(BLACK)

        #Stanica
        pygame.draw.rect(screen, BLUE, (station_x - 25, station_y - 25, 50, 50), 3)

        if not carrying:
            pygame.draw.circle(screen, YELLOW, (int(star_x), int(star_y)), 12)

        for fp in fuel_packs:
            pygame.draw.rect(screen, RED, (fp[0] - 8, fp[1] - 10, 16, 20), border_radius=5)

        for ast in asteroids:
            pygame.draw.circle(screen, GRAY, (int(ast[0]), int(ast[1])), 30)

        ship_color = YELLOW if carrying else WHITE
        ship_pts = [(ship_x, ship_y - 15), (ship_x - 10, ship_y + 10), (ship_x + 10, ship_y + 10)]
        pygame.draw.polygon(screen, ship_color, ship_pts, 2)

        #Gorivo
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

        pygame.display.flip()


if __name__ == "__main__":
    main()