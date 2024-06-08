import random
import sys
from enum import Enum

import pygame
from sys import exit

pygame.init()

class GameState(Enum):
    TITLE = 1
    PLAYING = 2
    LOST = 3
    SHOP = 4

# Global variables
score = 0
player_coins = 0
player_y_velocity = 0
current_hat = 0
platforms = []
coins = []
running = True
jumping = False
platform_spawnable = True
coin_spawnable = True
highscore = 0
GAMESTATE = GameState.TITLE

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

# Surfaces
dababy_surf = pygame.transform.scale(pygame.image.load('Assets/dababy.png').convert_alpha(), (80, 50))
dababy_rect = dababy_surf.get_rect(midbottom = (100, 400))
gun_surf = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (100, 50))

font = pygame.font.Font('Assets/Dafont.ttf', 36)
title_font = pygame.font.Font('Assets/Dafont.ttf', 100)
restart_surf = font.render("Play again?", True, 'White')
restart_rect = restart_surf.get_rect(center = (WIDTH/2, HEIGHT/2 + 60))

starting_platform = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (500, 250))

coin_frames = [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (50, 50)) for i in range(1, 6)]
tiny_coin_frames = [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (25, 25)) for i in range(1, 6)]
end_screen = pygame.transform.scale(pygame.image.load('Assets/end_screen.png'), (500, 250))
end_screen_rect = end_screen.get_rect(center = (WIDTH / 2, HEIGHT / 2))
#coin_frames += [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (50, 50)) for i in range(3, 1, -1)]

play_button = pygame.transform.scale(pygame.image.load('Assets/play_button.png'), (192, 72))
play_button_rect = play_button.get_rect(center = (WIDTH/2 - 150, HEIGHT/2 + 100))
shop_button = pygame.transform.scale(pygame.image.load('Assets/shop_button.png'), (192, 72))
shop_button_rect = shop_button.get_rect(center = (WIDTH/2 + 150, HEIGHT/2 + 100))
title_surf = title_font.render("Dagame", True, 'White')
title_rect = title_surf.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))
title_background_surf = pygame.surface.Surface((WIDTH,HEIGHT))
title_background_surf.fill('Blue')
title_background_rect = title_background_surf.get_rect(topleft = (0,0))
shop_box = pygame.transform.scale(pygame.image.load('Assets/shop_box.png'), (192 * 3, 64 * 3))
shop_box_rect = shop_box.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))
shop_arrow = pygame.surface.Surface((54,108))
shop_left_arrow_rect = shop_arrow.get_rect(topleft = (shop_box_rect.x + 42, shop_box_rect.y + 42))
shop_right_arrow_rect = shop_arrow.get_rect(topleft = (shop_box_rect.right - 96, shop_box_rect.y + 42))

wizard_hat = pygame.transform.scale(pygame.image.load('Assets/wizard hat.png'), (100, 100))
wizard_hat_rect = wizard_hat.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))
brick_hat = pygame.transform.scale(pygame.image.load('Assets/brick.png'), (100, 100))
brick_hat_rect = brick_hat.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))

class Hat():
    def __init__(self, surf, rect, price):
        self.surface = surf
        self.rect = rect
        self.price = price

hats = []
hats.append(Hat(wizard_hat, wizard_hat_rect, 1000))
hats.append(Hat(brick_hat, brick_hat_rect, 800))

class TinyAnimatedCoin(pygame.sprite.Sprite):
    frames = tiny_coin_frames
    animation_speed = COIN_ANIMATION_SPEED
    def __init__(self, pos):
        super().__init__()
        self.current_frame = 0
        self.frame = TinyAnimatedCoin.frames[self.current_frame]
        self.rect = self.frame.get_rect(topleft = pos)
        self.counter = 0

    def update(self):
        self.counter += TinyAnimatedCoin.animation_speed
        if self.counter >= 1:
            self.counter = 0
            self.current_frame = (self.current_frame + 1) % len(TinyAnimatedCoin.frames)
            self.frame = TinyAnimatedCoin.frames[self.current_frame]

shop_coin = TinyAnimatedCoin((shop_box_rect.center[0] - 70, shop_box_rect.bottom + 15))

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
    global restart_rect, highscore, GAMESTATE, shop_coin
    screen.blit(background, (0, 0))
    
    if GAMESTATE == GameState.PLAYING:
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
    
    elif GAMESTATE == GameState.TITLE:
        screen.fill((86, 215, 255))
        screen.blit(title_surf, title_rect)
        screen.blit(play_button, play_button_rect)
        screen.blit(shop_button, shop_button_rect)

    elif GAMESTATE == GameState.LOST:
        score_surf = font.render(f"Score: {score}", True, 'White')
        score_rect = score_surf.get_rect(center = (WIDTH/2, HEIGHT/2 - 75))
        screen.blit(end_screen, end_screen_rect)
        screen.blit(score_surf, score_rect)
        screen.blit(restart_surf, restart_rect)

        highscore_surf = font.render(f"Highscore: {highscore}", True, 'White')
        highscore_rect = score_surf.get_rect(center = (WIDTH/2 - 35, HEIGHT/2 - 25))
        screen.blit(highscore_surf, highscore_rect)
    
    elif GAMESTATE == GameState.SHOP:
        screen.fill((86, 215, 255))
        screen.blit(shop_box, shop_box_rect)
        screen.blit(hats[current_hat].surface, hats[current_hat].rect)
        price_surf = font.render(f"{hats[current_hat].price}", True, 'White')
        price_rect = price_surf.get_rect(center = (shop_box_rect.center[0], shop_box_rect.bottom + 26))
        screen.blit(shop_coin.frame, shop_coin.rect)
        screen.blit(price_surf, price_rect)
        shop_coin.update()

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
    global GAMESTATE
    if dababy_rect.top > HEIGHT:
        GAMESTATE = GameState.LOST
        updateHighscore()
        updatePlayerCoins()

def event_loop():
    global running, restart_rect, GAMESTATE, current_hat
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit()

        if GAMESTATE == GameState.LOST:
            if event.type == pygame.MOUSEBUTTONDOWN and restart_rect.collidepoint(event.pos):
                restart()
                GAMESTATE = GameState.PLAYING

        elif GAMESTATE == GameState.TITLE:
            if event.type == pygame.MOUSEBUTTONDOWN and play_button_rect.collidepoint(event.pos):
                GAMESTATE = GameState.PLAYING
            elif event.type == pygame.MOUSEBUTTONDOWN and shop_button_rect.collidepoint(event.pos):
                GAMESTATE = GameState.SHOP
        elif GAMESTATE == GameState.SHOP:
            if event.type == pygame.MOUSEBUTTONDOWN and shop_left_arrow_rect.collidepoint(event.pos) and current_hat > 0:
                current_hat -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN and shop_right_arrow_rect.collidepoint(event.pos) and current_hat < len(hats) - 1:
                current_hat += 1

    if GAMESTATE == GameState.PLAYING:
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
    global score, player_coins, current_hat, player_y_velocity, platforms, coins, GAMESTATE, jumping, platform_spawnable, coin_spawnable, dababy_rect
    score = 0
    getPlayerCoins()
    player_y_velocity = 0
    current_hat = 0
    platforms = []
    coins = []
    GAMESTATE = GameState.TITLE
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