"""
Gestor de sonidos y música.

Para agregar un sonido: 1) pon el archivo en assets/sounds/
                        2) agrégalo a SOUND_FILES (o MUSIC_FILES si es música)
                        3) llama self.sound_manager.play("nombre") donde ocurra el evento
Para quitar un sonido:  borra su línea de la tabla.
"""

import os
import pygame

SOUNDS_PATH = os.path.join(os.path.dirname(__file__), "assets", "sounds")

# EFECTOS DE SONIDO
SOUND_FILES = {
    # --- jugador ---
    "shoot":              ("Shoot_all.wav",              0.35, 0),
    "shoot_purple":       ("Shoot_purple.wav",           0.40, 0),
    "player_hit":         ("player_hit.wav",             0.70, 0),
    # --- enemigos y asteroides ---
    "enemy_hit":          ("Damage_Take_enemige.wav",    0.50, 80),
    "enemy_death":        ("UFO_DEATH.wav",              0.60, 0),
    "explosion_asteroid": ("meteorite_explosion.wav",    0.60, 0),
    "eye_spawn":          ("spawn_eyes.wav",             0.60, 1500),
    # --- jefe ---
    "boss_spawn":         ("Cthulhu_spawn.wav",          0.90, 0),
    "boss_hit":           ("Damage_Taken_Cthulhu.wav",   0.50, 150),
    "boss_death":         ("Cthulhu_death.wav",          1.00, 0),
    #- Otros sonidos -
    "enemy_shoot":      ("enemy_shoot.wav",            0.30, 0),
    "powerup_collect":  ("powerup_collect.wav",        0.60, 0),
    "level_transition": ("level_transition.wav",       0.70, 0),
    "game_over":        ("game_over.wav",              0.80, 0),
}

# MÚSICA POR NIVEL
MUSIC_FILES = {
    1: ("lvl1.ogg", 0.40),
    2: ("lvl2.ogg", 0.40),
    3: ("lvl3.ogg", 0.40),
}
MUSIC_FADE_IN_MS = 1500


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.cooldowns = {}
        self.last_played = {}
        self.current_music = None
        self.enabled = True

        # Si no hay dispositivo de audio, el juego sigue funcionando sin sonido
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(32)  # más canales = más sonidos a la vez
        except pygame.error as e:
            print(f"Audio desactivado: {e}")
            self.enabled = False
            return

        for name, (filename, volume, cooldown) in SOUND_FILES.items():
            self._load(name, filename, volume, cooldown)

    def _load(self, name, filename, volume=1.0, cooldown=0):
        path = os.path.join(SOUNDS_PATH, filename)
        if not os.path.exists(path):
            print(f"Sonido no encontrado: {path}")
            return
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        self.sounds[name] = sound
        self.cooldowns[name] = cooldown

    def play(self, name):
        """Reproduce un efecto. Si el nombre no existe, no hace nada."""
        if not self.enabled or name not in self.sounds:
            return
        cooldown = self.cooldowns.get(name, 0)
        if cooldown:
            now = pygame.time.get_ticks()
            if now - self.last_played.get(name, -cooldown) < cooldown:
                return
            self.last_played[name] = now
        self.sounds[name].play()

    # ----------------------------- música -----------------------------
    def play_music(self, level):
        """Pone la música del nivel. Si ya está sonando esa, no hace nada."""
        if not self.enabled or level == self.current_music:
            return
        self.current_music = level  # se marca ya para no reintentar cada frame
        entry = MUSIC_FILES.get(level)
        if entry is None:
            pygame.mixer.music.stop()
            return
        filename, volume = entry
        path = os.path.join(SOUNDS_PATH, filename)
        if not os.path.exists(path):
            print(f"Música no encontrada: {path}")
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1, fade_ms=MUSIC_FADE_IN_MS)  # -1 = en bucle

    def stop_music(self):
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        self.current_music = None
