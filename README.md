# Scoundrel Roguelike (Pygame)

Jogo de cartas em Python/Pygame com regras oficiais de **Scoundrel**.

## Regras (Scoundrel oficial)

- Setup original:
  - remover jokers, ases vermelhos e figuras vermelhas (copas/ouros A, J, Q, K)
  - vida inicial: 20
- Paus e espadas = monstros (A=14, J=11, Q=12, K=13)
- Copas = pocoes (so podes usar 1 por sala)
- Ouros = armas (arma nova substitui a antiga)
- Cada sala tem 4 cartas:
  - podes **evitar** a sala (nao podes evitar duas seguidas)
  - se nao evitares, escolhes 3 cartas e deixas 1 para a sala seguinte
- Combate com arma:
  - dano recebido = `max(0, monstro - arma)`
  - depois de usar arma num monstro, ela so pode ser usada em monstros com valor menor/igual ao ultimo abatido com arma

## Interacao das cartas

- Hover do rato: carta sobe e aumenta ligeiramente.
- Click: carta executa animacao curta e resolve acao.
- Cada click bloqueia input por um instante para animacao de resolucao.
- Cartas com visual pixel art e icones por tipo (`assets/icons`).

## Como correr

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Regenerar assets pixel art (opcional)

Se quiseres refazer os icones:

```bash
python3 scripts/generate_assets.py
```

## Controlos

- Menu:
  - escreve seed (opcional)
  - `ENTER` inicia run
  - `CTRL+C` copia seed do campo
- Combate:
  - `A` evita sala (quando permitido)
  - click esquerdo em monstro = tenta usar arma
  - click direito em monstro = luta de mao nua
  - `C` copia seed atual
  - `R` reinicia com mesma seed
  - `ESC` volta ao menu
- Global:
  - `F11` alterna fullscreen

## Estrutura

```text
main.py
game/
  constants.py
  game_app.py
  models/
    card.py
    deck.py
    player.py
  systems/
    assets.py
    card_sprite.py
  scenes/
    base_scene.py
    menu_scene.py
    combat_scene.py
    end_scene.py
assets/
  icons/ (monster, potion, weapon)
scripts/
  generate_assets.py
```
