"""
Gestión del estado del juego ( Interacciones, pantallas de carga, algunas actualizaciones de sprints)

"""

import pygame
from config import *
from entities import *
from levels import LevelManager
from collisions import CollisionManager
from sprite_manager import SpriteManager
from sound_manager import SoundManager


class GameState:
    """Gestiona el estado completo del juego"""

    def __init__(self):
        # Cargar sprites
        self.sprite_manager = SpriteManager()
        self.sound_manager = SoundManager()

        # Grupos de sprites
        self.player = Player(self.sprite_manager)
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.boss_sprite = None
        self.boss_group = pygame.sprite.Group()  # grupo propio del jefe (no es un enemigo normal)

        # Estado de pausa y record 
        self.paused = False
        self.high_score = self._load_high_score()

        # Gestores
        self.level_manager = LevelManager()
        self.collision_manager = CollisionManager(self.sprite_manager)

        # Boosts del jugador
        self.fire_rate_boost = 0
        self.speed_boost = 0

    def reset(self):
        """Reiniciar estado para nueva partida"""
        self.player = Player(self.sprite_manager)
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.asteroids.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.boss_sprite = None
        self.boss_group.empty()
        self.fire_rate_boost = 0
        self.speed_boost = 0
        self.level_manager.reset()
        self.collision_manager.score = 0

    def update(self, dt, keys, renderer=None):
        """Actualizar estado del juego"""

        if self.paused:
            return

        now = pygame.time.get_ticks()

        # Actualizar jugador con boosts
        self._update_player_boosts(now)
        should_shoot = self.player.update(keys, dt)
        if should_shoot:
            bullet = Bullet(self.player.rect.centerx, self.player.rect.top,
                          PLAYER_BULLET_SPEED, COLOR_PLAYER_BULLET,
                          sprite_manager=self.sprite_manager, bullet_type=self.player.bullet_type)
            self.player_bullets.add(bullet)
            self.sound_manager.play("shoot_purple" if self.player.bullet_type == "morada" else "shoot")

        # Actualizar nivel
        result = self.level_manager.update(dt, self.asteroids, self.enemies,
                                          self.player.rect.center, self.sprite_manager)

        # Música: sigue al nivel actual (cambia sola en el punto oscuro de la transición)
        if self.level_manager.level_state in ("game_over", "victory"):
            self._save_high_score()  # Puntaje guardado
            self.sound_manager.stop_music()
        else:
            self.sound_manager.play_music(self.level_manager.current_level)

        # Manejar resultados del nivel
        if result == "level_complete":
            self.sound_manager.play("level_transition")
            
        if result in ("level_complete", "boss_spawn", "victory", "game_over"):
            # Limpiar todas las entidades en pantalla antes de la transición
            self.player_bullets.empty()
            self.enemy_bullets.empty()
            self.asteroids.empty()
            self.enemies.empty()
            self.powerups.empty()

        if result == "boss_spawn" and self.level_manager.boss:
            self.boss_sprite = self.level_manager.boss
            self.boss_group.add(self.boss_sprite)  # necesario para que boss.alive() sea True
            self.sound_manager.play("boss_spawn")

        # Actualizar entidades
        self._update_entities(dt)

        # Colisiones
        events = self.collision_manager.check_all(
            self.player, self.player_bullets, self.enemy_bullets,
            self.asteroids, self.enemies, self.boss_sprite,
            self.level_manager, self.powerups
        )

        # Sonidos según los eventos de colisión
        if events["player_hit"]:
            self.sound_manager.play("player_hit")
        if events["asteroid_destroyed"]:
            self.sound_manager.play("explosion_asteroid")
        if events["enemy_destroyed"]:
            self.sound_manager.play("enemy_death")
        elif events["enemy_hit"]:
            self.sound_manager.play("enemy_hit")
        if events["boss_destroyed"]:
            self.sound_manager.play("boss_death")
        elif events["boss_hit"]:
            self.sound_manager.play("boss_hit")

        # Agregar explosiones cuando se destruyen entidades
        if renderer and events["explosions"]:
            for pos_x, pos_y in events["explosions"]:
                renderer.add_explosion(pos_x, pos_y, self.sprite_manager)
        

        # Aplicar power-ups
        if events["powerup_collected"]:
            self.sound_manager.play("powerup_collect")
            self._collect_powerup(events["powerup_collected"])
            if renderer and events["powerup_pos"]:
                px, py = events["powerup_pos"]
                renderer.add_powerup_pickup(px, py, events["powerup_collected"], self.sprite_manager)

        # Actualizar power-ups
        self.powerups.update(dt)

        # Game over
        if not self.player.alive:
            # Solo reproducirlo si aún no estábamos en estado de game_over
            if self.level_manager.level_state != "game_over":
                self.sound_manager.play("game_over") # <--- AÑADIR AQUÍ
                
            self.level_manager.level_state = "game_over"

    def _update_player_boosts(self, now):
        """Actualizar boosts del jugador"""
        if self.fire_rate_boost > 0:
            if self.player.bullet_type == "morada":
                self.player.fire_rate_multiplier = POWERUP_ORANGE_FIRE_RATE_MULTIPLIER
            elif self.player.bullet_type == "verde":
                self.player.fire_rate_multiplier = POWERUP_BLUE_FIRE_RATE_MULTIPLIER
        else:
            self.player.fire_rate_multiplier = 1.0

        if self.speed_boost > 0:
            self.player.speed = PLAYER_SPEED + POWERUP_SPEED_BOOST
        else:
            self.player.speed = PLAYER_SPEED

    def _update_entities(self, dt):
        """Actualizar todas las entidades"""
        self.player_bullets.update(dt)


        #Actualizar projectiles del boss guiandose en la posicion
        for bullet in self.enemy_bullets:
            if hasattr(bullet, 'update') and 'player_pos' in bullet.update.__code__.co_varnames:
                bullet.update(dt, self.player.rect.center)  # Eso de arriba permite al metodo
                                                            # update recibir la posicion sin saltar error
            else:
                bullet.update(dt) # En caso de que no sea los ojos, manda sin posicion


        self.asteroids.update(dt)

        # Actualizar enemigos
        for enemy in self.enemies:
            should_fire = enemy.update(dt, self.player.rect.center)
            if should_fire:
                #Comprueba si el enemigo dispara multiples proyectiles
                if hasattr(enemy, 'get_bullets'):
                    bullets = enemy.get_bullets(self.player.rect.center)
                    if bullets:
                        self.enemy_bullets.add(*bullets)
                        self.sound_manager.play("enemy_shoot")
                #O si un enemigo normal dispara de uno en uno
                elif hasattr(enemy, 'get_bullet'):
                    bullet = enemy.get_bullet(self.player.rect.center)
                    if bullet:
                        self.enemy_bullets.add(bullet)
                        self.sound_manager.play("enemy_shoot")

        # Actualizar jefe
        if self.boss_sprite and self.boss_sprite.alive():
            should_fire = self.boss_sprite.update(dt, self.player.rect.center)
            if should_fire and self.boss_sprite.phase == "attack":
                cuenta = getattr(self.boss_sprite, 'almace_cuenta', 1)
                for _ in range(cuenta):
                    new_proj = self.boss_sprite.spawn_projectile()
                    self.enemy_bullets.add(new_proj)
                self.sound_manager.play("eye_spwan")

            #Verifica si se destruyeron todos los proyectiles
            active_boss_projectiles = sum(1 for b in self.enemy_bullets
                                          if isinstance(b, BossProjectile))   
            if self.boss_sprite.phase == "attack" and self.boss_sprite.projectiles_spawned >= BOSS_MAX_PROJECTILES and active_boss_projectiles == 0:
                #Cambia a Fase vulnerable
                self.boss_sprite.phase = "vulnerable"
                self.boss_sprite.vulnerable_timer = 0

    def _collect_powerup(self, power_type):
        """Recoger power-up y aplicar efecto"""
        now = pygame.time.get_ticks()
        if power_type == "health":
            self.player.health = min(self.player.max_health,
                                    self.player.health + POWERUP_HEALTH_AMOUNT)
        elif power_type == "orange":
            # Power-up naranja: cambia a bala morada con +0.25% daño
            self.player.bullet_type = "morada"
            self.player.damage_multiplier = POWERUP_ORANGE_DAMAGE_MULTIPLIER
            self.player.fire_rate_multiplier = POWERUP_ORANGE_FIRE_RATE_MULTIPLIER #Aplica el efecto
            self.fire_rate_boost = now + POWERUP_DURATION
        
        elif power_type == "blue":
            # Power-up azul: cambia a bala verde con -1.25% daño pero más velocidad de disparo
            self.player.bullet_type = "verde"
            self.player.damage_multiplier = POWERUP_BLUE_DAMAGE_MULTIPLIER
            self.fire_rate_boost = now + POWERUP_DURATION

    def _apply_powerups(self):
        """Aplicar efectos de power-ups activos"""
        now = pygame.time.get_ticks()

        #Logica de duracion power ups
        if self.fire_rate_boost > 0 and now > self.fire_rate_boost:
            self.fire_rate_boost = 0
            self.player.damage_multiplier = 1.0
            self.player.fire_rate_multiplier = 1.0
            self.player.bullet_type = "dorada"  # Volver a bala original
        if self.speed_boost > 0 and now > self.speed_boost:
            self.speed_boost = 0

    def _load_high_score(self):
        """Carga el récord desde un archivo de texto"""
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_high_score(self):
        """Guarda el récord en el archivo si el puntaje actual es mayor"""
        if self.collision_manager.score > self.high_score:
            self.high_score = self.collision_manager.score
            try:
                with open(HIGH_SCORE_FILE, "w") as f:
                    f.write(str(self.high_score))
            except Exception as e:
                print(f"Error guardando high score: {e}")
