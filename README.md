# 🕹️ ShadowCroft — Protótipo 2D Metroidvania v2.0

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

### 3. Rodar o jogo
```bash
python3 scft.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `A` `D` | Mover |
| `W`, `Espaço` ou `Z` | Pular (segure para pular mais alto | duplo pulo no ar) |
| `Shift` | Dash direcional (invencível, 2s cooldown) |
| `X` ou `M1` | Atacar (combo de 2 golpes) |
| `R` | Renascer após morte |
| `ESC` | Menu de fases |

---

## 🧩 Mecânicas v2.0 Implementadas

- ✅ **Sistema de Persistência**: Salva progresso, almas e upgrades em JSON.
- ✅ **Dash & Duplo Pulo**: Movimentação avançada para exploração.
- ✅ **Transição Suave**: Efeito de fade-in global ao entrar nos níveis.
- ✅ **IA Aprimorada**: Inimigos que saltam plataformas durante perseguição.
- ✅ **Boss Final**: Encontro épico com 3 fases e mecânicas únicas.
- ✅ **Coyote Time & Jump Buffer**: Controles extremamente responsivos.
- ✅ **Sistema de Upgrades**: Use almas para aumentar sua vida máxima.
- ✅ **Dificuldade Ajustável**: Escolha entre Fácil, Normal e Difícil.
- ✅ **Mundo Expandido**: 5 levels redesenhados com novos desafios e segredos.

---

## 🏗️ Estrutura do Código

```
scft.py
├── Particle         — Efeitos visuais de partícula
├── Platform         — Plataformas sólidas e espinhos timed
├── Checkpoint       — Pontos de salvamento e respawn
├── Enemy            — IA básica com patrulha, chase e salto
├── FlyingEnemy      — Inimigo voador com mergulho
├── ShootingEnemy    — Inimigo à distância
├── Boss             — Boss com fases e múltiplos ataques
├── Player           — Protagonista com dash, combo e duplo pulo
├── Camera           — Câmera com interpolação e screenshake
├── HUD              — Interface de vida, dash, boss e almas
├── build_level()    — Geração dos layouts expandidos (v2.0)
└── Game             — Máquina de estados principal e persistência
```
