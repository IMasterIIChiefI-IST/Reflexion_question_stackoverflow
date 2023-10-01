from pygame.locals import *
import pygame
import sys
import math
import random

pygame.init()

# -----Options-----
WINDOW_SIZE = (1200, 800)  # Width x Height in pixels
NUM_RAYS = 360 # Must be between 1 and 360
SOLID_RAYS = False  # Can be somewhat glitchy. For best results, set NUM_RAYS to 360
NUM_WALLS = 5  # The amount of randomly generated walls
MAX_REFLECTIONS = 2  # Maximum number of reflections
# ------------------

screen = pygame.display.set_mode(WINDOW_SIZE)
display = pygame.Surface(WINDOW_SIZE)

mx, my = pygame.mouse.get_pos()
lastClosestPoint = (0, 0)
running = True
rays = []
walls = []
particles = []


class Ray:
    def __init__(self, x, y, angle, reflections=0, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.dir = (math.cos(angle), math.sin(angle))
        self.reflections = reflections
        self.color = color

    def update(self, mx, my):
        self.x = mx
        self.y = my

    def checkCollision(self, walls):
        if self.reflections >= MAX_REFLECTIONS:
            return

        closest = float('inf')
        closestPoint = None
        closestWall = None

        for wall in walls:
            x1 = wall.start_pos[0]
            y1 = wall.start_pos[1]
            x2 = wall.end_pos[0]
            y2 = wall.end_pos[1]
            x3 = self.x
            y3 = self.y
            x4 = self.x + self.dir[0]
            y4 = self.y + self.dir[1]
            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            epsilon = 1e-6  # Small epsilon value for float comparison

            if abs(denominator) < epsilon:
                continue  # Skip parallel lines

            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

            if 0 <= t <= 1 and u > 0:
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                distance = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
                if distance < closest:
                    closest = distance
                    closestPoint = (x, y)
                    closestWall = wall

        if closestPoint:
            pygame.draw.line(display, self.color, (self.x, self.y), closestPoint)
            self.x, self.y = closestPoint

            # Calculate the normal vector of the wall
            wall_dx = closestWall.end_pos[0] - closestWall.start_pos[0]
            wall_dy = closestWall.end_pos[1] - closestWall.start_pos[1]
            wall_length = math.sqrt(wall_dx ** 2 + wall_dy ** 2)
            wall_normal = (-wall_dy / wall_length, wall_dx / wall_length)

            # Calculate the dot product between ray direction and wall normal
            dot_product = self.dir[0] * wall_normal[0] + self.dir[1] * wall_normal[1]

            # Calculate the reflection direction using the dot product
            reflection_dir = (
                self.dir[0] - 2 * dot_product * wall_normal[0],
                self.dir[1] - 2 * dot_product * wall_normal[1]
            )

            self.dir = reflection_dir

            new_ray = Ray(self.x, self.y, angle=math.atan2(reflection_dir[1], reflection_dir[0]),
                          reflections=self.reflections + 1, color=self.color)
            new_ray.checkCollision(walls)
            rays.append(new_ray)


class Wall:
    def __init__(self, start_pos, end_pos, color='white'):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color

    def draw(self):
        pygame.draw.line(display, self.color, self.start_pos, self.end_pos, 3)


def generateWalls():
    walls.clear()
    walls.append(Wall((0, 0), (WINDOW_SIZE[0], 0)))
    walls.append(Wall((0, 0), (0, WINDOW_SIZE[1])))
    walls.append(Wall((WINDOW_SIZE[0], 0), (WINDOW_SIZE[0], WINDOW_SIZE[1])))
    walls.append(Wall((0, WINDOW_SIZE[1]), (WINDOW_SIZE[0], WINDOW_SIZE[1])))
    for i in range(NUM_WALLS):
        start_x = random.randint(0, WINDOW_SIZE[0])
        start_y = random.randint(0, WINDOW_SIZE[1])
        end_x = random.randint(0, WINDOW_SIZE[0])
        end_y = random.randint(0, WINDOW_SIZE[1])
        walls.append(Wall((start_x, start_y), (end_x, end_y), color='white'))


def draw():
    display.fill((0, 0, 0))
    for wall in walls:
        wall.draw()
    for ray in rays:
        ray.checkCollision(walls)
    screen.blit(display, (0, 0))
    pygame.display.update()


generateWalls()
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == pygame.K_SPACE:
                generateWalls()
    rays.clear()
    for i in range(0, 360, int(360 / NUM_RAYS)):
        rays.append(Ray(mx, my, angle=math.radians(i), reflections=0, color=(255, 255, 255)))
    draw()

pygame.quit()
sys.exit()
