"""

Sistema de animaciones de sprites ( mas que todo controla cuanto tiempo aparece los sprints [Se usa mas que todo en las explosiones])

"""

import pygame


class Animation:
    """Gestiona la animación de un sprite"""

    def __init__(self, frames, frame_duration=100):
        """
        Inicializar animación

        Args:
            frames: Lista de superficies (frames de la animación)
            frame_duration: Duración de cada frame en milisegundos
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = 0
        self.finished = False

    def update(self, dt):
        """Actualizar animación"""
        self.last_update += dt
        if self.last_update >= self.frame_duration:
            self.last_update = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                self.finished = True

    def get_current_frame(self):
        """Obtener frame actual"""
        return self.frames[self.current_frame]

    def reset(self):
        """Reiniciar animación"""
        self.current_frame = 0
        self.last_update = 0
        self.finished = False


class ExplosionAnimation:
    """Animación de explosión que se reproduce una sola vez"""

    def __init__(self, x, y, frames, frame_duration=80):
        """
        Inicializar animación de explosión

        Args:
            x, y: Posición de la explosión
            frames: Lista de frames de la animación
            frame_duration: Duración de cada frame en ms

        """
        self.x = x
        self.y = y
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0

    def update(self, dt):
        """Actualizar animación de explosión"""
        self.timer += dt
        if self.timer > self.frame_duration:
            self.timer = 0
            self.current_frame += 1

    def is_finished(self):
        """Verificar si la animación terminó"""
        return self.current_frame >= len(self.frames)

    def draw(self, screen):
        """Dibujar animación de explosión"""
        if not self.is_finished():
            frame = self.frames[self.current_frame]
            rect = frame.get_rect(center=(self.x, self.y))
            screen.blit(frame, rect)    
