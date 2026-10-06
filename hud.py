"""

        Interfaz de usuario y acceso para cambiar el color
         del texto

"""

import pygame
from config import *


class HUD:
    """Gestiona la interfaz visual en pantalla"""

    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def draw(self, surface, player, level_manager, score):
        """Dibujar todos los elementos del HUD"""
        # Barra de vida del jugador
        self._draw_player_health(surface, player)

        # Indicador de MODO DIOS
        if getattr(player, "god_mode", False):
            self._draw_god_mode(surface, player)

        # Información de nivel y objetivos
        self._draw_level_info(surface, level_manager)

        # Puntuación
        self._draw_score(surface, score)

        # Barra de vida del jefe (RF-13)
        if level_manager.boss:
            self._draw_boss_health(surface, level_manager.boss)

    def _draw_god_mode(self, surface, player):
        """Aviso 'MODO DIOS' junto a la barra de vida y un aro dorado alrededor de la nave"""
        gold = (255, 215, 0)
        text = self.font_small.render("MODO DIOS", True, gold)
        surface.blit(text, (330, 12))  # a la derecha de "HP: 100/100"
        radius = max(player.rect.width, player.rect.height) // 2 + 6
        pygame.draw.circle(surface, gold, player.rect.center, radius, 2)

    def _draw_player_health(self, surface, player):
        """Barra de vida del jugador"""
        bar_width = 200
        bar_height = 20
        x = 10
        y = 10

        # Fondo
        pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (x, y, bar_width, bar_height))
        # Vida actual
        health_width = int(bar_width * (player.health / player.max_health))
        color = COLOR_HEALTH_BAR if player.health > 30 else (255, 0, 0)
        pygame.draw.rect(surface, color, (x, y, health_width, bar_height)) # El draw en el codigo sirve para mostrar en pantalla, sin 
                                                                            # el solo es codigo
        # Borde
        pygame.draw.rect(surface, COLOR_HUD, (x, y, bar_width, bar_height), 2)
        # Texto
        text = self.font_small.render(f"HP: {player.health}/{player.max_health}", True, COLOR_HUD)
        surface.blit(text, (x + bar_width + 10, y))

    def _draw_level_info(self, surface, level_manager):
        """Información del nivel y objetivos"""
        objectives = level_manager.get_objectives()
        y = 40

        level_text = self.font_medium.render(f"NIVEL {level_manager.current_level}", True, COLOR_HUD)
        surface.blit(level_text, (10, y))
        y += 35

        if objectives["asteroids"] > 0:
            text = self.font_small.render(
                f"Asteroides: {level_manager.asteroids_destroyed}/{objectives['asteroids']}",
                True, COLOR_HUD
            )
            surface.blit(text, (10, y))
            y += 25

        if objectives["enemies"] > 0:
            text = self.font_small.render(
                f"Enemigos: {level_manager.enemies_destroyed}/{objectives['enemies']}",
                True, COLOR_HUD
            )
            surface.blit(text, (10, y))

    def _draw_score(self, surface, score):
        """Puntuación"""
        text = self.font_medium.render(f"Puntos: {score}", True, COLOR_HUD)
        surface.blit(text, (SCREEN_WIDTH - 200, 10))

    def _draw_boss_health(self, surface, boss):
        """Barra de vida del Cthulhu"""
        bar_width = 400
        bar_height = 25
        x = (SCREEN_WIDTH - bar_width) // 2
        y = SCREEN_HEIGHT - 40

        # Fondo oscuro para legibilidad
        pygame.draw.rect(surface, (0, 0, 0), (x - 5, y - 5, bar_width + 10, bar_height + 10))
        pygame.draw.rect(surface, COLOR_HEALTH_BAR_BG, (x, y, bar_width, bar_height))

        # Vida actual con gradiente de color
        health_width = int(bar_width * (boss.health / boss.max_health))
        if boss.health > boss.max_health * 0.5:
            color = (255, 50, 50)
        elif boss.health > boss.max_health * 0.25:
            color = (255, 150, 0)
        else:
            color = (255, 255, 0)
        pygame.draw.rect(surface, color, (x, y, health_width, bar_height))

        # Borde brillante
        pygame.draw.rect(surface, COLOR_BOSS, (x, y, bar_width, bar_height), 3)

        # Texto
        text = self.font_small.render(
            f"Cthulhu: {boss.health}/{boss.max_health}", True, COLOR_HUD
        )
        surface.blit(text, (x + bar_width // 2 - 50, y - 25))

    def draw_transition(self, surface, alpha, level):
        """Mensaje de transición de nivel"""
        if alpha <= 0:
            return

        # Overlay oscuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_TRANSITION)
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))

        # Mensaje
        if alpha > 200:
            if level == 2:
                text = self.font_large.render("FELICIDADES, AVANZANDO AL NIVEL 2", True, (0, 255, 0))
            elif level == 3:
                text = self.font_large.render("FELICIDADES, AVANZANDO AL NIVEL 3", True, (0, 255, 0))
            else:
                text = self.font_large.render("NIVEL COMPLETADO", True, (0, 255, 0))

            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(text, rect)

    def draw_victory(self, surface):
        """Pantalla de victoria"""
        surface.fill((0, 0, 50))
        text = self.font_large.render("¡VICTORIA!", True, (0, 255, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(text, rect)

        text2 = self.font_medium.render("Has derrotado al Jefe Final", True, COLOR_HUD)
        rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(text2, rect2)

        text3 = self.font_small.render("Presiona R para reiniciar", True, COLOR_HUD)
        rect3 = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        surface.blit(text3, rect3)

    def draw_game_over(self, surface):
        """Pantalla de game over"""
        surface.fill((50, 0, 0))
        text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(text, rect)

        text3 = self.font_small.render("Presiona R para reiniciar", True, COLOR_HUD)
        rect3 = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        surface.blit(text3, rect3)

    def draw_start_screen(self, surface):
        """Pantalla de inicio"""
        surface.fill((0, 0, 20))
        text = self.font_large.render("Las flipantes aventuras de juan", True, COLOR_PLAYER)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(text, rect)

        instructions = [
            "Controles:",
            "Flechas / WASD - Mover",
            "ESPACIO - Disparar",
            "",
            "Presiona ENTER para comenzar"
        ]

        y = SCREEN_HEIGHT // 2
        for line in instructions:
            text = self.font_small.render(line, True, COLOR_HUD)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            surface.blit(text, rect)
            y += 30
 