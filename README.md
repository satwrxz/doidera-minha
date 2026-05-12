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
python scft.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `←` `→` / `A` `D`| Mover |
| `W`, `Z` ou `Espaço` | Pular (segure para pular mais alto | Duplo pulo no ar) |
| `Shift` | Dash (invencível durante o movimento) |
| `X` ou `M1` | Atacar (combo de 2 golpes) |
| `R` | Renascer após morte |
| `ESC` | Menu de fases |

---

## 🧩 Mecânicas Implementadas (v2.0)

- ✅ **Sistema de Persistência**: Progresso salvo automaticamente (níveis, almas, upgrades).
- ✅ **Dash Direcional**: Esquiva com frames de invencibilidade e rastro visual.
- ✅ **Duplo Pulo**: Maior mobilidade aérea.
- ✅ **Sistema de Almas**: Inimigos dropam almas para comprar upgrades de vida.
- ✅ **Múltiplos Níveis**: 5 fases com designs únicos e desafios crescentes.
- ✅ **Boss Final**: Combate épico com múltiplas fases e padrões de ataque.
- ✅ **Fade-In Global**: Transições suaves ao iniciar as fases.
- ✅ **Níveis Expandidos**: Mapas com até 5200px de largura e maior densidade de inimigos.

---

## 🏗️ Estrutura do Código

```
scft.py
├── Particle         — Efeitos visuais de partícula
├── Platform         — Plataformas sólidas do cenário
├── Checkpoint       — Pontos de salvamento interativos
├── Enemy            — Inimigo com máquina de estados
│   ├── PATROL       — Patrulha entre pontos
│   ├── CHASE        — Perseguição ao player
│   ├── ATTACK       — Golpe corpo a corpo
│   ├── HURT         — Knockback ao tomar dano
│   └── DEAD         — Animação de morte
├── Player           — Personagem principal
│   ├── handle_input — Processa teclado
│   ├── apply_gravity — Física vertical
│   ├── move_and_collide — Movimento + colisões
│   └── draw         — Renderiza sprite geométrico
├── Camera           — Câmera suave com limites
├── HUD              — Interface (vida, mensagens)
├── build_level()    — Constrói o mapa da fase
└── Game             — Loop principal e estados
```

---

## 🔧 Expandindo o Projeto

Ideias para próximos passos:
- [ ] Múltiplas fases com transições
- [ ] Habilidade de dash
- [ ] Inimigos voadores
- [ ] Itens coletáveis / moeda
- [ ] Boss com fases de comportamento
- [ ] Sistema de upgrades
- [ ] Sons e música (pygame.mixer)
- [ ] Salvar progresso em arquivo JSON

---

## 📦 Dependências

```
pygame>=2.0.0
```
  
