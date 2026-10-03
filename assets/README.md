# Assets del Space Shooter

## Estructura de carpetas

```
assets/
├── images/          # Imágenes y animaciones
│   ├── player/      # Nave del jugador
│   ├── enemies/     # Naves enemigas
│   ├── boss/        # Jefe final
│   ├── asteroids/   # Meteoritos
│   ├── powerups/    # Power-ups
│   └── backgrounds/ # Fondos de cada nivel
└── sounds/          # Efectos de sonido
    ├── shoot.wav           # Disparo del jugador
    ├── enemy_shoot.wav     # Disparo enemigo
    ├── explosion_asteroid.wav  # Explosión de meteorito
    ├── explosion_enemy.wav     # Explosión de nave enemiga
    ├── explosion_boss.wav      # Explosión del jefe
    ├── powerup_collect.wav     # Recoger power-up
    ├── player_hit.wav          # Jugador recibe daño
    └── level_transition.wav    # Transición de nivel
```

## Formatos recomendados

- **Imágenes**: PNG con transparencia (32x32, 64x64, 128x128 según el sprite)
- **Sonidos**: WAV o OGG (44100 Hz, 16-bit, mono para efectos)

## Para agregar tus propios assets

1. Coloca las imágenes en la subcarpeta correspondiente
2. Coloca los sonidos en la carpeta `sounds/`
3. Actualiza las rutas en `config.py` si es necesario
