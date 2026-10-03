"""
Clases de entidades del juego ( TODOS LOS ENEMIGOS DEL JUEGO Y SU CODIGO AQUI )
Usa sprites cargados desde assets/images/
Pods: No eliminen la barra de vida de ninguno, es caotico

"""

import pygame
import random
import math
from config import *


class Player(pygame.sprite.Sprite):
    """Nave del jugador con control de movimiento y disparo """

    def __init__(self, sprite_manager=None):
        super().__init__()
        self.sprite_manager = sprite_manager
        # Usar sprite del jugador o forma geométrica como fallback
        if sprite_manager:
            self.image = sprite_manager.get_player_frame("centro", 0)
        else:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 40), (20, 30), (40, 40)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.last_shot = 0
        self.fire_rate = PLAYER_FIRE_RATE
        self.invulnerable = False
        self.invuln_timer = 0
        self.alive = True
        self.direction = "centro"  # Dirección para animación
        self.anim_frame = 0
        self.anim_timer = 0
        # Power-ups activos
        self.damage_multiplier = 1.0
        self.fire_rate_multiplier = 1.0
        self.bullet_type = "dorada"  # Tipo de bala actual (dorada, morada, verde)

    def update(self, keys, dt):
        """Actualizar posición """
        if not self.alive:
            return False

        # Movimiento
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.direction = "izq"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.direction = "der"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        # Si no hay movimiento horizontal, volver al centro
        if dx == 0:
            self.direction = "centro"

        # Normalizar diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Límites de pantalla
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        # Actualizar animación
        self.anim_timer += dt
        if self.anim_timer > 100:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 3

        # Disparo (RF-01)
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - self.last_shot > self.fire_rate * self.fire_rate_multiplier:
            self.last_shot = now
            return True  # Indica que debe disparar

        # Invulnerabilidad
        if self.invulnerable:
            if now - self.invuln_timer > PLAYER_INVULN_TIME:
                self.invulnerable = False

        return False

    def take_damage(self, amount):
        """Gestionar daño recibido """
        if self.invulnerable or not self.alive:
            return False
        self.health -= amount
        self.invulnerable = True
        self.invuln_timer = pygame.time.get_ticks()
        if self.health <= 0:
            self.health = 0
            self.alive = False
        return True

    def draw(self, surface):
        """Dibujar nave con parpadeo si es invulnerable"""
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        # Usar sprite según dirección
        if self.sprite_manager:
            self.image = self.sprite_manager.get_player_frame(self.direction, self.anim_frame)
        surface.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    """Proyectil genérico con sprites animados"""

    def __init__(self, x, y, speed, color, direction=(0, -1), radius=4, sprite_manager=None, bullet_type="dorada", damage=1):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.bullet_type = bullet_type
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.anim_frame = 0
        self.anim_timer = 0
        self.distance_traveled = 0

        # Usar sprite de bala o círculo como fallback
        if sprite_manager:
            if bullet_type == "boss":
                self.image = sprite_manager.get_boss_projectile_frame(0)
                self.image = pygame.transform.scale(self.image, (70, 70)) #Tamaño de las balas <---- Tamaño ( si modificas esto 
                                                                          # para no dañar la animacion tenes que modificar lo siguiente: 
                                                                          # esta en "def update" Actualizar animacion self.image)
            else:
                self.image = sprite_manager.get_bullet_frame(bullet_type, 0)
                # Escalar la bala según el tipo
                if bullet_type == "dorada":
                    self.image = pygame.transform.scale(self.image, (PLAYER_BULLET_SIZE, PLAYER_BULLET_SIZE))

                if bullet_type == "morada":
                    self.speed = BULLET_MORADA_SPEED  # Velocidad de la bala morada
                

            #Rotacion de las balas enemigas
            if self.direction[1] > 0 and bullet_type != "boss":
                self.image = pygame.transform.rotate(self.image, 180)
        
        else:
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        

    def update(self, dt):

        """Actualizar posición de la bala"""
        move_x = self.direction[0] * self.speed
        move_y = self.direction[1] * self.speed

        #Limitar distancia disparo
        self.rect.x += move_x
        self.rect.y += move_y

        #Acumula la distancia recorrida
        self.distance_traveled += math.hypot(move_x, move_y)

        #Limitacion
        if self.bullet_type == "verde" and self.distance_traveled > BULLET_VERDE_MAX_RANGE:
            self.kill()
            return
        
        # Actualizar animación
        self.anim_timer += dt
        if self.anim_timer > 50:
            self.anim_timer = 0
            self.anim_frame += 1

            if self.sprite_manager:
                if self.bullet_type == "boss":
                    self.image = self.sprite_manager.get_boss_projectile_frame(self.anim_frame)
                    self.image = pygame.transform.scale(self.image, (70, 70)) #Escala animacion <------ ESTO TAMBIEN LO TENES QUE MODIFICAR
                                                                                                        # solo los numeros
                else:
                    self.image = self.sprite_manager.get_bullet_frame(self.bullet_type, self.anim_frame)
                
                    if self.bullet_type == "dorada":
                        self.image = pygame.transform.scale(self.image, (PLAYER_BULLET_SIZE, PLAYER_BULLET_SIZE))

                    if self.direction[1] > 0:
                        self.image = pygame.transform.rotate(self.image, 180)
        
        # Eliminar si sale de pantalla
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or \
           self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Asteroid(pygame.sprite.Sprite):
    """Asteroide con animación de sprites"""

    def __init__(self, x=None, y=None, speed_multiplier=1.0, sprite_manager=None):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.radius = random.randint(ASTEROID_MIN_RADIUS, ASTEROID_MAX_RADIUS)
        # Usar sprite de asteroide o forma geométrica como fallback
        if sprite_manager:
            self.image = sprite_manager.get_asteroid_frame(0)
        else:
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = self.radius * random.uniform(0.7, 1.0)
                px = self.radius + r * math.cos(angle)
                py = self.radius + r * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(self.image, COLOR_ASTEROID, points)
        self.rect = self.image.get_rect()
        self.rect.centerx = x if x is not None else random.randint(0, SCREEN_WIDTH)
        self.rect.y = y if y is not None else -self.radius

        speed = random.uniform(LEVEL1_ASTEROID_SPEED_MIN, LEVEL1_ASTEROID_SPEED_MAX) * speed_multiplier
        angle = random.uniform(math.pi * 0.3, math.pi * 0.7)  # Hacia abajo
        self.vx = speed * math.cos(angle) * random.choice([-1, 1])
        self.vy = speed * math.sin(angle)
        self.health = int(self.radius / ASTEROID_HEALTH_DIVISOR) + 1
        self.max_health = self.health
        self.rotation = 0
        self.rot_speed = random.uniform(-2, 2)
        self.anim_frame = 0
        self.anim_timer = 0
        self.hit_timer = 0  # Para mostrar sprite de golpe

    def update(self, dt):
        """Actualizar posición y animación del asteroide"""
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.rotation += self.rot_speed
        # Actualizar animación - usar los 8 frames del asteroide
        self.anim_timer += dt
        if self.anim_timer > 80:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 8
            if self.sprite_manager:
                self.image = self.sprite_manager.get_asteroid_frame(self.anim_frame)
        # Temporizador de golpe
        if self.hit_timer > 0:
            self.hit_timer -= dt
        # Eliminar si sale de pantalla
        if self.rect.top > SCREEN_HEIGHT + 50 or \
           self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50:
            self.kill()

    def take_damage(self, amount=1):
        """Recibir daño y mostrar sprite de golpe"""
        self.health -= amount
        self.hit_timer = 200  # Mostrar sprite de golpe por 200ms
        if self.sprite_manager:
            self.image = self.sprite_manager.get_asteroid_hit()
        if self.health <= 0:
            self.kill()
            return True
        return False

    def draw(self, surface):
        """Dibujar asteroide con barra de vida"""
        surface.blit(self.image, self.rect)
        # Barra de vida pequeña
        bar_width = 30
        bar_height = 4
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 8
        # Fondo
        pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))
        # Vida
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))


class Enemy(pygame.sprite.Sprite):
    """Nave enemiga con patrones de movimiento y disparo """

    def __init__(self, pattern="sine", sprite_manager=None, enemy_type="rojo_abajo"):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.enemy_type = enemy_type
        # Usar sprite de enemigo o forma geométrica como fallback
        if sprite_manager:
            frames = sprite_manager.get_enemy_frames(enemy_type)
            self.image = frames[0]
        else:
            self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_ENEMY, [(17, 35), (0, 0), (17, 10), (35, 0)])
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -20))
        self.pattern = pattern
        # Configuración según tipo de enemigo
        self._setup_enemy_type()
        self.last_shot = 0
        self.time_alive = 0
        self.start_x = self.rect.centerx
        self.anim_frame = 0
        self.anim_timer = 0
        self.hit_timer = 0

    def _setup_enemy_type(self):
        """Configurar estadísticas según el tipo de enemigo"""
        if "rojo" in self.enemy_type:
            self.speed = ENEMY_ROJO_SPEED
            self.health = ENEMY_ROJO_HEALTH
            self.fire_rate = ENEMY_ROJO_FIRE_RATE
            self.bullet_damage = ENEMY_ROJO_BULLET_DAMAGE
            self.bullet_type = "blanca"
        elif "rosa" in self.enemy_type:
            self.speed = ENEMY_ROSA_SPEED
            self.health = ENEMY_ROSA_HEALTH
            self.fire_rate = ENEMY_ROSA_FIRE_RATE
            self.bullet_damage = ENEMY_ROSA_BULLET_DAMAGE
            self.bullet_type = "morada"
        elif "verde" in self.enemy_type:
            self.speed = ENEMY_VERDE_SPEED
            self.health = ENEMY_VERDE_HEALTH
            self.fire_rate = ENEMY_VERDE_FIRE_RATE
            self.bullet_damage = ENEMY_VERDE_BULLET_DAMAGE
            self.bullet_type = "verde"
        else:
            self.speed = LEVEL2_ENEMY_SPEED
            self.health = LEVEL2_ENEMY_HEALTH
            self.fire_rate = LEVEL2_ENEMY_FIRE_RATE
            self.bullet_damage = 10
            self.bullet_type = "blanca"
        self.max_health = self.health

    def update(self, dt, player_pos=None):
        """Patrones de movimiento predefinidos"""
        self.time_alive += dt

        # Verificar si salió de pantalla ANTES de cualquier otra lógica
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
            return False

        # Movimiento según tipo de enemigo
        if "rojo" in self.enemy_type:
            # Rojo: fila en parte superior, izquierda a derecha
            self.rect.y = 50  # Mantener en la parte superior
            self.rect.x += self.speed
            if self.rect.x > SCREEN_WIDTH - 30:
                self.rect.x = 30
        elif "rosa" in self.enemy_type:
            # Rosa: movimiento seno
            self.rect.x = self.start_x + math.sin(self.time_alive * 0.003) * 150
            self.rect.y += self.speed
        elif "verde" in self.enemy_type:
            # Verde: movimiento coseno
            self.rect.x = self.start_x + math.cos(self.time_alive * 0.004) * 120
            self.rect.y += self.speed * 0.5
        else:
            # Patrón por defecto
            if self.pattern == "sine":
                self.rect.x = self.start_x + math.sin(self.time_alive * 0.003) * 100
                self.rect.y += self.speed
            elif self.pattern == "zigzag":
                self.rect.x += self.speed * (1 if int(self.time_alive / 500) % 2 == 0 else -1)
                self.rect.y += self.speed * 0.5
            elif self.pattern == "dive":
                self.rect.y += self.speed * 1.5
                if player_pos:
                    self.rect.x += math.copysign(self.speed * 0.5, player_pos[0] - self.rect.x)

        # Actualizar animación
        self.anim_timer += dt
        if self.anim_timer > 150:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 3
            if self.sprite_manager:
                frames = self.sprite_manager.get_enemy_frames(self.enemy_type)
                self.image = frames[self.anim_frame]

        # Temporizador de golpe
        if self.hit_timer > 0:
            self.hit_timer -= dt

        # Disparo hacia el jugador  - solo si está en pantalla y por encima del jugador
        now = pygame.time.get_ticks()
        should_fire = False
        if player_pos and now - self.last_shot > self.fire_rate:
            # Solo disparar si el enemigo está por encima del jugador y en pantalla
            if self.rect.bottom < player_pos[1] and self.rect.top > 0:
                self.last_shot = now
                should_fire = True

        return should_fire

    def draw(self, surface):
        """Dibujar enemigo con barra de vida"""
        surface.blit(self.image, self.rect)
        # Barra de vida pequeña
        bar_width = 30
        bar_height = 4
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 8
        # Fondo
        pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))
        # Vida
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))

    def get_bullet(self, player_pos):

        """Crear proyectil dirigido hacia el jugador (solo si está por encima y no a los lados)"""
        if player_pos and self.rect.bottom < player_pos[1]:
            
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            # Evitar disparar si el jugador está demasiado a los lados
            if abs(dx) > abs(dy) * 1.5:
                return None 

            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
            return Bullet(
                self.rect.centerx, 
                self.rect.bottom, 
                speed = LEVEL2_ENEMY_BULLET_SPEED,
                color = COLOR_ENEMY_BULLET, 
                direction=(dx, dy), 
                sprite_manager=self.sprite_manager,
                bullet_type=self.bullet_type, 
                damage=self.bullet_damage
                )
        # Si no puede disparar, devolver None
        return None

    def take_damage(self, amount=1):
        """Recibir daño y mostrar sprite de golpe"""
        self.health -= amount
        self.hit_timer = 200
        if self.sprite_manager:
            self.image = self.sprite_manager.get_enemy_hit(self.enemy_type)
        if self.health <= 0:
            self.kill()
            return True
        return False


class Ciclope(pygame.sprite.Sprite):
    """Enemigo ciclope que aparece en el nivel 3 junto con las naves enemigas"""

    def __init__(self, sprite_manager=None):
        super().__init__()
        self.sprite_manager = sprite_manager
        # Usar sprite de ciclope o forma geométrica como fallback
        if sprite_manager:
            self.image = sprite_manager.get_ciclope_frame(0)
        else:
            self.image = pygame.Surface((45, 45), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 200, 100), (22, 22), 20)
            pygame.draw.circle(self.image, (255, 0, 0), (22, 22), 8)
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -30))
        self.speed = LEVEL2_ENEMY_SPEED * 0.8
        self.health = LEVEL2_ENEMY_HEALTH + 2
        self.max_health = self.health
        self.last_shot = 0
        self.fire_rate = 3500
        self.time_alive = 0
        self.start_x = self.rect.centerx
        self.pattern = "sine"  # Patrón de movimiento por defecto
        self.enemy_type = "ciclope"  # Tipo de enemigo
        self.anim_frame = 0
        self.anim_timer = 0
        self.hit_timer = 0

    def update(self, dt, player_pos=None):
        """Movimiento del ciclope según patrón asignado"""
        self.time_alive += dt

        # Verificar si salió de pantalla
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
            return False

        # Movimiento según patrón
        if self.pattern == "horizontal":
            # Movimiento horizontal (izquierda a derecha)
            self.rect.y = 50  # Mantener en la parte superior
            self.rect.x += self.speed
            if self.rect.x > SCREEN_WIDTH - 30:
                self.rect.x = 30
        else:
            # Movimiento oscilante (seno)
            self.rect.x = self.start_x + math.sin(self.time_alive * 0.002) * 120
            self.rect.y += self.speed

        # Actualizar animación - usar los 4 frames del ciclope
        self.anim_timer += dt
        if self.anim_timer > 120:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
            if self.sprite_manager:
                self.image = self.sprite_manager.get_ciclope_frame(self.anim_frame)

        # Temporizador de golpe
        if self.hit_timer > 0:
            self.hit_timer -= dt

        # Disparo hacia el jugador
        now = pygame.time.get_ticks()
        should_fire = False
        if player_pos and now - self.last_shot > self.fire_rate:
            if self.rect.bottom < player_pos[1] and self.rect.top > 0:
                self.last_shot = now
                should_fire = True

        return should_fire

    def draw(self, surface):
        """Dibujar ciclope con barra de vida"""
        surface.blit(self.image, self.rect)
        # Barra de vida
        bar_width = 35
        bar_height = 4
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 8
        pygame.draw.rect(surface, (100, 0, 0), (x, y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))

    def get_bullet(self, player_pos):
        """Crear proyectil dirigido hacia el jugador"""
        if player_pos and self.rect.bottom < player_pos[1]:
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            if abs(dx) > abs(dy) * 1.5:
                return None
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
            return Bullet(self.rect.centerx, self.rect.bottom, LEVEL2_ENEMY_BULLET_SPEED,
                         COLOR_ENEMY_BULLET, (dx, dy), sprite_manager=self.sprite_manager,
                         bullet_type="morada", damage=15)
        return None

    def take_damage(self, amount=1):
        """Recibir daño"""
        self.health -= amount
        self.hit_timer = 200
        if self.sprite_manager:
            self.image = self.sprite_manager.get_ciclope_hit()
        if self.health <= 0:
            self.kill()
            return True
        return False


class Boss(pygame.sprite.Sprite):
    """Cthulhu con patrones de ataque avanzados """

    def __init__(self, sprite_manager=None):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.state = "ataques" # Estado inicial
        self.anim_frame = 0
        self.anim_timer = 0

        # Usar sprite de jefe o forma geométrica como Hitbox
        if sprite_manager and hasattr(sprite_manager, 'boss_sprites'):
            raw_image = sprite_manager.boss_sprites["ataques"][0]
            self.image = pygame.transform.scale(raw_image, (100, 100)) #Ajuste animacion <---- Tamaño ( si modificas esto 
                                                                        # para no dañar la animacion tenes que modificar lo siguiente: 
                                                                        # esta en "def update" self.image )
        else:
            self.image = pygame.Surface((120, 80), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_BOSS, [
                (60, 80), (0, 40), (20, 0), (100, 0), (120, 40)
            ])
    
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, -60))
        self.health = BOSS_MAX_HEALTH
        self.max_health = BOSS_MAX_HEALTH
        self.speed = BOSS_SPEED
        self.last_shot = 0
        self.fire_rate = BOSS_FIRE_RATE
        self.pattern = 0
        self.pattern_timer = 0
        self.entering = True
        self.target_y = 80

    def update(self, dt, player_pos=None):


        #Actualizar animaciones
        self.anim_timer += dt
        if self.anim_timer > 100: #Velocidad de cuadro por ms
            self.anim_timer = 0
            if self.sprite_manager and hasattr(self.sprite_manager, 'boss_sprites'):
                frames = self.sprite_manager.boss_sprites[self.state]
                self.anim_frame = (self.anim_frame + 1) % len(frames)
                frame_image = frames[self.anim_frame]
                self.image = pygame.transform.scale(frame_image, (100, 100)) # ESTO SI O SI LO TENES QUE MODIFICAR

            #Si termina la animacion de impacto regresar a la anterior
            if self.state == "impacto" and self.anim_frame == 0:
                self.state = "ataques"


        """Patrones de ataque avanzados """
        # Entrada inicial
        if self.entering:
            self.rect.y += 2
            if self.rect.y >= self.target_y:
                self.entering = False
            return False

        self.pattern_timer += dt
        if self.pattern_timer > BOSS_PATTERN_CHANGE:
            self.pattern_timer = 0
            self.pattern = (self.pattern + 1) % 3

        # Movimiento según patrón
        if self.pattern == 0:  # Oscilación suave
            self.rect.x = SCREEN_WIDTH // 2 + math.sin(pygame.time.get_ticks() * 0.002) * 200
        elif self.pattern == 1:  # Persecución lenta
            if player_pos:
                self.rect.x += math.copysign(self.speed * 0.5, player_pos[0] - self.rect.x)
        elif self.pattern == 2:  # Movimiento en figura
            t = pygame.time.get_ticks() * 0.001
            self.rect.x = SCREEN_WIDTH // 2 + math.sin(t) * 150
            self.rect.y = self.target_y + math.cos(t * 2) * 30

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Disparo según patrón
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            return True
        return False

    def get_bullets(self, player_pos):
        """Crear proyectiles según patrón activo """
        bullets = []
        if self.pattern == 0:  # Disparo simple
            bullets.append(Bullet(self.rect.centerx, self.rect.bottom, BOSS_BULLET_SPEED,
                                 COLOR_BOSS_BULLET, (0, 1), sprite_manager=self.sprite_manager,
                                 bullet_type="boss", damage=15))
        elif self.pattern == 1:  # Triple disparo
            for angle in [-0.3, 0, 0.3]:
                dx = math.sin(angle)
                dy = math.cos(angle)
                bullets.append(Bullet(self.rect.centerx, self.rect.bottom, BOSS_BULLET_SPEED,
                                     COLOR_BOSS_BULLET, (dx, dy), sprite_manager=self.sprite_manager,
                                     bullet_type="boss", damage=15))
        elif self.pattern == 2:  # Abanico de 5 disparos
            for i in range(5):
                angle = (i - 2) * 0.25
                dx = math.sin(angle)
                dy = math.cos(angle)
                bullets.append(Bullet(self.rect.centerx, self.rect.bottom, BOSS_BULLET_SPEED,
                                     COLOR_BOSS_BULLET, (dx, dy), sprite_manager=self.sprite_manager,
                                     bullet_type="boss", damage=15))
        return bullets

    def take_damage(self, amount=1):
        """Recibir daño y cambiar de animacion"""
        self.health -= amount
        if self.state != "impacto":
            self.state = "impacto"
            self.anim_frame = 0

        if self.health <= 0:
            self.health = 0
            self.state = "muerte"
            self.kill()
            return True
        return False


class PowerUp(pygame.sprite.Sprite):
    """Power-up que aparece al destruir enemigos o asteroides"""

    def __init__(self, x, y, power_type="health", sprite_manager=None):
        super().__init__()
        self.power_type = power_type
        self.sprite_manager = sprite_manager
        # Usar sprite de power-up o forma geométrica como fallback
        if sprite_manager:
            self.image = sprite_manager.get_powerup(power_type)
        else:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            if power_type == "health":
                pygame.draw.circle(self.image, COLOR_POWERUP_HEALTH, (12, 12), 10)
            elif power_type == "orange":
                pygame.draw.circle(self.image, COLOR_POWERUP_ORANGE, (12, 12), 10)
            elif power_type == "blue":
                pygame.draw.circle(self.image, COLOR_POWERUP_BLUE, (12, 12), 10)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.time_alive = 0

    def update(self, dt):
        """Actualizar posición del power-up"""
        self.rect.y += self.speed
        self.time_alive += dt
        # Eliminar si sale de pantalla
        if self.rect.top > SCREEN_HEIGHT + 30:
            self.kill()
