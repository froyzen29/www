import sys
import os
from pygame import *
from random import randint

# Функция для корректной загрузки ресурсов в EXE и при обычном запуске
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, size=(65, 65)):
        super().__init__()
        # Загрузка изображения с использованием resource_path
        self.image = transform.scale(image.load(resource_path(player_image)), size)
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 70:
            self.rect.x += self.speed

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, size=(65, 65)):  
        super().__init__(player_image, player_x, player_y, player_speed, size)  
        self.is_asteroid = "asteroid" in player_image
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = 0
            self.rect.x = randint(0, win_width - self.rect.width)
            if not self.is_asteroid:
                global missed
                missed += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0: 
            self.kill()  

# Инициализация pygame
init()
mixer.init()

# Загрузка ресурсов с использованием resource_path
try:
    mixer.music.load(resource_path('space.ogg'))
    fire_sound = mixer.Sound(resource_path('fire.ogg'))
    background_img = resource_path('galaxy.jpg')
    rocket_img = resource_path('rocket.png')
    ufo_img = resource_path('ufo.png')
    asteroid_img = resource_path('asteroid.png')
    bullet_img = resource_path('bullet.png')
except Exception as e:
    print(f"Ошибка загрузки ресурсов: {e}")
    sys.exit()

# Настройка окна игры
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption('Космический шутер')
background = transform.scale(image.load(background_img), (win_width, win_height))

# Настройка шрифтов
font.init()
stats_font = font.SysFont('Arial', 36)
game_over_font = font.SysFont('Arial', 72)
score = 0
missed = 0

# Создание игрока
player = Player(rocket_img, win_width/2, win_height-80, 5)

# Создание групп спрайтов
enemies = sprite.Group()  
ufos = sprite.Group()     
asteroids = sprite.Group() 

# Создание врагов
for _ in range(3):
    enemy = Enemy(ufo_img, randint(0, win_width-65), -50, randint(1, 3))
    enemies.add(enemy)
    ufos.add(enemy)

# Создание астероидов
for _ in range(2):
    asteroid = Enemy(asteroid_img, randint(0, win_width-80), -100, randint(1, 2), size=(80, 80))
    enemies.add(asteroid)
    asteroids.add(asteroid)

# Группа пуль
bullets = sprite.Group()  

# Основные переменные игры
run = True
game_over = False
win = False
clock = time.Clock()
FPS = 60

# Воспроизведение фоновой музыки
try:
    mixer.music.play(-1)
except:
    print("Не удалось воспроизвести фоновую музыку")

# Главный игровой цикл
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE and not game_over:  
                bullet = Bullet(bullet_img, player.rect.centerx - 10, player.rect.top, 10)
                bullets.add(bullet)
                try:
                    fire_sound.play()
                except:
                    print("Не удалось воспроизвести звук выстрела")
            if e.key == K_r and game_over: 
                # Перезапуск игры
                score = 0
                missed = 0
                game_over = False
                win = False
                player.rect.x = win_width/2
                player.rect.y = win_height-80
                enemies.empty()
                ufos.empty()
                asteroids.empty()
                bullets.empty()

                for _ in range(3):
                    enemy = Enemy(ufo_img, randint(0, win_width-65), -50, randint(1, 3))
                    enemies.add(enemy)
                    ufos.add(enemy)

                for _ in range(2):
                    asteroid = Enemy(asteroid_img, randint(0, win_width-80), -100, randint(1, 2), (80, 80))
                    enemies.add(asteroid)
                    asteroids.add(asteroid)
    
    if not game_over:
        window.blit(background, (0,0))
        
        # Обновление спрайтов
        enemies.update()
        player.update()
        bullets.update()
        
        # Отрисовка спрайтов
        enemies.draw(window)
        player.reset()
        bullets.draw(window)
        
        # Проверка столкновений
        hits = sprite.groupcollide(ufos, bullets, True, True)
        for hit in hits:
            score += 1
            enemy = Enemy(ufo_img, randint(0, win_width-65), -50, randint(1, 3))
            enemies.add(enemy)
            ufos.add(enemy)
        
        # Проверка условий окончания игры
        if sprite.spritecollide(player, enemies, False):
            game_over = True
            win = False
        
        if missed >= 3:
            game_over = True
            win = False
        
        if score >= 10:
            game_over = True
            win = True
        
        # Отображение счета
        score_text = stats_font.render(f"Сбито: {score}", True, (255, 255, 255))
        missed_text = stats_font.render(f"Пропущено: {missed}", True, (255, 255, 255))
        window.blit(score_text, (10, 10))
        window.blit(missed_text, (10, 50))
    else:
        # Экран окончания игры
        if win:
            result_text = game_over_font.render("ПОБЕДА!", True, (0, 255, 0))
        else:
            result_text = game_over_font.render("ПОРАЖЕНИЕ!", True, (255, 0, 0))
        restart_text = stats_font.render("Нажмите R для рестарта", True, (255, 255, 255))
        
        window.blit(background, (0,0))
        window.blit(result_text, (win_width/2 - result_text.get_width()/2, win_height/2 - 50))
        window.blit(restart_text, (win_width/2 - restart_text.get_width()/2, win_height/2 + 50))
        window.blit(score_text, (10, 10))
        window.blit(missed_text, (10, 50))
    
    display.update()
    clock.tick(FPS)

quit()
