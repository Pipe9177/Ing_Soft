"""
Sistema de colisiones centralizado  ( mas que todo son hitbox y el como paso de ser un cuadrado a un circulo [ lo mas acercado ])

"""

import pygame
import random
from config import *
from entities import PowerUp


def asteroid_hitbox(asteroid):
    """Obtener rectángulo de colisión del asteroide (círculo aproximado)"""
    r = asteroid.radius * 0.8
    return pygame.Rect(
        asteroid.rect.centerx - r,
        asteroid.rect.centery - r,
        r * 2,
        r * 2
    )


class CollisionManager:
    """Gestiona todas las colisiones del juego"""

    def __init__(self):
        self.score = 0

    def check_all(self, player, player_bullets, enemy_bullets, asteroids, enemies, boss,
                  level_manager, powerups=None):
        """Verificar todas las colisiones y devolver eventos"""
        events = {
            "player_hit": False,
            "asteroid_destroyed": False,
            "enemy_destroyed": False,
            "boss_hit": False,
            "boss_destroyed": False,
            "powerup_collected": None,
            "explosions": [] #Guarda la ubicacion de la explosion para el sprint
        }

        if not player.alive:
            return events

        boss_alive = boss is not None and boss.alive()

        # Verificar si el jugador ya tiene un power-up activo para no darle otro 
        has_active_powerup = (
            player.damage_multiplier != 1.0 or
            player.fire_rate_multiplier != 1.0
        )

        # Balas del jugador vs asteroides
        for bullet in player_bullets:
            for asteroid in asteroids:
                if bullet.rect.colliderect(asteroid_hitbox(asteroid)):
                    bullet.kill()
                    # Aplicar multiplicador de daño del jugador
                    damage = int(bullet.damage * player.damage_multiplier)
                    if asteroid.take_damage(damage):
                        self.score += SCORE_ASTEROID
                        level_manager.on_asteroid_destroyed()
                        events["asteroid_destroyed"] = True

                        #Guarda la posicion antes de eliminarlo
                        events["explosions"].append((asteroid.rect.centerx, asteroid.rect.centery)) #No toquen esto, ayuda a los sprints
                                                                                                    # de las explosiones

                        # Power-up drop - solo si no hay power-up activo
                        if powerups is not None and not has_active_powerup and random.random() < POWERUP_DROP_CHANCE:
                            power_type = random.choice(["health", "orange", "blue"])
                            powerups.add(PowerUp(asteroid.rect.centerx, asteroid.rect.centery, power_type))
                    break

        # Balas del jugador vs enemigos
        for bullet in player_bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    # Aplicar multiplicador de daño del jugador
                    damage = int(bullet.damage * player.damage_multiplier)
                    if enemy.take_damage(damage):
                        self.score += SCORE_ENEMY
                        level_manager.on_enemy_destroyed()
                        events["enemy_destroyed"] = True

                        #Guarda la posicion antes de eliminarlo
                        events["explosions"].append((enemy.rect.centerx, enemy.rect.centery)) # Igual que el anterior no tocar

                        # Power-up drop - solo si no hay power-up activo
                        if powerups is not None and not has_active_powerup and random.random() < POWERUP_DROP_CHANCE:
                            power_type = random.choice(["health", "orange", "blue"])
                            powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type))
                    break

        # Balas del jugador vs jefe
        if boss_alive:
            for bullet in player_bullets:
                if bullet.rect.colliderect(boss.rect):
                    bullet.kill()
                    events["boss_hit"] = True
                    damage = int(bullet.damage * player.damage_multiplier)
                    if boss.take_damage(damage):
                        self.score += SCORE_BOSS
                        level_manager.on_boss_defeated()
                        events["boss_destroyed"] = True

                        #Guarda la posicion antes de eliminarlo
                        events["explosions"].append((boss.rect.centerx, boss.rect.centery))
                    break

        # Balas enemigas vs jugador
        for bullet in enemy_bullets:
            if bullet.rect.colliderect(player.rect):
                bullet.kill()
                if player.take_damage(bullet.damage):
                    events["player_hit"] = True

        # Asteroides vs jugador
        for asteroid in asteroids:
            if player.rect.colliderect(asteroid_hitbox(asteroid)):
                if player.take_damage(20):
                    events["player_hit"] = True
                asteroid.kill()

        # Enemigos vs jugador (colisión directa)
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                if player.take_damage(30):
                    events["player_hit"] = True
                enemy.kill()

        # Jefe vs jugador
        if boss_alive:
            if player.rect.colliderect(boss.rect):
                if player.take_damage(50):
                    events["player_hit"] = True

        # Power-ups vs jugador
        if powerups:
            for powerup in powerups:
                if player.rect.colliderect(powerup.rect):
                    events["powerup_collected"] = powerup.power_type
                    powerup.kill()

        return events
