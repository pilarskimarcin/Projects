import implementacja_problemu as ip
from typing import List


# → ← ↑ ↓ ·
# ⇨ ⇦ ⇧ ⇩ ○ ∘
# ↕ ⇳ ⟷ ⇔ ↔ ⇄ ⇅


def draw_solution_add_arrow(drawing, direction, coordinates):
    p = [char for char in drawing[coordinates[0]][coordinates[1]]]
    if direction == "left":
        if p[2] == "→":
            p[2] = "⇄"
        else:
            p[2] = "←"
    elif direction == "right":
        if p[2] == "←":
            p[2] = "⇄"
        else:
            p[2] = "→"
    elif direction == "up":
        if p[1] == "↓":
            p[1] = "⇅"
        else:
            p[1] = "↑"
    elif direction == "down":
        if p[1] == "↑":
            p[1] = "⇅"
        else:
            p[1] = "↓"
    else:
        print("Rysowanie strzałek się zepsuło")
    drawing[coordinates[0]][coordinates[1]] = "".join(p)
    return drawing


def draw_solution_add_ext(drawing, extractions):
    for ext in extractions:
        p = [char for char in drawing[ext[0]][ext[1]]]
        if p[2] == "←":
            p[2] = "⇦"
        elif p[2] == "→":
            p[2] = "⇨"
        elif p[2] == "⇄":
            p[2] = "⇔"
        elif p[2] == "·":
            p[2] = "○"

        if p[1] == "↑":
            p[1] = "⇧"
        elif p[1] == "↓":
            p[1] = "⇩"
        elif p[1] == "↕":
            p[1] = "⇳"
        elif p[1] == "·":
            p[1] = "○"
        drawing[ext[0]][ext[1]] = "".join(p)
    return drawing


def draw_solution(solution: List[ip.Edge], extractions: List[ip.Point_coordinates]):
    """
    Funkcja wyrysowująca rozwiązanie problemu. Strzałki są umiejscowione w punktach startowych krawędzi. Puste strzałki
    i/lub kółka oznaczają punkt poboru w danym miejscu.
    :param solution: Rozwiązanie które ma zostać rozrysowane.
    :param extractions: Współrzędne punktów poboru.
    """
    drawing: List[List[str]] = [[' ·· ' for _ in range(len(ip.point_matrix[0]))] for _ in range(len(ip.point_matrix))]
    for edge in solution:
        if edge[0][0] > edge[1][0]:
            drawing = draw_solution_add_arrow(drawing, "up", (edge[0][0], edge[0][1]))
        elif edge[0][0] < edge[1][0]:
            drawing = draw_solution_add_arrow(drawing, "down", (edge[0][0], edge[0][1]))
        elif edge[0][1] > edge[1][1]:
            drawing = draw_solution_add_arrow(drawing, "left", (edge[0][0], edge[0][1]))
        elif edge[0][1] < edge[1][1]:
            drawing = draw_solution_add_arrow(drawing, "right", (edge[0][0], edge[0][1]))
    drawing = draw_solution_add_ext(drawing, extractions)
    for line in drawing:
        print(*line, sep=' ')
    print()