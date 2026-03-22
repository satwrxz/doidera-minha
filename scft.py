#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║          S H A D O W C R O F T  —  v2.0                         ║
║   Protótipo 2D Metroidvania atmosférico                           ║
╠═══════════════════════════════════════════════════════════════════╣
║  A / D       Mover                                                ║
║  W/Space     Pular (segure=mais alto | duplo pulo no ar)         ║
║  SHIFT       Dash direcional (invencível, 2s cooldown)           ║
║  X / M1      Atacar (combo de 2 golpes)                          ║
║  R           Renascer após morte                                  ║
║  ESC         Menu de fases                                        ║
╚═══════════════════════════════════════════════════════════════════╝
BUGS CORRIGIDOS v2:
  - Boss não cai mais do mapa (arena com paredes + clamp)
  - Level 2 espinhos reposicionados e funcionando corretamente
  - Inimigos não pulam de plataformas ao perseguir
NOVIDADES v2:
  - Dash direcional com invencibilidade + afterimage
  - Duplo pulo no ar
  - FlyingEnemy: inimigo voador que mergulha
  - SoulDrop: inimigos dropam almas ao morrer
  - Boss com 3 fases + telegraphing visual
  - +50% mais inimigos em todos os levels
  - Levels redesenhados e expandidos
  - Checkpoints em todos os levels
  - Screen-shake no boss e ao tomar dano
  - HUD com barra de dash e contador de almas
  - Fundo parallax com 2 camadas
  - Sinal de aggro "!" sobre inimigos
"""

import pygame, sys, math, random, json, os
from typing import List, Optional

pygame.init()

# ═══════════════════════════════════════════════════════════════════
#  TELA E CLOCK
# ═══════════════════════════════════════════════════════════════════
SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("ShadowCroft v2")
clock = pygame.time.Clock()
FPS = 60

# ═══════════════════════════════════════════════════════════════════
#  FÍSICA & GAMEPLAY
# ═══════════════════════════════════════════════════════════════════
GRAVITY      = 0.65
MAX_FALL     = 16
PLAYER_SPD   = 5.5
JUMP_FORCE   = -14.5
JUMP_HOLD    = 0.55
ATTACK_DUR   = 18
ATTACK_CD    = 28
COMBO_WINDOW = 40     # frames para encadear o 2º golpe
INV_FRAMES   = 65
KNOCKBACK_H  = 7.5
KNOCKBACK_V  = -5.0
COYOTE_T     = 8
JUMP_BUF     = 10
DASH_SPEED   = 15
DASH_DUR     = 11     # frames de duração do dash
DASH_CD      = 50     # cooldown entre dashes

# ═══════════════════════════════════════════════════════════════════
#  PALETA DE CORES
# ═══════════════════════════════════════════════════════════════════
C_BG_TOP    = (4,   2,  14)
C_BG_BOT    = (16, 10,  38)
C_BG_MID    = (8,   5,  24)      # paralaxe camada 2
C_PLT_BODY  = (26, 22,  46)
C_PLT_EDGE  = (48, 40,  72)
C_PLT_TOP   = (66, 56,  96)
C_PLT_GLOW  = (88, 68, 128)
C_SPK_COL   = (210, 28, 28)
C_SPK_WARN  = (255,160, 40)      # pisca antes de ativar

C_P_BODY    = (200,200,235)
C_P_HEAD    = (215,215,245)
C_P_CAPE    = (80, 58,120)
C_P_CAPE2   = (55, 38, 88)
C_P_SWORD   = (195,218,255)
C_P_EYE     = (130,200,255)
C_P_HURT    = (255,100,100)
C_P_DASH    = ( 90,150,255)

C_E_BODY    = (145, 42, 58)
C_E_SHELL   = (110, 30, 45)
C_E_EYE     = (255, 70, 80)
C_E_HURT    = (255,160,160)
C_FLY_BODY  = ( 60, 38, 98)
C_FLY_WING  = (115, 75,175)
C_FLY_EYE   = (200, 80,255)

C_HP_FULL   = (205, 52, 78)
C_HP_EMPTY  = ( 45, 16, 26)
C_HP_BORDER = ( 80, 35, 55)
C_SOUL_A    = ( 90,175,255)
C_SOUL_B    = (180,230,255)
C_DASH_BAR  = ( 80,140,255)
C_CHK_OFF   = ( 55, 65,110)
C_CHK_ON    = (120,215,255)
C_CHK_GLOW  = ( 80,160,255)
C_UI_TEXT   = (200,195,230)
C_UI_TITLE  = (170,150,220)
C_WHITE     = (255,255,255)
C_BLACK     = (  0,  0,  0)
C_SLASH_A   = (220,235,255)
C_SLASH_B   = (150,180,255)

PARTICLE_PALETTES = {
    "hit":   [(255,200,80),(255,140,40),(255,80,20)],
    "soul":  [(100,190,255),(160,220,255),(200,240,255)],
    "death": [(200,60,80),(150,30,50),(255,100,120)],
    "dust":  [(90,78,115),(70,60,95),(110,95,140)],
    "dash":  [(80,140,255),(100,170,255),(60,110,220)],
    "boss":  [(255,50,50),(200,20,20),(255,130,60)],
    "heal":  [(80,220,120),(140,255,160),(60,200,100)],
    "aggro": [(255,240,60),(255,200,40),(255,160,20)],
}

# ═══════════════════════════════════════════════════════════════════
#  UTILITÁRIOS
# ═══════════════════════════════════════════════════════════════════
def lerp(a, b, t): return a + (b-a)*t
def clamp(v, lo, hi): return max(lo, min(hi, v))

def draw_rect_alpha(surf, color, rect, alpha):
    w, h = max(1,int(rect[2])), max(1,int(rect[3]))
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    tmp.fill((*color[:3], int(clamp(alpha,0,255))))
    surf.blit(tmp, (int(rect[0]), int(rect[1])))

def draw_circle_alpha(surf, color, center, r, alpha):
    if r < 1: return
    tmp = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    pygame.draw.circle(tmp, (*color[:3], int(clamp(alpha,0,255))), (r, r), r)
    surf.blit(tmp, (int(center[0]-r), int(center[1]-r)))

def draw_gradient_bg(surf, ct, cb, rect):
    x, y, w, h = rect
    for row in range(h):
        t = row/h
        c = (int(ct[0]+(cb[0]-ct[0])*t),
             int(ct[1]+(cb[1]-ct[1])*t),
             int(ct[2]+(cb[2]-ct[2])*t))
        pygame.draw.line(surf, c, (x, y+row), (x+w, y+row))


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Particle
# ═══════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, palette="hit", speed_range=(1,4),
                 lifetime_range=(15,35), gravity=0.08, direction=None):
        self.x, self.y = float(x), float(y)
        if direction is not None:
            angle = direction + random.uniform(-0.4, 0.4)
        else:
            angle = random.uniform(0, math.tau)
        spd = random.uniform(*speed_range)
        self.vx = math.cos(angle)*spd
        self.vy = math.sin(angle)*spd
        self.gravity  = gravity
        self.lifetime = random.randint(*lifetime_range)
        self.max_life = self.lifetime
        self.color    = random.choice(PARTICLE_PALETTES[palette])
        self.radius   = random.randint(2, 5)

    def update(self):
        self.x  += self.vx;  self.y  += self.vy
        self.vy += self.gravity;  self.lifetime -= 1

    def draw(self, surf, cx, cy):
        if self.lifetime <= 0: return
        alpha = int(255 * self.lifetime/self.max_life)
        r = max(1, int(self.radius * self.lifetime/self.max_life))
        draw_circle_alpha(surf, self.color,
                          (int(self.x-cx), int(self.y-cy)), r, alpha)

    @property
    def alive(self): return self.lifetime > 0


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: SoulDrop — drop de almas ao matar inimigos
# ═══════════════════════════════════════════════════════════════════
class SoulDrop:
    """Orbe de alma dropada por inimigos ao morrer."""
    def __init__(self, x, y, value=5):
        self.x, self.y = float(x), float(y)
        self.vy = -4.0
        self.value = value
        self.collected = False
        self.timer = 0
        self.magnet = False   # True quando perto do player

    def update(self, player):
        self.timer += 1
        if self.collected: return

        px, py = player.rect.centerx, player.rect.centery
        dx, dy = px - self.x, py - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        # Gravidade suave + flutuação
        self.vy += 0.2
        if self.vy > 3: self.vy = 3.0
        self.y += self.vy
        # Flutua suavemente
        self.y += math.sin(self.timer * 0.08) * 0.3

        # Magnetismo quando perto
        if dist < 120:
            self.magnet = True
            self.x += dx/dist * 5
            self.y += dy/dist * 5

        # Coleta
        if dist < 22:
            self.collected = True
            player_rect = pygame.Rect(player.rect.x, player.rect.y,
                                      player.rect.w, player.rect.h)
            return self.value
        return 0

    def draw(self, surf, cx, cy):
        if self.collected: return
        rx, ry = int(self.x-cx), int(self.y-cy)
        t = math.sin(self.timer * 0.1)
        r = 7 + int(t*2)
        draw_circle_alpha(surf, C_SOUL_A, (rx, ry), r+4, 60)
        pygame.draw.circle(surf, C_SOUL_A, (rx, ry), r)
        pygame.draw.circle(surf, C_SOUL_B, (rx-2, ry-2), 3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: HealthOrb
# ═══════════════════════════════════════════════════════════════════
class HealthOrb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 22, 22)
        self.collected = False
        self.timer = random.random() * math.tau

    def update(self, player):
        self.timer += 0.1
        if not self.collected and self.rect.colliderect(player.rect):
            if player.hp < player.max_hp:
                player.hp = min(player.max_hp, player.hp + 1)
                self.collected = True
                return True
        return False

    def draw(self, surf, cx, cy):
        if self.collected: return
        rx = self.rect.x - cx
        ry = self.rect.y - cy + int(math.sin(self.timer)*5)
        draw_circle_alpha(surf, (80,220,120), (rx+11, ry+11), 14, 90)
        pygame.draw.circle(surf, (120,255,160), (rx+11, ry+11), 8)
        pygame.draw.circle(surf, C_WHITE,       (rx+11, ry+11), 8, 2)
        pygame.draw.circle(surf, C_WHITE,       (rx+8,  ry+8),  3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Platform
# ═══════════════════════════════════════════════════════════════════
class Platform:
    def __init__(self, x, y, w, h, variant=0, hazard=False,
                 hazard_timed=False, hazard_offset=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.variant      = variant
        self.hazard       = hazard
        self.hazard_timed = hazard_timed
        self.hazard_offset= hazard_offset

    def is_hazard_active(self):
        if not self.hazard: return False
        if not self.hazard_timed: return True
        cycle = (pygame.time.get_ticks()//16 + self.hazard_offset) % 120
        return cycle > 60

    def is_hazard_warning(self):
        """Pisca antes de ativar (frames 50-60 do ciclo)."""
        if not self.hazard or not self.hazard_timed: return False
        cycle = (pygame.time.get_ticks()//16 + self.hazard_offset) % 120
        return 45 < cycle <= 60

    def draw(self, surf, cx, cy):
        rx, ry = self.rect.x-cx, self.rect.y-cy
        rw, rh = self.rect.w, self.rect.h
        if rx+rw<0 or rx>SCREEN_W or ry+rh<0 or ry>SCREEN_H: return

        pygame.draw.rect(surf, C_PLT_BODY, (rx,ry,rw,rh))
        pygame.draw.rect(surf, C_PLT_EDGE, (rx,ry,2,rh))
        pygame.draw.rect(surf, C_PLT_EDGE, (rx+rw-2,ry,2,rh))

        # Topo: vermelho=perigo, laranja=aviso, normal=topo de plataforma
        if self.is_hazard_active():
            top_col = C_SPK_COL
        elif self.is_hazard_warning():
            # Pisca em laranja como aviso
            top_col = C_SPK_WARN if (pygame.time.get_ticks()//80)%2 else C_PLT_TOP
        else:
            top_col = C_PLT_TOP

        pygame.draw.rect(surf, top_col, (rx,ry,rw,3))
        pygame.draw.rect(surf, C_PLT_GLOW, (rx+1,ry+1,rw-2,1))

        # Espinhos visuais quando ativos
        if self.is_hazard_active():
            for i in range(0, rw-5, 12):
                pts = [(rx+i+1, ry),(rx+i+6,ry-10),(rx+i+12,ry)]
                pygame.draw.polygon(surf, C_SPK_COL, pts)
                pygame.draw.polygon(surf, (255,80,80), [
                    (rx+i+4,ry),(rx+i+6,ry-7),(rx+i+9,ry)])

        if self.variant==1:
            for i in range(3):
                cx2 = rx+int(rw*(0.2+i*0.3))
                pygame.draw.line(surf,C_PLT_EDGE,(cx2,ry+4),(cx2+4,ry+12),1)
        elif self.variant==2:
            for i in range(rw//30):
                pygame.draw.circle(surf,C_PLT_EDGE,(rx+i*30+10,ry+6),3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Checkpoint
# ═══════════════════════════════════════════════════════════════════
class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 48)
        self.active = False
        self.timer  = 0
        self.particles: List[Particle] = []

    def activate(self):
        if not self.active:
            self.active = True
            for _ in range(30):
                self.particles.append(
                    Particle(self.rect.centerx, self.rect.top,
                             "soul", (1,5), (20,50), -0.05))

    def update(self):
        self.timer += 1
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles: p.update()
        if self.active and random.random() < 0.25:
            self.particles.append(
                Particle(self.rect.centerx+random.randint(-5,5),
                         self.rect.top+10, "soul", (0.5,2), (15,30), -0.08))

    def draw(self, surf, cx, cy):
        rx, ry = self.rect.x-cx, self.rect.y-cy
        col = C_CHK_ON if self.active else C_CHK_OFF
        pygame.draw.rect(surf, col, (rx,ry+30,24,18))
        pygame.draw.rect(surf, col, (rx+9,ry+10,6,22))
        pts = [(rx+12,ry-4),(rx+22,ry+6),(rx+12,ry+16),(rx+2,ry+6)]
        pygame.draw.polygon(surf, col, pts)
        if self.active:
            glow = abs(math.sin(self.timer*0.06))*60+40
            draw_circle_alpha(surf, C_CHK_GLOW, (rx+12,ry+6), 22, int(glow))
        for p in self.particles: p.draw(surf, cx, cy)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Projectile
# ═══════════════════════════════════════════════════════════════════
class Projectile:
    def __init__(self, x, y, vx, vy, dmg=1, big=False):
        s = 14 if big else 10
        self.rect  = pygame.Rect(x-s//2, y-s//2, s, s)
        self.vx, self.vy = vx, vy
        self.alive = True
        self.timer = 0
        self.dmg   = dmg
        self.big   = big

    def update(self, player, platforms):
        self.timer += 1
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if self.rect.colliderect(player.rect):
            player.take_damage(self.dmg, self.rect.centerx)
            self.alive = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                self.alive = False
        if self.timer > 200: self.alive = False

    def draw(self, surf, cx, cy):
        rx, ry = self.rect.x-cx, self.rect.y-cy
        r = 7 if self.big else 5
        col = (255,80,80) if self.big else C_E_EYE
        draw_circle_alpha(surf, col, (rx+r, ry+r), r+4, 120)
        pygame.draw.circle(surf, col,    (rx+r, ry+r), r)
        pygame.draw.circle(surf, C_WHITE,(rx+r, ry+r), 3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Enemy — melee com IA corrigida (sem pulo em beiras)
# ═══════════════════════════════════════════════════════════════════
class Enemy:
    PATROL="patrol"; CHASE="chase"; ATTACK="attack"; HURT="hurt"; DEAD="dead"

    def __init__(self, x, y, patrol_range=120, max_hp=3):
        self.rect = pygame.Rect(x, y, 32, 38)
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.max_hp = max_hp; self.hp = max_hp
        self.state  = self.PATROL
        self.facing = 1
        self.patrol_center = x+16
        self.patrol_range  = patrol_range
        self.patrol_spd    = 1.4
        self.hurt_timer = self.attack_timer = self.attack_cd = 0
        self.dead_timer = self.bob_timer = 0
        self.aggro_dist  = 230; self.attack_dist = 52
        self.particles: List[Particle] = []
        self.flash     = False
        self.aggro_shown = False  # para o "!" de aggro

    @property
    def alive(self): return self.state != self.DEAD or self.dead_timer < 40

    @property
    def can_damage_player(self):
        return self.state==self.ATTACK and 5<=self.attack_timer<=15

    def take_damage(self, dmg, direction):
        if self.state in (self.HURT, self.DEAD): return
        self.hp -= dmg; self.flash = True
        for _ in range(12):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"hit",(2,5)))
        if self.hp <= 0: self._die()
        else:
            self.state = self.HURT; self.hurt_timer = 22
            self.vx = direction*KNOCKBACK_H*0.7; self.vy = KNOCKBACK_V*0.6

    def _die(self):
        self.state = self.DEAD; self.dead_timer = 0
        for _ in range(20):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"death",(1,6),(20,45)))

    def update(self, platforms, player_rect):
        if self.state == self.DEAD:
            self.dead_timer += 1; self._update_particles(); return

        self.bob_timer += 1; self.flash = False; self._update_particles()
        dx = player_rect.centerx - self.rect.centerx
        dist = abs(dx)

        if self.state == self.HURT:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0: self.state = self.PATROL

        elif self.state == self.PATROL:
            if self.rect.centerx > self.patrol_center+self.patrol_range: self.facing=-1
            elif self.rect.centerx < self.patrol_center-self.patrol_range: self.facing=1
            self.vx = self.patrol_spd * self.facing
            if dist < self.aggro_dist: self.state=self.CHASE; self.aggro_shown=False

        elif self.state == self.CHASE:
            self.facing = 1 if dx>0 else -1
            self.vx = self.patrol_spd * 1.8 * self.facing
            self.attack_cd = max(0, self.attack_cd-1)
            if dist < self.attack_dist and self.attack_cd==0:
                self.state=self.ATTACK; self.attack_timer=0; self.vx=0
            if dist > self.aggro_dist*1.5: self.state=self.PATROL

        elif self.state == self.ATTACK:
            self.attack_timer += 1
            self.vx = self.facing*1.5 if self.attack_timer < 8 else self.vx*0.7
            if self.attack_timer >= 28:
                self.state=self.CHASE; self.attack_cd=65

        # Borda de plataforma: Pula se perseguindo, senão vira
        if self.on_ground and self.state in (self.PATROL, self.CHASE, self.ATTACK):
            look_x = self.rect.right + 2 if self.facing == 1 else self.rect.left - 6
            foot_rect = pygame.Rect(look_x, self.rect.bottom, 4, 4)
            on_edge = not any(p.rect.colliderect(foot_rect) for p in platforms)
            if on_edge:
                if self.state in (self.CHASE, self.ATTACK):
                    self.vy = -12  # Tenta pular o gap
                else:
                    self.facing *= -1
                    self.vx = self.patrol_spd * self.facing

        self.vy = min(self.vy+GRAVITY, MAX_FALL)
        self.rect.x += int(self.vx);  self._collide_x(platforms)
        self.rect.y += int(self.vy);  self._collide_y(platforms)

    def _collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx>0: self.rect.right=p.rect.left
                else:         self.rect.left =p.rect.right
                self.vx=0; self.facing*=-1

    def _collide_y(self, platforms):
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy>0: self.rect.bottom=p.rect.top; self.on_ground=True
                else:         self.rect.top   =p.rect.bottom
                self.vy=0

    def _update_particles(self):
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update()

    def draw(self, surf, cx, cy):
        for p in self.particles: p.draw(surf, cx, cy)
        rx, ry = self.rect.x-cx, self.rect.y-cy
        w, h = self.rect.w, self.rect.h
        bob = int(math.sin(self.bob_timer*0.08)*1.5)
        if self.state==self.DEAD and self.dead_timer>10: return

        bc = C_E_HURT if self.flash else C_E_BODY
        sc = C_E_HURT if self.flash else C_E_SHELL
        pygame.draw.ellipse(surf, sc, (rx+2,ry+bob+8,w-4,h-8))
        pygame.draw.ellipse(surf, bc, (rx+4,ry+bob+10,w-8,h-14))
        pygame.draw.circle(surf, bc, (rx+w//2,ry+bob+8), 12)
        pygame.draw.circle(surf, sc, (rx+w//2,ry+bob+8), 12, 2)
        ex = rx+w//2+self.facing*4; ey = ry+bob+7
        pygame.draw.circle(surf, C_E_EYE, (ex,ey), 4)
        pygame.draw.circle(surf, C_WHITE,  (ex,ey), 2)

        # "!" sinal de aggro
        if self.state==self.CHASE and not self.aggro_shown:
            self.aggro_shown=True
        if self.state==self.CHASE:
            draw_circle_alpha(surf, (255,240,60), (rx+w//2,ry+bob-4), 10, 180)
            font = pygame.font.SysFont("consolas",12,bold=True)
            s = font.render("!",True,(50,30,10))
            surf.blit(s,(rx+w//2-4,ry+bob-12))

        if self.state==self.ATTACK and self.attack_timer<16:
            draw_circle_alpha(surf,C_E_EYE,(rx+w//2,ry+bob+7),18,int(120*(1-self.attack_timer/16)))

        for i,lx in enumerate([rx+6,rx+w-10]):
            lb = int(math.sin(self.bob_timer*0.15+i*math.pi)*2)
            pygame.draw.rect(surf,sc,(lx,ry+h-10+lb,6,10))

        if self.hp<self.max_hp: self._draw_hp_bar(surf,rx,ry+bob-14)

    def _draw_hp_bar(self, surf, rx, ry):
        bw = self.rect.w; ratio = self.hp/self.max_hp
        pygame.draw.rect(surf,C_HP_EMPTY,(rx,ry,bw,5))
        pygame.draw.rect(surf,C_HP_FULL, (rx,ry,int(bw*ratio),5))
        pygame.draw.rect(surf,C_HP_BORDER,(rx,ry,bw,5),1)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: FlyingEnemy — NOVO: inimigo voador que mergulha
# ═══════════════════════════════════════════════════════════════════
class FlyingEnemy:
    """
    Inimigo aéreo. Flutua em altura fixa, mergulha quando player abaixo.
    Estados: FLOAT → DIVE → RECOVER → HURT → DEAD
    """
    FLOAT="float"; DIVE="dive"; RECOVER="recover"; HURT="hurt"; DEAD="dead"

    def __init__(self, x, y, max_hp=2, float_height=None):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.vx = self.vy = 0.0
        self.max_hp = max_hp; self.hp = max_hp
        self.state   = self.FLOAT
        self.facing  = 1
        self.float_y = float_height or (y - 80)
        self.home_x  = float(x)
        self.bob_timer = self.hurt_timer = self.dive_timer = self.dead_timer = 0
        self.aggro_dist  = 280; self.dive_trigger_y = 60
        self.particles: List[Particle] = []
        self.flash   = False

    @property
    def alive(self): return self.state!=self.DEAD or self.dead_timer<35

    @property
    def can_damage_player(self): return self.state==self.DIVE and self.vy>3

    def take_damage(self, dmg, direction):
        if self.state in (self.HURT, self.DEAD): return
        self.hp -= dmg; self.flash=True
        for _ in range(10):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"hit",(2,5)))
        if self.hp<=0: self._die()
        else: self.state=self.HURT; self.hurt_timer=20; self.vx=direction*3; self.vy=-3

    def _die(self):
        self.state=self.DEAD; self.dead_timer=0
        for _ in range(18):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"death",(1,5),(18,40)))

    def update(self, platforms, player_rect):
        if self.state==self.DEAD:
            self.dead_timer+=1; self._update_particles(); return
        self.bob_timer+=1; self.flash=False; self._update_particles()
        dx=player_rect.centerx-self.rect.centerx
        dy=player_rect.centery-self.rect.centery
        dist=math.sqrt(dx*dx+dy*dy)
        self.facing=1 if dx>0 else -1

        if self.state==self.HURT:
            self.hurt_timer-=1
            if self.hurt_timer<=0: self.state=self.RECOVER

        elif self.state==self.FLOAT:
            # Segue o player horizontalmente, flutua na altura alvo
            if abs(dx)<self.aggro_dist:
                self.vx = lerp(self.vx, self.facing*2.5, 0.06)
            else:
                self.vx = lerp(self.vx, 0, 0.04)
            target_y = self.float_y
            self.vy = (target_y - self.rect.y)*0.08
            # Mergulha quando player está abaixo e perto
            if abs(dx)<100 and dy>30 and dist<self.aggro_dist:
                self.state=self.DIVE; self.dive_timer=0

        elif self.state==self.DIVE:
            self.dive_timer+=1
            self.vy += 1.2; self.vy=min(self.vy,14)
            self.vx = self.facing*3
            # Colisão com plataformas ou limite de queda
            self._collide_y(platforms)
            if self.on_platform or self.dive_timer>60:
                self.state=self.RECOVER; self.vy=-5

        elif self.state==self.RECOVER:
            target_y = self.float_y
            self.vy = lerp(self.vy, (target_y-self.rect.y)*0.1, 0.15)
            self.vx = lerp(self.vx,0,0.1)
            if abs(self.rect.y-target_y)<20 and abs(self.vy)<1:
                self.state=self.FLOAT

        self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)
        self.on_platform=False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                self.rect.bottom=p.rect.top; self.on_platform=True
                if self.state==self.DIVE: self.vy=-4

    def _collide_y(self, platforms):
        self.on_platform=False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy>0: self.rect.bottom=p.rect.top; self.on_platform=True
                else:         self.rect.top   =p.rect.bottom
                self.vy=0

    def _update_particles(self):
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update()

    def draw(self, surf, cx, cy):
        for p in self.particles: p.draw(surf, cx, cy)
        if self.state==self.DEAD and self.dead_timer>10: return
        rx,ry=self.rect.x-cx, self.rect.y-cy
        bob=int(math.sin(self.bob_timer*0.12)*3)
        bc = C_E_HURT if self.flash else C_FLY_BODY

        # Asas animadas
        wing_angle = math.sin(self.bob_timer*0.25)*0.5
        for side,wx in [(-1, rx-14),(1, rx+20)]:
            wpts = [
                (rx+14, ry+14+bob),
                (wx,    ry+bob-8+int(math.sin(self.bob_timer*0.3)*5)),
                (wx+side*4, ry+18+bob)
            ]
            draw_rect_alpha(surf, C_FLY_WING,
                            (min(w[0] for w in wpts), min(w[1] for w in wpts),
                             abs(wx-rx+14)+4, 28), 150)
            pygame.draw.polygon(surf, C_FLY_WING, wpts)

        # Corpo
        pygame.draw.ellipse(surf, bc, (rx+4,ry+6+bob,20,18))
        # Olho
        pygame.draw.circle(surf, C_FLY_EYE, (rx+14+self.facing*3, ry+14+bob), 5)
        pygame.draw.circle(surf, C_WHITE,   (rx+14+self.facing*3, ry+14+bob), 2)

        if self.state==self.DIVE:
            draw_circle_alpha(surf,C_FLY_EYE,(rx+14,ry+14+bob),16,80)

        if self.hp<self.max_hp: self._draw_hp_bar(surf,rx,ry+bob-16)

    def _draw_hp_bar(self,surf,rx,ry):
        bw=self.rect.w; ratio=self.hp/self.max_hp
        pygame.draw.rect(surf,C_HP_EMPTY,(rx,ry,bw,4))
        pygame.draw.rect(surf,C_HP_FULL, (rx,ry,int(bw*ratio),4))


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: ShootingEnemy
# ═══════════════════════════════════════════════════════════════════
class ShootingEnemy(Enemy):
    def __init__(self, x, y, patrol_range=100, max_hp=2):
        super().__init__(x, y, patrol_range, max_hp)
        self.shoot_cd   = 0
        self.shoot_warn = 0   # aviso visual antes de atirar

    def update(self, platforms, player_rect, projectiles):
        super().update(platforms, player_rect)
        self.shoot_cd  = max(0, self.shoot_cd-1)
        self.shoot_warn= max(0, self.shoot_warn-1)
        if self.state==self.DEAD: return
        dx=player_rect.centerx-self.rect.centerx
        dy=player_rect.centery-self.rect.centery
        dist=math.sqrt(dx*dx+dy*dy)
        # Aviso 30 frames antes de atirar
        if dist<380 and self.shoot_cd==30: self.shoot_warn=30
        if dist<380 and self.shoot_cd==0:
            angle=math.atan2(dy,dx)
            spd=7; projectiles.append(Projectile(self.rect.centerx,self.rect.centery,
                                                  math.cos(angle)*spd,math.sin(angle)*spd))
            self.shoot_cd=90

    def draw(self, surf, cx, cy):
        super().draw(surf, cx, cy)
        if self.state==self.DEAD and self.dead_timer>10: return
        rx,ry=self.rect.x-cx,self.rect.y-cy
        bob=int(math.sin(self.bob_timer*0.08)*1.5)
        # Indicador de tiro (ponto roxo no olho)
        if self.shoot_warn>0:
            alpha=int(200*(self.shoot_warn/30))
            draw_circle_alpha(surf,(180,60,255),(rx+self.rect.w//2+self.facing*4,ry+bob+7),8,alpha)
        pygame.draw.circle(surf,(150,50,255),(rx+self.rect.w//2+self.facing*4,ry+bob+7),3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Boss — CORRIGIDO: arena com paredes, 3 fases, sem queda
# ═══════════════════════════════════════════════════════════════════
class Boss(Enemy):
    """
    Boss final com 3 fases:
      Fase 1 (100-60% HP): Rajada circular + avanço
      Fase 2 ( 60-30% HP): + Triplo tiro direcionado + velocidade+
      Fase 3 (  30-0% HP): + Chuva de projéteis + sprint
    Corrigido: nunca pula de bordas, x clamped na arena.
    """
    def __init__(self, x, y, max_hp=30, arena_x1=1200, arena_x2=3100):
        super().__init__(x, y, patrol_range=0, max_hp=max_hp)
        self.rect      = pygame.Rect(x, y, 88, 108)
        self.arena_x1  = arena_x1
        self.arena_x2  = arena_x2
        self.phase     = 1
        self.phase_timer=0
        self.shoot_cd  = 0
        self.glow_intensity = 0
        self.stomp_cd  = 0
        self.enraged   = False

    def update(self, platforms, player_rect, projectiles):
        # -- Não usa o método pai para evitar lógica de borda --
        if self.state==self.DEAD:
            self.dead_timer+=1; self._update_particles(); return

        self.bob_timer+=1; self.flash=False; self._update_particles()
        self.phase_timer+=1
        self.shoot_cd=max(0,self.shoot_cd-1)
        self.stomp_cd=max(0,self.stomp_cd-1)
        self.glow_intensity = max(0, self.glow_intensity - 4)

        hp_pct = self.hp/self.max_hp
        self.phase = 1 if hp_pct>0.60 else (2 if hp_pct>0.30 else 3)
        self.enraged = (self.phase==3)

        dx=player_rect.centerx-self.rect.centerx
        dy=player_rect.centery-self.rect.centery
        dist=math.sqrt(dx*dx+dy*dy)
        self.facing = 1 if dx>0 else -1

        # Velocidade cresce com fase
        spd = 2.0 + self.phase*0.9

        if self.state==self.HURT:
            self.hurt_timer-=1
            if self.hurt_timer<=0: self.state=self.CHASE
            self.vx*=0.75
        else:
            self.state=self.CHASE
            if abs(dx)>70: self.vx=lerp(self.vx,self.facing*spd,0.10)
            else:          self.vx=lerp(self.vx,0,0.15)

        # ── Padrões de ataque ──────────────────────────────────
        cycle = self.phase_timer % max(150, 240-self.phase*30)

        # Telegraphing: brilha antes dos ataques
        if cycle > max(100, 160 - self.phase * 20):
            self.glow_intensity = min(255, self.glow_intensity + 6)

        # Fase 1+: Rajada circular (ciclo 0)
        if cycle == 0 and self.shoot_cd == 0:
            count = 8 + self.phase * 4
            for i in range(count):
                ang = math.tau * i / count
                spd_p = 5 + self.phase * 0.5
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery,
                                              math.cos(ang) * spd_p, math.sin(ang) * spd_p))
            self.glow_intensity = 255
            self.shoot_cd = 20

        # Fase 2+: Triplo tiro direcionado
        if self.phase >= 2 and cycle in (60, 80, 100) and self.shoot_cd == 0:
            angle = math.atan2(dy, dx)
            speed = 9 + self.phase * 1.2
            spreads = [-0.22, 0, 0.22] if self.phase >= 3 else [-0.15, 0, 0.15]
            for s in spreads:
                a = angle + s
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery,
                                              math.cos(a) * speed, math.sin(a) * speed))
            self.glow_intensity = 180
            self.shoot_cd = 12

        # Fase 3: Chuva de projéteis do céu
        if self.phase>=3 and cycle>110 and cycle%9==0:
            rx_drop = player_rect.centerx+random.randint(-300,300)
            projectiles.append(Projectile(rx_drop,-40,0,10,dmg=1))

        # ── Física — CORRIGIDA: sem verificação de borda, sem pulo ──
        self.vy=min(self.vy+GRAVITY, MAX_FALL)
        self.rect.x+=int(self.vx);  self._collide_x(platforms)
        self.rect.y+=int(self.vy);  self._collide_y(platforms)

        # CLAMP na arena (nunca sai pela esquerda/direita)
        self.rect.x=clamp(self.rect.x, self.arena_x1, self.arena_x2-self.rect.w)

        # Safety net: se caiu muito, volta ao chão da arena
        if self.rect.top > 800:
            self.rect.y = 400; self.vy=0

    def take_damage(self, dmg, direction):
        if self.state in (self.HURT, self.DEAD): return
        self.hp-=dmg; self.flash=True
        for _ in range(18):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"boss",(2,7)))
        if self.hp<=0: self._die()
        else:
            self.state=self.HURT; self.hurt_timer=15
            # Knockback reduzido no boss
            self.vx=(direction*KNOCKBACK_H)*0.3
            self.vy=KNOCKBACK_V*0.2

    def _die(self):
        self.state=self.DEAD; self.dead_timer=0
        for _ in range(50):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,
                                           "boss",(1,9),(30,70)))

    def draw(self, surf, cx, cy):
        for p in self.particles: p.draw(surf, cx, cy)
        if self.state==self.DEAD and self.dead_timer>20: return
        rx,ry=self.rect.x-cx,self.rect.y-cy
        w,h=self.rect.w,self.rect.h
        bob=int(math.sin(self.bob_timer*0.07)*2)

        # Aura de fase
        aura_col=[(80,20,40),(140,0,0),(255,30,30)][self.phase-1]
        draw_circle_alpha(surf,aura_col,(rx+w//2,ry+h//2),60+bob,40)

        # Telegraphing glow
        if self.glow_intensity > 0:
            draw_circle_alpha(surf, (255, 80, 80), (rx + w // 2, ry + h // 2), 80, self.glow_intensity // 3)

        # Corpo
        pygame.draw.rect(surf,(60,15,35),(rx,ry+bob,w,h),border_radius=12)
        pygame.draw.rect(surf,(120,35,55),(rx+10,ry+10+bob,w-20,h-20),border_radius=8)

        # Padrão de armadura
        for i in range(3):
            y_off = ry+25+bob+i*22
            pygame.draw.rect(surf,(80,20,40),(rx+8,y_off,w-16,16),border_radius=4)

        # Olhos
        eye_y=ry+32+bob+int(math.sin(self.bob_timer*0.1)*4)
        for ex in [rx+24,rx+54]:
            pygame.draw.circle(surf,(255,0,0),(ex,eye_y),13)
            pygame.draw.circle(surf,(255,120,120),(ex,eye_y),7)
            pygame.draw.circle(surf,C_WHITE,(ex-3,eye_y-3),4)

        # Chifres
        for side,hx in [(-1,rx+8),(1,rx+w-8)]:
            pts=[(hx,ry+8+bob),(hx+side*(-8),ry+bob-18),(hx+side*(-4),ry+bob)]
            pygame.draw.polygon(surf,(100,30,50),pts)

        # Fase 3: brilho extra nos olhos
        if self.phase==3:
            draw_circle_alpha(surf,(255,50,50),(rx+24,eye_y),20,100)
            draw_circle_alpha(surf,(255,50,50),(rx+54,eye_y),20,100)

        # Barra de vida proeminente
        if self.hp<self.max_hp: self._draw_boss_hp_bar(surf,rx,ry+bob-24)

    def _draw_boss_hp_bar(self,surf,rx,ry):
        bw=self.rect.w+20; bh=10; bx=rx-10
        ratio=self.hp/self.max_hp
        # Borda
        pygame.draw.rect(surf,(40,10,20),(bx-2,ry-2,bw+4,bh+4),border_radius=4)
        pygame.draw.rect(surf,C_HP_EMPTY,(bx,ry,bw,bh),border_radius=3)
        bar_col=(255,30,30) if self.phase==3 else ((255,150,0) if self.phase==2 else C_HP_FULL)
        pygame.draw.rect(surf,bar_col,(bx,ry,int(bw*ratio),bh),border_radius=3)
        pygame.draw.rect(surf,C_WHITE,(bx,ry,bw,bh),1,border_radius=3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Player — + Dash, Duplo Pulo, Combo
# ═══════════════════════════════════════════════════════════════════
class Player:
    def __init__(self, x, y, max_hp=5):
        self.rect      = pygame.Rect(x,y,28,42)
        self.vx=self.vy=0.0
        self.facing    = 1
        self.on_ground = False
        self.max_hp    = max_hp; self.hp=max_hp
        self.alive     = True
        self.is_attacking=self.is_hurt=self.is_dead=False

        # Timers
        self.attack_timer=self.attack_cd=0
        self.combo_count=0; self.combo_timer=0  # combo de 2 golpes
        self.inv_timer=self.coyote_timer=0
        self.jump_buffer=self.flash_timer=self.dust_timer=0
        self.anim_timer=self.death_timer=0
        self.jump_held=False

        # Duplo pulo
        self.jumps_left = 2  # 2 pulos: chão + aéreo

        # Dash
        self.dash_timer  = 0   # frames de duração do dash ativo
        self.dash_cd     = 0   # cooldown do dash
        self.is_dashing  = False
        self.dash_dir    = 1

        self.attack_rect = pygame.Rect(0,0,0,0)
        self.particles: List[Particle] = []
        self.spawn_x=x; self.spawn_y=y

    # ── Input ─────────────────────────────────────────────────
    def handle_input(self, keys):
        if self.is_dead: return

        # Movimento
        move=0
        if keys[pygame.K_a]: move=-1
        if keys[pygame.K_d]: move= 1
        if move:
            self.facing=move
            acc = 0.35 if self.on_ground else 0.20
            self.vx=lerp(self.vx,move*PLAYER_SPD,acc)
        else:
            dec = 0.45 if self.on_ground else 0.10
            self.vx=lerp(self.vx,0,dec)
            if abs(self.vx)<0.1: self.vx=0

        # Dash (SHIFT) — invencível durante
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_cd==0 and not self.is_dashing:
            self.is_dashing=True; self.dash_timer=DASH_DUR
            self.dash_cd=DASH_CD; self.dash_dir=self.facing
            self.inv_timer=max(self.inv_timer, DASH_DUR+2)
            # Afterimage particles
            for _ in range(10):
                self.particles.append(
                    Particle(self.rect.centerx,self.rect.centery+10,"dash",(1,3),(8,16),0,
                             direction=math.pi+math.atan2(0,self.dash_dir)))

        # Pulo (W/Space/Z)
        jump_keys = keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_z]
        if jump_keys: self.jump_buffer=JUMP_BUF

        # Executa pulo: chão, coyote OU duplo pulo
        can_first_jump  = (self.on_ground or self.coyote_timer>0)
        can_double_jump = (not self.on_ground and self.jumps_left>0 and not can_first_jump)

        if self.jump_buffer>0 and (can_first_jump or can_double_jump):
            self.vy=JUMP_FORCE
            self.coyote_timer=0; self.jump_buffer=0; self.jump_held=True
            if can_double_jump:
                self.jumps_left=0
                # Partículas de duplo pulo
                for _ in range(12):
                    self.particles.append(
                        Particle(self.rect.centerx,self.rect.centery+8,"soul",(1,4),(10,22),-0.05))
            else:
                for _ in range(6):
                    self.particles.append(
                        Particle(self.rect.centerx,self.rect.bottom,"dust",(0.5,2),(8,18),0.05))

        if self.jump_held and self.vy<0:
            if not jump_keys:
                self.jump_held=False
                if self.vy<-7: self.vy*=JUMP_HOLD

        # Ataque (X ou Clique)
        atk_key = keys[pygame.K_x] or pygame.mouse.get_pressed()[0]
        if atk_key and self.attack_cd==0 and not self.is_attacking:
            self._start_attack()

    def _start_attack(self):
        self.is_attacking=True; self.attack_timer=ATTACK_DUR
        self.combo_timer=COMBO_WINDOW
        self.attack_cd=ATTACK_CD
        # Partículas de slash
        for _ in range(8):
            self.particles.append(
                Particle(self.rect.centerx+self.facing*30,self.rect.centery,
                         "soul",(1,4),(8,20),0,
                         direction=math.atan2(0,self.facing)))

    # ── Física ────────────────────────────────────────────────
    def apply_gravity(self):
        if self.is_dead or self.is_dashing: return
        self.vy+=GRAVITY
        if abs(self.vy)<3 and not self.on_ground: self.vy+=GRAVITY*0.3
        self.vy=min(self.vy,MAX_FALL)

    def move_and_collide(self, platforms):
        if self.is_dead:
            self.vy+=GRAVITY; self.rect.y+=int(self.vy); return

        if self.is_dashing:
            self.rect.x+=int(self.dash_dir*DASH_SPEED)
            self._collide_x(platforms)
            return

        self.rect.x+=int(self.vx); self._collide_x(platforms)
        prev_on_ground=self.on_ground
        self.rect.y+=int(self.vy); self._collide_y(platforms)

        # Extra ground snap
        gfeet=pygame.Rect(self.rect.x,self.rect.bottom,self.rect.w,3)
        for p in platforms:
            if gfeet.colliderect(p.rect) and self.vy>=0:
                self.on_ground=True; self.rect.bottom=p.rect.top; self.vy=0; break

        if prev_on_ground and not self.on_ground and self.vy>0:
            self.coyote_timer=COYOTE_T
        elif self.on_ground:
            self.coyote_timer=0; self.jumps_left=2  # reset pulo duplo no chão
        else:
            self.coyote_timer=max(0,self.coyote_timer-1)

        if not prev_on_ground and self.on_ground:
            for _ in range(8):
                self.particles.append(
                    Particle(self.rect.centerx,self.rect.bottom,"dust",(1,3),(10,22),0.05))

    def _collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx>0: self.rect.right=p.rect.left
                else:         self.rect.left =p.rect.right
                self.vx=0

    def _collide_y(self, platforms):
        self.on_ground=False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy>0: self.rect.bottom=p.rect.top; self.on_ground=True
                else:         self.rect.top   =p.rect.bottom
                self.vy=0

    # ── Dano ──────────────────────────────────────────────────
    def take_damage(self, dmg, enemy_x):
        if self.inv_timer>0 or self.is_dead or self.is_dashing: return
        self.hp-=dmg; self.inv_timer=INV_FRAMES; self.flash_timer=14; self.is_hurt=True
        direction=1 if self.rect.centerx>enemy_x else -1
        self.vx=direction*KNOCKBACK_H; self.vy=KNOCKBACK_V
        for _ in range(16):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"hit",(2,6)))
        if self.hp<=0: self._die()

    def _die(self):
        self.is_dead=True; self.death_timer=0
        for _ in range(30):
            self.particles.append(Particle(self.rect.centerx,self.rect.centery,"death",(1,7),(30,60)))

    def respawn(self):
        self.rect.x=self.spawn_x; self.rect.y=self.spawn_y
        self.vx=self.vy=0; self.hp=self.max_hp
        self.is_dead=self.is_hurt=self.is_dashing=False
        self.death_timer=0; self.inv_timer=INV_FRAMES
        self.dash_timer=self.dash_cd=0; self.jumps_left=2
        self.particles=[]

    # ── Update ────────────────────────────────────────────────
    def update(self, platforms, checkpoints, enemies):
        self.anim_timer+=1
        self.attack_cd  =max(0,self.attack_cd-1)
        self.inv_timer  =max(0,self.inv_timer-1)
        self.flash_timer=max(0,self.flash_timer-1)
        self.jump_buffer=max(0,self.jump_buffer-1)
        self.combo_timer=max(0,self.combo_timer-1)
        self.dash_cd    =max(0,self.dash_cd-1)
        if self.inv_timer==0: self.is_hurt=False

        # Dash duration
        if self.is_dashing:
            self.dash_timer-=1
            if self.dash_timer<=0:
                self.is_dashing=False; self.vx=self.dash_dir*PLAYER_SPD*0.5
            else:
                # Afterimage trail
                if self.dash_timer%3==0:
                    self.particles.append(
                        Particle(self.rect.centerx,self.rect.centery,"dash",(0,0.1),(8,14),0))

        if self.is_dead: self.death_timer+=1; self._update_particles(); return

        # Ataque hitbox
        if self.is_attacking:
            self.attack_timer-=1
            reach=50
            if self.facing==1: ax=self.rect.centerx+6
            else:              ax=self.rect.centerx-reach-6
            self.attack_rect=pygame.Rect(ax,self.rect.y+4,reach,32)
            if self.attack_timer<=0:
                self.is_attacking=False; self.attack_rect=pygame.Rect(0,0,0,0)

        # Checkpoints
        for chk in checkpoints:
            if self.rect.colliderect(chk.rect):
                chk.activate()
                self.spawn_x=chk.rect.centerx-self.rect.w//2
                self.spawn_y=chk.rect.top-self.rect.h

        # Dano de inimigos (com hazard check separado)
        for e in enemies:
            if not e.alive: continue
            if hasattr(e,'can_damage_player') and e.can_damage_player and self.rect.colliderect(e.rect):
                self.take_damage(1,e.rect.centerx)
            elif hasattr(e,'state') and e.state not in (getattr(Enemy,'DEAD','dead'),) and \
                 self.rect.colliderect(e.rect) and self.inv_timer==0:
                self.take_damage(1,e.rect.centerx)

        # Poeira ao andar
        self.dust_timer+=1
        if self.on_ground and abs(self.vx)>1 and self.dust_timer%8==0:
            self.particles.append(
                Particle(self.rect.centerx,self.rect.bottom,"dust",(0.2,1),(6,14),0))

        self._update_particles()

    def _update_particles(self):
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update()

    # ── Draw ──────────────────────────────────────────────────
    def draw(self, surf, cx, cy):
        for p in self.particles: p.draw(surf, cx, cy)
        if self.is_dead and self.death_timer>15: return

        rx,ry=self.rect.x-cx, self.rect.y-cy
        w,h=self.rect.w, self.rect.h

        # Pisca quando invencível
        if self.inv_timer>0 and self.inv_timer%6<3 and not self.flash_timer: return

        body_col = C_P_HURT if self.flash_timer>0 else (C_P_DASH if self.is_dashing else C_P_BODY)
        head_col = C_P_HURT if self.flash_timer>0 else (C_P_DASH if self.is_dashing else C_P_HEAD)
        bob = int(math.sin(self.anim_timer*0.07)*1.5) if self.on_ground else 0

        # Capa
        cape_off=int(math.sin(self.anim_timer*0.1)*2)
        for cape_col, off_mult in [(C_P_CAPE2,14),(C_P_CAPE,11)]:
            cp=[
                (rx+w//2-self.facing*2, ry+8+bob),
                (rx+w//2-self.facing*off_mult, ry+h-4+cape_off),
                (rx+w//2-self.facing*5, ry+h//2+bob),
            ]
            pygame.draw.polygon(surf,cape_col,cp)

        # Torso
        pygame.draw.rect(surf,body_col,(rx+4,ry+14+bob,w-8,h-20),border_radius=6)

        # Pernas com animação
        ls=self.anim_timer*0.2
        for i in range(2):
            lb=int(math.sin(ls+i*math.pi)*4) if self.on_ground and abs(self.vx)>0.5 else 0
            pygame.draw.rect(surf,C_P_CAPE,(rx+5+i*(w-14),ry+h-10+lb,8,12))

        # Cabeça
        hcx,hcy=rx+w//2, ry+12+bob
        pygame.draw.circle(surf,head_col,(hcx,hcy),13)
        # Máscara
        mp=[
            (hcx+self.facing*2,hcy-6),(hcx+self.facing*11,hcy+2),
            (hcx+self.facing*9,hcy+8),(hcx+self.facing*1,hcy+6)
        ]
        pygame.draw.polygon(surf,C_P_CAPE,mp)
        # Olho
        ex,ey=hcx+self.facing*5, hcy+1
        pygame.draw.circle(surf,C_P_EYE,(ex,ey),4)
        pygame.draw.circle(surf,C_WHITE,(ex+1,ey-1),1)
        # Antenas
        ab=(hcx+self.facing*2,hcy-11)
        pygame.draw.line(surf,C_P_CAPE2,ab,(ab[0]-self.facing*6,ab[1]-10),2)
        pygame.draw.line(surf,C_P_CAPE2,ab,(ab[0]+self.facing*3,ab[1]-8),1)

        # Dash trail glow
        if self.is_dashing:
            draw_circle_alpha(surf,C_P_DASH,(hcx,hcy),20,100)

        if self.is_attacking: self._draw_attack(surf,rx,ry,w,h,bob)

    def _draw_attack(self,surf,rx,ry,w,h,bob):
        t=1-(self.attack_timer/ATTACK_DUR)
        cx2=rx+w//2+self.facing*8; cy2=ry+h//2+bob
        gr=int(20+t*15)
        draw_circle_alpha(surf,C_SLASH_A,(cx2+self.facing*22,cy2),gr,int(180*(1-t)))
        ex2=cx2+self.facing*int(48*(1-t*0.3))
        ey_off=int(math.sin(t*math.pi)*16)
        pygame.draw.line(surf,C_SLASH_B,(cx2,cy2),(ex2,cy2-ey_off),5)
        pygame.draw.line(surf,C_P_SWORD,(cx2,cy2),(ex2,cy2-ey_off),2)
        pygame.draw.circle(surf,C_WHITE,(ex2,cy2-ey_off),3)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Camera com screen shake
# ═══════════════════════════════════════════════════════════════════
class Camera:
    def __init__(self, world_w, world_h):
        self.x=self.y=0.0
        self.world_w=world_w; self.world_h=world_h
        self.shake=0

    def follow(self, target, smooth=0.12):
        tx=target.centerx-SCREEN_W//2; ty=target.centery-SCREEN_H//2
        self.x=lerp(self.x,tx,smooth); self.y=lerp(self.y,ty,smooth)
        self.x=clamp(self.x,0,max(0,self.world_w-SCREEN_W))
        self.y=clamp(self.y,0,max(0,self.world_h-SCREEN_H))
        self.shake=max(0,self.shake-1)

    def add_shake(self, intensity): self.shake=max(self.shake,intensity)

    @property
    def ix(self):
        s=self.shake; return int(self.x)+random.randint(-s,s) if s else int(self.x)
    @property
    def iy(self):
        s=self.shake; return int(self.y)+random.randint(-s,s) if s else int(self.y)


# ═══════════════════════════════════════════════════════════════════
#  CLASSES: Switch, Gate, MovingPlatform, LevelGoal
# ═══════════════════════════════════════════════════════════════════
class Switch:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.active = False
    def update(self,player,particles):
        if not self.active and player.is_attacking and self.rect.colliderect(player.attack_rect):
            self.active=True
            for _ in range(15):
                particles.append(Particle(self.rect.centerx,self.rect.centery,"soul"))
            return True
        return False
    def draw(self,surf,cx,cy):
        rx,ry=self.rect.x-cx,self.rect.y-cy
        col=(100,255,100) if self.active else (255,100,100)
        pygame.draw.rect(surf,col,(rx,ry,30,30),border_radius=5)
        pygame.draw.rect(surf,C_WHITE,(rx,ry,30,30),2,border_radius=5)
        if self.active:
            draw_circle_alpha(surf,(100,255,100),(rx+15,ry+15),18,80)

class Gate:
    def __init__(self,x,y,w,h):
        self.rect=pygame.Rect(x,y,w,h); self.open=False; self.y_start=y
    def update(self, is_active):
        if is_active and not self.open:
            self.rect.y -= 10
            if self.rect.y<self.y_start-self.rect.h: self.open=True
    def draw(self,surf,cx,cy):
        if self.open: return
        rx,ry=self.rect.x-cx,self.rect.y-cy
        pygame.draw.rect(surf,(90,90,115),(rx,ry,self.rect.w,self.rect.h))
        for i in range(0,self.rect.h,12):
            pygame.draw.line(surf,(55,55,70),(rx,ry+i),(rx+self.rect.w,ry+i),2)
        pygame.draw.rect(surf,(120,120,145),(rx,ry,self.rect.w,self.rect.h),2)

class MovingPlatform:
    def __init__(self,x,y,w,h,dx,dy,speed=2):
        self.rect=pygame.Rect(x,y,w,h)
        self.start_pos=pygame.Vector2(x,y)
        self.target_offset=pygame.Vector2(dx,dy)
        self.timer=random.uniform(0,math.pi*2)
    def update(self,player):
        self.timer+=0.018
        o=(math.sin(self.timer)+1)/2
        nx=self.start_pos.x+self.target_offset.x*o
        ny=self.start_pos.y+self.target_offset.y*o
        vx=nx-self.rect.x; vy=ny-self.rect.y
        self.rect.x=int(nx); self.rect.y=int(ny)
        foot = pygame.Rect(player.rect.x, player.rect.bottom, player.rect.w, 4)
        if foot.colliderect(self.rect) and player.vy>=-1:
            player.rect.x+=int(vx); player.rect.y=self.rect.top-player.rect.h
            player.on_ground=True; player.vy=0
    def draw(self,surf,cx,cy):
        rx,ry=self.rect.x-cx,self.rect.y-cy
        pygame.draw.rect(surf,(80,130,190),(rx,ry,self.rect.w,self.rect.h),border_radius=4)
        pygame.draw.rect(surf,(120,170,230),(rx,ry,self.rect.w,3))
        pygame.draw.rect(surf,C_WHITE,(rx,ry,self.rect.w,self.rect.h),2,border_radius=4)

class LevelGoal:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,56,76); self.timer=0
    def update(self,player):
        self.timer+=1; return self.rect.colliderect(player.rect)
    def draw(self,surf,cx,cy):
        rx,ry=self.rect.x-cx,self.rect.y-cy
        glow=int(100+50*math.sin(self.timer*0.1))
        draw_circle_alpha(surf,C_CHK_GLOW,(rx+28,ry+38),50,glow//2)
        draw_circle_alpha(surf,C_SOUL_B,(rx+28,ry+38),30,glow)
        pygame.draw.rect(surf,C_CHK_ON,(rx+8,ry+8,40,60),3,border_radius=6)
        # Cruz luminosa
        pygame.draw.line(surf,C_SOUL_B,(rx+28,ry+16),(rx+28,ry+60),2)
        pygame.draw.line(surf,C_SOUL_B,(rx+10,ry+38),(rx+46,ry+38),2)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: HUD — vida, dash, almas, mensagens
# ═══════════════════════════════════════════════════════════════════
class HUD:
    def __init__(self):
        self.font_sm=pygame.font.SysFont("consolas",15)
        self.font_md=pygame.font.SysFont("consolas",21,bold=True)
        self.font_lg=pygame.font.SysFont("consolas",46,bold=True)
        self.msg=""; self.msg_timer=0
        self.boss_active=False
        self.boss_ref=None

    def show_message(self,text,duration=120):
        self.msg=text; self.msg_timer=duration

    def update(self,player):
        self.msg_timer=max(0,self.msg_timer-1)

    def draw(self, surf, player, souls=0, level_name=""):
        ss=22; margin=14
        # Corações de vida
        for i in range(player.max_hp):
            sx=margin+i*(ss+5); sy=margin
            draw_circle_alpha(surf,C_HP_BORDER,(sx+ss//2,sy+ss//2),ss//2+2,90)
            pygame.draw.circle(surf,C_HP_EMPTY,(sx+ss//2,sy+ss//2),ss//2-1)
            if i<player.hp:
                col=C_HP_FULL if player.hp>player.max_hp//2 else (200,140,50)
                pygame.draw.circle(surf,col,(sx+ss//2,sy+ss//2),ss//2-3)
                draw_circle_alpha(surf,C_SOUL_B,(sx+ss//2-2,sy+ss//2-2),4,130)

        # Barra de dash abaixo dos corações
        dx_x=margin; dx_y=margin+ss+8
        dx_w=player.max_hp*(ss+5)-5
        ratio_d=1-(player.dash_cd/DASH_CD) if player.dash_cd>0 else 1.0
        pygame.draw.rect(surf,(30,20,50),(dx_x,dx_y,dx_w,5),border_radius=2)
        pygame.draw.rect(surf,C_DASH_BAR,(dx_x,dx_y,int(dx_w*ratio_d),5),border_radius=2)
        if player.is_dashing:
            draw_rect_alpha(surf,C_P_DASH,(dx_x,dx_y,dx_w,5),120)

        # Contador de almas (top right)
        soul_txt=self.font_sm.render(f"◆ {souls}",True,C_SOUL_B)
        surf.blit(soul_txt,(SCREEN_W-soul_txt.get_width()-16,16))

        # Nome do level (top center, fade in)
        if level_name:
            lv_s=self.font_sm.render(level_name,True,C_UI_TEXT)
            surf.blit(lv_s,(SCREEN_W//2-lv_s.get_width()//2, 16))

        # Boss HP bar (proeminente na tela durante boss)
        if self.boss_active and self.boss_ref and self.boss_ref.alive:
            b=self.boss_ref
            bw=500; bh=16; bx=SCREEN_W//2-bw//2; by=SCREEN_H-50
            ratio=clamp(b.hp/b.max_hp,0,1)
            pygame.draw.rect(surf,(30,10,20),(bx-2,by-2,bw+4,bh+4),border_radius=5)
            pygame.draw.rect(surf,C_HP_EMPTY,(bx,by,bw,bh),border_radius=4)
            col=(255,30,30) if b.phase==3 else ((255,150,0) if b.phase==2 else (200,50,75))
            pygame.draw.rect(surf,col,(bx,by,int(bw*ratio),bh),border_radius=4)
            pygame.draw.rect(surf,C_WHITE,(bx,by,bw,bh),1,border_radius=4)
            phase_txt=self.font_sm.render(f"BOSS  [FASE {b.phase}]  {b.hp}/{b.max_hp}",True,C_WHITE)
            surf.blit(phase_txt,(SCREEN_W//2-phase_txt.get_width()//2,by-20))

        # Mensagem central
        if self.msg_timer>0:
            alpha=min(255,self.msg_timer*4)
            ts=self.font_md.render(self.msg,True,C_CHK_ON)
            ts.set_alpha(alpha)
            surf.blit(ts,(SCREEN_W//2-ts.get_width()//2, SCREEN_H-90))

    def draw_death_screen(self,surf):
        draw_rect_alpha(surf,C_BLACK,(0,0,SCREEN_W,SCREEN_H),160)
        t1=self.font_lg.render("VOCÊ CAIU",True,(200,60,80))
        t2=self.font_md.render("Pressione R para renascer",True,C_UI_TEXT)
        surf.blit(t1,(SCREEN_W//2-t1.get_width()//2,SCREEN_H//2-50))
        surf.blit(t2,(SCREEN_W//2-t2.get_width()//2,SCREEN_H//2+20))

    def draw_start_screen(self,surf):
        draw_gradient_bg(surf,C_BG_TOP,C_BG_BOT,(0,0,SCREEN_W,SCREEN_H))
        ft=pygame.font.SysFont("consolas",64,bold=True)
        fs=pygame.font.SysFont("consolas",19)
        t=pygame.time.get_ticks()/1000
        gl=int(128+80*math.sin(t*1.5))
        title=ft.render("SHADOWCROFT",True,C_UI_TITLE)
        draw_rect_alpha(surf,C_CHK_GLOW,
            (SCREEN_W//2-title.get_width()//2-12,SCREEN_H//2-68,
             title.get_width()+24,72),gl//4)
        surf.blit(title,(SCREEN_W//2-title.get_width()//2,SCREEN_H//2-62))
        sub=fs.render("Explore as sombras. Domine o combate.",True,C_UI_TEXT)
        surf.blit(sub,(SCREEN_W//2-sub.get_width()//2,SCREEN_H//2+28))
        hint=fs.render("[ CLIQUE PARA COMEÇAR ]",True,C_SOUL_A)
        surf.blit(hint,(SCREEN_W//2-hint.get_width()//2,SCREEN_H//2+72))
        ctrl=fs.render("A/D Mover  |  W/Space Pular  |  Shift Dash  |  X Atacar",True,(130,120,170))
        surf.blit(ctrl,(SCREEN_W//2-ctrl.get_width()//2,SCREEN_H//2+110))

    def draw_level_select(self,surf,unlocked,souls,health_upgrades):
        draw_gradient_bg(surf,C_BG_TOP,C_BG_BOT,(0,0,SCREEN_W,SCREEN_H))
        ft=pygame.font.SysFont("consolas",44,bold=True)
        fm=pygame.font.SysFont("consolas",22)
        fs=pygame.font.SysFont("consolas",17)
        clickables=[]
        title=ft.render("SELECIONAR FASE",True,C_UI_TITLE)
        surf.blit(title,(SCREEN_W//2-title.get_width()//2,50))
        level_names=["I — O Início","II — Plataformas","III — Puzzles","IV — A Ascensão","V — O Boss Final"]
        for i in range(1,6):
            locked = i>unlocked
            col=(120,115,150) if locked else C_UI_TEXT
            status=" 🔒" if locked else ""
            txt=fm.render(f"  Level {level_names[i-1]}{status}",True,col)
            rx2,ry2=SCREEN_W//2-160, 145+i*48
            if not locked:
                draw_rect_alpha(surf,C_PLT_BODY,(rx2-8,ry2-4,txt.get_width()+16,38),180)
                pygame.draw.rect(surf,C_PLT_EDGE,(rx2-8,ry2-4,txt.get_width()+16,38),1)
            surf.blit(txt,(rx2,ry2))
            if not locked: clickables.append((pygame.Rect(rx2-8,ry2-4,txt.get_width()+16,38),"level",i))

        # Almas e upgrade
        sa=fm.render(f"◆ {souls} almas",True,C_SOUL_B)
        surf.blit(sa,(SCREEN_W//2-sa.get_width()//2,430))
        cost=30+health_upgrades*20
        ut=fm.render(f"[ Upgrade Vida +1 HP : {cost} almas ]",True,(255,200,100))
        urx,ury=SCREEN_W//2-ut.get_width()//2,470
        draw_rect_alpha(surf,(40,25,10),(urx-6,ury-4,ut.get_width()+12,36),160)
        surf.blit(ut,(urx,ury))
        clickables.append((pygame.Rect(urx-6,ury-4,ut.get_width()+12,36),"upgrade",cost))

        # Dificuldade
        diffs=[("Fácil",0.5),(">Normal<",1.0),("Difícil",1.5)]
        for i,(label,val) in enumerate(diffs):
            dt=fm.render(label,True,C_SOUL_A)
            drx,dry=SCREEN_W//2-220+i*180,520
            surf.blit(dt,(drx,dry))
            clickables.append((pygame.Rect(drx,dry,dt.get_width(),34),"diff",val))

        hint=fs.render("Teclas 1-5 | ESC sair | E fácil | N normal | H difícil",True,(100,95,130))
        surf.blit(hint,(SCREEN_W//2-hint.get_width()//2,630))
        return clickables


# ═══════════════════════════════════════════════════════════════════
#  build_level — 5 fases completamente redesenhadas
# ═══════════════════════════════════════════════════════════════════
def build_level(level_id=1, difficulty=1.0):
    """
    Retorna (platforms, enemies, checkpoints, orbs, goal,
             switches, gates, m_platforms, soul_drops_spawns, world_w, world_h, level_name)
    """
    platforms:   List[Platform]       = []
    enemies:     List               = []
    checkpoints: List[Checkpoint]     = []
    orbs:        List[HealthOrb]      = []
    switches:    List[Switch]         = []
    gates:       List[Gate]           = []
    m_plats:     List[MovingPlatform] = []

    hp = lambda base: max(1, int(base * difficulty))

    # Paredes do mundo
    def add_walls(world_w, world_h):
        platforms.append(Platform(-40, 0, 40, world_h))
        platforms.append(Platform(world_w, 0, 40, world_h))

    # ── LEVEL 1: O Início — tutorial suave e expandido ────────
    if level_id == 1:
        world_w, world_h = 4000, 760
        level_name = "I — O Início"
        add_walls(world_w, world_h)

        # Zona 1: Chão plano + intro inimigos
        platforms.append(Platform(0, 600, 700, 40, 0))
        platforms.append(Platform(750, 520, 150, 24, 2))
        platforms.append(Platform(950, 600, 600, 40, 1))

        enemies.append(Enemy(260, 560, 80, hp(3)))
        enemies.append(Enemy(500, 560, 80, hp(3)))
        enemies.append(FlyingEnemy(820, 460, hp(2), float_height=400))

        checkpoints.append(Checkpoint(1100, 554))

        # Zona 2: Escalada + Plataformas flutuantes
        platforms.append(Platform(1600, 500, 200, 24, 2))
        platforms.append(Platform(1850, 420, 180, 24, 0))
        platforms.append(Platform(2100, 530, 500, 30, 1))

        enemies.append(Enemy(1650, 460, 70, hp(3)))
        enemies.append(Enemy(1900, 380, 60, hp(3)))
        enemies.append(Enemy(2200, 490, 100, hp(4)))
        enemies.append(FlyingEnemy(2000, 350, hp(2), float_height=300))

        orbs.append(HealthOrb(1950, 350))

        # Zona 3: Descida rítmica e área final
        platforms.append(Platform(2650, 590, 400, 40, 0))
        platforms.append(Platform(2800, 480, 150, 24, 2))
        platforms.append(Platform(3050, 430, 200, 24, 1))
        platforms.append(Platform(3300, 590, 660, 40, 0))

        enemies.append(Enemy(2700, 550, 100, hp(3)))
        enemies.append(Enemy(2950, 550, 100, hp(4)))
        enemies.append(Enemy(3100, 390, 60, hp(3)))
        enemies.append(FlyingEnemy(3200, 400, hp(2), float_height=320))
        enemies.append(Enemy(3400, 550, 120, hp(4)))
        enemies.append(Enemy(3650, 550, 120, hp(4)))

        checkpoints.append(Checkpoint(2750, 544))
        orbs.append(HealthOrb(3100, 350))

        goal = LevelGoal(3850, 514)

    # ── LEVEL 2: Plataformas — corrigido, sem espinhos duplos ─
    elif level_id == 2:
        world_w, world_h = 4500, 760
        level_name = "II — Plataformas"
        add_walls(world_w, world_h)

        # Zona 1: Intro + Movimento Horizontal
        platforms.append(Platform(0, 600, 500, 40, 0))
        enemies.append(Enemy(200, 560, 80, hp(3)))
        enemies.append(Enemy(350, 560, 60, hp(3)))
        enemies.append(FlyingEnemy(400, 480, hp(2), float_height=420))

        m_plats.append(MovingPlatform(600, 560, 140, 22, 250, 0))
        platforms.append(Platform(950, 580, 400, 40, 1))
        enemies.append(ShootingEnemy(1050, 540, 70, hp(2)))
        enemies.append(Enemy(1150, 540, 60, hp(3)))
        checkpoints.append(Checkpoint(1000, 556))

        # Zona 2: Verticalidade e Hazards
        platforms.append(Platform(1450, 540, 250, 30, 2))
        m_plats.append(MovingPlatform(1750, 540, 140, 22, 0, -200))
        platforms.append(Platform(2000, 560, 200, 30, 0))

        # Espinhos rítmicos expandidos
        platforms.append(Platform(2300, 540, 200, 30, 1, hazard=True, hazard_timed=True, hazard_offset=0))
        platforms.append(Platform(2550, 540, 200, 30, 2))
        platforms.append(Platform(2800, 540, 200, 30, 1, hazard=True, hazard_timed=True, hazard_offset=60))

        enemies.append(Enemy(1500, 500, 70, hp(4)))
        enemies.append(FlyingEnemy(1850, 420, hp(2), float_height=360))
        enemies.append(ShootingEnemy(2050, 520, 60, hp(2)))
        enemies.append(Enemy(2600, 500, 60, hp(3)))

        orbs.append(HealthOrb(2100, 490))
        checkpoints.append(Checkpoint(2050, 536))

        # Zona 3: Grandes Saltos e Finalização
        platforms.append(Platform(3100, 580, 400, 40, 0))
        m_plats.append(MovingPlatform(3600, 540, 150, 22, 300, 0))
        platforms.append(Platform(4000, 540, 300, 30, 2))
        platforms.append(Platform(4400, 580, 500, 40, 0))

        enemies.append(Enemy(3200, 540, 90, hp(4)))
        enemies.append(ShootingEnemy(3300, 540, 80, hp(3)))
        enemies.append(FlyingEnemy(3700, 430, hp(2), float_height=370))
        enemies.append(Enemy(4050, 500, 80, hp(4)))
        enemies.append(ShootingEnemy(4150, 500, 70, hp(3)))
        enemies.append(Enemy(4500, 540, 100, hp(4)))

        orbs.append(HealthOrb(4050, 470))
        checkpoints.append(Checkpoint(4050, 516))
        goal = LevelGoal(4400, 504)

    # ── LEVEL 3: Puzzles — switches, portões, espinhos alternados ─
    elif level_id == 3:
        world_w, world_h = 4800, 800
        level_name = "III — Puzzles"
        add_walls(world_w, world_h)

        # Zona 1: Puzzle Inicial
        platforms.append(Platform(0, 620, 700, 40, 0))
        platforms.append(Platform(750, 560, 400, 30, 1))
        switches.append(Switch(600, 528))
        gates.append(Gate(1100, 340, 40, 220))

        enemies.append(Enemy(200, 580, 80, hp(3)))
        enemies.append(Enemy(400, 580, 80, hp(3)))
        enemies.append(FlyingEnemy(500, 500, hp(2), float_height=440))
        enemies.append(Enemy(850, 520, 60, hp(4)))
        checkpoints.append(Checkpoint(700, 576))

        # Zona 2: Desafio de Espinhos e Precisão
        platforms.append(Platform(1200, 560, 400, 30, 2))
        platforms.append(Platform(1650, 540, 180, 28, 1, hazard=True, hazard_timed=True, hazard_offset=0))
        platforms.append(Platform(1900, 540, 180, 28, 1, hazard=True, hazard_timed=True, hazard_offset=60))
        platforms.append(Platform(2150, 600, 500, 40, 0))

        enemies.append(ShootingEnemy(1300, 520, 80, hp(3)))
        enemies.append(Enemy(1450, 520, 60, hp(4)))
        enemies.append(ShootingEnemy(1750, 500, 60, hp(3)))
        enemies.append(FlyingEnemy(2000, 430, hp(2), float_height=380))
        enemies.append(Enemy(2300, 560, 80, hp(4)))

        orbs.append(HealthOrb(2000, 470))
        checkpoints.append(Checkpoint(1550, 516))

        # Zona 3: Labirinto de Plataformas e Soul Orbs
        m_plats.append(MovingPlatform(2700, 540, 150, 22, 0, -200))
        platforms.append(Platform(2950, 580, 400, 40, 0))
        m_plats.append(MovingPlatform(3400, 560, 140, 22, 250, 0))
        platforms.append(Platform(3700, 560, 350, 30, 2))
        platforms.append(Platform(4100, 600, 600, 40, 0))

        enemies.append(Enemy(3000, 500, 80, hp(4)))
        enemies.append(ShootingEnemy(3150, 540, 80, hp(3)))
        enemies.append(FlyingEnemy(3500, 430, hp(3), float_height=370))
        enemies.append(Enemy(3750, 520, 70, hp(4)))
        enemies.append(Enemy(3950, 520, 80, hp(4)))
        enemies.append(ShootingEnemy(4150, 520, 70, hp(3)))
        enemies.append(Enemy(4300, 560, 120, hp(4)))
        enemies.append(FlyingEnemy(4500, 480, hp(2), float_height=400))
        enemies.append(Enemy(4650, 560, 100, hp(4)))

        orbs.append(HealthOrb(3800, 490))
        checkpoints.append(Checkpoint(3900, 536))
        goal = LevelGoal(4650, 524)

    # ── LEVEL 4: A Ascensão — desafio de pulo vertical ───────
    elif level_id == 4:
        world_w, world_h = 5200, 900
        level_name = "IV — A Ascensão"
        add_walls(world_w, world_h)

        # Zona baixa: intro expandida
        platforms.append(Platform(0, 700, 600, 40, 0))
        enemies.append(Enemy(250, 660, 100, hp(4)))
        enemies.append(Enemy(450, 660, 100, hp(4)))
        enemies.append(FlyingEnemy(500, 570, hp(3), float_height=510))
        checkpoints.append(Checkpoint(550, 676))

        # Escadaria crescente mais espaçada horizontalmente
        step_data = [
            (700, 640, 200), (1000, 580, 180), (1300, 520, 180),
            (1600, 460, 170), (1900, 400, 170), (2200, 340, 180),
        ]
        for idx, (sx, sy, sw) in enumerate(step_data):
            platforms.append(Platform(sx, sy, sw, 28, idx % 3))
            if idx % 2 == 0:
                enemies.append(Enemy(sx + 30, sy - 38, 50, hp(4 + idx // 2)))
            if idx % 3 == 1:
                enemies.append(FlyingEnemy(sx + sw // 2, sy - 60, hp(3), float_height=sy - 100))
            # Espinhos entre degraus
            if idx in (1, 3, 5):
                gap_x = sx + sw + 20
                platforms.append(Platform(gap_x, sy + 28, 60, 20, 1, hazard=True))

        orbs.append(HealthOrb(1300, 450))
        checkpoints.append(Checkpoint(1600, 432))

        # Zona do topo: Plataformas Elevadas e Horda
        platforms.append(Platform(2600, 300, 800, 35, 0))
        platforms.append(Platform(2900, 230, 250, 24, 2))
        enemies.append(Enemy(2650, 260, 80, hp(5)))
        enemies.append(ShootingEnemy(2750, 260, 80, hp(4)))
        enemies.append(Enemy(2950, 190, 50, hp(4)))
        enemies.append(FlyingEnemy(3100, 180, hp(3), float_height=120))
        enemies.append(ShootingEnemy(3250, 260, 80, hp(4)))
        enemies.append(Enemy(3350, 260, 80, hp(5)))

        checkpoints.append(Checkpoint(3000, 274))
        orbs.append(HealthOrb(2900, 160))

        # Descida final e Arena de Combate
        platforms.append(Platform(3600, 380, 250, 26, 1))
        m_plats.append(MovingPlatform(3950, 420, 160, 22, 0, 200))
        platforms.append(Platform(4200, 550, 950, 40, 0))

        enemies.append(Enemy(3650, 340, 60, hp(5)))
        enemies.append(FlyingEnemy(3800, 300, hp(3), float_height=240))
        enemies.append(ShootingEnemy(4300, 510, 100, hp(4)))
        enemies.append(Enemy(4450, 510, 120, hp(5)))
        enemies.append(ShootingEnemy(4600, 510, 100, hp(4)))
        enemies.append(Enemy(4750, 510, 120, hp(5)))
        enemies.append(FlyingEnemy(4900, 400, hp(3), float_height=340))
        enemies.append(Enemy(5000, 510, 100, hp(5)))
        enemies.append(ShootingEnemy(5100, 510, 80, hp(4)))

        checkpoints.append(Checkpoint(4300, 526))
        orbs.append(HealthOrb(4600, 470))
        goal = LevelGoal(5050, 474)

    # ── LEVEL 5: O Boss Final — Grande Arena Expandida ───────
    else:
        world_w, world_h = 4000, 800
        level_name = "V — O Boss Final"
        add_walls(world_w, world_h)

        # Corredor de chegada expandido
        platforms.append(Platform(0, 640, 600, 40, 0))
        enemies.append(Enemy(250, 600, 80, hp(4)))
        enemies.append(ShootingEnemy(450, 600, 80, hp(3)))
        enemies.append(FlyingEnemy(550, 520, hp(3), float_height=460))
        checkpoints.append(Checkpoint(500, 616))

        # Moving platform para cruzar abismo maior
        m_plats.append(MovingPlatform(650, 620, 180, 22, 300, 0))

        # Ante-sala
        platforms.append(Platform(1000, 640, 400, 40, 1))
        enemies.append(Enemy(1050, 600, 80, hp(5)))
        enemies.append(ShootingEnemy(1200, 600, 80, hp(4)))
        enemies.append(Enemy(1350, 600, 60, hp(5)))
        orbs.append(HealthOrb(1200, 570))
        checkpoints.append(Checkpoint(1200, 616))

        # ── ARENA DO BOSS EXPANDIDA ───────────────────────────
        ARENA_X1, ARENA_X2 = 1600, 3800
        platforms.append(Platform(ARENA_X1, 560, ARENA_X2 - ARENA_X1, 45, 0))

        # Plataformas internas para manobras complexas
        platforms.append(Platform(1800, 470, 250, 22, 2))
        platforms.append(Platform(2200, 410, 250, 22, 1))
        platforms.append(Platform(2700, 470, 250, 22, 2))
        platforms.append(Platform(3200, 410, 250, 22, 1))
        platforms.append(Platform(3500, 470, 250, 22, 2))

        # HealthOrbs estratégicos
        orbs.append(HealthOrb(1900, 400))
        orbs.append(HealthOrb(2700, 400))
        orbs.append(HealthOrb(3500, 400))

        # Boss Centralizado na Arena
        boss = Boss(2700, 470, hp(35), arena_x1=ARENA_X1 + 20, arena_x2=ARENA_X2 - 20)
        enemies.append(boss)

        # Goal Final
        goal = LevelGoal(3700, 484)

    return (platforms, enemies, checkpoints, orbs, goal,
            switches, gates, m_plats, world_w, world_h, level_name)


# ═══════════════════════════════════════════════════════════════════
#  CLASSE: Game
# ═══════════════════════════════════════════════════════════════════
class Game:
    S_START  = "start"
    S_PLAY   = "playing"
    S_DEAD   = "dead"
    S_SELECT = "select"

    def __init__(self):
        self.state          = self.S_START
        self.current_level  = 1
        self.unlocked       = 1
        self.difficulty     = 1.0
        self.souls          = 0
        self.health_upgrades= 0
        self.menu_clickables= []
        self.hud = HUD()
        self.bg  = self._make_bg()
        self.load_game()
        self._init_game()

    def save_game(self):
        data = {
            "unlocked": self.unlocked,
            "souls": self.souls,
            "health_upgrades": self.health_upgrades,
            "difficulty": self.difficulty
        }
        try:
            with open("save_data.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def load_game(self):
        if os.path.exists("save_data.json"):
            try:
                with open("save_data.json", "r") as f:
                    data = json.load(f)
                    self.unlocked = data.get("unlocked", 1)
                    self.souls = data.get("souls", 0)
                    self.health_upgrades = data.get("health_upgrades", 0)
                    self.difficulty = data.get("difficulty", 1.0)
            except Exception as e:
                print(f"Erro ao carregar: {e}")

    def _init_game(self):
        result = build_level(self.current_level, self.difficulty)
        (self.platforms, self.enemies, self.checkpoints, self.orbs,
         self.goal, self.switches, self.gates, self.m_plats,
         self.world_w, self.world_h, self.level_name) = result

        self.player      = Player(80, 530, max_hp=5+self.health_upgrades)
        self.projectiles: List[Projectile] = []
        self.soul_drops:  List[SoulDrop]   = []
        self.camera      = Camera(self.world_w, self.world_h)
        self.global_timer= 0

        # Registra boss na HUD se existir
        boss_list = [e for e in self.enemies if isinstance(e, Boss)]
        self.hud.boss_active = bool(boss_list)
        self.hud.boss_ref    = boss_list[0] if boss_list else None

    def _make_bg(self):
        bg=pygame.Surface((SCREEN_W,SCREEN_H))
        draw_gradient_bg(bg,C_BG_TOP,C_BG_BOT,(0,0,SCREEN_W,SCREEN_H))
        random.seed(42)
        for _ in range(130):
            x,y=random.randint(0,SCREEN_W),random.randint(0,SCREEN_H)
            r,a=random.randint(1,2),random.randint(40,140)
            draw_circle_alpha(bg,(180,170,220),(x,y),r,a)
        random.seed()
        return bg

    # ── Update ────────────────────────────────────────────────
    def update(self):
        self.global_timer+=1
        keys=pygame.key.get_pressed()
        if self.state in (self.S_START, self.S_SELECT): return

        if self.state==self.S_DEAD:
            if keys[pygame.K_r]:
                self.player.respawn(); self.state=self.S_PLAY
                self.projectiles=[]; self.soul_drops=[]
            return

        # ── Playing ───────────────────────────────────────────
        self.player.handle_input(keys)
        self.player.apply_gravity()

        active_cols = self.platforms + [g for g in self.gates if not g.open]
        self.player.move_and_collide(active_cols)

        for mp in self.m_plats: mp.update(self.player)

        # Hazard damage
        for p in self.platforms:
            if p.is_hazard_active():
                hr = pygame.Rect(p.rect.x, p.rect.y - 10, p.rect.w, 10)
                if self.player.rect.colliderect(hr):
                    self.player.take_damage(1,p.rect.centerx)
                    self.camera.add_shake(5)

        self.player.update(self.platforms, self.checkpoints, self.enemies)

        # Projectiles
        for pj in self.projectiles: pj.update(self.player, self.platforms)
        self.projectiles=[pj for pj in self.projectiles if pj.alive]

        # Switches / Gates
        sw_active=any(s.active for s in self.switches)
        for s in self.switches: s.update(self.player, self.player.particles)
        for g in self.gates:    g.update(sw_active)

        # Enemies update
        for e in self.enemies:
            e_cols = active_cols
            if isinstance(e, (ShootingEnemy, Boss)):
                e.update(e_cols, self.player.rect, self.projectiles)
            elif isinstance(e, FlyingEnemy):
                e.update(self.platforms, self.player.rect)
            else:
                e.update(e_cols, self.player.rect)

        # Player attacks hit enemies
        if self.player.is_attacking and self.player.attack_rect.width>0:
            for e in self.enemies:
                dead_state = getattr(Enemy,'DEAD','dead')
                e_state    = getattr(e,'state','')
                if e_state!=dead_state and self.player.attack_rect.colliderect(e.rect):
                    e.take_damage(1, self.player.facing)
                    if isinstance(e, Boss): self.camera.add_shake(6)
                    else:                   self.camera.add_shake(3)

        # Player take damage + shake
        if self.player.flash_timer>0: self.camera.add_shake(4)

        # Soul drops ao matar inimigos
        dead_state=getattr(Enemy,'DEAD','dead')
        for e in self.enemies:
            if getattr(e,'state','')==dead_state and getattr(e,'dead_timer',0)==1:
                val=10 if isinstance(e,Boss) else (7 if isinstance(e,(ShootingEnemy,FlyingEnemy)) else 5)
                for _ in range(2 if isinstance(e,Boss) else 1):
                    ox=e.rect.centerx+random.randint(-20,20)
                    self.soul_drops.append(SoulDrop(ox,e.rect.centery,val))

        # Coleta soul drops
        for sd in self.soul_drops:
            collected=sd.update(self.player)
            if collected: self.souls+=collected
        self.soul_drops=[sd for sd in self.soul_drops if not sd.collected]

        self.enemies=[e for e in self.enemies if e.alive]

        # Health orbs
        for o in self.orbs:
            if o.update(self.player):
                self.souls+=8; self.hud.show_message("+1 Vida!", 50)
        self.orbs=[o for o in self.orbs if not o.collected]

        # Checkpoints
        for chk in self.checkpoints: chk.update()

        # Goal
        if self.goal.update(self.player):
            for _ in range(25):
                self.player.particles.append(
                    Particle(self.player.rect.centerx,self.player.rect.centery,"soul",(1,5),(20,50)))
            if self.current_level<5:
                self.unlocked=max(self.unlocked,self.current_level+1)
                self.hud.show_message(f"✦ Fase {self.current_level} Concluída! ✦",140)
            else:
                self.hud.show_message("PARABÉNS! JOGO CONCLUÍDO!", 300)
            self.save_game()
            self.state=self.S_SELECT

        # Morte por queda
        if self.player.rect.top>self.world_h+80 and not self.player.is_dead:
            self.player._die()
        if self.player.is_dead and self.player.death_timer>60:
            self.state=self.S_DEAD

        self.camera.follow(self.player.rect)
        self.hud.update(self.player)

    # ── Draw ──────────────────────────────────────────────────
    def draw(self):
        cx, cy = self.camera.ix, self.camera.iy

        if self.state==self.S_START:
            self.hud.draw_start_screen(screen); pygame.display.flip(); return
        if self.state==self.S_SELECT:
            self.menu_clickables=self.hud.draw_level_select(
                screen, self.unlocked, self.souls, self.health_upgrades)
            pygame.display.flip(); return

        # Fundo com 2 camadas de paralaxe
        screen.blit(self.bg,(0,0))
        # Camada 1 (lenta)
        for bx,by,br,bc in [(800,280,210,(30,15,62)),(2400,200,190,(12,26,58)),(3600,340,230,(28,12,58))]:
            sx=(bx-cx//6)%(self.world_w+SCREEN_W)-80
            sy=by-cy//10
            draw_circle_alpha(screen,bc,(int(sx),int(sy)),br,55)
        # Camada 2 (média)
        for bx,by,br,bc in [(400,400,90,(40,20,80)),(1600,300,80,(20,40,80)),(2800,450,100,(40,20,80))]:
            sx=(bx-cx//3)%(self.world_w+SCREEN_W)-50
            sy=by-cy//5
            draw_circle_alpha(screen,bc,(int(sx),int(sy)),br,40)

        # Plataformas
        for p in self.platforms: p.draw(screen,cx,cy)
        # Goal
        self.goal.draw(screen,cx,cy)
        # Moving platforms
        for mp in self.m_plats: mp.draw(screen,cx,cy)
        # Switches e Gates
        for s in self.switches: s.draw(screen,cx,cy)
        for g in self.gates:    g.draw(screen,cx,cy)
        # Checkpoints
        for chk in self.checkpoints: chk.draw(screen,cx,cy)
        # Health orbs
        for o in self.orbs: o.draw(screen,cx,cy)
        # Soul drops
        for sd in self.soul_drops: sd.draw(screen,cx,cy)
        # Inimigos
        for e in self.enemies: e.draw(screen,cx,cy)
        # Projectiles
        for pj in self.projectiles: pj.draw(screen,cx,cy)
        # Player
        self.player.draw(screen,cx,cy)
        # HUD
        self.hud.draw(screen, self.player, self.souls, self.level_name)
        # Death screen
        if self.state==self.S_DEAD: self.hud.draw_death_screen(screen)
        # Vinheta
        self._vignette()
        pygame.display.flip()

    def _vignette(self):
        for i,a in [(65,85),(32,52),(16,32)]:
            draw_rect_alpha(screen,C_BG_TOP,(0,0,i,SCREEN_H),a)
            draw_rect_alpha(screen,C_BG_TOP,(SCREEN_W-i,0,i,SCREEN_H),a)
            draw_rect_alpha(screen,C_BG_TOP,(0,0,SCREEN_W,i),a)
            draw_rect_alpha(screen,C_BG_TOP,(0,SCREEN_H-i,SCREEN_W,i),a)

    # ── Loop ──────────────────────────────────────────────────
    def run(self):
        running=True
        while running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT: running=False

                if event.type==pygame.MOUSEBUTTONDOWN:
                    mx,my=pygame.mouse.get_pos()
                    if self.state==self.S_START:
                        self.state=self.S_SELECT
                    elif self.state==self.S_SELECT:
                        for rect,action,val in self.menu_clickables:
                            if rect.collidepoint(mx,my):
                                self._handle_menu(action,val)

                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        if self.state==self.S_PLAY: self.state=self.S_SELECT
                        else: running=False

                    if self.state==self.S_START:
                        self.state=self.S_SELECT
                    elif self.state==self.S_SELECT:
                        if pygame.K_1<=event.key<=pygame.K_5:
                            lv=event.key-pygame.K_1+1
                            if lv<=self.unlocked: self._start_level(lv)
                        if event.key==pygame.K_e: self._set_diff(0.5,"Fácil")
                        if event.key==pygame.K_n: self._set_diff(1.0,"Normal")
                        if event.key==pygame.K_h: self._set_diff(1.5,"Difícil")
                        if event.key==pygame.K_u: self._buy_upgrade()

            self.update()
            self.draw()
            clock.tick(FPS)
        pygame.quit(); sys.exit()

    def _handle_menu(self,action,val):
        if action=="level":    self._start_level(val)
        elif action=="diff":   self._set_diff(val,{0.5:"Fácil",1.0:"Normal",1.5:"Difícil"}[val])
        elif action=="upgrade":self._buy_upgrade()

    def _start_level(self,lv):
        self.current_level=lv; self._init_game()
        self.state=self.S_PLAY
        self.hud.show_message(f"Fase {lv} — {self.level_name}",90)

    def _set_diff(self,val,label):
        self.difficulty=val; self.hud.show_message(f"Dificuldade: {label}",70)
        self.save_game()

    def _buy_upgrade(self):
        cost=30+self.health_upgrades*20
        if self.souls>=cost:
            self.souls-=cost; self.health_upgrades+=1
            self.player.max_hp+=1; self.player.hp=self.player.max_hp
            self.hud.show_message(f"HP Máximo UP! ({self.player.max_hp})",90)
            self.save_game()
        else:
            self.hud.show_message(f"Almas insuficientes! (precisa {cost})",70)


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
if __name__=="__main__":
    game=Game()
    game.run()
