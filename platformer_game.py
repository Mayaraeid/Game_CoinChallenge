#Importe de bibliotecas permitidas no projeto
import pgzrun
import random
import math
from pygame import Rect

#Tamanho da janela
WIDTH = 800
HEIGHT = 600

#Título do jogo
TITLE = "Desafio das Moedas"

#Cores usadas no jogo
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

#Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2

#Estado atual do jogo - Inicialização
game_state = MENU

#Configuração de áudio - Inicialização
music_on = True
sound_on = True

# Pontuação
score = 0

#Criação do herói (objeto)
hero = Actor('hero_idle1', (WIDTH // 4, HEIGHT - 100))
hero.speed_y = 0
hero.speed_x = 0
hero.on_ground = False
hero.frame = 0
hero.animation_timer = 0
hero.facing_right = True
hero.alive = True

#Criação das plataformas
platforms = [
    Rect(0, HEIGHT - 40, WIDTH, 40),
    Rect(100, HEIGHT - 150, 200, 20),
    Rect(400, HEIGHT - 200, 200, 20),
    Rect(200, HEIGHT - 300, 150, 20),
    Rect(500, HEIGHT - 350, 200, 20),
]

#Criação dos inimigos (objeto) - aleatoriedade
enemies = []
for i in range(3):
    enemy = Actor('enemy_idle1', (random.randint(200, WIDTH - 100), 0))
    enemy.speed_x = random.choice([-2, 2])
    enemy.speed_y = 0
    enemy.frame = 0
    enemy.animation_timer = 0
    enemy.platform_index = random.randint(1, len(platforms) - 1)
    enemy.pos = (platforms[enemy.platform_index].x + platforms[enemy.platform_index].width // 2, platforms[enemy.platform_index].y - 30)
    enemy.patrol_start = enemy.pos[0] - 100
    enemy.patrol_end = enemy.pos[0] + 100
    enemy.facing_right = True
    enemies.append(enemy)

#Criação das moedas (objeto) - aleatoriedade
collectibles = []
for i in range(5):
    collectible = Actor('coin', (random.randint(100, WIDTH - 100), 0))
    platform_index = random.randint(0, len(platforms) - 1)
    collectible.pos = (random.randint(platforms[platform_index].left + 20, platforms[platform_index].right - 20),
                      platforms[platform_index].top - 30)
    collectibles.append(collectible)

#Botão do menu
start_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
sound_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
exit_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)

#Funções de animação - Heroi
def animate_hero():
    hero.animation_timer += 1
    
    if not hero.on_ground:
        #Pulo
        if hero.speed_y < 0:
            hero.image = 'hero_jump'
        else:
            hero.image = 'hero_fall'
    elif abs(hero.speed_x) > 0.1:
        #Corrida
        if hero.animation_timer % 6 == 0:
            hero.frame = (hero.frame + 1) % 4
            hero.image = f'hero_run{hero.frame + 1}'
    else:
        #Idle
        if hero.animation_timer % 10 == 0:
            hero.frame = (hero.frame + 1) % 2
            hero.image = f'hero_idle{hero.frame + 1}'
    
    #Virar sprite baseado na direção
    if hero.speed_x > 0:
        hero.facing_right = True
    elif hero.speed_x < 0:
        hero.facing_right = False
        
    if not hero.facing_right:
        hero.flip_x = True
    else:
        hero.flip_x = False

#Funções de animação - Inimigo
def animate_enemies():
    for enemy in enemies:
        enemy.animation_timer += 1
        
        if abs(enemy.speed_x) > 0.1:
            #Movimento
            if enemy.animation_timer % 8 == 0:
                enemy.frame = (enemy.frame + 1) % 2
                enemy.image = f'enemy_run{enemy.frame + 1}'
        else:
            #Idle
            if enemy.animation_timer % 12 == 0:
                enemy.frame = (enemy.frame + 1) % 2
                enemy.image = f'enemy_idle{enemy.frame + 1}'
        
        #Virar sprite baseado na direção
        if enemy.speed_x > 0:
            enemy.facing_right = True
            enemy.flip_x = False
        else:
            enemy.facing_right = False
            enemy.flip_x = True

#Lógica do jogo
def update():
    global game_state, score, music_on, sound_on
    
    #Música de background - On e Off
    if music_on and not music.is_playing('background_music'):
        music.play('background_music')
    elif not music_on and music.is_playing('background_music'):
        music.stop()
    
    #Menu principal
    if game_state == MENU:
        return
    
    #Jogo
    if game_state == PLAYING and hero.alive:
        update_hero()
        update_enemies()
        check_collisions()
        animate_hero()
        animate_enemies()
    
    #Game Over
    elif game_state == GAME_OVER:
        if keyboard.space:
            reset_game()

def update_hero():
    global game_state
    
    #Gravidade
    hero.speed_y += 0.5
    
    #Movimento horizontal
    if keyboard.left:
        hero.speed_x = -5
    elif keyboard.right:
        hero.speed_x = 5
    else:
        hero.speed_x *= 0.8
    
    #Pulo
    if keyboard.up and hero.on_ground:
        hero.speed_y = -12
        if sound_on:
            sounds.jump.play()
    
    #Atualizar posição
    hero.x += hero.speed_x
    hero.y += hero.speed_y
    
    #Limites da tela
    if hero.x < 30:
        hero.x = 30
    if hero.x > WIDTH - 30:
        hero.x = WIDTH - 30
    
    #Verificar colisão com plataforma
    hero.on_ground = False
    for platform in platforms:
        if (hero.colliderect(platform) and hero.speed_y > 0 and 
            hero.y < platform.y + platform.height // 2):
            hero.y = platform.y - hero.height // 2
            hero.on_ground = True
            hero.speed_y = 0
    
    #Verificar se caiu da tela
    if hero.y > HEIGHT:
        if sound_on:
            sounds.death.play()
        hero.alive = False
        game_state = GAME_OVER

def update_enemies():
    for enemy in enemies:
        #Movimento de patrulha
        if enemy.x <= enemy.patrol_start:
            enemy.speed_x = 2
        elif enemy.x >= enemy.patrol_end:
            enemy.speed_x = -2
            
        enemy.x += enemy.speed_x
        
        #Gravidade
        enemy.speed_y += 0.5
        enemy.y += enemy.speed_y
        
        #Colisão com plataformas
        for platform in platforms:
            if (enemy.colliderect(platform) and enemy.speed_y > 0 and 
                enemy.y < platform.y + platform.height // 2):
                enemy.y = platform.y - enemy.height // 2
                enemy.speed_y = 0

def check_collisions():
    global score, game_state
    
    #Colisão com inimigos
    for enemy in enemies:
        if hero.colliderect(enemy):
            if hero.speed_y > 0 and hero.y < enemy.y - enemy.height // 4:
                #Pular no inimigo
                hero.speed_y = -10
                enemies.remove(enemy)
                score += 50
                if sound_on:
                    sounds.stomp.play()
            else:
                #Morte
                if sound_on:
                    sounds.death.play()
                hero.alive = False
                game_state = GAME_OVER
    
    #Colisão com moeda
    for collectible in list(collectibles):
        if hero.colliderect(collectible):
            collectibles.remove(collectible)
            score += 100
            if sound_on:
                sounds.coin.play()

def reset_game():
    global game_state, score, hero, enemies, collectibles
    
    #Reset do status e ponto
    game_state = PLAYING
    score = 0
    
    #Reset do heroi
    hero.pos = (WIDTH // 4, HEIGHT - 100)
    hero.speed_y = 0
    hero.speed_x = 0
    hero.alive = True
    
    #Reset dos inimigos
    enemies = []
    for i in range(3):
        enemy = Actor('enemy_idle1', (random.randint(200, WIDTH - 100), 0))
        enemy.speed_x = random.choice([-2, 2])
        enemy.speed_y = 0
        enemy.frame = 0
        enemy.animation_timer = 0
        enemy.platform_index = random.randint(1, len(platforms) - 1)
        enemy.pos = (platforms[enemy.platform_index].x + platforms[enemy.platform_index].width // 2,
                    platforms[enemy.platform_index].y - 30)
        enemy.patrol_start = enemy.pos[0] - 100
        enemy.patrol_end = enemy.pos[0] + 100
        enemy.facing_right = True
        enemies.append(enemy)
    
    #Reset das moedas
    collectibles = []
    for i in range(5):
        collectible = Actor('coin', (random.randint(100, WIDTH - 100), 0))
        platform_index = random.randint(0, len(platforms) - 1)
        collectible.pos = (random.randint(platforms[platform_index].left + 20, platforms[platform_index].right - 20),
                          platforms[platform_index].top - 30)
        collectibles.append(collectible)

def on_mouse_down(pos):
    global game_state, music_on, sound_on
    
    #Lógica de click no menu
    if game_state == MENU:
        if start_button.collidepoint(pos):
            game_state = PLAYING
            if sound_on:
                sounds.click.play()
        elif sound_button.collidepoint(pos):
            music_on = not music_on
            sound_on = not sound_on
            if sound_on:
                sounds.click.play()
        elif exit_button.collidepoint(pos):
            exit()
    
    #Tela de game over - restart
    elif game_state == GAME_OVER:
        reset_game()

def draw():
    screen.fill(BLACK)
    
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING or game_state == GAME_OVER:
        draw_game()
        
        if game_state == GAME_OVER:
            draw_game_over()

def draw_menu():
    #Título
    screen.draw.text("DESAFIO DAS MOEDAS", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color=WHITE)
    
    #Botões
    screen.draw.filled_rect(start_button, GREEN)
    screen.draw.filled_rect(sound_button, BLUE)
    screen.draw.filled_rect(exit_button, RED)
    
    #Texto dos botões
    screen.draw.text("INICIAR!", center=start_button.center, fontsize=30, color=BLACK)
    sound_text = "DESLIGAR SOM" if sound_on else "LIGAR SOM"
    screen.draw.text(sound_text, center=sound_button.center, fontsize=30, color=BLACK)
    screen.draw.text("SAIR", center=exit_button.center, fontsize=30, color=BLACK)
    
    #Instruções
    screen.draw.text("Controle seu heroi com as setas!", center=(WIDTH // 2, HEIGHT - 100), fontsize=25, color=WHITE)

def draw_game():
    #Desenhar plataformas
    for platform in platforms:
        screen.draw.filled_rect(platform, (100, 100, 100))
    
    #Desenhar coletáveis
    for collectible in collectibles:
        collectible.draw()
    
    #Desenhar inimigos
    for enemy in enemies:
        enemy.draw()
    
    #Desenhar herói
    if hero.alive:
        hero.draw()
    
    #Desenhar pontuação
    screen.draw.text(f"Pontos: {score}", topleft=(20, 20), fontsize=30, color=WHITE)

def draw_game_over():
    #Tela de Game Over
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color=RED)
    screen.draw.text(f"Ponto total: {score}", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=40, color=WHITE)
    screen.draw.text("Clique na tecla de espaco pra iniciar novamente", center=(WIDTH // 2, HEIGHT // 2 + 80), fontsize=30, color=WHITE)

pgzrun.go()