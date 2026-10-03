"""
Parámetros centralizados de configuración del juego ( Aca mas que todo configuras la pantalla, los valores de vida de cada cosa
                                                     cuanto daño aplican cada cosa que funciona en el juego, etc...)
                                                     Si agregas algo aca lo tenes que llamar a algun codigo, es como la base

"""

# === Ventana ===
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "LAS FLIPANTES AVENTURAS DE YESID BALANTA"

# === Jugador  ===
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_FIRE_RATE = 250  # ms entre disparos
PLAYER_BULLET_SPEED = 8
PLAYER_INVULN_TIME = 1500  # ms de invulnerabilidad tras recibir daño
PLAYER_BULLET_SIZE = 40  # Tamaño de las balas del jugador (75% del original)



# === Nivel 1: Lluvia de Asteroides 
LEVEL1_ASTEROID_GOAL = 15
LEVEL1_ASTEROID_SPAWN_RATE = 800  # ms entre spawns
LEVEL1_ASTEROID_SPEED_MIN = 1.5
LEVEL1_ASTEROID_SPEED_MAX = 3.5
LEVEL1_ASTEROID_SPAWN_CHANCE = 0.7  # probabilidad de spawn en cada tick

# === Nivel 2: Combate Mixto 
LEVEL2_ENEMY_GOAL = 9
LEVEL2_ASTEROID_GOAL = 5
LEVEL2_ENEMY_SPAWN_RATE = 2000
LEVEL2_ASTEROID_SPAWN_RATE = 2500
LEVEL2_ENEMY_SPEED = 2
LEVEL2_ENEMY_FIRE_RATE = 1500
LEVEL2_ENEMY_HEALTH = 2
LEVEL2_ENEMY_BULLET_SPEED = 5

# === Nivel 3: Jefe Final 
LEVEL3_WAVE_ENEMIES = 6
LEVEL3_ENEMY_SPAWN_RATE = 1500
BOSS_MAX_HEALTH = 500
BOSS_SPEED = 2.5
BOSS_FIRE_RATE = 800
BOSS_BULLET_SPEED = 6
BOSS_PATTERN_CHANGE = 3000  # ms entre cambios de patrón

# === Asteroides (compartido) ===
ASTEROID_MIN_RADIUS = 30  # Aumentado 25% (15 -> 19)
ASTEROID_MAX_RADIUS = 50  # Aumentado 25% (40 -> 50)
ASTEROID_HEALTH_DIVISOR = 20  # salud = radio / divisor

# === Enemigos por tipo ===
# Rojo: fila de 5, izquierda a derecha, ataca cada 2 seg, 50% más lento
ENEMY_ROJO_COUNT = 5
ENEMY_ROJO_FIRE_RATE = 2000
ENEMY_ROJO_SPEED = 1.0  # 50% más lento que el base
ENEMY_ROJO_HEALTH = 2
ENEMY_ROJO_BULLET_DAMAGE = 50  # Mata de 2 golpes (100 HP / 50 = 2)

# Rosa: 3 en nivel 2, movimiento seno, ataca cada 3 seg
ENEMY_ROSA_COUNT = 3
ENEMY_ROSA_FIRE_RATE = 3500
ENEMY_ROSA_SPEED = 1.5
ENEMY_ROSA_HEALTH = 2
ENEMY_ROSA_BULLET_DAMAGE = 50

# Verde: 2 en nivel 2, movimiento coseno, ataca cada 1.75 seg
ENEMY_VERDE_COUNT = 2
ENEMY_VERDE_FIRE_RATE = 1750
ENEMY_VERDE_SPEED = 2.0
ENEMY_VERDE_HEALTH = 2
ENEMY_VERDE_BULLET_DAMAGE = 50


# === Power-ups ===
POWERUP_HEALTH_AMOUNT = 30
POWERUP_DROP_CHANCE = 0.15  # 15% de probabilidad de drop
POWERUP_DURATION = 7000  # ms de duración para power-ups temporales (7 segundos)

# Power-up naranja (bala morada): +0.00025 daño
POWERUP_ORANGE_DAMAGE_MULTIPLIER = 1.00025
POWERUP_ORANGE_FIRE_RATE_MULTIPLIER = 2.0  # Aumenta el tiempo de recarga (mas lento)
BULLET_MORADA_SPEED = 1.5  # Velocidad de la bala morada

# Power-up azul (bala verde): -1.25% daño pero dispara más rápido
POWERUP_BLUE_DAMAGE_MULTIPLIER = 0.9875
POWERUP_BLUE_FIRE_RATE_MULTIPLIER = 0.5  # Dispara el doble de rápido
BULLET_VERDE_MAX_RANGE = 250

# === Colores ===
COLOR_BG_LEVEL1 = (10, 10, 30)
COLOR_BG_LEVEL2 = (20, 5, 40)
COLOR_BG_LEVEL3 = (40, 5, 10)
COLOR_PLAYER = (0, 200, 255)
COLOR_PLAYER_BULLET = (255, 255, 0)
COLOR_ENEMY = (255, 80, 80)
COLOR_ENEMY_BULLET = (255, 100, 100)
COLOR_ASTEROID = (150, 150, 150)
COLOR_BOSS = (200, 0, 100)
COLOR_BOSS_BULLET = (255, 0, 150)
COLOR_HUD = (255, 255, 255)
COLOR_HEALTH_BAR = (0, 255, 0)
COLOR_HEALTH_BAR_BG = (100, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_TRANSITION = (0, 0, 0)

# === Colores Power-ups ===
COLOR_POWERUP_HEALTH = (255, 0, 0)  # Rojo - vida
COLOR_POWERUP_ORANGE = (255, 165, 0)  # Naranja - bala morada (+daño)
COLOR_POWERUP_BLUE = (0, 150, 255)  # Azul - bala verde (+velocidad)

# === Puntuación ===
SCORE_ASTEROID = 10
SCORE_ENEMY = 50
SCORE_BOSS = 500

# === Otros ===
POWERUP_SPEED_BOOST = 2.0  # Velocidad extra al recoger power-up azul