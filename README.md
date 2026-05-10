# 🕹️ ShadowCroft — Protótipo 2D Platformer v2.0

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
| `W`, `Z` ou `Espaço` | Pular (segure para pular mais alto | Duplo pulo no ar) |
| `SHIFT` | Dash direcional (invencível durante o dash) |
| `X` ou `M1` | Atacar (combo de 2 golpes) |
| `R` | Renascer após morte |
| `ESC` | Menu de fases |

---

## 🧩 Mecânicas v2.0 Implementadas

- ✅ Movimento lateral fluido com aceleração/desaceleração
- ✅ Pulo responsivo com altura variável e **Duplo Pulo**
- ✅ **Dash Direcional** com frames de invencibilidade e rastro visual
- ✅ **Coyote Time** e **Jump Buffer** para precisão no platforming
- ✅ Ataque corpo a corpo com combo e feedback visual (screenshake)
- ✅ Inimigos com IA variada: Patrulha, Atiradores e **Inimigos Voadores**
- ✅ **Boss Final** com 3 fases de comportamento e telegraphing visual
- ✅ Sistema de **Almas (Souls)**: Dropadas por inimigos para comprar upgrades
- ✅ Sistema de **Persistência**: Salva progresso, almas e upgrades em `save_data.json`
- ✅ 5 Fases expandidas com desafios crescentes e puzzles (switches/gates)
- ✅ Checkpoints em todas as fases
- ✅ HUD moderna com barra de dash e contador de almas
- ✅ Efeito global de **Fade-in** ao entrar nas fases
- ✅ Câmera suave com sistema de screenshake para impactos

---

## 🏗️ Estrutura do Código

```
scft.py
├── Particle         — Efeitos visuais (dust, hit, soul, etc.)
├── SoulDrop         — Sistema de coleta de almas
├── Platform         — Plataformas com suporte a hazards (espinhos)
├── MovingPlatform   — Plataformas móveis sincronizadas
├── Checkpoint       — Pontos de salvamento e respawn
├── Enemy/Boss       — Inimigos com máquina de estados (PATROL, CHASE, ATTACK, etc.)
├── Player           — Personagem com mecânicas avançadas (Dash, Double Jump)
├── Camera           — Câmera com interpolação e shake
├── HUD              — Interface dinâmica e menus
├── build_level()    — Geração procedural/estática de 5 levels expandidos
└── Game             — Gerenciamento de estados, persistência e loop principal
```

---

## 📦 Dependências

```
pygame>=2.0.0
```
