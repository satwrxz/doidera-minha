# doidera-minha

# 🕹️ ShadowCroft — Protótipo 2D Platformer

Jogo 2D atmosférico inspirado em mecânicas de metroidvania, desenvolvido com **Python + Pygame**.

---

## ⚙️ Como Instalar e Rodar

### 1. Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### 2. Instalar dependência
```bash
pip install pygame
```

> Se usar Python 3.10+:
> ```bash
> pip install pygame --upgrade
> ```

### 3. Rodar o jogo
```bash
python3 scft.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `A` `D` | Mover |
| `W` `Z` ou `Espaço` | Pular / Duplo Pulo |
| `Shift` | Dash (invencibilidade temporária) |
| `X` ou `M1` | Atacar (combo) |
| `R` | Renascer após morte |
| `ESC` | Menu de fases |

---

## 🧩 Mecânicas v2.0 Implementadas

- ✅ **Persistência JSON**: Progresso, almas e upgrades salvos automaticamente.
- ✅ **Dash Direcional**: Movimento rápido com frames de invencibilidade.
- ✅ **Pulo Duplo**: Maior agilidade aérea.
- ✅ **IA Aprimorada**: Inimigos saltam vãos em perseguição.
- ✅ **Inimigos Voadores**: FlyingEnemy com comportamento de mergulho.
- ✅ **Sistema de Almas**: Colete almas ao derrotar inimigos para comprar upgrades.
- ✅ **Boss Multi-fase**: O Boss Final com 3 padrões de ataque distintos.
- ✅ **Coyote Time & Jump Buffer**: Controles ultra-responsivos.
- ✅ **Efeitos Visuais**: Fade global, parallax em 2 camadas e screen-shake.
- ✅ **5 Níveis Expandidos**: Mapas de até 5200px com puzzles e segredos.

---

## 🗺️ Progressão

```
Level I → Level II → Level III (Puzzles) → Level IV (Ascensão) → Level V (Boss)
```

Total de 5 fases ricas em conteúdo e desafios variados.

---

## 🏗️ Estrutura do Código

```
scft.py
├── Particle         — Sistema de partículas dinâmicas
├── SoulDrop         — Sistema de coleta e economia (Almas)
├── Platform         — Plataformas sólidas e perigos (espinhos)
├── Enemy variants   — Enemy (Melee), ShootingEnemy (Ranged), FlyingEnemy (Air), Boss
├── Player           — Movimentação, Dash, Combate e Estados
├── Camera           — Smooth follow com Screen Shake
├── HUD              — Vida, Almas, Barra de Dash e Boss HP
├── build_level()    — Gerador de mapas v2.0
└── Game             — Engine principal, Estados e Persistência
```

---

## 📦 Dependências

```
pygame>=2.0.0
```

---

## 📦 Dependências

```
pygame>=2.0.0
```
  
