"""
Sistema de colisiones centralizado  ( mas que todo son hitbox y el como paso de ser un cuadrado a un circulo [ lo mas acercado ])

"""

import pygame
import random
from config import *
from entities import PowerUp, BossProjectile


def asteroid_hitbox(asteroid):
    """Obtener rectángulo de colisión del asteroide (círculo aproximado)"""
    r = asteroid.radius * 0.8
    return pygame.Rect(
        asteroid.rect.centerx - r,
        asteroid.rect.centery - r,
        r * 2,
        r * 2
    )

def player_hitbox(player):
    """Retorna el area o hitbox del jugador si este se encuentra en el modo DIOS"""

    if getattr(player, "god_mode", False):
        #El  radio debe coincidir con el del HUD dibujado
        radius = max(player.rect.width, player.rect.height) // 2 + 6
        return pygame.Rect(
            player.rect.centerx - radius,
            player.rect.centery - radius,
            radius * 2,
            radius * 2 
        )
    return player.rect


class CollisionManager:
    """Gestiona todas las colisiones del juego"""

    def __init__(self, sprite_manager=None):
        self.score = 0
        self.sprite_manager = sprite_manager  # para que los power-ups usen sus sprites

    def check_all(self, player, player_bullets, enemy_bullets, asteroids, enemies, boss,
                  level_manager, powerups=None):
        
        """Verificar todas las colisiones y devolver eventos"""
        events = {
            "player_hit": False,
            "asteroid_destroyed": False,
            "enemy_destroyed": False,
            "enemy_hit": False,
            "boss_hit": False,
            "boss_destroyed": False,
            "powerup_collected": None,
            "powerup_pos": None,  # donde se recogio (para la animacion)
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
                            powerups.add(PowerUp(asteroid.rect.centerx, asteroid.rect.centery, power_type, self.sprite_manager))
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
                            powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type, self.sprite_manager))
                    else:
                        events["enemy_hit"] = True  # recibió daño pero sigue vivo
                    break

        # Balas del jugador vs OJOS SALTONES (RAGEBAIT DE ODIO SI NO ENCONTRAS ESTA LINEA) <--------
            for bullet in player_bullets:
                for enemy_bullet in list(enemy_bullets):
                    if isinstance(enemy_bullet, BossProjectile) and bullet.rect.colliderect(enemy_bullet.rect):  
                       
                        bullet.kill()                                               # El isinstance vericifa si el objeto pertenece a la clase 
                                                                                    # especificada ( True ) en caso de que no False
                        damage = int(bullet.damage * player.damage_multiplier)       # tambien comprueba si la bala no es la misma que la de 
                                                                                    # las naves o ciclopes

                        if enemy_bullet.take_damage(damage):
                            self.score += SCORE_ENEMY
                            events["enemy_destroyed"] = True
                            events["explosions"].append((enemy_bullet.rect.centerx, enemy_bullet.rect.centery))

                            #Drop de power ups ( mayoritariamente vida [se rigue por porcentaje: 60% vida, 20% Naranja, 20% Azul])
                            if powerups is not None and random.random() < 0.40:
                               power_type = random.choices(["health", "orange", "blue"], weights=[0.60, 0.20, 0.20])[0]
                               powerups.add(PowerUp(enemy_bullet.rect.centerx, enemy_bullet.rect.centery, power_type, self.sprite_manager))
                        break 

        
        #Balas del jugador vs Boss (solo si esta en fase vulnerable)
        if boss_alive:
            for bullet in player_bullets:
                if bullet.rect.colliderect(boss.rect):
                    bullet.kill()
                    damage = int(bullet.damage * player.damage_multiplier)
                    if boss.phase == "vulnerable":
                        if boss.take_damage(damage):
                            self.score += SCORE_BOSS
                            level_manager.on_boss_defeated()
                            events["boss_destroyed"] = True

                            #Guarda la posicion antes de eliminarlo
                            events["explosions"].append((boss.rect.centerx, boss.rect.centery))
                        else: 
                            events["boss_hit"] = True
                    break

        # Balas enemigas / projectiles del jefe vs jugador
        p_box = player_hitbox(player)
        for bullet in enemy_bullets:
            if p_box.colliderect(bullet.rect):
                bullet.kill()
                if player.take_damage(bullet.damage):
                    events["player_hit"] = True

                # Si es un projectile del boss explota al chocar y puede soltar power ups
                if isinstance(bullet, BossProjectile):
                    events["explosions"].append((bullet.rect.centerx, bullet.rect.centery))
                    if powerups is not None and random.random() < 0.40:
                        power_type = random.choices(["health", "orange", "blue"], weights=[0.60, 0.20, 0.20])[0]
                        powerups.add(PowerUp(bullet.rect.centerx, bullet.rect.centery, power_type, self.sprite_manager))


        # Asteroides vs jugador
        p_box = player_hitbox(player) # Para el modo dios
        for asteroid in asteroids:
            if p_box.colliderect(asteroid_hitbox(asteroid)):
                if player.take_damage(20):
                    events["player_hit"] = True

                #Si se encuentra en el dichoso modo dios suma el puntaje    
                if getattr(player, "god_mode", False):
                    self.score += SCORE_ASTEROID
                    level_manager.on_asteroid_destroyed()
                    events["asteroid_destroyed"] = True
                    events["explosions"].append((asteroid.rect.centerx, asteroid.rect.centery))
                    asteroid.kill()
                elif not player.god_mode:
                    asteroid.kill()

        # Enemigos vs jugador (colisión directa)
        for enemy in enemies:
            if p_box.colliderect(enemy.rect):
                if player.take_damage(30):
                    events["player_hit"] = True


                #Registra destruccion si choca en el modo DIOS
                if getattr(player, "god_mode", False):
                    self.score += SCORE_ENEMY
                    level_manager.on_enemy_destroyed()
                    events["enemy_destroyed"] = True
                    events["explosions"].append((enemy.rect.centerx, enemy.rect.centery))
                    enemy.kill()
                elif not player.god_mode:
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
                    events["powerup_pos"] = powerup.rect.center
                    powerup.kill()

        return events
