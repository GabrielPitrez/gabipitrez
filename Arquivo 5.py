import pygame
import math


pygame.init()

WIDTH, HEIGHT =  800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)

class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 250 / AU  # 1AU = 100 pixels
    TIMESTEP = 3600*24 # 1 day

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (x, y), self.radius)
        
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)}km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))


def main():
    run = True
    clock = pygame.time.Clock()

    planets = []
    creating_planet = False
    mouse_start_pos = None
    planet_radius = 8
    planet_mass = 1e24

    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True
    planets.append(sun)

    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_start_pos = pygame.mouse.get_pos()
                    creating_planet = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    creating_planet = False
                    mouse_end_pos = pygame.mouse.get_pos()
                    x1, y1 = mouse_start_pos
                    x2, y2 = mouse_end_pos
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx**2 + dy**2)
                    angle = math.atan2(dy, dx)
                    x = (x1 + x2) / 2
                    y = (y1 + y2) / 2
                    x_vel = math.cos(angle) * distance / Planet.SCALE / Planet.TIMESTEP
                    y_vel = math.sin(angle) * distance / Planet.SCALE / Planet.TIMESTEP
                    new_planet = Planet((x - WIDTH / 2) / Planet.SCALE, (y - HEIGHT / 2) / Planet.SCALE, planet_radius, DARK_GREY, planet_mass)
                    new_planet.x_vel = x_vel
                    new_planet.y_vel = y_vel
                    planets.append(new_planet)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    planet_mass *= 10
                elif event.key == pygame.K_DOWN:
                    planet_mass /= 10

        for planet in planets:
            if planet.sun == False:
                planet.update_position(planets)
            planet.draw(WIN)

        if creating_planet:
            mouse_end_pos = pygame.mouse.get_pos()
            x1, y1 = mouse_start_pos
            x2, y2 = mouse_end_pos
            pygame.draw.line(WIN, WHITE, mouse_start_pos, mouse_end_pos, 1)
            pygame.draw.circle(WIN, DARK_GREY, ((x1 + x2) // 2, (y1 + y2) // 2), planet_radius)

        pygame.display.update()

    pygame.quit()


main()