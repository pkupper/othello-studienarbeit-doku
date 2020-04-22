```python
%%HTML
<style>
.container { width:100% }
</style>
```

# Implementierung der Spiellogik

Im Folgenden ist die Spielelogik des Spiels Othello implementiert. Dazu gehört die Implementation aller im \autoref{sec:spieltheorie} genannten Aspekte, wie zum Beispiel die erzeugung eines Startzustands, sowie die die Bestimmung und Durchführung von Spielzügen ausgehend von einem Spielzustand. Ausgangspunkt für diese Implementierung ist das Python Gui für Othello von Kevan Nguyen, welches unter <https://github.com/kevannguyen/Othello> verfügbar ist.

## Importieren der externen Abhängigkeiten

Die Implementation stützt sich für bessere Performanz auf die Python-Bibliothek `numpy`, welche unter anderem homogene Felder und Matrizen implementiert. Eine solche Matrix wird als interne Repräsentation des Othello Spielfeldes genutzt. Insbesondere Operationen, die auf einen größeren Teil des Spielfeldes zugreifen müssen werden, können dadurch beschleunigt werden.


```python
import numpy
```

## Globale Konstanten

Im Folgenden Abschnitt werden zunächst einige Konstanten definiert, welche in der späteren Implementation häufig genutzt werden.

Die Konstante `BOARD_SIZE` gibt die Anzahl an Zeilen und Spalten des quadratischen Othello Spielfelds an. `BOARD_SIZE` wird beispielsweise zur Iteration über Zeilen und Spalten des Spielfeldes genutzt, sowie zur Überprüfung, ob gegebene Koordinaten innerhalb des Spielfeldes liegen.

Die Konstanten `BLACK`, `WHITE` und `NONE` werden auf die Zahlenwerte -1 , 1 und 0 abgebildet und werden für mehrere Zwecke genutzt:
1. Repräsentation des Spielfeldes: Das Othello Spielbrett wird als $8\times 8$ Matrix von Ganzzahlen definiert, welche jeweils einen der drei Werte annehmen können. Hierbei stehen die Werte `BLACK` und `WHITE` jeweils für einen Stein des jeweiligen Spielers, während `NONE` ein leeres Feld repräsentiert.
2. Repräsentation der Spieler: `BLACK` und `WHITE` werden zur Repäsentation eines Spielers genutzt. Beispielsweise enthält der Spielzustand eine Variable `turn` die angibt, welcher Spieler am Zug ist.
3. Berechnung der Heuristiken: Die Werte `BLACK`, `WHITE` und `NONE` sind so gewählt, dass sie sich für die Berechnung der Heuristiken eignen. Der in der Künstlichen Intelligenz maximierende Spieler hat den positiven Wert 1, während der minimierende Spieler durch den negativen Wert -1 repräsentiert wird. Kein Spieler, wird durch den Wert 0 dargestellt.


```python
BOARD_SIZE = 8

BLACK = -1  # MINIMIZING PLAYER
WHITE = 1  # MAXIMIZING PLAYER
NONE = 0 # NO PLAYER
```

## Game State

Die Klasse `GameState` repäsentiert einen Spielzustand von Othello. Dieser wird durch die im Folgenden genannten Attribute beschrieben
- Das Spielfeld `board`, welches durch eine zweidimensionale Numpy Matrix repräsentiert wird, bei der jede Zelle die die Werte `BLACK`, `WHITE` und `NONE` annehmen kann.
- Den Spieler `turn`, der im Spielzustand am Zug ist.
Zusätzlich enthält der Spielzustand weitere Informationen welche zur Verbesserung der Performanz genutzt werden.
- Die im aktuellen Spielzustand möglichen Züge, werden als Paare von Koordinaten in der Variable `possible_moves` gespeichert werden. Ein Koordinatenpaar steht hierbei für das Setzen eines Spielsteins auf die entsprechende Stelle auf dem Spielfeld unter Anwendung der Othello Regeln. Diese Variable ist Teil von `GameState` damit pro Spielzustand, die möglichen Züge nicht mehrfach berechnet werden müssen.
- Die Menge der freien Felder, die horizontal, vertikal oder diagonal an einen Stein angrenzen werden in der Variable `frontier` gespeichert. Beim Ermitteln der möglichen Züge kann dadurch die Performanz wesentlich gesteigert werden, da nur diese Menge und nicht das gesamte Spielfeld überprüft werden muss.
- Die Anzahl an Spielsteinen auf dem Spielfeld wird in der Variable `num_pieces` gehalten.
- Ob der Spielzustand ein Endzustand ist, wird in der Variable `game_over` gespeichert.
- Die Koordinaten des letzten Spielzugs werden zur späteren Visualisierung in der Grafischen Benutzeroberfläche in der Variable `last_move` gespeichert.

Die zur Performance-Verbesserung genutzen Variablen werden im Laufe des Spielverlaufs immer aktuell gehalten.

In dem Konstruktor `__init__` der Klasse `GameState` wird ein neuer Spielzustand entsprechend den Othello Spielregeln instanziert, indem alle Variablen entsprechen initialisiert werden.

Die Funktion `__lt__` ist implementiert, damit auf `GameState`-Objekten der Vergleichsoperator angewendet werden kann. Das ist nötig, damit in der Künstlichen Intelligenz Tupel sortiert werden können, die beispielsweise aus einer Priorität und einen `GameState` bestehen. Da in diesem Fall nur die Sortierung nach der Priorität wichtig ist, ist die implementation von `__lt__` irrelevant. Daher wird, der Einfachkeit wegen, immer True zurückgegeben.


```python
class GameState:
    def __init__(self):
        self.board = numpy.zeros((BOARD_SIZE, BOARD_SIZE), dtype=numpy.int8)
        self.board[3, 3] = WHITE
        self.board[3, 4] = BLACK
        self.board[4, 3] = BLACK
        self.board[4, 4] = WHITE
        self.turn = BLACK
        self.possible_moves = [(2, 3), (3, 2), (4, 5), (5, 4)]
        self.frontier = {(2, 2), (2, 3), (2, 4), (2, 5),
                         (3, 2), (3, 5), (4, 2), (4, 5),
                         (5, 2), (5, 3), (5, 4), (5, 5)}
        self.num_pieces = 4
        self.game_over = False
        self.last_move = None

    def __lt__(self, other):
        return True
```

Die Liste `directions` enthält alle horizontalen, vertikalen und diagonalen Richtungen auf dem Spielfeld als Zwei-Tupel. Die beiden Zahlen stellen hierbei jeweils den Versatz in Reihen- und Spaltenrichtung dar. Diese Liste wird später in mehreren Funktionen genutzt.


```python
directions = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
```

Die Exception `InvalidMoveException`, wird später in der Funktion `make_move` geworfen, wenn ein ungültigen Spielzug gefordert wird. Dies dient der Fehlerbehandlung.


```python
class InvalidMoveException(Exception):
    pass
```

Die Funktion `make_move` führt im Spielzustand `state`, falls möglich, einen Zug auf die Koordinaten `row` und `col` aus.

Dazu werden zunächst alle gegnerischen Steine umgedreht, die durch den Zug eingesperrt wurden. Wenn mindestens ein Stein umgedreht wurde, wird `disks_flipped` auf `True`gesetzt. Wenn das nicht der Fall war, handelt es sich nicht um einen gültigen Zug und es wird eine Exception geworfen. Sonst wird der neue Stein gesetzt und im Zustand die Frontier, der aktuelle Spieler, ob das Spiel vorbei ist und die möglichen Züge des nächsten Spielers aktualisiert.


```python
def make_move(state, pos):
    if pos not in state.frontier:
        print(pos, "not in Frontier")
        raise InvalidMoveException
    disks_flipped = False
    
    (row, col) = pos
    board = state.board.tolist()
    for (row_dir, col_dir) in directions:
        if can_flip_in_dir(board, row, col, row_dir, col_dir, state.turn):
            disks_flipped = True
            flip_in_dir(state, row, col, row_dir, col_dir, state.turn)

    if disks_flipped:
        state.num_pieces += 1
        state.board[pos] = state.turn
        state.last_move = pos
        update_frontier(state, row, col)
        state.turn = -state.turn
        state.possible_moves = get_possible_moves(state, state.turn)
        if len(state.possible_moves) == 0:
            state.turn = -state.turn
            state.possible_moves = get_possible_moves(state, state.turn)
            if len(state.possible_moves) == 0:
                state.game_over = True
                return state
    else:
        raise InvalidMoveException()
    return state
```

Die Funktion `can_flip_in_dir` überprüft für ein Spielfeld `board` und den Spieler `player`, ob beim Setzen eines Steins auf die Position `(row, col)` in die durch `(rowdelta, coldelta)` gegebene Richtung Steine umgedreht werden können. `board` ist ein Spielfeld als Python-Liste, da der Zugriff deutlich schneller ist, als auf eine numpy array.


```python
def can_flip_in_dir(board, row, col, rowdelta, coldelta, player):
    current_row = row + rowdelta
    current_col = col + coldelta
    if not (0 <= current_row < 8 and 0 <= current_col < 8):
        return False
    if not board[current_row][current_col] == -player:
        return False
    current_row += rowdelta
    current_col += coldelta
    
    while True:
        if not (0 <= current_row < 8 and 0 <= current_col < 8):
            return False
        if board[current_row][current_col] == NONE:
            return False           
        if board[current_row][current_col] == player:
            return True
    
        current_row += rowdelta
        current_col += coldelta
```

Die Funktion `is_move_valid` überprüft für ein gegebenes Spielfeld `board`, ob ein Zug auf die angegebenen Koordinaten `row` und `col` für den Spieler `player` möglich ist. Das Ergebnis wird als Wahrheitswert zurückgegeben. `board` ist hier ebenfalls eine Python-Liste, da der Zugriff auf Elemente schneller ist, als in einem numpy array.


```python
def is_move_valid(board, row, col, player):
    for rowdelta, coldelta in directions:
        if can_flip_in_dir(board, row, col, rowdelta, coldelta, player):
            return True
    return False
```

`get_utility` bestimmt für einen Endzustand den Gewinner des Spiels. Gewinnt Weiß, so wird der Wert 1 zurückgegeben. Gewinnt Schwarz, wird der Wert -1 zurückgegeben. Bei einem Unentschieden wird der Wert 0 zurückgegeben.


```python
def get_utility(state):
    black_disks = count_disks(state, BLACK)
    white_disks = count_disks(state, WHITE)
    if black_disks > white_disks:
        return BLACK
    if white_disks > black_disks:
        return WHITE
    else:
        return NONE
```

Die Funktion `get_possible_moves` bestimmt für einen Spielzustand `state` und den Spieler `player` die möglichen Züge, die der Spieler machen kann. Die Züge werden als Liste von Koordinaten zurückgegeben.


```python
def get_possible_moves(state, player):
    board = state.board.tolist()
    possible_moves = []
    for (row, col) in state.frontier:
        if is_move_valid(board, row, col, player):
            possible_moves.append((row, col))
    return possible_moves
```

Diese Funktion dreht im Spielzustand `state`, ausgehend von dem durch `row` und `col` gegebenen Feld, die für den Spieler `player` generischen Steine in die durch `rowdelta` und `coldelta` gegebene Richtung um.


```python
def flip_in_dir(state, row, col, rowdelta, coldelta, player):
    current_row = row + rowdelta
    current_col = col + coldelta
    
    while state.board[current_row, current_col] == -player:
        state.board[(current_row, current_col)] = player
        current_row += rowdelta
        current_col += coldelta
```

`update_frontier` wird nach jedem Zug aufgerufen um die Menge Frontier zu aktualisieren. Die durch `row` und `col` Gegebene Koordinate wird entfernt, während die Koordinaten von leeren umliegenden Feldern hinzugefügt werden.


```python
def update_frontier(state, row, col):
    for current_row in range(row-1, row+2):
        if not 0 <= current_row < 8:
            continue
        for current_col in range(col-1, col+2):
            if not 0 <= current_col < 8:
                continue
            if state.board[current_row, current_col] == NONE:
                state.frontier.add((current_row, current_col))
    state.frontier.remove((row, col))
```

Die Funktion `count_disks` zählt die Steine, die der Spieler `player` im Spielzustand `state` auf dem Spielfeld hat.


```python
def count_disks(state, player):
    return numpy.count_nonzero(state.board == player)
```

`get_player_string` konvertiert die ID des Spielers `player` in dessen Name. Ist `player == NONE` so wird 'Nobody' zurückgegeben.


```python
def get_player_string(player):
    return {BLACK: 'Black', WHITE: 'White', NONE: 'Nobody'}[player]
```

`make_state` erzeugt einen Spielzustand aus dem Spielfeld `board` und dem zu ziehenden Spieler `turn`. Diese Funktion wird zu Testzwecken genutzt.


```python
def make_state(board, turn):
    state = GameState()
    state.board = board
    state.turn = turn
    state.frontier = set()
    for row in range(8):
        for col in range(8):
            for current_row in range(row-1, row+2):
                if not 0 <= current_row < 8:
                    continue
                for current_col in range(col-1, col+2):
                    if not 0 <= current_col < 8:
                        continue
                    if state.board[current_row, current_col] == NONE:
                        state.frontier.add((current_row, current_col))
            
    state.possible_moves = get_possible_moves(state, turn)
    state.game_over = False
    if len(state.possible_moves) == 0:
        if len(get_possible_moves(state, -turn)) == 0:
            state.game_over = True
    state.num_pieces = count_disks(state, WHITE) + count_disks(state, BLACK)
    state.last_move = None
    return state
```
