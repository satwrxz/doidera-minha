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
| `←` `→` (ou A/D) | Mover |
| `W`, `Z` ou `Espaço` | Pular (segure para mais alto | duplo pulo no ar) |
| `X` ou Clique M1 | Atacar (Combo de 2 golpes) |
| `Shift` | Dash direcional (Invencível) |
| `R` | Renascer após morte |
| `ESC` | Voltar ao Menu / Sair |

---

## 🧩 Mecânicas Implementadas

- ✅ Movimento lateral fluido com aceleração/desaceleração
- ✅ Pulo responsivo com altura variável (hold para mais alto)
- ✅ **Coyote Time** (pode pular por alguns frames após sair de plataforma)
- ✅ **Jump Buffer** (input de pulo antecipado é registrado)
- ✅ Gravidade e colisão com plataformas
- ✅ Ataque corpo a corpo com hitbox e animação de slash
- ✅ Inimigos com IA: Patrol → Chase → Attack
- ✅ Sistema de vida (player: 5 HP, inimigos: 3–7 HP)
- ✅ Knockback ao receber dano
- ✅ Invencibilidade temporária após dano (pisca o sprite)
- ✅ 3 Checkpoints com efeito visual e save de posição
- ✅ HUD com corações animados
- ✅ Partículas em golpes, dano, morte, poeira, etc.
- ✅ Câmera suave seguindo o player
- ✅ Tela de morte e reinício

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
  
