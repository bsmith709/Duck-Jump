import random
import sys
from enum import Enum

import pygame
from sys import exit

dababy_mode = False

pygame.init()

class GameState(Enum):
    TITLE = 1
    PLAYING = 2
    LOST = 3
    SHOP = 4

# Constants
PLAYER_SPEED = 10
JUMP_VELOCITY = -25
GRAVITY = 1.5
PLATFORM_SPEED = 5
WIDTH = 1000
HEIGHT = 600
FPS = 60
SPEED_MULTIPLIER = 0.5
COIN_ANIMATION_SPEED = 0.1

# Global variables
score = 0
player_coins = 0
current_hat = 0
platforms = []
coins = []
platform_spawnable = True
coin_spawnable = True
highscore = 0
GAMESTATE = GameState.TITLE

# Screen and clock setup
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

# Font Setup
font = pygame.font.Font('Assets/Dafont.ttf', 36)
title_font = pygame.font.Font('Assets/Dafont.ttf', 100)

# Changes some surfaces depending on whether dababy mode is active
if dababy_mode:
    pygame.display.set_caption("Dagame")
    background = pygame.image.load('Assets/1729603_fritorio_dababy.jpg').convert()
    player_surf = pygame.transform.scale(pygame.image.load('Assets/dababy.png').convert_alpha(), (80, 50))
    player_rect = player_surf.get_rect(midbottom = (300, 400))
    platform_surf = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (100, 50))
    starting_platform = pygame.transform.scale(pygame.image.load('Assets/gun.png').convert_alpha(), (500, 250))
    title_surf = title_font.render("Dagame", True, 'White')
    title_rect = title_surf.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))

else:
    pygame.display.set_caption("Duck Game")
    background = pygame.transform.scale(pygame.image.load('Assets/first_background.png'), (1000, 600))
    player_surf = pygame.transform.scale(pygame.image.load('Assets/the_man.png').convert_alpha(), (50, 50))
    player_rect = player_surf.get_rect(midbottom = (300, 400))
    platform_surf =  pygame.transform.scale(pygame.image.load('Assets/grass_platform.png'), (100, 25))
    starting_platform =pygame.transform.scale(pygame.image.load('Assets/grass_platform.png'), (500, 50))
    title_surf = title_font.render("Duck Game", True, 'White')
    title_rect = title_surf.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))

# Text for the play again button after losing
restart_surf = font.render("Play again?", True, 'White')
restart_rect = restart_surf.get_rect(center = (WIDTH/2, HEIGHT/2 + 60))

# Frames for coin and small coin animations
coin_frames = [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (50, 50)) for i in range(1, 6)]
tiny_coin_frames = [pygame.transform.scale(pygame.image.load(f'Assets/Coin/coin{i}.png'), (25, 25)) for i in range(1, 6)]

# Surface and rect for the box that displays when the player loses
end_screen = pygame.transform.scale(pygame.image.load('Assets/end_screen.png'), (500, 250))
end_screen_rect = end_screen.get_rect(center = (WIDTH / 2, HEIGHT / 2))

# Surface and rect for the play button on the title screen
play_button = pygame.transform.scale(pygame.image.load('Assets/play_button.png'), (192, 72))
play_button_rect = play_button.get_rect(center = (WIDTH/2 - 150, HEIGHT/2 + 100))

# Surface and rect for the shop button on the title screen
shop_button = pygame.transform.scale(pygame.image.load('Assets/shop_button.png'), (192, 72))
shop_button_rect = shop_button.get_rect(center = (WIDTH/2 + 150, HEIGHT/2 + 100))

# Surface and rects for the box containing hats in the shop and the arrows on each side
shop_box = pygame.transform.scale(pygame.image.load('Assets/shop_box.png'), (192 * 3, 64 * 3))
shop_box_rect = shop_box.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))
shop_arrow = pygame.surface.Surface((54,108))
shop_left_arrow_rect = shop_arrow.get_rect(topleft = (shop_box_rect.x + 42, shop_box_rect.y + 42))
shop_right_arrow_rect = shop_arrow.get_rect(topleft = (shop_box_rect.right - 96, shop_box_rect.y + 42))

# Surface and rect for the back arrow used in the shop plus rect for back arrow used in losing screen
back_arrow = pygame.transform.scale(pygame.image.load('Assets/back_arrow.png'), (64, 64))
back_arrow_rect = back_arrow.get_rect(topleft =  (25, 25))

# Surface and rect for the buy button used in the shop
buy_button = pygame.transform.scale(pygame.image.load('Assets/buy_button.png'), (128, 64))
buy_button_rect = buy_button.get_rect(center = (WIDTH / 2 + 75, HEIGHT / 2 + 125))

# Surface and rect for the equip button used in the shop
equip_button = pygame.transform.scale(pygame.image.load('Assets/equip_button.png'), (128, 64))
equip_button_rect = equip_button.get_rect(center = (WIDTH / 2 - 75, HEIGHT / 2 + 125))

# Surface and rect for the equip button used in the shop when equipping is not possible
cant_equip_button = pygame.transform.scale(pygame.image.load('Assets/cant_equip_button.png'), (128, 64))
cant_equip_button_rect = cant_equip_button.get_rect(center = (WIDTH / 2 - 75, HEIGHT / 2 + 125))

# Surfaces and rects for the hats to be displayed in the shop
wizard_hat = pygame.transform.scale(pygame.image.load('Assets/wizard hat.png'), (100, 100))
wizard_hat_rect = wizard_hat.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))
brick_hat = pygame.transform.scale(pygame.image.load('Assets/brick.png'), (100, 100))
brick_hat_rect = brick_hat.get_rect(center = (WIDTH/2, HEIGHT/2 - 100))

# Player class used for the main player character
class Player(pygame.sprite.Sprite):
    def __init__(self, surf = player_surf, rect = player_rect, hat = None):
        self.surf = surf
        self.rect = rect
        self.jump_limit = 1
        self.jumps_used = 0
        self.y_velocity = 0
        self.gravity = GRAVITY
        self.hat = hat
        self.jump_cooldown = 10
        self.jump_cooldown_counter = 0
        self.jump_on_cooldown = False

    def jump(self):
        if not self.jump_on_cooldown and self.jumps_used < self.jump_limit:
            self.jumps_used += 1
            self.y_velocity = JUMP_VELOCITY
            self.jump_on_cooldown = True

    def update(self):
        if self.jump_on_cooldown:
            self.jump_cooldown_counter += 1
            if self.jump_cooldown_counter >= self.jump_cooldown:
                self.jump_on_cooldown = False

    def resetJumps(self):
        player.jumps_used = 0
        player.jump_on_cooldown = False
        player.jump_cooldown_counter = 0
    
    def reset(self):
        self.rect = player_surf.get_rect(midbottom = (300, 400))
        self.jumps_used = 0
        self.y_velocity = 0
        self.jump_cooldown_counter = 0
        self.jump_on_cooldown = False
    
    def equipHat(self, hat):
        self.hat = hat
        hat.addStats(self)
        self.surf = hat.player_with_hat

    def removeHat(self):
        self.hat.removeStats(self)
        self.hat = None
        self.surf = player_surf

# Initialize player
player = Player()

# Hat class used to store data about each hat
class Hat():
    def __init__(self, surf, rect, name, description, price, player_with_hat):
        self.surface = surf
        self.rect = rect
        self.name = name
        self.description = description
        self.price = price
        self.player_with_hat = player_with_hat
        self.owned = False
    
    def addStats(self):
        pass
    def removeStats(self):
        pass

class WizardHat(Hat):
    def addStats(self, player):
        pass
    
    def removeStats(self, player):
        pass
        

class BrickHat(Hat):
    def addStats(self, player):
        player.gravity = 2
        player.jump_limit = 2
    
    def removeStats(self, player):
        player.gravity = GRAVITY
        player.jump_limit = 1

        

# Initialize list of hats and add each hat
hats = []
hats.append(WizardHat(wizard_hat, wizard_hat_rect, "Wizard Hat", "Allows slow falling when holding spacebar", 1000, pygame.transform.scale(pygame.image.load('Assets/duck_wizard_hat.png'), (50, 50))))
hats.append(BrickHat(brick_hat, brick_hat_rect, "Brick Hat", "Gives double jump ability but increases falling speed", 800, pygame.transform.scale(pygame.image.load('Assets/duck_brick_hat.png'), (50, 50))))

# Class for the small animated coins
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

# Class for the large animated coins
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

# Class for the platforms
class Platform:
    global score
    surface = platform_surf
    def __init__(self, s = surface, pos = None, touch = False):
        if not pos:
            pos = (WIDTH, random.randint(200,400))
        self.surf = s
        self.rect = s.get_rect(topleft = pos)
        self.touched = touch
        self.speed = PLATFORM_SPEED + (score * SPEED_MULTIPLIER)
        self.reached_mid = False

# Checks whether platforms can be spawned based on whether the last platform has passed a certain point and spawns a platform if so
# Also moves each of the currently spawned platforms
def handlePlatforms():
    global platform_spawnable
    if platform_spawnable:
        platforms.append(Platform())
        platform_spawnable = False
    for platform in platforms:
        platform.rect.x -= platform.speed
        if platform.rect.right < 0:
            platforms.remove(platform)
        elif platform.rect.left < 550 and not platform.reached_mid:
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

        if player.rect.colliderect(coin):
            if not coin.reached_mid:
                coin_spawnable = True
            player_coins += 1
            coins.remove(coin)

def gravity():
    player.y_velocity += player.gravity
    player.rect.y += player.y_velocity
    for platform in platforms:
        checkScore(platform)
        if player.rect.colliderect(platform.rect) and player.y_velocity > 0 and player.rect.y < platform.rect.y:
            player.rect.bottom = platform.rect.top
            player.y_velocity = 0
            player.rect.x -= platform.speed
            player.resetJumps()

def draw_window():
    global restart_rect, highscore, GAMESTATE, shop_coin
    screen.blit(background, (0, 0))
    
    if GAMESTATE == GameState.PLAYING:
        for platform in platforms:
            screen.blit(platform.surf, platform.rect)
        for coin in coins:
            screen.blit(coin.frame, coin.rect)
            coin.update()
        screen.blit(player.surf, player.rect)

        score_surf = font.render(f"Score: {score}", True, 'Black')
        score_rect = score_surf.get_rect(topleft = (10,10))
        screen.blit(score_surf, score_rect)

        player_coins_surf = font.render(f"Coins: {player_coins}", True,'Black')
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
        screen.blit(back_arrow, back_arrow_rect)

        highscore_surf = font.render(f"Highscore: {highscore}", True, 'White')
        highscore_rect = score_surf.get_rect(center = (WIDTH/2 - 35, HEIGHT/2 - 25))
        screen.blit(highscore_surf, highscore_rect)
    
    elif GAMESTATE == GameState.SHOP:
        screen.fill((86, 215, 255))
        screen.blit(back_arrow, back_arrow_rect)
        screen.blit(buy_button, buy_button_rect)
    
        if not hats[current_hat] == player.hat and hats[current_hat].owned:
            screen.blit(equip_button, equip_button_rect)
        else:
            screen.blit(cant_equip_button, cant_equip_button_rect)

        screen.blit(shop_box, shop_box_rect)
        screen.blit(hats[current_hat].surface, hats[current_hat].rect)

        if not hats[current_hat].owned:
            price_surf = font.render(f"{hats[current_hat].price}", True, 'White')
            price_rect = price_surf.get_rect(center = (shop_box_rect.center[0], shop_box_rect.bottom + 26))
            screen.blit(shop_coin.frame, shop_coin.rect)
            screen.blit(price_surf, price_rect)

        elif hats[current_hat] == player.hat:
            equipped_surf = font.render("EQUIPPED", True, 'White')
            equipped_rect = equipped_surf.get_rect(center = (shop_box_rect.center[0], shop_box_rect.bottom + 26))
            screen.blit(equipped_surf, equipped_rect)
        else:
            owned_surf = font.render("OWNED", True, 'White')
            owned_rect = owned_surf.get_rect(center = (shop_box_rect.center[0], shop_box_rect.bottom + 26))
            screen.blit(owned_surf, owned_rect)

        player_coins_text = font.render(f"Your Coins:     {player_coins}", True, 'White')
        hat_description = font.render(hats[current_hat].description, True, 'White')
        hat_description_rect = hat_description.get_rect(center = (WIDTH/2, HEIGHT/2 + 50))
        screen.blit(hat_description, hat_description_rect)
        screen.blit(player_coins_text, (shop_box_rect.center[0] - 150, 25))
        screen.blit(shop_coin.frame, (shop_box_rect.center[0] + 40, 35))
        shop_coin.update()

    pygame.display.update()

def movement():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        player.rect.x += PLAYER_SPEED
    if keys[pygame.K_a]:
        player.rect.x -= PLAYER_SPEED
    if keys[pygame.K_SPACE]:
        player.jump()

def checkScore(platform):
    global score
    if player.rect.colliderect(platform.rect) and not platform.touched:
        platform.touched = True
        score += 1

def checkLost():
    global GAMESTATE
    if player.rect.top > HEIGHT:
        GAMESTATE = GameState.LOST
        updateHighscore()
        updatePlayerCoins()

def event_loop():
    global running, restart_rect, GAMESTATE, current_hat, player_coins
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            exit()

        if GAMESTATE == GameState.LOST:
            if event.type == pygame.MOUSEBUTTONDOWN and restart_rect.collidepoint(event.pos):
                restart()
                GAMESTATE = GameState.PLAYING
            elif event.type == pygame.MOUSEBUTTONDOWN and back_arrow_rect.collidepoint(event.pos):
                restart()
                GAMESTATE = GameState.TITLE

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
            elif event.type == pygame.MOUSEBUTTONDOWN and back_arrow_rect.collidepoint(event.pos):
                GAMESTATE = GameState.TITLE
            elif event.type == pygame.MOUSEBUTTONDOWN and buy_button_rect.collidepoint(event.pos):
                if hats[current_hat].price < player_coins:
                    player_coins -= hats[current_hat].price
                    updatePlayerCoins()
                    hats[current_hat].owned = True
                    updateOwnedHats()
            elif event.type == pygame.MOUSEBUTTONDOWN and equip_button_rect.collidepoint(event.pos):
                if not hats[current_hat] == player.hat and hats[current_hat].owned:
                    if not player.hat == None:
                        player.removeHat()
                    player.equipHat(hats[current_hat])

    if GAMESTATE == GameState.PLAYING:
        player.update()
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
    with open('player_coins.txt', 'r') as file:
        player_coins = int(file.read())

def getOwnedHats():
    with open('owned_hats.txt', 'r') as file:
        for line in file:
            for hat in hats:
                if line.strip() == hat.name:
                    hat.owned = True

def updateOwnedHats():
    with open('owned_hats.txt', 'w') as file:
        for hat in hats:
            if hat.owned:
                file.write(hat.name + '\n')

def updatePlayerCoins():
    with open('player_coins.txt', 'w') as file:
        file.write(f"{player_coins}")

def restart():
    global score, player_coins, current_hat, platforms, coins, GAMESTATE, platform_spawnable, coin_spawnable
    score = 0
    getPlayerCoins()
    getOwnedHats()
    current_hat = 0
    platforms = []
    coins = []
    GAMESTATE = GameState.TITLE
    platform_spawnable = True
    coin_spawnable = True
    getHighscore()
    platforms.append(Platform(starting_platform, (300, 400), True))
    platforms[0].reached_mid = True
    player.reset()

def main():
    restart()
    while True:
        draw_window()
        event_loop()
        clock.tick(60)

if __name__ == '__main__':
    main()