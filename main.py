import random
import sys

import pygame
from sys import exit

pygame.init()

# Global variables
score = 0
player_y_velocity = 0
platforms = []
running = True
done = False
jumping = False
spawnable = True
restart_background_rect = None

# Constants
PLAYER_SPEED = 10
JUMP_VELOCITY = -30
GRAVITY = 1.5
PLATFORM_SPEED = 10
WIDTH = 1000
HEIGHT = 600
FPS = 60

# Screen and clock setup
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Dagame")
background = pygame.image.load('Assets/1729603_fritorio_dababy.jpg').convert()
clock = pygame.time.Clock()

# Dababy and gun surfaces
dababy_surf = pygame.transform.scale(pygame.image.load('Assets/dababy.png').convert_alpha(), (80, 50))
dababy_rect = dababy_surf.get_rect(midbottom = (100, 400))
gun_surf = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (100, 50))

font = pygame.font.Font(None, 36)

starting_platform = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (500, 100))

class Platform:
    global score
    surface = gun_surf
    def __init__(self, s = surface, pos = None, touch = False):
        if not pos:
            pos = (WIDTH, random.randint(200,500))
        self.surf = s
        self.rect = s.get_rect(topleft = pos)
        self.touched = touch
        self.speed = PLATFORM_SPEED + (score * 0.1)
        self.reached_mid = False

def make_platforms():
    global spawnable
    if spawnable:
        platforms.append(Platform())
        spawnable = False
    for platform in platforms:
        platform.rect.x -= platform.speed
        if platform.rect.right < 0:
            platforms.remove(platform)
        elif platform.rect.left < 400 and not platform.reached_mid:
            spawnable = True
            platform.reached_mid = True

def gravity():
    global player_y_velocity, jumping
    player_y_velocity += GRAVITY
    dababy_rect.y += player_y_velocity
    for platform in platforms:
        checkScore(platform)
        if dababy_rect.colliderect(platform.rect) and player_y_velocity > 0:
            jumping = False
            dababy_rect.bottom = platform.rect.top
            player_y_velocity = 0
            dababy_rect.x -= platform.speed

def draw_window():
    global done, restart_background_rect
    screen.blit(background, (0, 0))
    if not done:
        for platform in platforms:
            screen.blit(platform.surf, platform.rect)
        screen.blit(dababy_surf, dababy_rect)
        score_surf = font.render("Score: " + str(score), True, 'Black')
        score_rect = score_surf.get_rect(topleft = (0,0))
        screen.blit(score_surf, score_rect)

    else:
        score_background = pygame.Surface((400,200))
        score_background.fill('White')
        score_background_rect = score_background.get_rect(center = (WIDTH/2,HEIGHT/2))
        score_surf = font.render("Score: " + str(score), True, 'Black')
        score_rect = score_surf.get_rect(center = (WIDTH/2,HEIGHT/2 - 25))
        screen.blit(score_background, score_background_rect)
        screen.blit(score_surf, score_rect)

        restart_surf = font.render("Play again?", True, 'White')
        restart_rect = restart_surf.get_rect(center = (WIDTH/2, HEIGHT/2 + 50))
        restart_background = pygame.Surface((200, 50))
        restart_background.fill('Black')
        restart_background_rect = restart_background.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(restart_background, restart_background_rect)
        screen.blit(restart_surf, restart_rect)

    pygame.display.update()

def movement():
    global player_y_velocity, jumping
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        dababy_rect.x += PLAYER_SPEED
    if keys[pygame.K_a]:
        dababy_rect.x -= PLAYER_SPEED
    if keys[pygame.K_SPACE] and not jumping:
        jumping = True
        player_y_velocity = JUMP_VELOCITY
        gravity()

def checkScore(platform):
    global score
    if dababy_rect.colliderect(platform.rect) and not platform.touched:
        platform.touched = True
        score += 1

def checkLost():
    global done
    if dababy_rect.top > HEIGHT:
        done = True

def event_loop():
    global running, restart_background_rect
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos
            if done and restart_background_rect.collidepoint(click_pos):
                restart()
    make_platforms()
    checkLost()
    movement()
    gravity()

def restart():
    global score, player_y_velocity, platforms, done, jumping, spawnable, dababy_rect
    score = 0
    player_y_velocity = 0
    platforms = []
    done = False
    jumping = False
    spawnable = True
    platforms.append(Platform(starting_platform, (300, 400), True))
    platforms[0].reached_mid = True
    dababy_rect = dababy_surf.get_rect(midbottom=(400, 400))

def main():
    restart()
    while running:
        draw_window()
        event_loop()
        clock.tick(60)

if __name__ == '__main__':
    main()