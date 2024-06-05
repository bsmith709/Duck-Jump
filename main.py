import random
import sys

import pygame
from sys import exit

pygame.init()

# Global variables
score = 0
player_coins = 0
player_y_velocity = 0
platforms = []
coins = []
running = True
player_lost = False
jumping = False
platform_spawnable = True
coin_spawnable = True
restart_background_rect = None
highscore = 0

# Constants
PLAYER_SPEED = 10
JUMP_VELOCITY = -30
GRAVITY = 1.5
PLATFORM_SPEED = 5
WIDTH = 1000
HEIGHT = 600
FPS = 60
SPEED_MULTIPLIER = 0.5
COIN_ANIMATION_SPEED = 0.1

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

coin_frames = [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (50, 50)) for i in range(1, 6)]
#coin_frames += [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (50, 50)) for i in range(3, 1, -1)]

class AnimatedCoin(pygame.sprite.Sprite):
    frames = coin_frames
    animation_speed = COIN_ANIMATION_SPEED
    def __init__(self):
        super().__init__()
        self.current_frame = 0
        self.frame = AnimatedCoin.frames[self.current_frame]
        self.rect = self.frame.get_rect(topleft = (WIDTH, random.randint(100,200)))
        self.counter = 0
        self.speed = PLATFORM_SPEED + (score * SPEED_MULTIPLIER)
        self.reached_mid = False

    def update(self):
        self.counter += AnimatedCoin.animation_speed
        if self.counter >= 1:
            self.counter = 0
            self.current_frame = (self.current_frame + 1) % len(AnimatedCoin.frames)
            self.frame = AnimatedCoin.frames[self.current_frame]

class Platform:
    global score
    surface = gun_surf
    def __init__(self, s = surface, pos = None, touch = False):
        if not pos:
            pos = (WIDTH, random.randint(200,500))
        self.surf = s
        self.rect = s.get_rect(topleft = pos)
        self.touched = touch
        self.speed = PLATFORM_SPEED + (score * SPEED_MULTIPLIER)
        self.reached_mid = False

def handlePlatforms():
    global platform_spawnable
    if platform_spawnable:
        platforms.append(Platform())
        platform_spawnable = False
    for platform in platforms:
        platform.rect.x -= platform.speed
        if platform.rect.right < 0:
            platforms.remove(platform)
        elif platform.rect.left < 400 and not platform.reached_mid:
            platform_spawnable = True
            platform.reached_mid = True

def handleCoins():
    global coin_spawnable, player_coins
    if coin_spawnable:
        coins.append(AnimatedCoin())
        coin_spawnable = False
    for coin in coins:
        coin.rect.x -= coin.speed
        if coin.rect.right < 0:
            coins.remove(coin)
        elif coin.rect.left < 400 and not coin.reached_mid:
            coin_spawnable = True
            coin.reached_mid = True

        if dababy_rect.colliderect(coin):
            if not coin.reached_mid:
                coin_spawnable = True
            player_coins += 1
            coins.remove(coin)

def gravity():
    global player_y_velocity, jumping
    player_y_velocity += GRAVITY
    dababy_rect.y += player_y_velocity
    for platform in platforms:
        checkScore(platform)
        if dababy_rect.colliderect(platform.rect) and player_y_velocity > 0 and dababy_rect.y < platform.rect.y:
            jumping = False
            dababy_rect.bottom = platform.rect.top
            player_y_velocity = 0
            dababy_rect.x -= platform.speed

def draw_window():
    global player_lost, restart_background_rect, highscore
    screen.blit(background, (0, 0))
    if not player_lost:
        for platform in platforms:
            screen.blit(platform.surf, platform.rect)
        for coin in coins:
            screen.blit(coin.frame, coin.rect)
            coin.update()
        screen.blit(dababy_surf, dababy_rect)

        score_surf = font.render(f"Score: {score}", True, 'White')
        score_rect = score_surf.get_rect(topleft = (10,10))
        screen.blit(score_surf, score_rect)

        player_coins_surf = font.render(f"Coins: {player_coins}", True,'White')
        player_coins_rect = player_coins_surf.get_rect(topleft = (10, 40))
        screen.blit(player_coins_surf, player_coins_rect)

    else:
        score_background = pygame.Surface((400,200))
        score_background.fill('White')
        score_background_rect = score_background.get_rect(center = (WIDTH/2,HEIGHT/2))
        score_surf = font.render("Score: " + str(score), True, 'Black')
        score_rect = score_surf.get_rect(center = (WIDTH/2,HEIGHT/2 - 75))
        screen.blit(score_background, score_background_rect)
        screen.blit(score_surf, score_rect)

        restart_surf = font.render("Play again?", True, 'White')
        restart_rect = restart_surf.get_rect(center = (WIDTH/2, HEIGHT/2 + 50))
        restart_background = pygame.Surface((200, 50))
        restart_background.fill('Black')
        restart_background_rect = restart_background.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        screen.blit(restart_background, restart_background_rect)
        screen.blit(restart_surf, restart_rect)

        highscore_surf = font.render(f"Highscore: {highscore}", True, 'Black')
        highscore_rect = score_surf.get_rect(center = (WIDTH/2,HEIGHT/2 - 25))
        screen.blit(highscore_surf, highscore_rect)

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
    global player_lost
    if dababy_rect.top > HEIGHT:
        player_lost = True
        updateHighscore()
        updatePlayerCoins()

def event_loop():
    global running, restart_background_rect
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos
            if player_lost and restart_background_rect.collidepoint(click_pos):
                restart()
    handleCoins()
    handlePlatforms()
    checkLost()
    movement()
    gravity()

def getHighscore():
    global highscore
    with open('highscore.txt', 'r') as file:
        highscore = int(file.read())

def updateHighscore():
    global highscore
    if score > highscore:
        highscore = score
        with open('highscore.txt', 'w') as file:
            file.write(f"{highscore}")

def getPlayerCoins():
    global player_coins
    with open('playercoins.txt', 'r') as file:
        player_coins = int(file.read())

def updatePlayerCoins():
    with open('playercoins.txt', 'w') as file:
        file.write(f"{player_coins}")

def restart():
    global score, player_coins, player_y_velocity, platforms, coins, player_lost, jumping, platform_spawnable, coin_spawnable, dababy_rect
    score = 0
    getPlayerCoins()
    player_y_velocity = 0
    platforms = []
    coins = []
    player_lost = False
    jumping = False
    platform_spawnable = True
    coin_spawnable = True
    getHighscore()
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