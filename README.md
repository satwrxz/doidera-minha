# 🕹️ ShadowCroft — Metroidvania Atmosférico v2.0

ShadowCroft é um protótipo de jogo 2D atmosférico inspirado em mecânicas clássicas de metroidvania, desenvolvido com **Python + Pygame**.

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
| `A` `D` / `←` `→` | Mover lateralmente |
| `W` / `Z` / `Espaço` | Pular / Duplo Pulo (segure para pular mais alto) |
| `X` / `Clique Esquerdo` | Atacar (Combo de 2 golpes) |
| `Shift` | Dash Direcional (invencível durante o uso) |
| `R` | Renascer após morte |
| `ESC` | Abrir Seleção de Fases / Sair |
| `K` | Resetar progresso (na tela de seleção) |

---

## 🧩 Novidades da Versão 2.0

- ✅ **Sistema de Persistência:** Progresso salvo automaticamente em JSON.
- ✅ **Movimentação Avançada:** Dash direcional e Duplo Pulo.
- ✅ **Combate Refinado:** Combo de ataques e inimigos voadores.
- ✅ **Boss Final:** Encontro épico com 3 fases de comportamento.
- ✅ **Mundo Expandido:** 5 níveis redesenhados com novos desafios e segredos.
- ✅ **Atmósfera:** Efeitos de fade-in, partículas de alma e paralaxe aprimorado.
- ✅ **Customização:** Sistema de upgrades de HP e seleção de dificuldade.

---

## 🏗️ Estrutura do Código

```
scft.py
├── Particle         — Efeitos visuais (hit, death, dash, soul)
├── SoulDrop         — Sistema de moedas/experiência
├── Enemy / Boss     — IA de combate terrestre, aéreo e padrões de chefão
├── Player           — Física avançada, dash e gerenciamento de estado
├── Persistence      — Sistema de save/load via JSON
└── build_level()    — Gerador de cenários procedurais e estáticos
```

---

## 📦 Dependências

```
pygame>=2.0.0
```
