"""

Carga y gestiona todos los sprites del juego (Ok miren, aca deben tener demasiado cuidado, aca son todos las animaciones
                                             las listas sirven para guardar y extraer la informacion de las carpetas
                                             que les anexare, los diccionarios son para ubicarlos en un solo lado
                                             , si cambias el tamaño de la pantalla en config.py aca lo tenes que modificar en
                                             resize_background)

"""

import pygame
import os
from config import POWERUP_SCALE

# Ruta base de las imágenes
IMAGES_PATH = os.path.join(os.path.dirname(__file__), "assets", "images")


class SpriteManager:
    """Carga y gestiona todos los sprites del juego"""

    def __init__(self):
        # Diccionarios para almacenar los sprites cargados - todo lo que veas dentro de {} son el nombre que les das aqui en el codigo, no el
        # de la carpeta

        self.asteroids = []
        self.asteroid_hit = []
        self.bullets = {
            "dorada": [],
            "blanca": [],
            "morada": [],
            "verde": []
        }
        self.ciclope = []
        self.ciclope_hit = []
        self.explosions = []
        self.enemies = {
            "rojo_abajo": [],
            "rosa_abajo": [],
            "verde_abajo": [],
   
        }
        self.enemy_hit = {
            "rojo_abajo": [],
            "rosa_abajo": [],
            "verde_abajo": [],
  
        }
        self.player = {
            "centro": [],
            "izq": [],
            "der": []
        }
        self.player_hit = []
        self.backgrounds = {}
        self.bg_level1_frames = []  # Fondo animado nivel 1: Atardecer
        self.bg_level2_frames = []  # Fondo animado nivel 2: Espacio
        self.bg_levels3_frames = [] # Sprints nvl 3
        self.bg_boss_frames = [] # Sprints boss
        self.powerups = {}

        # Cargar todos los sprites
        self._load_all_sprites()

    def _load_image(self, path): # Estos path lo que hacen es, buscar en la ubicacion que le mencionas la carpeta señalada. OJO tiene
                                # que ser el mismo nombre ( Ej: Tenes carpeta OsU ----> OsU_path)
        """Cargar una imagen y escalarla si es necesario"""
        try:
            image = pygame.image.load(path).convert_alpha()
            return image
        except pygame.error as e:
            print(f"Error cargando imagen {path}: {e}")
            # Crear una superficie de fallback
            surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0), (20, 20), 15)
            return surface

    def _load_asteroids(self):
        """Cargar sprites de asteroides"""
        asteroide_path = os.path.join(IMAGES_PATH, "asteroide")
        for i in range(1, 9):
            img = self._load_image(os.path.join(asteroide_path, f"asteroide_{i}.png")) #os.path.join es complementario para path
                                                                                        # aca lo tengo _{i} debido a que en la carpeta aparece
                                                                                        # asteroide_1.png ( vaya es una lista )
            self.asteroids.append(img)
        # Sprite de golpe
        self.asteroid_hit.append(self._load_image(os.path.join(asteroide_path, "asteroide_golpe.png")))

    def _load_bullets(self):
        """Cargar sprites de balas"""
        balas_path = os.path.join(IMAGES_PATH, "balas") # <---- En caso de que este en una subcarpeta se llama asi, mismo nombre OJO 
        bullet_types = {
            "dorada": "bala1_dorada",
            "blanca": "bala2_blanca",
            "morada": "bala3_morada",
            "verde": "bala4_verde"
        }
        for bullet_type, folder in bullet_types.items():
            type_path = os.path.join(balas_path, folder)
            for i in range(1, 5):
                img = self._load_image(os.path.join(type_path, f"{folder}_{i}.png")) # No toquen, animacion del boss muchas balas
                self.bullets[bullet_type].append(img)

    def _load_ciclope(self):
        """Cargar sprites del ciclope"""
        ciclope_path = os.path.join(IMAGES_PATH, "ciclope")
        for i in range(1, 5):
            img = self._load_image(os.path.join(ciclope_path, f"ciclope_{i}.png"))
            self.ciclope.append(img)
        self.ciclope_hit.append(self._load_image(os.path.join(ciclope_path, "ciclope_golpe.png")))

    def _load_explosions(self):
        """Cargar sprites de explosión"""
        self.explosions = []
        explosion_path = os.path.join(IMAGES_PATH, "explosion")
        #Mostrara los sprints de explosion
        for i in range(1, 8):
            img = self._load_image(os.path.join(explosion_path, f"explosion_{i}.png"))
            self.explosions.append(img)

    def _load_enemies(self):
        """Cargar sprites de naves enemigas"""
        naves_path = os.path.join(IMAGES_PATH, "naves")
        enemy_types = [
            "rojo_abajo",
            "rosa_abajo",
            "verde_abajo"
        ]
        for enemy_type in enemy_types:
            type_path = os.path.join(naves_path, f"enemigo_{enemy_type}")
            for i in range(1, 4):
                img = self._load_image(os.path.join(type_path, f"enemigo_{enemy_type}_{i}.png"))
                self.enemies[enemy_type].append(img)
            # Sprite de golpe
            hit_img = self._load_image(os.path.join(type_path, f"enemigo_{enemy_type}_golpe.png"))
            self.enemy_hit[enemy_type].append(hit_img)

    def _load_player(self):
        """Cargar sprites de la nave del jugador"""
        naves_path = os.path.join(IMAGES_PATH, "naves", "prota_morado")
        # Centro
        for i in range(1, 4):
            img = self._load_image(os.path.join(naves_path, f"prota_morado_centro_{i}.png"))
            self.player["centro"].append(img)
        # Izquierda
        for i in range(1, 4):
            img = self._load_image(os.path.join(naves_path, f"prota_morado_izq_{i}.png"))
            self.player["izq"].append(img)
        # Derecha
        for i in range(1, 4):
            img = self._load_image(os.path.join(naves_path, f"prota_morado_der_{i}.png"))
            self.player["der"].append(img)
        # Golpe
        self.player_hit.append(self._load_image(os.path.join(naves_path, "prota_morado_golpe.png")))

    def _load_backgrounds(self):
        """Cargar fondos de pantalla"""
        fondo_path = os.path.join(IMAGES_PATH, "Fondo")
        # Fondos animados fotograma a fotograma para niveles 1 y 2.
        # Se ordenan por nombre para conservar la secuencia de los frames.

        #Fondo1
        atardecer_path = os.path.join(fondo_path, "Atardecer")
        if os.path.isdir(atardecer_path):
            for file in sorted(os.listdir(atardecer_path)):
                if file.lower().endswith(".png"):
                    img = self._load_image(os.path.join(atardecer_path, file))
                    self.bg_level1_frames.append(self._resize_background(img))

        #Fondo2
        espacio_path = os.path.join(fondo_path, "Espacio")
        if os.path.isdir(espacio_path):
            for file in sorted(os.listdir(espacio_path)):
                if file.lower().endswith(".png"):
                    img = self._load_image(os.path.join(espacio_path, file))
                    self.bg_level2_frames.append(self._resize_background(img))

        #Fondo 3 - Nivel 3 
        Fondo3_path = os.path.join(fondo_path, "Fondo3")
        for i in range(1, 14):
            img = self._load_image(os.path.join(Fondo3_path, f"Fondo3.{i}.png"))
            self.bg_levels3_frames.append(self._resize_background(img))

        # JEFE FINAL SPRINTS
        boss_path = os.path.join(fondo_path, "Boss")
        for i in range(1, 14):
            img = self._load_image(os.path.join(boss_path, f"Fondo4.{i}.png"))
            self.bg_boss_frames.append(self._resize_background(img))


    def _resize_background(self, image):
        """Redimensionar fondo para cubrir toda la pantalla"""
        screen_width = pygame.display.get_surface().get_width() if pygame.display.get_surface() else 800
        screen_height = pygame.display.get_surface().get_height() if pygame.display.get_surface() else 600

        img_width, img_height = image.get_size()
        # Calcular escala para cubrir toda la pantalla
        scale_x = screen_width / img_width
        scale_y = screen_height / img_height
        scale = max(scale_x, scale_y)  # Usar la escala mayor para cubrir todo

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        return pygame.transform.scale(image, (new_width, new_height))

    def _scale_powerup(self, image):
        """Escalar un sprite de power-up segun POWERUP_SCALE (config.py)"""
        if POWERUP_SCALE == 1:
            return image
        w, h = image.get_size()
        return pygame.transform.scale(image, (round(w * POWERUP_SCALE), round(h * POWERUP_SCALE)))

    def _load_powerups(self):
        """Cargar sprites de power-ups (animados: flotar y recoger)"""
        powerups_path = os.path.join(IMAGES_PATH, "powerups")
        # Clave que usa el codigo -> carpeta en assets/images/powerups
        # OJO: "orange" = bala MORADA (+daño) y "blue" = bala VERDE (+velocidad de disparo)
        folders = {
            "health": "powerup_vida",
            "orange": "powerup_balas_moradas",
            "blue": "powerup_balas_verdes",
        }
        self.powerup_float = {}   # 8 frames mientras cae/flota
        self.powerup_pickup = {}  # 6 frames al recogerlo
        for power_type, folder in folders.items():
            folder_path = os.path.join(powerups_path, folder)
            self.powerup_float[power_type] = [
                self._scale_powerup(self._load_image(os.path.join(folder_path, f"{folder}_flotar_{i}.png")))
                for i in range(1, 9)
            ]
            self.powerup_pickup[power_type] = [
                self._scale_powerup(self._load_image(os.path.join(folder_path, f"{folder}_recoger_{i}.png")))
                for i in range(1, 7)
            ]
            # Primer frame como sprite fijo (compatibilidad con get_powerup)
            self.powerups[power_type] = self.powerup_float[power_type][0]


    def _load_boss(self): # Si quieren tocar esto, mas les vale tener una copia de este codigo listo
        "SPRINTS DEL JEFE FINAL"

        boss_path = os.path.join(IMAGES_PATH, "Boss")

        #Subcarpetas
        self.boss_sprites = {
            "ataques": [],
            "impacto": [], 
            "muerte": [],
            "proyectiles": []
        }  

        #Sprints de ataques
        ataques_path = os.path.join(boss_path, "Ataques")
        for i in range(1, 15):
            img = self._load_image(os.path.join(ataques_path, f"Ataque{i}.png"))     
            self.boss_sprites["ataques"].append(img)

        #Sprints de impacto
        impacto_path = os.path.join(boss_path, "Impacto")
        for i in range(1, 5):
            img = self._load_image(os.path.join(impacto_path, f"Golpe{i}.png"))
            self.boss_sprites["impacto"].append(img)    

        #Sprints de Muerte
        muerte_path = os.path.join(boss_path, "Muerte")
        for i in range(1, 7):
            img = self._load_image(os.path.join(muerte_path, f"Muerte{i}.png"))
            self.boss_sprites["muerte"].append(img)

        #Sprints de proyectiles 
        proyectiles_path = os.path.join(boss_path, "Proyectiles")
        if os.path.exists(proyectiles_path):
            #Sube todas las imagenes de la carpeta al juego
            for file in sorted(os.listdir(proyectiles_path)):
                if file.endswith(".png"): 
                    img = self._load_image(os.path.join(proyectiles_path, file))
                    self.boss_sprites["proyectiles"].append(img)
    

    def _load_all_sprites(self): # Si agregamos nuevos sprints aca SI O SI tienen que venir todos 
        """Cargar todos los sprites del juego"""
        self._load_asteroids() # Cargar sprites de asteroides
        self._load_bullets() # Cargar sprites de balas
        self._load_ciclope() # Cargar sprites del ciclope
        self._load_explosions() # Cargar sprites de explosiones
        self._load_enemies() # Cargar sprites de enemigos
        self._load_player() # Cargar sprites del jugador
        self._load_backgrounds() # Cargar fondos de pantalla
        self._load_powerups()  # Cargar sprites de power-ups
        self._load_boss() # Cargar sprites del jefe final

    def get_asteroid_frame(self, frame_index):
        """Obtener frame de animación de asteroide"""
        return self.asteroids[frame_index % len(self.asteroids)]

    def get_asteroid_hit(self):
        """Obtener sprite de asteroide golpeado"""
        return self.asteroid_hit[0]

    def get_bullet_frame(self, bullet_type, frame_index):
        """Obtener frame de animación de bala"""
        frames = self.bullets.get(bullet_type, self.bullets["dorada"])
        return frames[frame_index % len(frames)]

    def get_ciclope_frame(self, frame_index):
        """Obtener frame de animación del ciclope"""
        return self.ciclope[frame_index % len(self.ciclope)]

    def get_ciclope_hit(self):
        """Obtener sprite de ciclope golpeado"""
        return self.ciclope_hit[0]

    def get_explosion_frame(self, frame_index):
        """Obtener frame de animación de explosión"""
        return self.explosions[frame_index % len(self.explosions)]

    def get_enemy_frames(self, enemy_type):
        """Obtener frames de animación de enemigo"""
        return self.enemies.get(enemy_type, self.enemies["rojo_abajo"])

    def get_enemy_hit(self, enemy_type):
        """Obtener sprite de enemigo golpeado"""
        return self.enemy_hit.get(enemy_type, self.enemy_hit["rojo_abajo"])[0]

    def get_player_frame(self, direction, frame_index):
        """Obtener frame de animación del jugador"""
        frames = self.player.get(direction, self.player["centro"])
        return frames[frame_index % len(frames)]

    def get_player_hit(self):
        """Obtener sprite de jugador golpeado"""
        return self.player_hit[0]

    def get_background(self, level, ticks=0, is_boss_active=False):
        """Obtener fondo según el nivel"""
        if level == 1:
            if self.bg_level1_frames:
                frame_index = (ticks // 100) % len(self.bg_level1_frames)
                return self.bg_level1_frames[frame_index]
            return self.bg_levels3_frames[0] if self.bg_levels3_frames else None
        elif level == 2:
            if self.bg_level2_frames:
                frame_index = (ticks // 100) % len(self.bg_level2_frames)
                return self.bg_level2_frames[frame_index]
            return self.bg_levels3_frames[0] if self.bg_levels3_frames else None
        elif level == 3:
            #Si el Jefe final esta activo mostrar animacion
            if is_boss_active and self.bg_boss_frames:
                frame_index = (ticks // 100) % len(self.bg_boss_frames)
                return self.bg_boss_frames[frame_index]
            
            #Animacion de fondo para el nivel 3
            if self.bg_levels3_frames:
                #Dependiendo de como queremos que corra la animacion se modifica el numero 100
                frame_index = (ticks // 100) % len(self.bg_levels3_frames)
                return self.bg_levels3_frames[frame_index]
            return self.bg_level2_frames[0] if self.bg_level2_frames else None  # Fallback si no hay frames
        return self.bg_level1_frames[0] if self.bg_level1_frames else None  # Fallback si el nivel no es válido

    def get_powerup(self, power_type):
        """Obtener sprite de power-up"""
        return self.powerups.get(power_type, self.powerups["health"])

    def get_powerup_float_frame(self, power_type, frame_index):
        """Obtener frame de la animacion de flotar del power-up"""
        frames = self.powerup_float.get(power_type, self.powerup_float["health"])
        return frames[frame_index % len(frames)]

    def get_powerup_pickup_frames(self, power_type):
        """Obtener los frames de la animacion de recoger el power-up"""
        return self.powerup_pickup.get(power_type, self.powerup_pickup["health"])


    def get_boss_projectile_frame(self, frame_index): # Tocar bajo cuidado

        #Obtiene la animacion de frames para el boss
        if hasattr (self, 'boss_sprites') and self.boss_sprites.get("proyectiles"):
            frames = self.boss_sprites["proyectiles"]
            return frames[frame_index % len(frames)]
        # En caso de no encontrar sprites utilizar verdes
        return self.get_bullet_frame("verde", frame_index)