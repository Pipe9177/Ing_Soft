"""

Gestor de niveles y transiciones ( Si queres cambiar algo, el movimiento de los enemigos o cuantos aparecen, aca es)

"""

import pygame
import random
from config import *
from entities import Asteroid, Enemy, Boss, Ciclope


class LevelManager:
    """Gestiona la lógica de cada nivel y las transiciones"""

    def __init__(self):
        self.current_level = 1
        self.level_state = "playing"  # playing, transition, victory, game_over
        self.transition_timer = 0
        self.transition_duration = 3000  # ms
        self.transition_alpha = 0
        self.transition_target = 0
        self._pending_level = 1

        # Contadores de objetivos
        self.asteroids_destroyed = 0
        self.enemies_destroyed = 0
        self.asteroids_spawned = 0
        self.enemies_spawned = 0

        # Acumulaciones enemigos generados
        self.rosas_spawned = 0
        self.rojos_spawned = 0
        self.verdes_spawned = 0
        self.ciclope_spawned = 0

        # Spawning
        self.last_asteroid_spawn = 0
        self.last_enemy_spawn = 0

        # Jefe
        self.boss = None
        self.boss_spawned = False
        self.boss_defeated = False

        # Fondo
        self.bg_color = COLOR_BG_LEVEL1
        self.target_bg_color = COLOR_BG_LEVEL1

    def reset(self):
        """Reiniciar para nueva partida"""
        self.current_level = 1
        self.level_state = "playing"
        self.asteroids_destroyed = 0
        self.enemies_destroyed = 0
        self.asteroids_spawned = 0
        self.enemies_spawned = 0

        # Reinicio acumulaciones
        self.rosas_spawned = 0
        self.rojos_spawned = 0
        self.verdes_spawned = 0
        self.ciclope_spawned = 0

        self.boss = None
        self.boss_spawned = False #Reiniciar el estado de spawn del jefe
        self.boss_defeated = False
        self.bg_color = COLOR_BG_LEVEL1
        self.target_bg_color = COLOR_BG_LEVEL1

    def get_objectives(self):
        """Obtener objetivos del nivel actual"""
        if self.current_level == 1:
            return {"asteroids": LEVEL1_ASTEROID_GOAL, "enemies": 0}
        elif self.current_level == 2:
            return {"asteroids": LEVEL2_ASTEROID_GOAL, "enemies": LEVEL2_ENEMY_GOAL}
        else:
            return {"asteroids": 0, "enemies": LEVEL3_WAVE_ENEMIES}

    def update(self, dt, asteroids_group, enemies_group, player_pos=None, sprite_manager=None):
        """Actualizar lógica del nivel"""

        self._sprite_manager_ref = sprite_manager  # Guardar referencia para generar el jefe final

        if self.level_state == "transition":
            self._update_transition(dt)
            return None

        if self.level_state != "playing":
            return None

        now = pygame.time.get_ticks()

        # Generación de entidades según nivel
        if self.current_level == 1:
            self._update_level1(now, asteroids_group, sprite_manager)
        elif self.current_level == 2:
            self._update_level2(now, asteroids_group, enemies_group, sprite_manager)
        elif self.current_level == 3:
            self._update_level3(now, asteroids_group, enemies_group, sprite_manager)

        # Verificar objetivos
        return self._check_objectives(asteroids_group, enemies_group)

    def _update_level1(self, now, asteroids_group, sprite_manager=None):
        
        """Nivel 1: Lluvia de asteroides"""
        if now - self.last_asteroid_spawn > LEVEL1_ASTEROID_SPAWN_RATE:
            if random.random() < LEVEL1_ASTEROID_SPAWN_CHANCE:
                asteroids_group.add(Asteroid(sprite_manager=sprite_manager))
                self.asteroids_spawned += 1
            self.last_asteroid_spawn = now

    def _update_level2(self, now, asteroids_group, enemies_group, sprite_manager=None):

        """Nivel 2: Combate mixto con patrones específicos"""
        # Asteroides en menor densidad
        if now - self.last_asteroid_spawn > LEVEL2_ASTEROID_SPAWN_RATE:
            if self.asteroids_spawned < LEVEL2_ASTEROID_GOAL * 3:
                asteroids_group.add(Asteroid(speed_multiplier=0.8, sprite_manager=sprite_manager))
                self.asteroids_spawned += 1
            self.last_asteroid_spawn = now

        # Generar enemigos con patrones específicos
        self._spawn_enemies_level2(enemies_group, sprite_manager)


    # Nivel 2: Generación de enemigos 

    def _spawn_enemies_level2(self, enemies_group, sprite_manager=None):
        """Generar enemigos del nivel 2 CON MAXIMO 9 enemigos
        """

        max_enemies = 9

        if len(enemies_group) >= max_enemies:
            return  # No generar más enemigos si ya hay 9 en pantalla

        now = pygame.time.get_ticks()

        #Inicia temporizador de oleada si no está iniciado
        if not hasattr(self, '_last_enemy_type_spawn'):
            self._last_enemy_type_spawn = 0

        #Mostrar enemigos cada tiempo si hay cupo
        if now - self._last_enemy_type_spawn < 2000:
            return  # Esperar 2 segundos entre oleadas    

        # Contar enemigos por tipo
        rojos = sum(1 for e in enemies_group if "rojo" in e.enemy_type)
        rosas = sum(1 for e in enemies_group if "rosa" in e.enemy_type)
        verdes = sum(1 for e in enemies_group if "verde" in e.enemy_type)

        max_rojos_total = 4
        max_rosas_total = 3
        max_verdes_total = 2



        # Fase 1 : Enemigos verdes (movimiento coseno)
        if self.verdes_spawned < max_verdes_total:
            enemy = Enemy(pattern="cosine", sprite_manager=sprite_manager, enemy_type="verde_abajo")
            enemy.rect.centerx = 160 + (self.verdes_spawned * 300)  # Espaciado horizontal
            enemy.rect.y = -20
            enemy.start_x = enemy.rect.centerx
            enemies_group.add(enemy)
            self.verdes_spawned += 1
            self._last_enemy_type_spawn = now  # Reiniciar temporizador de oleada
            return

        #Fase 2 : Enemigos rojos (movimiento horizontal)
        if self.rojos_spawned < max_rojos_total:
            enemy = Enemy(pattern="horizontal", sprite_manager=sprite_manager, enemy_type="rojo_abajo")
            enemy.rect.centerx = 80 + (self.rojos_spawned * 180)  # Distribución horizontal uniforme
            enemy.rect.y = 50
            enemy.start_x = enemy.rect.centerx
            enemies_group.add(enemy)
            self.rojos_spawned += 1
            self._last_enemy_type_spawn = now  # Reiniciar temporizador de oleada
            return

        # Fase 3 : Enemigos rosas (movimiento seno)
        if self.rosas_spawned < max_rosas_total:
            enemy = Enemy(pattern="sine", sprite_manager=sprite_manager, enemy_type="rosa_abajo")
            enemy.rect.centerx = 120 + (self.rosas_spawned * 240)  # Espaciado horizontal
            enemy.rect.y = -20
            enemy.start_x = enemy.rect.centerx
            enemies_group.add(enemy)
            self.rosas_spawned += 1
            self._last_enemy_type_spawn = now  # Reiniciar temporizador de oleada
            return


    #Nivel 3: Oleada pre-jefe con ciclope 

    def _update_level3(self, now, asteroids_group, enemies_group, sprite_manager=None):
        """Nivel 3: Oleada pre-jefe con ciclope"""
       
        if not self.boss_spawned and self.boss is None and not self.boss_defeated:
            # Generar enemigos con patrones similares al nivel 2 pero más densos
            self._spawn_enemies_level3(enemies_group, sprite_manager)

    def _spawn_enemies_level3(self, enemies_group, sprite_manager=None):
        """Generar enemigos del nivel 3 - maximo 7 enemigos ciclopes reemplazan a naves rojas"""

        MAX_ENEMIES = 7  # Máximo de enemigos en pantalla

        if len(enemies_group) >= MAX_ENEMIES:
            return  # No generar más enemigos si ya hay 7 en pantalla
        
        
        # Contar enemigos por tipo
        rosas = sum(1 for e in enemies_group if "rosa" in e.enemy_type)
        ciclope = sum(1 for e in enemies_group if isinstance(e, Ciclope))

        # En nivel 3: enemigos distribuidos en 7
        max_ciclope_total = 4
        max_rosas_total = 3


        # Prioridad y distribución espacial
        if self.ciclope_spawned < max_ciclope_total:
            enemy = Ciclope(sprite_manager=sprite_manager)
            enemy.pattern = "horizontal"
            enemy.fire_rate = 3000 
            enemy.speed = 1.5
            enemy.rect.centerx = 100 + (self.ciclope_spawned * 250)  # Mejor distribución horizontal
            enemy.rect.y = 50
            enemy.start_x = enemy.rect.centerx
            enemies_group.add(enemy)
            self.ciclope_spawned += 1

        elif self.rosas_spawned < max_rosas_total:
            enemy = Enemy(pattern="sine", sprite_manager=sprite_manager, enemy_type="rosa_abajo")
            enemy.rect.centerx = 150 + (self.rosas_spawned * 350)  # Mejor distribución horizontal
            enemy.rect.y = -20
            enemy.start_x = enemy.rect.centerx
            enemies_group.add(enemy)
            self.rosas_spawned += 1

    def _check_objectives(self, asteroids_group, enemies_group):

        """Verificar si se completaron los objetivos del nivel"""
        objectives = self.get_objectives()

        if self.current_level == 1:
            if self.asteroids_destroyed >= objectives["asteroids"]:
                self._start_transition(2)
                return "level_complete"

        elif self.current_level == 2:
            if self.enemies_destroyed >= objectives["enemies"]:
                self._start_transition(3)
                return "level_complete"

        elif self.current_level == 3:
            # Verificar si apareció el jefe
            if not self.boss_spawned and self.boss is None and self.enemies_destroyed >= LEVEL3_WAVE_ENEMIES:
                self.boss = Boss(
                    sprite_manager=self._sprite_manager_ref 
                    if hasattr(
                    self, '_sprite_manager_ref') 
                    else None
                    )
                self.boss_spawned = True
                return "boss_spawn"

            # Verificar victoria 
            if self.boss_defeated:
                self.level_state = "victory"
                return "victory"

        return None

    def _start_transition(self, next_level):
        """Iniciar transición de nivel """
        self.level_state = "transition"
        self.transition_timer = 0
        self.transition_target = 255
        self._pending_level = next_level

    def _update_transition(self, dt):
        """Actualizar transición visual fluida"""
        self.transition_timer += dt
        progress = min(1.0, self.transition_timer / self.transition_duration)

        # Fade out -> cambio de nivel -> fade in
        if progress < 0.5:
            self.transition_alpha = int(255 * (progress * 2))
        elif progress < 0.6:
            # Cambio de nivel en el punto más oscuro
            if self.level_state == "transition":
                self.current_level = self._pending_level
                self.asteroids_destroyed = 0
                self.enemies_destroyed = 0
                self.asteroids_spawned = 0
                self.enemies_spawned = 0

                # Reinicio acumulaciones
                self.rosas_spawned = 0
                self.rojos_spawned = 0
                self.verdes_spawned = 0
                self.ciclope_spawned = 0

                self.boss = None
                self.boss_defeated = False

                # Cambiar fondo 
                if self.current_level == 2:
                    self.bg_color = COLOR_BG_LEVEL2
                elif self.current_level == 3:
                    self.bg_color = COLOR_BG_LEVEL3
        else:
            self.transition_alpha = int(255 * (1 - (progress - 0.5) * 2))

        if progress >= 1.0:
            self.level_state = "playing"
            self.transition_alpha = 0

    def on_asteroid_destroyed(self):
        """Registrar asteroide destruido"""
        self.asteroids_destroyed += 1

    def on_enemy_destroyed(self):
        """Registrar enemigo destruido"""
        self.enemies_destroyed += 1

    def on_boss_defeated(self):
        """Registrar jefe derrotado (RF-14)"""
        self.boss_defeated = True
        self.boss = None
