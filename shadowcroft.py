#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              S H A D O W C R O F T                          ║
║   Protótipo 2D inspirado em mecânicas de metroidvania        ║
║   Desenvolvido com Python + Pygame                           ║
╠══════════════════════════════════════════════════════════════╣
║  CONTROLES:                                                  ║
║    A D       Mover                                          ║
║    W / Space Pular  (segure para pulo mais alto)            ║
║    M1/Click  Atacar                                          ║
║    R         Reiniciar (após morte)                          ║
║    ESC       Sair                                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import math
import random
from typing import List, Optional

# ═══════════════════════════════════════════════════════════════
#  INICIALIZAÇÃO
# ═══════════════════════════════════════════════════════════════
pygame.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("ShadowCroft")
clock = pygame.time.Clock()
FPS = 60

# ═══════════════════════════════════════════════════════════════
#  CONSTANTES DE FÍSICA E GAMEPLAY
# ═══════════════════════════════════════════════════════════════
GRAVITY        = 0.65    # Aceleração da gravidade por frame
MAX_FALL_SPD   = 16      # Velocidade máxima de queda
PLAYER_SPD     = 5.5     # Velocidade horizontal do jogador
JUMP_FORCE     = -14.5   # Força inicial do pulo
JUMP_HOLD_MULT = 0.55    # Multiplicador ao segurar o pulo
ATTACK_DUR     = 20      # Frames que o hitbox de ataque fica ativo
ATTACK_CD      = 35      # Frames de cooldown entre ataques
INV_FRAMES     = 65      # Frames de invencibilidade após levar dano
KNOCKBACK_H    = 7.5     # Força horizontal do knockback
KNOCKBACK_V    = -5      # Força vertical do knockback (empurra para cima)
COYOTE_TIME    = 8       # Frames de "coyote time" após sair de plataforma
JUMP_BUFFER    = 10      # Frames de buffer para input de pulo

# ═══════════════════════════════════════════════════════════════
#  PALETA DE CORES — atmosfera sombria e mística
# ═══════════════════════════════════════════════════════════════
C_BG_TOP     = (5,   3,  15)   # Fundo superior
C_BG_BOT     = (18, 12,  40)   # Fundo inferior
C_PLT_BODY   = (28, 23,  48)   # Corpo das plataformas
C_PLT_EDGE   = (50, 42,  75)   # Bordas laterais
C_PLT_TOP    = (68, 58,  98)   # Borda superior (linha de chão)
C_PLT_GLOW   = (90, 70, 130)   # Brilho sutil nas plataformas

C_P_BODY     = (200, 200, 235) # Corpo do player
C_P_HEAD     = (215, 215, 245) # Cabeça (levemente mais clara)
C_P_CAPE     = (80,  58, 120)  # Capa
C_P_CAPE2    = (55,  38,  88)  # Sombra da capa
C_P_SWORD    = (195, 218, 255) # Espada
C_P_SWORD2   = (140, 170, 220) # Cabo da espada
C_P_EYE      = (130, 200, 255) # Olho brilhante (bug vibe)
C_P_HURT     = (255, 100, 100) # Flash de dano

C_E_BODY     = (145,  42,  58) # Corpo do inimigo
C_E_SHELL    = (110,  30,  45) # Casca/armadura
C_E_EYE     = (255,  70,  80) # Olho do inimigo
C_E_HURT     = (255, 160, 160) # Flash de dano inimigo

C_SLASH_A    = (220, 235, 255) # Cor do slash de ataque
C_SLASH_B    = (150, 180, 255) # Borda do slash

C_HP_FULL    = (205,  52,  78) # Vida cheia
C_HP_HALF    = (210, 130,  50) # Vida na metade
C_HP_EMPTY   = (45,  16,  26)  # Slot vazio de vida
C_HP_BORDER  = (80,  35,  55)  # Borda do indicador

C_SOUL_A     = (90,  175, 255) # Alma (moeda de vida)
C_SOUL_B     = (180, 230, 255) # Brilho da alma

C_CHK_OFF    = (55,  65, 110)  # Checkpoint desativado
C_CHK_ON     = (120, 215, 255) # Checkpoint ativado
C_CHK_GLOW   = (80,  160, 255) # Halo do checkpoint

C_UI_TEXT    = (200, 195, 230) # Texto da UI
C_UI_TITLE   = (170, 150, 220) # Título

C_WHITE      = (255, 255, 255)
C_BLACK      = (0,   0,   0)
C_TRANS      = (0,   0,   0,   0)

# Partículas
PARTICLE_PALETTES = {
    "hit":    [(255, 200, 80),  (255, 140, 40),  (255, 80,  20)],
    "soul":   [(100, 190, 255), (160, 220, 255), (200, 240, 255)],
    "death":  [(200,  60,  80), (150,  30,  50), (255, 100, 120)],
    "dust":   [(90,  78, 115),  (70,  60,  95),  (110, 95, 140)],
}


# ═══════════════════════════════════════════════════════════════
#  CLASSE: HealthOrb  —  item de cura
# ═══════════════════════════════════════════════════════════════
class HealthOrb:
    """
    Orbe que restaura vida ao jogador.
    """
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.timer = random.random() * math.tau

    def update(self, player):
        self.timer += 0.1
        if not self.collected and self.rect.colliderect(player.rect):
            if player.hp < player.max_hp:
                player.hp += 1
                self.collected = True
                return True
        return False

    def draw(self, surface, cam_x: int, cam_y: int):
        if self.collected:
            return
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y + int(math.sin(self.timer) * 5)

        # Brilho externo
        draw_circle_alpha(surface, C_SOUL_A, (rx + 10, ry + 10), 12, 100)
        # Núcleo
        pygame.draw.circle(surface, C_WHITE, (rx + 10, ry + 10), 6)
        pygame.draw.circle(surface, C_SOUL_B, (rx + 10, ry + 10), 6, 2)


# ═══════════════════════════════════════════════════════════════
#  FUNÇÕES UTILITÁRIAS
# ═══════════════════════════════════════════════════════════════

def lerp(a: float, b: float, t: float) -> float:
    """Interpolação linear."""
    return a + (b - a) * t

def clamp(value: float, mn: float, mx: float) -> float:
    """Limita um valor entre mínimo e máximo."""
    return max(mn, min(mx, value))

def draw_rect_alpha(surface, color, rect, alpha: int):
    """Desenha retângulo com transparência."""
    tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    tmp.fill((*color[:3], alpha))
    surface.blit(tmp, (rect[0], rect[1]))

def draw_circle_alpha(surface, color, center, radius: int, alpha: int):
    """Desenha círculo com transparência."""
    tmp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(tmp, (*color[:3], alpha), (radius, radius), radius)
    surface.blit(tmp, (center[0] - radius, center[1] - radius))

def draw_gradient_bg(surface, color_top, color_bot, rect):
    """Fundo com gradiente vertical."""
    x, y, w, h = rect
    for row in range(h):
        t = row / h
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x, y + row), (x + w, y + row))


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Particle  —  efeitos visuais de partícula
# ═══════════════════════════════════════════════════════════════
class Particle:
    """
    Partícula de efeito visual.
    Usada em golpes, dano, checkpoints e morte.
    """
    def __init__(self, x: float, y: float, palette: str = "hit",
                 speed_range=(1, 4), lifetime_range=(15, 35), gravity=0.08):
        self.x = x
        self.y = y
        # Direção aleatória
        angle = random.uniform(0, math.tau)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = gravity
        self.lifetime = random.randint(*lifetime_range)
        self.max_life = self.lifetime
        self.color = random.choice(PARTICLE_PALETTES[palette])
        self.radius = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

    def draw(self, surface, cam_x: int, cam_y: int):
        if self.lifetime <= 0:
            return
        alpha = int(255 * (self.lifetime / self.max_life))
        r = max(1, int(self.radius * (self.lifetime / self.max_life)))
        draw_circle_alpha(surface, self.color,
                          (int(self.x - cam_x), int(self.y - cam_y)), r, alpha)

    @property
    def alive(self) -> bool:
        return self.lifetime > 0


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Platform  —  plataformas do cenário
# ═══════════════════════════════════════════════════════════════
class Platform:
    """
    Plataforma sólida do mundo.
    Suporta variações de cor para criar profundidade visual.
    """
    def __init__(self, x: int, y: int, w: int, h: int, variant: int = 0, hazard: bool = False):
        self.rect = pygame.Rect(x, y, w, h)
        self.variant = variant  # 0=normal, 1=pedra, 2=raiz orgânica
        self.hazard = hazard    # Espinhos/perigo

    def draw(self, surface, cam_x: int, cam_y: int):
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        rw = self.rect.w
        rh = self.rect.h

        # Só renderiza se estiver na tela (culling simples)
        if rx + rw < 0 or rx > SCREEN_W or ry + rh < 0 or ry > SCREEN_H:
            return

        # Corpo principal
        pygame.draw.rect(surface, C_PLT_BODY, (rx, ry, rw, rh))

        # Bordas laterais (mais escuras)
        pygame.draw.rect(surface, C_PLT_EDGE, (rx, ry, 2, rh))
        pygame.draw.rect(surface, C_PLT_EDGE, (rx + rw - 2, ry, 2, rh))

        # Topo destacado (onde o player pisa)
        top_col = (255, 50, 50) if self.hazard else C_PLT_TOP
        pygame.draw.rect(surface, top_col, (rx, ry, rw, 3))

        # Linha de brilho sutil no topo
        pygame.draw.rect(surface, C_PLT_GLOW, (rx + 1, ry + 1, rw - 2, 1))

        if self.hazard:
            # Desenha "espinhos" simples
            for i in range(0, rw, 10):
                pts = [(rx + i, ry), (rx + i + 5, ry - 8), (rx + i + 10, ry)]
                pygame.draw.polygon(surface, (200, 30, 30), pts)

        # Detalhes visuais por variante
        if self.variant == 1:
            # Rachaduras na pedra
            for i in range(3):
                cx = rx + int(rw * (0.2 + i * 0.3))
                pygame.draw.line(surface, C_PLT_EDGE,
                                 (cx, ry + 4), (cx + 4, ry + 12), 1)
        elif self.variant == 2:
            # Padrão orgânico/raiz
            for i in range(rw // 30):
                bx = rx + i * 30 + 10
                pygame.draw.circle(surface, C_PLT_EDGE, (bx, ry + 6), 3)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Checkpoint  —  ponto de salvamento
# ═══════════════════════════════════════════════════════════════
class Checkpoint:
    """
    Checkpoint interativo.
    Salva a posição do jogador ao tocar.
    Anima uma chama mística ao ser ativado.
    """
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 24, 48)
        self.active = False
        self.timer  = 0
        self.particles: List[Particle] = []

    def activate(self):
        if not self.active:
            self.active = True
            # Burst de partículas ao ativar
            for _ in range(30):
                p = Particle(self.rect.centerx, self.rect.top,
                             palette="soul", speed_range=(1, 5),
                             lifetime_range=(20, 50), gravity=-0.05)
                self.particles.append(p)

    def update(self):
        self.timer += 1
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()
        # Emite partículas contínuas quando ativo
        if self.active and random.random() < 0.25:
            p = Particle(self.rect.centerx + random.randint(-5, 5),
                         self.rect.top + 10,
                         palette="soul", speed_range=(0.5, 2),
                         lifetime_range=(15, 30), gravity=-0.08)
            self.particles.append(p)

    def draw(self, surface, cam_x: int, cam_y: int):
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y

        # Corpo do checkpoint (espécie de totem/cristal)
        color = C_CHK_ON if self.active else C_CHK_OFF
        # Base
        pygame.draw.rect(surface, color, (rx, ry + 30, 24, 18))
        # Haste
        pygame.draw.rect(surface, color, (rx + 9, ry + 10, 6, 22))
        # Cristal no topo (losango)
        cx, cy = rx + 12, ry + 6
        size = 10
        pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
        pygame.draw.polygon(surface, color, pts)

        # Halo de brilho
        if self.active:
            glow = abs(math.sin(self.timer * 0.06)) * 60 + 40
            draw_circle_alpha(surface, C_CHK_GLOW, (rx + 12, ry + 6), 20, int(glow))

        # Partículas
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Enemy  —  inimigo com IA de patrulha
# ═══════════════════════════════════════════════════════════════
class Enemy:
    """
    Inimigo básico com máquina de estados:
      - PATROL: anda entre dois pontos
      - CHASE:  persegue o jogador
      - ATTACK: golpeia quando perto
      - HURT:   knockback ao levar dano
      - DEAD:   animação de morte
    """
    PATROL = "patrol"
    CHASE  = "chase"
    ATTACK = "attack"
    HURT   = "hurt"
    DEAD   = "dead"

    def __init__(self, x: int, y: int, patrol_range: int = 120, max_hp: int = 3):
        self.rect = pygame.Rect(x, y, 32, 38)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False

        self.max_hp  = max_hp
        self.hp      = max_hp
        self.state   = self.PATROL
        self.facing  = 1            # 1=direita, -1=esquerda

        # Patrulha
        self.patrol_center = x + 16
        self.patrol_range  = patrol_range
        self.patrol_spd    = 1.4

        # Timers
        self.hurt_timer    = 0
        self.attack_timer  = 0
        self.attack_cd     = 0
        self.aggro_dist    = 220    # distância para entrar em chase
        self.attack_dist   = 50    # distância para atacar
        self.dead_timer    = 0
        self.bob_timer     = 0

        # Efeitos
        self.particles: List[Particle] = []
        self.flash = False

    @property
    def alive(self) -> bool:
        return self.state != self.DEAD or self.dead_timer < 40

    @property
    def can_damage_player(self) -> bool:
        """True quando o inimigo está no frame de ataque ativo."""
        return self.state == self.ATTACK and 5 <= self.attack_timer <= 15

    def take_damage(self, damage: int, direction: int):
        """Recebe dano e entra em estado de hurt."""
        if self.state in (self.HURT, self.DEAD):
            return
        self.hp -= damage
        self.flash = True
        # Partículas de hit
        for _ in range(12):
            p = Particle(self.rect.centerx, self.rect.centery,
                         palette="hit", speed_range=(2, 5))
            self.particles.append(p)
        if self.hp <= 0:
            self._die()
        else:
            self.state = self.HURT
            self.hurt_timer = 20
            self.vx = direction * KNOCKBACK_H * 0.7
            self.vy = KNOCKBACK_V * 0.6

    def _die(self):
        self.state = self.DEAD
        self.dead_timer = 0
        for _ in range(25):
            p = Particle(self.rect.centerx, self.rect.centery,
                         palette="death", speed_range=(1, 6),
                         lifetime_range=(20, 45))
            self.particles.append(p)

    def update(self, platforms: List[Platform], player_rect: pygame.Rect):
        if self.state == self.DEAD:
            self.dead_timer += 1
            self._update_particles()
            return

        self.bob_timer += 1
        self.flash = False
        self._update_particles()

        dx = player_rect.centerx - self.rect.centerx
        dist = abs(dx)

        # --- Máquina de estados ---
        if self.state == self.HURT:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.state = self.PATROL

        elif self.state == self.PATROL:
            # Vai e volta entre os extremos da patrulha
            if self.rect.centerx > self.patrol_center + self.patrol_range:
                self.facing = -1
            elif self.rect.centerx < self.patrol_center - self.patrol_range:
                self.facing = 1
            self.vx = self.patrol_spd * self.facing
            # Detecta jogador
            if dist < self.aggro_dist:
                self.state = self.CHASE

        elif self.state == self.CHASE:
            # Persegue o player
            self.facing = 1 if dx > 0 else -1
            self.vx = self.patrol_spd * 1.8 * self.facing
            self.attack_cd = max(0, self.attack_cd - 1)
            if dist < self.attack_dist and self.attack_cd == 0:
                self.state = self.ATTACK
                self.attack_timer = 0
                self.vx = 0
            # Perde aggro
            if dist > self.aggro_dist * 1.5:
                self.state = self.PATROL

        elif self.state == self.ATTACK:
            self.attack_timer += 1
            # Luneta suave na direção do player
            if self.attack_timer < 8:
                self.vx = self.facing * 1.5
            else:
                self.vx *= 0.7
            if self.attack_timer >= 28:
                self.state = self.CHASE
                self.attack_cd = 60

        # Não cai de plataformas (limite de borda)
        if self.on_ground:
            look_x = self.rect.x + (self.rect.w if self.facing == 1 else -4)
            foot_rect = pygame.Rect(look_x, self.rect.bottom, 4, 4)
            on_edge = not any(p.rect.colliderect(foot_rect) for p in platforms)
            if on_edge:
                if self.state == self.PATROL:
                    self.facing *= -1
                    self.vx = self.patrol_spd * self.facing
                elif self.state in (self.CHASE, self.ATTACK):
                    # Tenta pular entre plataformas se estiver perseguindo
                    self.vy = -11.0
                    self.on_ground = False
                else:
                    self.vx = 0

        # --- Física ---
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPD)
        self.rect.x += int(self.vx)
        self._collide_x(platforms)
        self.rect.y += int(self.vy)
        self._collide_y(platforms)

    def _collide_x(self, platforms: List[Platform]):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                self.vx = 0
                self.facing *= -1

    def _collide_y(self, platforms: List[Platform]):
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                self.vy = 0

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surface, cam_x: int, cam_y: int):
        # Partículas sempre por baixo
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)

        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        w, h = self.rect.w, self.rect.h
        bob = int(math.sin(self.bob_timer * 0.08) * 1.5)

        if self.state == self.DEAD and self.dead_timer > 10:
            return  # Já dissolveu

        # Cor base com flash de dano
        body_col = C_E_HURT if self.flash else C_E_BODY
        shell_col = C_E_HURT if self.flash else C_E_SHELL

        # Corpo principal (concha/armadura arredondada)
        pygame.draw.ellipse(surface, shell_col,
                            (rx + 2, ry + bob + 8, w - 4, h - 8))
        pygame.draw.ellipse(surface, body_col,
                            (rx + 4, ry + bob + 10, w - 8, h - 14))

        # Cabeça
        pygame.draw.circle(surface, body_col,
                           (rx + w // 2, ry + bob + 8), 12)
        pygame.draw.circle(surface, shell_col,
                           (rx + w // 2, ry + bob + 8), 12, 2)

        # Olho
        eye_x = rx + w // 2 + self.facing * 4
        eye_y = ry + bob + 7
        pygame.draw.circle(surface, C_E_EYE, (eye_x, eye_y), 4)
        pygame.draw.circle(surface, C_WHITE,  (eye_x, eye_y), 2)

        # Indicador de ataque (brilho avermelhado)
        if self.state == self.ATTACK and self.attack_timer < 16:
            draw_circle_alpha(surface, C_E_EYE,
                              (rx + w // 2, ry + bob + 7), 16,
                              int(120 * (1 - self.attack_timer / 16)))

        # Pernas simples
        for i, lx in enumerate([rx + 6, rx + w - 10]):
            leg_bob = int(math.sin(self.bob_timer * 0.15 + i * math.pi) * 2)
            pygame.draw.rect(surface, shell_col,
                             (lx, ry + h - 10 + leg_bob, 6, 10))

        # Barra de vida acima do inimigo (só se tiver tomado dano)
        if self.hp < self.max_hp:
            self._draw_hp_bar(surface, rx, ry + bob - 12)

    def _draw_hp_bar(self, surface, rx: int, ry: int):
        bar_w = self.rect.w
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, C_HP_EMPTY, (rx, ry, bar_w, 5))
        pygame.draw.rect(surface, C_HP_FULL,  (rx, ry, int(bar_w * ratio), 5))
        pygame.draw.rect(surface, C_HP_BORDER, (rx, ry, bar_w, 5), 1)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Projectile  —  projétil disparado por inimigos
# ═══════════════════════════════════════════════════════════════
class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.rect = pygame.Rect(x - 6, y - 6, 12, 12)
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.timer = 0

    def update(self, player, platforms):
        self.timer += 1
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        if self.rect.colliderect(player.rect):
            player.take_damage(1, self.rect.centerx)
            self.alive = False

        for p in platforms:
            if self.rect.colliderect(p.rect):
                self.alive = False

        # Timeout
        if self.timer > 180:
            self.alive = False

    def draw(self, surface, cam_x: int, cam_y: int):
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        draw_circle_alpha(surface, C_E_EYE, (rx + 6, ry + 6), 8, 180)
        pygame.draw.circle(surface, C_WHITE, (rx + 6, ry + 6), 4)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: ShootingEnemy  —  inimigo que atira
# ═══════════════════════════════════════════════════════════════
class ShootingEnemy(Enemy):
    def __init__(self, x: int, y: int, patrol_range: int = 100, max_hp: int = 2):
        super().__init__(x, y, patrol_range, max_hp)
        self.shoot_cd = 0

    def update(self, platforms, player_rect, projectiles):
        super().update(platforms, player_rect)
        self.shoot_cd = max(0, self.shoot_cd - 1)

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 400 and self.shoot_cd == 0 and self.state != self.DEAD:
            # Atira
            angle = math.atan2(dy, dx)
            pvx = math.cos(angle) * 7
            pvy = math.sin(angle) * 7
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, pvx, pvy))
            self.shoot_cd = 100

    def draw(self, surface, cam_x, cam_y):
        super().draw(surface, cam_x, cam_y)
        if self.state == self.DEAD and self.dead_timer > 10: return
        # Diferencia visualmente (cor roxa no olho ou algo assim)
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        bob = int(math.sin(self.bob_timer * 0.08) * 1.5)
        pygame.draw.circle(surface, (150, 50, 255), (rx + self.rect.w//2 + self.facing*4, ry + bob + 7), 2)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Boss  —  inimigo final de nível
# ═══════════════════════════════════════════════════════════════
class Boss(Enemy):
    def __init__(self, x, y, max_hp=20):
        super().__init__(x, y, patrol_range=200, max_hp=max_hp)
        self.rect = pygame.Rect(x, y, 80, 100)
        self.phase_timer = 0
        self.shoot_cd = 0

    def update(self, platforms, player_rect, projectiles):
        super().update(platforms, player_rect)
        self.shoot_cd = max(0, self.shoot_cd - 1)
        self.phase_timer += 1

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)

        if self.state != self.DEAD and dist < 600:
            # Padrão de ataque: rajada circular
            if self.phase_timer % 100 == 0:
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    pvx, pvy = math.cos(rad) * 4, math.sin(rad) * 4
                    projectiles.append(Projectile(self.rect.centerx, self.rect.centery, pvx, pvy))

            # Tiro direcionado (apenas se tiver cooldown e player estiver perto)
            if self.shoot_cd == 0:
                angle = math.atan2(dy, dx)
                # Mais rápido conforme HP diminui
                speed = 7 + (1 - self.hp/self.max_hp) * 5
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery, math.cos(angle)*speed, math.sin(angle)*speed))
                self.shoot_cd = max(20, 50 - int((1 - self.hp/self.max_hp) * 30))

    def draw(self, surface, cam_x, cam_y):
        if self.state == self.DEAD and self.dead_timer > 20: return
        rx, ry = self.rect.x - cam_x, self.rect.y - cam_y
        # Visual de Boss imponente
        pygame.draw.rect(surface, (80, 20, 40), (rx, ry, 80, 100), border_radius=10)
        pygame.draw.rect(surface, (150, 40, 60), (rx + 10, ry + 10, 60, 80), border_radius=8)
        # Olhos grandes
        eye_y = ry + 30 + int(math.sin(self.bob_timer*0.1)*5)
        pygame.draw.circle(surface, (255, 0, 0), (rx + 25, eye_y), 10)
        pygame.draw.circle(surface, (255, 0, 0), (rx + 55, eye_y), 10)
        if self.hp < self.max_hp:
            self._draw_hp_bar(surface, rx, ry - 20)

    def _draw_hp_bar(self, surface, rx, ry):
        bar_w = self.rect.w
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, C_HP_EMPTY, (rx, ry, bar_w, 10))
        pygame.draw.rect(surface, (255, 0, 0),  (rx, ry, int(bar_w * ratio), 10))
        pygame.draw.rect(surface, C_WHITE, (rx, ry, bar_w, 10), 1)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Player  —  personagem principal
# ═══════════════════════════════════════════════════════════════
class Player:
    """
    Jogador principal com:
    - Movimento fluido com aceleração
    - Pulo responsivo (hold para mais alto)
    - Coyote time e jump buffer
    - Sistema de ataque com hitbox e duração
    - Knockback e invencibilidade ao levar dano
    - Animações por estado
    """
    def __init__(self, x: int, y: int, max_hp: int = 5):
        self.rect      = pygame.Rect(x, y, 28, 42)
        self.vx        = 0.0
        self.vy        = 0.0
        self.facing    = 1
        self.on_ground = False

        # Vida
        self.max_hp = max_hp
        self.hp     = max_hp
        self.alive  = True

        # Estados booleanos
        self.is_attacking  = False
        self.is_hurt       = False
        self.is_dead       = False

        # Timers
        self.attack_timer  = 0      # Frame atual do ataque
        self.attack_cd     = 0      # Cooldown do ataque
        self.inv_timer     = 0      # Invencibilidade
        self.coyote_timer  = 0      # Coyote time
        self.jump_buffer   = 0      # Buffer de input de pulo
        self.death_timer   = 0      # Animação de morte
        self.anim_timer    = 0      # Timer geral de animação

        # Input
        self.jump_held     = False

        # Hitbox de ataque
        self.attack_rect   = pygame.Rect(0, 0, 0, 0)

        # Efeitos
        self.particles: List[Particle] = []
        self.flash_timer = 0
        self.dust_timer  = 0

        # Checkpoint de respawn
        self.spawn_x = x
        self.spawn_y = y

    # ── Input e movimento ──────────────────────────────────────
    def handle_input(self, keys):
        """Processa input do teclado e aplica velocidades."""
        if self.is_dead:
            return

        # Movimento horizontal com aceleração suave
        move = 0
        if keys[pygame.K_a]:
            move = -1
        if keys[pygame.K_d]:
            move = 1

        if move != 0:
            self.facing = move
            target_vx = move * PLAYER_SPD
            # Aceleração mais responsiva
            self.vx = lerp(self.vx, target_vx, 0.35 if self.on_ground else 0.2)
        else:
            # Desaceleração mais seca para precisão
            self.vx = lerp(self.vx, 0, 0.45 if self.on_ground else 0.1)
            if abs(self.vx) < 0.1:
                self.vx = 0

        # Buffer de pulo (permite pressionar um pouco antes de chegar ao chão)
        jump_keys = keys[pygame.K_w] or keys[pygame.K_z] or keys[pygame.K_SPACE]
        if jump_keys:
            self.jump_buffer = JUMP_BUFFER

        # Pulo
        can_jump = self.on_ground or self.coyote_timer > 0
        if self.jump_buffer > 0 and can_jump:
            self.vy = JUMP_FORCE
            self.coyote_timer = 0
            self.jump_buffer  = 0
            self.jump_held    = True
            # Partículas de poeira no pulo
            for _ in range(6):
                p = Particle(self.rect.centerx, self.rect.bottom,
                             palette="dust", speed_range=(0.5, 2),
                             lifetime_range=(8, 18), gravity=0.05)
                self.particles.append(p)

        # Pulo mais alto segurando (variável jump height)
        if self.jump_held and self.vy < 0:
            if not jump_keys:
                self.jump_held = False
                if self.vy < -7:
                    self.vy *= JUMP_HOLD_MULT

        # Ataque (X ou Clique do Mouse)
        mouse_click = pygame.mouse.get_pressed()[0]
        if (keys[pygame.K_x] or mouse_click) and self.attack_cd == 0 and not self.is_attacking:
            self._start_attack()

    def _start_attack(self):
        """Inicia animação e hitbox de ataque."""
        self.is_attacking = True
        self.attack_timer = ATTACK_DUR
        self.attack_cd    = ATTACK_CD
        # Partículas de slash
        sx = self.rect.centerx + self.facing * 30
        sy = self.rect.centery
        for _ in range(8):
            p = Particle(sx, sy, palette="soul",
                         speed_range=(1, 4), lifetime_range=(8, 20), gravity=0)
            self.particles.append(p)

    # ── Física ────────────────────────────────────────────────
    def apply_gravity(self):
        if self.is_dead:
            return
        self.vy += GRAVITY
        # Queda mais lenta no pico do pulo (feel responsivo)
        if abs(self.vy) < 3 and not self.on_ground:
            self.vy += GRAVITY * 0.3
        self.vy = min(self.vy, MAX_FALL_SPD)

    def move_and_collide(self, platforms: List[Platform]):
        """Move o player e resolve colisões com plataformas."""
        if self.is_dead:
            self.vy += GRAVITY
            self.rect.y += int(self.vy)
            return

        # Horizontal
        self.rect.x += int(self.vx)
        self._collide_x(platforms)

        # Vertical
        prev_on_ground = self.on_ground
        self.rect.y += int(self.vy)
        self._collide_y(platforms)

        # Ground detection extra para garantir pulo estável
        ground_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, 2)
        for p in platforms:
            if ground_rect.colliderect(p.rect) and self.vy >= 0:
                self.on_ground = True
                self.rect.bottom = p.rect.top
                self.vy = 0
                break

        # Coyote time: mantém alguns frames de pulo após sair de borda
        if prev_on_ground and not self.on_ground and self.vy > 0:
            self.coyote_timer = COYOTE_TIME
        elif self.on_ground:
            self.coyote_timer = 0
        else:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        # Poeira ao aterrissar
        if not prev_on_ground and self.on_ground:
            for _ in range(8):
                p = Particle(self.rect.centerx, self.rect.bottom,
                             palette="dust", speed_range=(1, 3),
                             lifetime_range=(10, 22), gravity=0.05)
                self.particles.append(p)

    def _collide_x(self, platforms: List[Platform]):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                self.vx = 0

    def _collide_y(self, platforms: List[Platform]):
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground   = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                self.vy = 0

    # ── Dano ──────────────────────────────────────────────────
    def take_damage(self, damage: int, enemy_x: int):
        """Recebe dano de um inimigo."""
        if self.inv_timer > 0 or self.is_dead:
            return
        self.hp -= damage
        self.inv_timer  = INV_FRAMES
        self.flash_timer = 12
        self.is_hurt    = True
        # Knockback
        direction = 1 if self.rect.centerx > enemy_x else -1
        self.vx = direction * KNOCKBACK_H
        self.vy = KNOCKBACK_V
        # Partículas
        for _ in range(16):
            p = Particle(self.rect.centerx, self.rect.centery,
                         palette="hit", speed_range=(2, 6))
            self.particles.append(p)
        if self.hp <= 0:
            self._die()

    def _die(self):
        self.is_dead   = True
        self.death_timer = 0
        for _ in range(30):
            p = Particle(self.rect.centerx, self.rect.centery,
                         palette="death", speed_range=(1, 7),
                         lifetime_range=(30, 60))
            self.particles.append(p)

    def respawn(self):
        """Respawn no último checkpoint."""
        self.rect.x   = self.spawn_x
        self.rect.y   = self.spawn_y
        self.vx, self.vy = 0, 0
        self.hp        = self.max_hp
        self.is_dead   = False
        self.is_hurt   = False
        self.death_timer = 0
        self.inv_timer  = INV_FRAMES
        self.particles  = []

    # ── Update ────────────────────────────────────────────────
    def update(self, platforms: List[Platform],
               checkpoints: List[Checkpoint],
               enemies: List[Enemy]):
        """Atualiza todos os sistemas do player."""
        self.anim_timer += 1

        # Timers
        self.attack_cd   = max(0, self.attack_cd   - 1)
        self.inv_timer   = max(0, self.inv_timer   - 1)
        self.flash_timer = max(0, self.flash_timer - 1)
        self.jump_buffer = max(0, self.jump_buffer - 1)
        if self.inv_timer == 0:
            self.is_hurt = False

        if self.is_dead:
            self.death_timer += 1
            self._update_particles()
            return

        # Atualiza hitbox de ataque
        if self.is_attacking:
            self.attack_timer -= 1
            reach = 48
            ax = self.rect.centerx + (self.facing * 10) if self.facing == 1 else self.rect.centerx - reach - 10
            self.attack_rect = pygame.Rect(ax if self.facing == 1 else self.rect.centerx - reach,
                                           self.rect.y + 6, reach, 30)
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_rect  = pygame.Rect(0, 0, 0, 0)

        # Checkpoints
        for chk in checkpoints:
            if self.rect.colliderect(chk.rect):
                chk.activate()
                self.spawn_x = chk.rect.centerx - self.rect.w // 2
                self.spawn_y = chk.rect.top - self.rect.h

        # Colisão com inimigos (dano ao player)
        for e in enemies:
            if not e.alive:
                continue
            if e.can_damage_player and self.rect.colliderect(e.rect):
                self.take_damage(1, e.rect.centerx)
            # Colisão de contato simples
            elif e.state != Enemy.DEAD and self.rect.colliderect(e.rect) and self.inv_timer == 0:
                self.take_damage(1, e.rect.centerx)

        # Poeira ao andar
        self.dust_timer += 1
        if self.on_ground and abs(self.vx) > 1 and self.dust_timer % 8 == 0:
            p = Particle(self.rect.centerx, self.rect.bottom,
                         palette="dust", speed_range=(0.2, 1),
                         lifetime_range=(6, 14), gravity=0)
            self.particles.append(p)

        self._update_particles()

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    # ── Desenho ───────────────────────────────────────────────
    def draw(self, surface, cam_x: int, cam_y: int):
        """Renderiza o jogador com sprites geométricos."""
        # Partículas por baixo do sprite
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)

        if self.is_dead and self.death_timer > 15:
            return

        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
        w, h = self.rect.w, self.rect.h

        # Flash de invencibilidade (piscada)
        if self.inv_timer > 0 and self.inv_timer % 6 < 3 and not self.flash_timer:
            return  # Pisca quando invencível

        # Cor base com flash de dano
        body_col = C_P_HURT if self.flash_timer > 0 else C_P_BODY
        head_col = C_P_HURT if self.flash_timer > 0 else C_P_HEAD

        # Idle bob
        bob = int(math.sin(self.anim_timer * 0.07) * 1.5) if self.on_ground else 0

        # Capa (atrás do corpo)
        cape_off = int(math.sin(self.anim_timer * 0.1) * 2)
        cape_pts = [
            (rx + w // 2 - self.facing * 2, ry + 8 + bob),
            (rx + w // 2 - self.facing * 14, ry + h - 4 + cape_off),
            (rx + w // 2 - self.facing * 6,  ry + h // 2 + bob),
        ]
        pygame.draw.polygon(surface, C_P_CAPE2, cape_pts)
        cape_pts2 = [
            (rx + w // 2 - self.facing * 2, ry + 10 + bob),
            (rx + w // 2 - self.facing * 11, ry + h - 6 + cape_off),
            (rx + w // 2 - self.facing * 5,  ry + h // 2 + 2 + bob),
        ]
        pygame.draw.polygon(surface, C_P_CAPE, cape_pts2)

        # Corpo (torso arredondado)
        torso_rect = (rx + 4, ry + 14 + bob, w - 8, h - 20)
        pygame.draw.rect(surface, body_col, torso_rect, border_radius=6)

        # Pernas (animação de andar)
        leg_spd = self.anim_timer * 0.2
        for i, sign in enumerate([-1, 1]):
            leg_bob = int(math.sin(leg_spd + i * math.pi) * 4) if self.on_ground and abs(self.vx) > 0.5 else 0
            pygame.draw.rect(surface, C_P_CAPE,
                             (rx + 5 + i * (w - 14), ry + h - 10 + leg_bob, 8, 12))

        # Cabeça
        head_cx = rx + w // 2
        head_cy = ry + 12 + bob
        pygame.draw.circle(surface, head_col, (head_cx, head_cy), 13)

        # Máscara/viseira (detalhe de cavaleiro-inseto)
        mask_pts = [
            (head_cx + self.facing * 2, head_cy - 6),
            (head_cx + self.facing * 11, head_cy + 2),
            (head_cx + self.facing * 9,  head_cy + 8),
            (head_cx + self.facing * 1,  head_cy + 6),
        ]
        pygame.draw.polygon(surface, C_P_CAPE, mask_pts)

        # Olho brilhante
        eye_x = head_cx + self.facing * 5
        eye_y = head_cy + 1
        pygame.draw.circle(surface, C_P_EYE, (eye_x, eye_y), 4)
        # Reflexo
        pygame.draw.circle(surface, C_WHITE, (eye_x + 1, eye_y - 1), 1)

        # Antenas
        ant_base = (head_cx + self.facing * 2, head_cy - 11)
        pygame.draw.line(surface, C_P_CAPE2, ant_base,
                         (ant_base[0] - self.facing * 6, ant_base[1] - 10), 2)
        pygame.draw.line(surface, C_P_CAPE2, ant_base,
                         (ant_base[0] + self.facing * 3, ant_base[1] - 8), 1)

        # Espada / ataque
        if self.is_attacking:
            self._draw_attack(surface, rx, ry, w, h, bob)

    def _draw_attack(self, surface, rx, ry, w, h, bob):
        """Desenha o slash do ataque."""
        t = 1 - (self.attack_timer / ATTACK_DUR)   # 0.0 → 1.0
        # Arco do slash
        cx = rx + w // 2 + self.facing * 8
        cy = ry + h // 2 + bob

        # Halo de energia
        glow_r = int(20 + t * 15)
        draw_circle_alpha(surface, C_SLASH_A, (cx + self.facing * 20, cy), glow_r,
                          int(180 * (1 - t)))

        # Linha da espada
        sx = cx
        ex = cx + self.facing * int(46 * (1 - t * 0.3))
        ey_off = int(math.sin(t * math.pi) * 14)
        pygame.draw.line(surface, C_SLASH_B, (sx, cy), (ex, cy - ey_off), 4)
        pygame.draw.line(surface, C_P_SWORD, (sx, cy), (ex, cy - ey_off), 2)

        # Ponta brilhante
        pygame.draw.circle(surface, C_WHITE, (ex, cy - ey_off), 3)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Camera  —  câmera suave seguindo o player
# ═══════════════════════════════════════════════════════════════
class Camera:
    """
    Câmera com interpolação suave.
    Limita o scroll nas bordas do mundo.
    """
    def __init__(self, world_w: int, world_h: int):
        self.x = 0.0
        self.y = 0.0
        self.world_w = world_w
        self.world_h = world_h

    def follow(self, target: pygame.Rect, smooth: float = 0.1):
        """Interpola suavemente em direção ao alvo."""
        target_x = target.centerx - SCREEN_W // 2
        target_y = target.centery - SCREEN_H // 2
        self.x = lerp(self.x, target_x, smooth)
        self.y = lerp(self.y, target_y, smooth)
        # Clamp nas bordas do mundo
        self.x = clamp(self.x, 0, max(0, self.world_w - SCREEN_W))
        self.y = clamp(self.y, 0, max(0, self.world_h - SCREEN_H))

    @property
    def ix(self) -> int:
        return int(self.x)

    @property
    def iy(self) -> int:
        return int(self.y)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Switch  —  interruptor para puzzles
# ═══════════════════════════════════════════════════════════════
class Switch:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40) # Aumentado para facilitar hit
        self.active = False
        self.color = (255, 100, 100)

    def update(self, player, particles):
        # Hitbox de ativação generosa
        if not self.active and player.is_attacking and self.rect.colliderect(player.attack_rect):
            self.active = True
            self.color = (100, 255, 100)
            # Burst de partículas para feedback
            for _ in range(15):
                particles.append(Particle(self.rect.centerx, self.rect.centery, palette="soul"))
            return True
        return False

    def draw(self, surface, cam_x, cam_y):
        rx, ry = self.rect.x - cam_x, self.rect.y - cam_y
        pygame.draw.rect(surface, self.color, (rx, ry, 30, 30), border_radius=5)
        pygame.draw.rect(surface, C_WHITE, (rx, ry, 30, 30), 2, border_radius=5)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Gate  —  portão que abre com switch
# ═══════════════════════════════════════════════════════════════
class Gate:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.open = False
        self.y_start = y

    def update(self, is_active):
        if is_active and not self.open:
            self.rect.y -= 4 # Velocidade de abertura aumentada
            if self.rect.y < self.y_start - self.rect.h:
                self.open = True
        elif not is_active and self.open: # Reclose if needed? No, usually stay open.
            pass

    def draw(self, surface, cam_x, cam_y):
        rx, ry = self.rect.x - cam_x, self.rect.y - cam_y
        pygame.draw.rect(surface, (100, 100, 120), (rx, ry, self.rect.w, self.rect.h))
        for i in range(0, self.rect.h, 10):
            pygame.draw.line(surface, (50, 50, 60), (rx, ry + i), (rx + self.rect.w, ry + i), 2)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: MovingPlatform  —  plataforma móvel
# ═══════════════════════════════════════════════════════════════
class MovingPlatform:
    def __init__(self, x, y, w, h, dx, dy, speed=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.start_pos = pygame.Vector2(x, y)
        self.target_offset = pygame.Vector2(dx, dy)
        self.speed = speed
        self.timer = 0

    def update(self, player):
        self.timer += 0.02
        # Movimento senoidal suave
        offset = (math.sin(self.timer) + 1) / 2
        new_x = self.start_pos.x + self.target_offset.x * offset
        new_y = self.start_pos.y + self.target_offset.y * offset

        # Calcula vx/vy para carregar o player
        vx = new_x - self.rect.x
        vy = new_y - self.rect.y

        self.rect.x = int(new_x)
        self.rect.y = int(new_y)

        # Se o player estiver em cima, move ele junto
        # Aumentamos a margem de detecção para 4px para garantir o snap em descidas
        foot_rect = pygame.Rect(player.rect.x, player.rect.bottom, player.rect.w, 4)
        if foot_rect.colliderect(self.rect) and player.vy >= -1:
            player.rect.x += int(vx)
            player.rect.y = self.rect.top - player.rect.h
            player.on_ground = True
            player.vy = 0

    def draw(self, surface, cam_x, cam_y):
        rx, ry = self.rect.x - cam_x, self.rect.y - cam_y
        pygame.draw.rect(surface, (100, 150, 200), (rx, ry, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, C_WHITE, (rx, ry, self.rect.w, self.rect.h), 2)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: LevelGoal  —  objetivo final da fase
# ═══════════════════════════════════════════════════════════════
class LevelGoal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 80)
        self.timer = 0

    def update(self, player):
        self.timer += 1
        return self.rect.colliderect(player.rect)

    def draw(self, surface, cam_x, cam_y):
        rx, ry = self.rect.x - cam_x, self.rect.y - cam_y
        glow = int(120 + 40 * math.sin(self.timer * 0.1))
        draw_circle_alpha(surface, C_CHK_GLOW, (rx + 30, ry + 40), 40, glow // 2)
        pygame.draw.rect(surface, C_CHK_ON, (rx + 10, ry + 10, 40, 60), 3, border_radius=5)


# ═══════════════════════════════════════════════════════════════
#  CLASSE: HUD  —  interface do jogador (vida, etc.)
# ═══════════════════════════════════════════════════════════════
class HUD:
    """
    Heads-Up Display com:
    - Corações/almas de vida
    - Animação ao perder vida
    - Mensagens de checkpoint
    """
    def __init__(self):
        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_md = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_lg = pygame.font.SysFont("consolas", 48, bold=True)
        self.msg = ""
        self.msg_timer = 0
        self.shake = 0  # Pequeno shake da tela ao tomar dano

    def show_message(self, text: str, duration: int = 120):
        self.msg = text
        self.msg_timer = duration

    def update(self, player: Player):
        self.msg_timer = max(0, self.msg_timer - 1)
        self.shake = max(0, self.shake - 1)
        if player.flash_timer > 0:
            self.shake = 8

    def draw(self, surface, player: Player, debug: bool = False):
        # --- Vida (almas) ---
        soul_size = 22
        margin    = 14
        for i in range(player.max_hp):
            sx = margin + i * (soul_size + 6)
            sy = margin
            # Halo do slot
            draw_circle_alpha(surface, C_HP_BORDER, (sx + soul_size // 2, sy + soul_size // 2),
                              soul_size // 2 + 2, 90)
            # Fundo vazio
            pygame.draw.circle(surface, C_HP_EMPTY,
                               (sx + soul_size // 2, sy + soul_size // 2), soul_size // 2 - 1)
            # Preenchimento
            if i < player.hp:
                col = C_HP_FULL if player.hp > player.max_hp // 2 else (200, 140, 50)
                pygame.draw.circle(surface, col,
                                   (sx + soul_size // 2, sy + soul_size // 2), soul_size // 2 - 3)
                # Brilho interno
                draw_circle_alpha(surface, C_SOUL_B,
                                  (sx + soul_size // 2 - 2, sy + soul_size // 2 - 2), 4, 130)

        # --- Mensagem de centro ---
        if self.msg_timer > 0:
            alpha = min(255, self.msg_timer * 4)
            txt_surf = self.font_md.render(self.msg, True, C_CHK_ON)
            txt_surf.set_alpha(alpha)
            x = SCREEN_W // 2 - txt_surf.get_width() // 2
            surface.blit(txt_surf, (x, SCREEN_H - 80))

        # --- Debug info ---
        if debug:
            lines = [
                f"HP: {player.hp}/{player.max_hp}",
                f"VX: {player.vx:.1f}  VY: {player.vy:.1f}",
                f"Ground: {player.on_ground}",
                f"State: {'attacking' if player.is_attacking else 'hurt' if player.is_hurt else 'normal'}",
            ]
            for i, line in enumerate(lines):
                s = self.font_sm.render(line, True, (150, 150, 200))
                surface.blit(s, (10, SCREEN_H - 90 + i * 18))

    def draw_death_screen(self, surface):
        """Tela de morte semi-transparente."""
        draw_rect_alpha(surface, (0, 0, 0), (0, 0, SCREEN_W, SCREEN_H), 160)
        t1 = self.font_lg.render("VOCÊ CAIU", True, (200, 60, 80))
        t2 = self.font_md.render("Pressione R para renascer", True, C_UI_TEXT)
        surface.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 50))
        surface.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 + 20))

    def draw_start_screen(self, surface):
        """Tela de início do jogo."""
        draw_gradient_bg(surface, C_BG_TOP, C_BG_BOT, (0, 0, SCREEN_W, SCREEN_H))
        font_title = pygame.font.SysFont("consolas", 64, bold=True)
        font_sub   = pygame.font.SysFont("consolas", 20)

        t = pygame.time.get_ticks() / 1000
        glow_a = int(128 + 80 * math.sin(t * 1.5))

        title = font_title.render("SHADOWCROFT", True, C_UI_TITLE)
        draw_rect_alpha(surface, C_CHK_GLOW,
                        (SCREEN_W // 2 - title.get_width() // 2 - 10, SCREEN_H // 2 - 65,
                         title.get_width() + 20, 70), glow_a // 4)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))

        sub = font_sub.render("Explore as sombras. Domine o combate.", True, C_UI_TEXT)
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 30))

        btn_txt = font_sub.render("[ CLIQUE PARA COMEÇAR ]", True, C_SOUL_A)
        surface.blit(btn_txt, (SCREEN_W // 2 - btn_txt.get_width() // 2, SCREEN_H // 2 + 80))

    def draw_level_select(self, surface, unlocked, souls, health_upgrades):
        """Menu de seleção de fases e dificuldade. Retorna lista de (rect, action, value)."""
        draw_gradient_bg(surface, C_BG_TOP, C_BG_BOT, (0, 0, SCREEN_W, SCREEN_H))
        font_title = pygame.font.SysFont("consolas", 48, bold=True)
        font_md = pygame.font.SysFont("consolas", 24)
        clickables = []

        title = font_title.render("SELEÇÃO DE FASES", True, C_UI_TITLE)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        for i in range(1, 6):
            color = C_UI_TEXT if i <= unlocked else (100, 100, 100)
            status = "" if i <= unlocked else " [BLOQUEADO]"
            txt = font_md.render(f"Level {i}{status}", True, color)
            rx, ry = SCREEN_W // 2 - 100, 150 + i * 45
            surface.blit(txt, (rx, ry))
            if i <= unlocked:
                clickables.append((pygame.Rect(rx, ry, 200, 35), "level", i))

        souls_txt = font_md.render(f"Almas: {souls}", True, C_WHITE)
        surface.blit(souls_txt, (SCREEN_W // 2 - souls_txt.get_width() // 2, 420))

        cost = 30 + health_upgrades * 20
        upg_txt = font_md.render(f"[Upgrade Vida: {cost}]", True, (255, 200, 100))
        urx, ury = SCREEN_W // 2 - upg_txt.get_width() // 2, 460
        surface.blit(upg_txt, (urx, ury))
        clickables.append((pygame.Rect(urx, ury, upg_txt.get_width(), 35), "upgrade", cost))

        # Dificuldade
        dx_start = SCREEN_W // 2 - 250
        for i, (label, d_val, d_key) in enumerate([("Fácil", 0.5, "e"), ("Normal", 1.0, "n"), ("Difícil", 1.5, "h")]):
            d_txt = font_md.render(label, True, C_SOUL_A)
            drx, dry = dx_start + i * 180, 530
            surface.blit(d_txt, (drx, dry))
            clickables.append((pygame.Rect(drx, dry, 120, 35), "diff", d_val))

        hint = font_md.render("Clique para selecionar | ESC para Sair", True, (130, 120, 170))
        surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 630))
        return clickables


# ═══════════════════════════════════════════════════════════════
#  FUNÇÃO: build_level  —  constrói o mapa da fase
# ═══════════════════════════════════════════════════════════════
def build_level(level_id=1, difficulty=1.0):
    """
    Cria as plataformas, inimigos, checkpoints, orbes, objetivos e mecanismos.
    Retorna (platforms, enemies, checkpoints, orbs, goal, switches, gates, m_platforms, world_w, world_h).
    """
    platforms: List[Platform]   = []
    enemies:   List[Enemy]      = []
    checkpoints: List[Checkpoint] = []
    orbs: List[HealthOrb] = []
    switches: List[Switch] = []
    gates: List[Gate] = []
    m_platforms: List[MovingPlatform] = []

    world_w = 2000 + level_id * 800
    world_h = 800

    platforms.append(Platform(-40, 0, 40, world_h))
    platforms.append(Platform(world_w, 0, 40, world_h))
    platforms.append(Platform(0, 600, 400, 40))

    if level_id == 1:
        # Level 1: Introdução Suave
        platforms.append(Platform(450, 520, 200, 30))
        platforms.append(Platform(750, 480, 200, 30))
        enemies.append(Enemy(800, 440, max_hp=int(3*difficulty)))
        platforms.append(Platform(1050, 550, 250, 30))
        orbs.append(HealthOrb(1100, 480))
        platforms.append(Platform(1400, 580, world_w - 1400, 40))
        goal = LevelGoal(world_w - 120, 500)

    elif level_id == 2:
        # Level 2: Introdução a Moving Platforms
        m_platforms.append(MovingPlatform(450, 520, 120, 25, 200, 0))
        platforms.append(Platform(850, 450, 200, 30))
        enemies.append(ShootingEnemy(900, 400, max_hp=int(2*difficulty)))
        m_platforms.append(MovingPlatform(1150, 500, 120, 25, 0, -150))
        platforms.append(Platform(1350, 350, 250, 30, hazard=True))
        orbs.append(HealthOrb(1450, 280))
        platforms.append(Platform(1750, 550, world_w - 1750, 40))
        goal = LevelGoal(world_w - 150, 470)

    elif level_id == 3:
        # Level 3: Puzzle e Combate Ranged
        platforms.append(Platform(400, 600, 400, 40))
        switches.append(Switch(550, 560))
        gates.append(Gate(850, 360, 40, 240))

        platforms.append(Platform(400, 400, 250, 30))
        enemies.append(ShootingEnemy(450, 350, max_hp=int(3*difficulty)))

        platforms.append(Platform(1000, 550, 300, 30))
        m_platforms.append(MovingPlatform(1400, 450, 150, 25, 300, 0))

        platforms.append(Platform(1800, 350, 200, 30, hazard=True))
        orbs.append(HealthOrb(1850, 280))

        platforms.append(Platform(2100, 550, world_w - 2100, 40))
        goal = LevelGoal(world_w - 150, 470)

    elif level_id == 4:
        # Level 4: "Ascensão" (Desafio de pulo) - Mais plataformas para garantir alcance
        for i in range(14):
            px, py = 500 + i * 300, 550 - (i % 4) * 80
            platforms.append(Platform(px, py, 180, 30))
            if i % 3 == 0 and i > 0:
                enemies.append(ShootingEnemy(px + 40, py - 50, max_hp=int(4*difficulty)))
            if i < 13:
                # Spikes posicionados de forma mais clara
                platforms.append(Platform(px + 200, 650, 80, 20, hazard=True))
        platforms.append(Platform(world_w - 500, 500, 500, 40))
        goal = LevelGoal(world_w - 120, 420)

    else:
        # Level 5: Arena do Boss Final
        world_w = 3500 # Arena estendida
        platforms.append(Platform(400, 500, 300, 30))
        m_platforms.append(MovingPlatform(800, 450, 200, 25, 300, 0))
        platforms.append(Platform(1200, 550, 2000, 40)) # Chão da Arena
        enemies.append(Boss(2000, 450, max_hp=int(60*difficulty)))
        platforms.append(Platform(1500, 380, 200, 20))
        platforms.append(Platform(2500, 380, 200, 20))
        orbs.append(HealthOrb(1600, 320))
        orbs.append(HealthOrb(2600, 320))
        goal = LevelGoal(world_w - 150, 470)

    return platforms, enemies, checkpoints, orbs, goal, switches, gates, m_platforms, world_w, world_h


# ═══════════════════════════════════════════════════════════════
#  CLASSE: Game  —  loop principal do jogo
# ═══════════════════════════════════════════════════════════════
class Game:
    """
    Orquestra todos os sistemas:
    - Loop principal (update / draw)
    - Gerenciamento de estado (tela de início, jogando, morto)
    - Fundo parallax
    - Colisão jogador-inimigos
    """

    STATE_START   = "start"
    STATE_PLAYING = "playing"
    STATE_DEAD    = "dead"
    STATE_LEVEL_SELECT = "level_select"

    def __init__(self):
        self.state = self.STATE_START
        self.current_level = 1
        self.unlocked_levels = 1
        self.difficulty = 1.0  # 0.5 Easy, 1.0 Normal, 1.5 Hard
        self.souls = 0
        self.health_upgrades = 0
        self._init_game()
        self.hud = HUD()
        self.bg_surface = self._create_bg_surface()

    def _init_game(self):
        """(Re)inicializa todos os objetos do jogo."""
        (self.platforms, self.enemies, self.checkpoints, self.orbs,
         self.goal, self.switches, self.gates, self.m_platforms, self.world_w, self.world_h) = build_level(self.current_level, self.difficulty)
        self.player = Player(80, 520, max_hp=5 + self.health_upgrades)
        self.projectiles = []
        self.camera = Camera(self.world_w, self.world_h)
        self.camera.x = 0
        self.camera.y = 0
        self.global_timer = 0

    def _create_bg_surface(self) -> pygame.Surface:
        """Gera textura de fundo uma vez para performance."""
        bg = pygame.Surface((SCREEN_W, SCREEN_H))
        draw_gradient_bg(bg, C_BG_TOP, C_BG_BOT, (0, 0, SCREEN_W, SCREEN_H))

        # Estrelas / partículas de fundo
        random.seed(42)
        for _ in range(120):
            x = random.randint(0, SCREEN_W)
            y = random.randint(0, SCREEN_H)
            r = random.randint(1, 2)
            a = random.randint(40, 140)
            draw_circle_alpha(bg, (180, 170, 220), (x, y), r, a)
        random.seed()
        return bg

    # ── Atualização ───────────────────────────────────────────
    def update(self):
        self.global_timer += 1
        keys = pygame.key.get_pressed()

        if self.state == self.STATE_START:
            return

        if self.state == self.STATE_LEVEL_SELECT:
            return

        if self.state == self.STATE_DEAD:
            if keys[pygame.K_r]:
                self.player.respawn()
                self.state = self.STATE_PLAYING
                # Reinicia inimigos mortos
                for e in self.enemies:
                    if e.state == Enemy.DEAD:
                        e.__init__(e.patrol_center - e.patrol_range // 2,
                                   e.rect.y + e.rect.h // 2,
                                   e.patrol_range, e.max_hp)
            return

        # --- Estado: PLAYING ---
        self.player.handle_input(keys)
        self.player.apply_gravity()

        # Merge platforms and active gates
        active_colliders = self.platforms + [g for g in self.gates if not g.open]
        self.player.move_and_collide(active_colliders)

        # Plataformas Móveis (update após colisão para garantir estado on_ground)
        for mp in self.m_platforms:
            mp.update(self.player)

        # Hazard check (espinhos)
        for p in self.platforms:
            if p.hazard:
                # Cria uma hitbox ligeiramente deslocada para cima para pegar os espinhos visuais
                hazard_rect = pygame.Rect(p.rect.x, p.rect.y - 10, p.rect.w, 15)
                if self.player.rect.colliderect(hazard_rect):
                    self.player.take_damage(1, p.rect.centerx)
        self.player.update(self.platforms, self.checkpoints, self.enemies)

        # Projectiles
        for p in self.projectiles:
            p.update(self.player, self.platforms)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Switches and Gates
        switch_active = any(s.active for s in self.switches)
        for s in self.switches:
            s.update(self.player, self.player.particles)
        for g in self.gates:
            g.update(switch_active)

        # Goal
        if self.goal.update(self.player):
            if self.current_level < 5:
                # Burst de vitória
                for _ in range(20):
                    self.player.particles.append(Particle(self.player.rect.centerx, self.player.rect.centery, palette="soul"))
                self.unlocked_levels = max(self.unlocked_levels, self.current_level + 1)
                self.state = self.STATE_LEVEL_SELECT
                self.hud.show_message(f"Level {self.current_level} Completo!", 120)
            else:
                for _ in range(50):
                    self.player.particles.append(Particle(self.player.rect.centerx, self.player.rect.centery, palette="soul"))
                self.hud.show_message("PARABÉNS! JOGO CONCLUÍDO!", 300)
                self.state = self.STATE_LEVEL_SELECT

        # Morreu ao cair no abismo
        if self.player.rect.top > self.world_h + 100 and not self.player.is_dead:
            self.player._die()

        if self.player.is_dead and self.player.death_timer > 60:
            self.state = self.STATE_DEAD

        # Atualiza inimigos
        for e in self.enemies:
            # Inimigos também colidem com portões fechados
            enemy_colliders = self.platforms + [g for g in self.gates if not g.open]
            if isinstance(e, (ShootingEnemy, Boss)):
                e.update(enemy_colliders, self.player.rect, self.projectiles)
            else:
                e.update(enemy_colliders, self.player.rect)

        # Dano dos ataques do player nos inimigos
        if self.player.is_attacking and self.player.attack_rect.width > 0:
            for e in self.enemies:
                if e.state != Enemy.DEAD and self.player.attack_rect.colliderect(e.rect):
                    e.take_damage(1, self.player.facing)

        # Inimigos mortos (limpa após animação)
        self.enemies = [e for e in self.enemies if e.alive]

        # Checkpoints
        for chk in self.checkpoints:
            chk.update()

        # Health Orbs
        for orb in self.orbs:
            if orb.update(self.player):
                self.souls += 10
                self.hud.show_message("Vida restaurada! +10 Almas", 60)
        self.orbs = [o for o in self.orbs if not o.collected]

        # Câmera
        self.camera.follow(self.player.rect, smooth=0.12)

        # HUD
        self.hud.update(self.player)

    # ── Renderização ──────────────────────────────────────────
    def draw(self):
        cam_x = self.camera.ix
        cam_y = self.camera.iy

        # Screenshake
        if self.hud.shake > 0:
            cam_x += random.randint(-self.hud.shake, self.hud.shake)
            cam_y += random.randint(-self.hud.shake, self.hud.shake)

        # Tela de início
        if self.state == self.STATE_START:
            self.hud.draw_start_screen(screen)
            pygame.display.flip()
            return

        if self.state == self.STATE_LEVEL_SELECT:
            self.menu_clickables = self.hud.draw_level_select(screen, self.unlocked_levels, self.souls, self.health_upgrades)
            pygame.display.flip()
            return

        # Fundo (fixo — parallax suave)
        screen.blit(self.bg_surface, (0, 0))

        # Paralaxe leve (fundo move 20% da câmera)
        px_off = int(cam_x * 0.2) % SCREEN_W

        # Nebulosas de fundo (círculos grandes desfocados)
        for i, (bx, by, br, bc) in enumerate([
            (600,  300, 200, (30, 15, 60)),
            (1800, 200, 180, (10, 25, 55)),
            (3200, 350, 220, (25, 10, 55)),
        ]):
            sx = (bx - cam_x // 5) % (self.world_w + SCREEN_W) - 100
            sy = by - cam_y // 8
            draw_circle_alpha(screen, bc, (int(sx), int(sy)), br, 60)

        # Plataformas
        for p in self.platforms:
            p.draw(screen, cam_x, cam_y)

        # Goal
        self.goal.draw(screen, cam_x, cam_y)

        # Moving Platforms
        for mp in self.m_platforms:
            mp.draw(screen, cam_x, cam_y)

        # Switches and Gates
        for s in self.switches:
            s.draw(screen, cam_x, cam_y)
        for g in self.gates:
            g.draw(screen, cam_x, cam_y)

        # Checkpoints
        for chk in self.checkpoints:
            chk.draw(screen, cam_x, cam_y)

        # Health Orbs
        for orb in self.orbs:
            orb.draw(screen, cam_x, cam_y)

        # Inimigos
        for e in self.enemies:
            e.draw(screen, cam_x, cam_y)

        # Projectiles
        for p in self.projectiles:
            p.draw(screen, cam_x, cam_y)

        # Hitbox de ataque (debug opcional — comente para ocultar)
        # if self.player.is_attacking:
        #     pygame.draw.rect(screen, (255, 0, 0),
        #                      (self.player.attack_rect.x - cam_x,
        #                       self.player.attack_rect.y - cam_y,
        #                       self.player.attack_rect.w,
        #                       self.player.attack_rect.h), 1)

        # Player
        self.player.draw(screen, cam_x, cam_y)

        # HUD
        self.hud.draw(screen, self.player)

        # Tela de morte
        if self.state == self.STATE_DEAD:
            self.hud.draw_death_screen(screen)

        # Vinheta nas bordas (efeito cinematográfico)
        self._draw_vignette()

        pygame.display.flip()

    def _draw_vignette(self):
        """Vinheta escura nas bordas da tela."""
        for i, alpha in [(60, 80), (30, 50), (15, 30)]:
            draw_rect_alpha(screen, C_BG_TOP, (0, 0, i, SCREEN_H), alpha)
            draw_rect_alpha(screen, C_BG_TOP, (SCREEN_W - i, 0, i, SCREEN_H), alpha)
            draw_rect_alpha(screen, C_BG_TOP, (0, 0, SCREEN_W, i), alpha)
            draw_rect_alpha(screen, C_BG_TOP, (0, SCREEN_H - i, SCREEN_W, i), alpha)

    # ── Loop principal ────────────────────────────────────────
    def run(self):
        running = True
        self.menu_clickables = []
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.state == self.STATE_START:
                        self.state = self.STATE_LEVEL_SELECT
                    elif self.state == self.STATE_LEVEL_SELECT:
                        for rect, action, val in self.menu_clickables:
                            if rect.collidepoint(mx, my):
                                if action == "level":
                                    self.current_level = val
                                    self._init_game()
                                    self.state = self.STATE_PLAYING
                                elif action == "diff":
                                    self.difficulty = val
                                    self.hud.show_message(f"Dificuldade Alterada", 60)
                                elif action == "upgrade":
                                    if self.souls >= val:
                                        self.souls -= val
                                        self.health_upgrades += 1
                                        self.player.max_hp += 1
                                        self.player.hp = self.player.max_hp
                                        self.hud.show_message(f"HP Max UP!", 80)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == self.STATE_PLAYING:
                            self.state = self.STATE_LEVEL_SELECT
                        else:
                            running = False

                    if self.state == self.STATE_START:
                        self.state = self.STATE_LEVEL_SELECT

                    elif self.state == self.STATE_LEVEL_SELECT:
                        if pygame.K_1 <= event.key <= pygame.K_5:
                            lv = event.key - pygame.K_1 + 1
                            if lv <= self.unlocked_levels:
                                self.current_level = lv
                                self._init_game()
                                self.state = self.STATE_PLAYING
                        if event.key == pygame.K_e:
                            self.difficulty = 0.5
                            self.hud.show_message("Dificuldade: Fácil", 60)
                        if event.key == pygame.K_n:
                            self.difficulty = 1.0
                            self.hud.show_message("Dificuldade: Normal", 60)
                        if event.key == pygame.K_h:
                            self.difficulty = 1.5
                            self.hud.show_message("Dificuldade: Difícil", 60)
                        if event.key == pygame.K_u:
                            cost = 30 + self.health_upgrades * 20
                            if self.souls >= cost:
                                self.souls -= cost
                                self.health_upgrades += 1
                                self.player.max_hp += 1
                                self.player.hp = self.player.max_hp
                                self.hud.show_message(f"Upgrade! Max HP: {self.player.max_hp}", 80)
                            else:
                                self.hud.show_message(f"Almas insuficientes ({cost})", 60)

            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()
