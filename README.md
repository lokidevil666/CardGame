# Scoundrel Roguelike (Pygame)

Jogo de cartas em Python/Pygame inspirado no conceito de Scoundrel, com estrutura roguelike.

## Regras usadas

- Baralho normal de 52 cartas.
- Espadas e paus sao criaturas.
- Copas sao pocoes de cura.
- Ouros sao espadas para defesa.
- Objetivo: sobreviver ate acabar o baralho.

## Interacao das cartas

- Hover do rato: carta sobe e aumenta ligeiramente.
- Click: carta executa animacao curta e resolve acao.
- Cada click bloqueia input por um instante para animacao de resolucao.

## Como correr

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Controlos

- `ENTER` ou click no botao para iniciar.
- `ESC` no combate para voltar ao menu.
- `R` para reiniciar run.
- No ecras final:
  - `R` nova run
  - `M` menu
  - `ESC` sair

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
    card_sprite.py
  scenes/
    base_scene.py
    menu_scene.py
    combat_scene.py
    end_scene.py
```
