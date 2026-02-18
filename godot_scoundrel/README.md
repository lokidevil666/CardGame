# Scoundrel Roguelike - Godot 4 + C#

Esta pasta contem uma versao do jogo refeita em **Godot 4 com C#**.

## Funcionalidades implementadas

- Regras oficiais de Scoundrel (modo original):
  - HP inicial 20
  - remove ases/figuras vermelhas (copas e ouros A/J/Q/K)
  - sala com 4 cartas, resolves 3 e deixas 1
  - evitar sala sem repetir duas vezes seguidas
  - 1 pocao por sala
  - regra de limite da arma pelo ultimo monstro abatido com ela
- Layout pedido:
  - deck no topo
  - 4 cartas de jogo no centro
  - espada equipada em baixo
- Animacao de cartas a deslizar do deck para os slots da sala
- Seed personalizada (ou aleatoria) e copia para clipboard
- Fullscreen com F11

## Como abrir

1. Instala **Godot .NET 4.2.x** (nao usar build standard sem C#).
2. Instala **.NET SDK 6.0**.
3. Abre a pasta `godot_scoundrel` no Godot.
4. Se o editor pedir, aceita criar/restaurar a solucao C#.
5. Corre a cena principal.

Cena principal:

- `res://scenes/Main.tscn`

## Troubleshooting rapido

Se nao iniciar, verifica:

1. **Godot certo**  
   No titulo da app deve aparecer `.NET` (ex.: `Godot_v4.2.x-stable_mono`).

2. **SDK dotnet instalado**  
   No terminal:

   ```bash
   dotnet --list-sdks
   ```

   Deve aparecer uma linha `6.0.x`.

3. **Abriste a pasta correta**  
   Abre `.../godot_scoundrel` (nao a raiz do repositorio).

4. **Rebuild da solucao C#**  
   No Godot: `Project -> Tools -> C# -> Create C# Solution` (se necessario) e depois `Build`.

## Controlos

- **Menu**
  - Enter: iniciar run
  - Ctrl+C: copiar seed
- **Combate**
  - Clique esquerdo em monstro: tenta usar arma
  - Clique direito em monstro: combate de mao nua
  - A: evitar sala (quando permitido)
  - C: copiar seed
  - R: reiniciar com mesma seed
- **Global**
  - F11: fullscreen
