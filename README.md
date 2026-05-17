# doidera-minha

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

### 3. Rodar o jogo
```bash
python3 scft.py
```

---

## 🎮 Controles

| Tecla | Ação |
|-------|------|
| `A` `D` | Mover |
| `W`, `Espaço` ou `Z` | Pular (Pulo Duplo no Ar) |
| `Shift` | Dash (Invencível) |
| `X` ou `M1` | Atacar (Combo) |
| `R` | Renascer após morte |
| `ESC` | Menu de Fases / Sair |
| `K` | Resetar Progresso (no Menu) |

---

## 🧩 Mecânicas Implementadas (v2.0)

- ✅ **Sistema de Salvamento:** Progresso, almas e upgrades persistentes em JSON.
- ✅ **Dash Direcional:** Com frames de invencibilidade e rastro visual.
- ✅ **Pulo Duplo:** Maior mobilidade aérea.
- ✅ **Múltiplos Níveis:** 5 fases expandidas com novos biomas e desafios.
- ✅ **Boss Final:** Arena complexa com boss de 3 fases e ataques variados.
- ✅ **Upgrades:** Sistema de compra de vida extra usando almas coletadas.
- ✅ **IA Aprimorada:** Inimigos terrestres e voadores com detecção de borda e mergulho.
- ✅ **Efeitos Visuais:** Fade-in global, screen-shake, paralaxe em 2 camadas e vinheta.

---

## 🗺️ Mapa da Fase

```
[Início] → [Gap] → [Checkpoint 1] → [Escalada] → [Planalto]
         → [Checkpoint 2] → [Caverna] → [Checkpoint 3] → [Área Final]
```

Total de ~4500px de largura com:
- 18+ plataformas em alturas variadas
- 13 inimigos posicionados estrategicamente
- 3 checkpoints de respawn

---

## 🏗️ Estrutura do Código

```
shadowcroft.py
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
  
