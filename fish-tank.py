import pygame
import sys
from pygame.locals import *
from random import uniform, randint
from math import hypot

SCREEN_WIDTH, SCREEN_HEIGHT = 1365, 768
FISH_COUNT = 100
NEIGHBOR_RADIUS = 100
FOOD_RADIUS = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Fish Tank Simulation')

background_image = pygame.image.load('.\\assets\\tank.jpg')

def load_fish_sprite(file, sprite_width, sprite_height):
    sprite = pygame.image.load(file)
    sprite = pygame.transform.scale(sprite, (sprite_width, sprite_height))
    return sprite

yellow_fish_sprite = load_fish_sprite('.\\assets\\dory.png', 87, 50)
pink_fish_sprite = load_fish_sprite('.\\assets\\salmon.png', 87, 50)

class Fish(pygame.sprite.Sprite):
    def __init__(self, sprite, species):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.rect.x = randint(0, SCREEN_WIDTH)
        self.rect.y = randint(0, SCREEN_HEIGHT)
        self.speed = 2
        self.velocity = pygame.Vector2(uniform(-1, 1), uniform(-1, 1))
        self.velocity.scale_to_length(self.speed)
        self.species = species

    def update(self, fishes, foods):
        self.flock(fishes)
        self.move_towards_food(foods)
        self.rect.move_ip(self.velocity)
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.velocity.x = -self.velocity.x
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.velocity.y = -self.velocity.y

    def flock(self, fishes):
        alignment = pygame.Vector2(0, 0)
        cohesion = pygame.Vector2(0, 0)
        separation = pygame.Vector2(0, 0)
        total = 1
        for fish in fishes:
            if fish != self and fish.species == self.species and self.rect.colliderect(fish.rect.inflate(NEIGHBOR_RADIUS, NEIGHBOR_RADIUS)):
                alignment += fish.velocity
                cohesion += pygame.Vector2(*fish.rect.center)
                distance = hypot(self.rect.x - fish.rect.x, self.rect.y - fish.rect.y)
                if distance < 20:
                    separation += pygame.Vector2(*self.rect.center) - pygame.Vector2(*fish.rect.center)
                total += 1
        if total > 1:
            alignment /= total
            cohesion /= total
            cohesion = pygame.Vector2(cohesion.x - self.rect.centerx, cohesion.y - self.rect.centery)
            if alignment.length() > 0:
                alignment.scale_to_length(self.speed)
            if cohesion.length() > 0:
                cohesion.scale_to_length(self.speed)
            if separation.length() > 0:
                separation.scale_to_length(self.speed)
            self.velocity = alignment * 0.5 + cohesion * 0.3 + separation * 0.2 + self.velocity
            if self.velocity.length() > 0:
                self.velocity.scale_to_length(self.speed)

    def move_towards_food(self, foods):
        closest_food = None
        min_distance = float('inf')
        for food in foods:
            distance = hypot(self.rect.centerx - food.rect.centerx, self.rect.centery - food.rect.centery)
            if distance < FOOD_RADIUS:
                food.kill()
            elif distance < min_distance:
                min_distance = distance
                closest_food = food
        if closest_food and min_distance < NEIGHBOR_RADIUS:
            move = pygame.Vector2(closest_food.rect.centerx - self.rect.centerx, closest_food.rect.centery - self.rect.centery)
            move.scale_to_length(self.speed)
            self.velocity = self.velocity * 0.8 + move * 0.2
            self.velocity.scale_to_length(self.speed)

fishes = pygame.sprite.Group([Fish(yellow_fish_sprite, 'dory') if i < FISH_COUNT // 2 else Fish(pink_fish_sprite, 'salmon') for i in range(FISH_COUNT)])
foods = pygame.sprite.Group()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            food = pygame.sprite.Sprite()
            food.image = pygame.Surface((10, 10))
            food.image.fill((255, 0, 0))
            food.rect = food.image.get_rect(center=pygame.mouse.get_pos())
            foods.add(food)

    screen.blit(background_image, (0, 0))
    fishes.update(fishes, foods)
    foods.update()

    fishes.draw(screen)
    foods.draw(screen)

    pygame.display.flip()
    pygame.time.wait(20)
