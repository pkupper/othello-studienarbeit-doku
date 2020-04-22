```python
%%HTML
<style>
.container { width:100% }
</style>
```

# Implementation der Grafischen Benutzeroberfläche

Im folgenden Abschnitt wird eine Benutzeroberfläche für das Spiel Othello implementiert.

## Importieren der externen Abhängigkeiten

Die Grafische Benutzeroberfläche verwendet zur Darstellung des Spielzustandes, zum Anzeigen weiterer Informationen sowie für die Benutzerinteraktion die Bibliotheken `ipycanvas` und `ipywidgets`. Diese Lassen sich direkt im Jupyter Notebook verwenden.

Zusätzlich werden aus dem Paket `math` der Python Standardbibliothek die Variable `pi` sowie die Funktion `floor` benötigt.


```python
import ipycanvas
import ipywidgets
import math
from ipywidgets import RadioButtons, HBox, VBox, IntSlider, Label
```

## Globale Konstanten

## Canvas Initialisieren

`SHOW_FRONTIER` gibt an ob in der Visualisierung leere Felder, die an bereits gesetzte Spielsteine angrenzen hervorgehoben werden sollen.


`SHOW_POSSIBLE_MOVES` gibt ob für den aktuell ziehenden Spieler mögliche Züge visualisiert werden sollen.


```python
SHOW_FRONTIER = False
SHOW_POSSIBLE_MOVES = True
```


```python
CELL_SIZE = 60

CANVAS_SIZE = BOARD_SIZE * CELL_SIZE

canvas = ipycanvas.MultiCanvas(2, width=CANVAS_SIZE, height=CANVAS_SIZE)
canvas[0].fill_style = 'darkgreen'
canvas[0].stroke_style = 'black'
canvas[0].fill_rect(0, 0, CANVAS_SIZE, CANVAS_SIZE)
canvas[0].begin_path()
for i in range(BOARD_SIZE+1):
    pos = i * CELL_SIZE
    canvas[0].move_to(pos, 0)
    canvas[0].line_to(pos, CANVAS_SIZE)
    canvas[0].move_to(0, pos)
    canvas[0].line_to(CANVAS_SIZE, pos)
canvas[0].stroke()
```

## Widgets Initialisieren

Das `score_lbl` Widget enthält die Steinzahl beider Spieler im aktuellen Spielzustand


```python
score_lbl = ipywidgets.widgets.Label()
```

Das `turn_lbl` Widget nennt den Spieler, der gerade am Zug ist


```python
turn_lbl = ipywidgets.widgets.Label()
```

Das `output` Widget macht die Ausgabe mithilfe von `print()`, sowie die Ausgabe von Fehlermeldungen trotz der Verwendung von IPyWidgets und IPyCanvas möglich.


```python
output = ipywidgets.widgets.Output()
```


```python
utility_lbl = ipywidgets.widgets.Label()
```

Die Funktion `display_board` stellt den angegebenen Spielzustand dar, indem zunächst der Canvas aktualisiert, und dann zusammen mit den Status-Widgets angezeigt wird.


```python
def display_board(state):
    output.clear_output()
    update_output(state)
    display(canvas)
    display(score_lbl)
    display(turn_lbl)
    display(utility_lbl)
    display(output)
```

In der Funktion `update_output` wird der Spielzustand `state` auf den Canvas gezeichnet.


```python
def update_output(state):
    with ipycanvas.hold_canvas(canvas):
        canvas[1].clear()
        for ((x, y), val) in numpy.ndenumerate(state.board):
            if val == NONE:
                continue
            elif val == BLACK:
                canvas[1].fill_style = 'black'
            else:
                canvas[1].fill_style = 'white'
            canvas[1].fill_arc((x + 0.5) * CELL_SIZE, (y + 0.5)
                               * CELL_SIZE, CELL_SIZE / 2.2, 0, 2 * math.pi)

        if state.last_move != None:
            (x, y) = state.last_move
            canvas[1].stroke_style = 'red'
            canvas[1].line_width = 2
            canvas[1].stroke_arc((x + 0.5) * CELL_SIZE, (y + 0.5)
                               * CELL_SIZE, CELL_SIZE / 2.2, 0, 2 * math.pi)

        if SHOW_FRONTIER:
            for (x, y) in state.frontier:
                canvas[1].fill_style = 'gray'
                canvas[1].fill_arc((x + 0.5) * CELL_SIZE, (y + 0.5)
                                   * CELL_SIZE, CELL_SIZE / 6, 0, 2 * math.pi)

        if SHOW_POSSIBLE_MOVES:
            for (x, y) in get_possible_moves(state, state.turn):
                if state.turn == BLACK:
                    canvas[1].fill_style = 'black'
                else:
                    canvas[1].fill_style = 'white'
                canvas[1].fill_arc((x + 0.5) * CELL_SIZE, (y + 0.5)
                                   * CELL_SIZE, CELL_SIZE / 6, 0, 2 * math.pi)

    b_score = count_disks(state, BLACK)
    w_score = count_disks(state, WHITE)
    score_lbl.value = f'Black Player : {b_score} White Player : {w_score}'
    b_util = utilities[BLACK]
    w_util = utilities[WHITE]
    utility_lbl.value = f'Utility: Black: {b_util} / White: {w_util}'
    if state.game_over:
        turn_lbl.value = f'{get_player_string(get_utility(state))} wins'
    else:
        turn_lbl.value = f'{get_player_string(state.turn)}s Move'
```

Für den menschlichen Spieler ist es nötig festzustellen, ob dieser auf das Spielfeld geklickt hat, dies geschieht in der callback funktion `mouse_down` welche die x und y Koordinaten des Mausklicks relativ zum Canvas erhält. Auf Basis dieser Position wird, falls möglich, ein Zug auf das angeklickte Feld gemacht. Die Funktion wird durch den aufruf von `Canvas.on_mouse_down` bei IPyCanvas als Callback Funktion registriert.


```python
def mouse_down(x_px, y_px):
    if not state.game_over:
        with output:
            x = math.floor(x_px / CELL_SIZE)
            y = math.floor(y_px / CELL_SIZE)
            try:
                make_move(state, (x, y))
            except InvalidMoveException:
                print('Invalid Move')
            update_output(state)
            try:
                next_move(state)
            except KeyboardInterrupt:
                pass


canvas[1].on_mouse_down(mouse_down)
```

## Spieleinstellungen


```python
algorithms = { 'Menschlicher Spieler': None,
               'ProbCut': probcut,
               'AlphaBeta': alphabeta,
               'Minimax': minimax,
               'Zufällig': random_ai }
modes = { 'Feste Tiefe': ai_make_move,
          'Iterative Vertiefung': ai_make_move_id,
          'Zeitbegrenzte Vertiefung': ai_make_move_id_timelimited }
heuristics = { 'Cowthello': cowthello_heuristic,
               'Cowthello+': cowthello_safe_heuristic,
               'Mobilität': mobility_heuristic,
               'Kombiniert': combined_heuristic }
black_algorithm = RadioButtons(
    options=algorithms.keys(),
    value='Menschlicher Spieler',
    description='Schwarz:'
)
black_heuristic = RadioButtons(
    options=heuristics.keys(),
    value='Kombiniert'
)
black_mode = RadioButtons(
    options=modes.keys(),
    value='Zeitbegrenzte Vertiefung'
)
black_depth = IntSlider(value = 5, min=1, max=10, description='Suchtiefe:')
black_config = HBox([black_algorithm, black_mode, black_heuristic, black_depth])

white_algorithm = RadioButtons(
    options=algorithms.keys(),
    value='ProbCut',
    description='Weiß:'
)
white_heuristic = RadioButtons(
    options=heuristics.keys(),
    value='Kombiniert'
)
white_mode = RadioButtons(
    options=modes.keys(),
    value='Zeitbegrenzte Vertiefung'
)
white_depth = IntSlider(value = 5, min=1, max=10, description='Suchtiefe:')
white_config = HBox([white_algorithm, white_mode, white_heuristic, white_depth])
settings = ipywidgets.VBox([black_config, white_config])
```


```python
def configure_settings():
    display(settings)
```


```python
def get_settings():
    return { BLACK: { 'heuristic': heuristics[black_heuristic.value],
                      'algorithm': algorithms[black_algorithm.value],
                      'depth': black_depth.value,
                      'mode': modes[black_mode.value] },
             WHITE: { 'heuristic': heuristics[white_heuristic.value],
                      'algorithm': algorithms[white_algorithm.value],
                      'depth': white_depth.value,
                      'mode': modes[white_mode.value] }}
```
