"""
Punto de entrada del juego Space Shooter (No le veo necesidad de que toquen esto)

"""

import pygame
import sys # Gestiona posibles errores
from config import * # Valores inalterables del juego base 
from game_state import GameState
from renderer import Renderer


class Game:
    """Clase principal del juego"""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)  # audio estéreo, poca latencia
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_started = False

        # Estado y renderizador
        self.game_state = GameState()
        self.renderer = Renderer(self.screen)

    def run(self):
        """Bucle principal del juego"""
        while self.running:
            dt = self.clock.tick(FPS)  # 60 FPS

            self._handle_events()

            if self.game_started:
                keys = pygame.key.get_pressed() # Teclas
                self.game_state.update(dt, keys, self.renderer)
                self.game_state._apply_powerups()
                self.renderer.update_explosions(dt)
                self.renderer.draw(self.game_state)
            else:
                self.renderer.draw_start_screen()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Manejar eventos de entrada"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_RETURN and not self.game_started:
                    self.game_started = True
                if event.key == pygame.K_r and self.game_state.level_manager.level_state in ("victory", "game_over"):
                    self.game_state.reset()


if __name__ == "__main__":
    game = Game()
    game.run()