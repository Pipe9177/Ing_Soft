"""
Renderizado del juego ( Aqui esta el renderizado de las explosiones, uno que otro draw, el jefe esta aca [ Solo el draw ])

"""

import pygame
from config import *
from hud import HUD
from animations import ExplosionAnimation


class Renderer:
    """Gestiona todo el renderizado del juego"""

    def __init__(self, screen):
        self.screen = screen
        self.hud = HUD()
        self.explosions = []  # Lista de animaciones de explosión activas

    def add_explosion(self, x, y, sprite_manager=None):
        """Agregar una animación de explosión en la posición dada"""
        if sprite_manager:
            frames = sprite_manager.explosions
            # Escalar frames para que no sean demasiado grandes
            scaled_frames = []
            for frame in frames:
                scaled = pygame.transform.scale(frame, (120, 120))
                scaled_frames.append(scaled)
            explosion = ExplosionAnimation(x, y, scaled_frames, frame_duration=80)
            self.explosions.append(explosion)

    def add_powerup_pickup(self, x, y, power_type, sprite_manager):
        """Animacion al recoger un power-up (se reproduce una vez, igual que las explosiones)"""
        frames = sprite_manager.get_powerup_pickup_frames(power_type)
        self.explosions.append(ExplosionAnimation(x, y, frames, frame_duration=50))

    def update_explosions(self, dt):
        """Actualizar todas las animaciones de explosión"""
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if explosion.is_finished():
                self.explosions.remove(explosion)

    def draw_explosions(self):
        """Dibujar todas las animaciones de explosión"""
        for explosion in self.explosions:
            explosion.draw(self.screen)

    def draw(self, game_state):
        """Dibujar todo el juego"""
        # Fondo - usar imagen de fondo si está disponible o si hay animacion
        if game_state.sprite_manager:
            ticks = pygame.time.get_ticks()

            #Verifica si esta el jefe final
            is_boss_active = (
                game_state.boss_sprite is not None or
                game_state.level_manager.boss_defeated
            )
            bg = game_state.sprite_manager.get_background(game_state.level_manager.current_level, ticks, is_boss_active) #No toquen
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill(game_state.level_manager.bg_color)

        # Dibujar entidades
        game_state.asteroids.draw(self.screen)
        game_state.enemies.draw(self.screen)
        game_state.player_bullets.draw(self.screen)
        game_state.enemy_bullets.draw(self.screen)
        game_state.powerups.draw(self.screen)

        # Dibujar explosiones
        self.draw_explosions()

        # Jefe
        if game_state.boss_sprite and game_state.boss_sprite.alive(): #No tocar
            self.screen.blit(game_state.boss_sprite.image, game_state.boss_sprite.rect)

        # Jugador
        game_state.player.draw(self.screen)

        # HUD
        self.hud.draw(self.screen, game_state.player, game_state.level_manager,
                     game_state.collision_manager.score)

        # Transición
        if game_state.level_manager.level_state == "transition":
            self.hud.draw_transition(self.screen, game_state.level_manager.transition_alpha,
                                    game_state.level_manager.current_level)

        # Victoria
        if game_state.level_manager.level_state == "victory":
            self.hud.draw_victory(self.screen, game_state.collision_manager.score, game_state.high_score)

        # Game Over
        if game_state.level_manager.level_state == "game_over":
            self.hud.draw_game_over(self.screen, game_state.collision_manager.score, game_state.high_score)


        # Menu de pausa 
        if game_state.paused:
            self.hud.draw_pause(self.screen)

        pygame.display.flip()

    def draw_start_screen(self):
        """Pantalla de inicio"""
        self.hud.draw_start_screen(self.screen)
        pygame.display.flip()
