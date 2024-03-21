from typing import List, Optional, Tuple
import random
import implementacja_problemu as ip
import numpy as np


def change_knot(solution: ip.Solution, knot_cord: ip.Point_coordinates, new_knot_kind: List[float]):
    """
    Funkcja zmieniająca rodzaj węzła w danym rozwiązaniu:
    :param solution: aktualne rozwiązanie
    :param knot_cord: wybrany węzeł
    :param new_knot_kind: nowy rodzaj węzła
    """
    knot = solution.point_matrix[knot_cord[0]][knot_cord[1]]
    out_list = solution.solution_graph[knot_cord]  # wyznaczenie listy krawędzi wychodzących z węzła
    for i in range(len(new_knot_kind)):
        out_cord = out_list[i][0]
        out = solution.point_matrix[out_cord[0]][out_cord[1]]
        old_flow = out.flow  # odczytanie starej wartości przepływu
        out.flow = knot.flow * new_knot_kind[i]
        solution.update_extraction_point(out_cord, is_add_knot=True)
        dflow = out.flow - old_flow
        if out_cord in solution.solution_graph.keys():
            solution.update_flow(out_cord, dflow)
    knot.is_knot["out"] = new_knot_kind


def change_random_knot(solution: ip.Solution, max_iteration: int = 10):
    """
    Funkcja realizująca zmianę stosunków w losowo wybranym węźle:
    :param solution: aktualne rozwiązanie
    :param max_iteration: maksymalna liczba prób wylosowania węzła
    """
    if len(solution.knots) == 0:
        raise ValueError("W rozwiązaniu nie ma węzłów")
    knot = solution.knots[random.randint(0, len(solution.knots) - 1)]  # wylosowanie węzła
    knot_point = solution.point_matrix[knot[0]][knot[1]]  # znalezienie punktu odpowiadającego wylosowanemu węzłowi
    iteration = 0
    while "out" not in knot_point.is_knot.keys():  # jeżeli punkt nie jest węzłem wychodzącym, musimy wylosować kolejny
        # węzeł
        iteration += 1
        knot = solution.knots[random.randint(0, len(solution.knots) - 1)]  # wylosowanie węzła
        knot_point = solution.point_matrix[knot[0]][knot[1]]  # znalezienie punktu odpowiadającego wylosowanemu węzłowi
        if iteration > max_iteration:
            raise ValueError("Nie można wylosować węzła")
    outs_number = len(knot_point.is_knot["out"])
    new_knot_kind = ip.knot_kinds[outs_number][random.randint(0, len(ip.knot_kinds[outs_number]) - 1)]
    if new_knot_kind == knot_point.is_knot["out"]:  # jeśli wylosowano taki sam węzeł jak obecny, to próbujemy zamienić
        # stosunki
        for i in range(outs_number):
            new_knot_kind[i] = knot_point.is_knot["out"][i - 1]
    change_knot(solution, knot, new_knot_kind)


def delete_edges(solution: ip.Solution, start: Optional[ip.Point] = None):
    """
    Funkcja usuwająca zbędne krawędzie, zaczynając od końcowgo punktu
    :param solution: rozwiązanie, z którego usuwamy krawędzie
    :param start: punkt początkowy
    """
    # Sprawdzenie, który z punktów poboru ma zerowy przepływ i jest w kluczach grafu - oznacza to, że od niego wychodzi
    # ścieżka z zerowym przepływem - należy ją usunąć
    for ex_p in solution.extraction_points:
        if start is None:
            start: ip.Point = solution.point_matrix[ex_p.coordinates[0]][ex_p.coordinates[1]]
        if start.flow == 0 and start.coordinates in solution.solution_graph.keys():
            # Początkowy pierwszy wierzchołek to start
            prev_point: ip.Point = start
            # Ścieżkę należy usuwać do momentu, aż pierwszy wierzchołek krawędzi nie będzie węzłem wchodzącym lub
            # punktem poboru, należy jednak dodatkowo uwzględnić punkt startowy, gdyż jest on punktem poboru
            while prev_point == start or (prev_point.coordinates not in
                                          [ex.coordinates for ex in solution.extraction_points]
                                          and "in" not in prev_point.is_knot.keys()):
                # Jeśli punkt jest węzłem wychodzącym (ma więcej niż jedną krawędź w liście sąsiedztwa) trzeba usunąć
                # wszystkie
                for i in range(len(solution.solution_graph[prev_point.coordinates])):
                    edge: Tuple[ip.Point_coordinates, str, float, float] = \
                        solution.solution_graph[prev_point.coordinates][i]
                    next_point: ip.Point = solution.point_matrix[edge[0][0]][edge[0][1]]
                    # Usunięcie krawędzi z listy sąsiedztwa
                    solution.solution_graph[prev_point.coordinates].pop(i)
                    # Redukcja sum kosztów i czasów o wartości dodane przez tę krawędź
                    solution.costs_sum -= edge[2]
                    solution.times_sum -= edge[3]
                    # Jeśli pierwszy wierzchołek nie jest startowym, trzeba usunąć go z listy punktów rozwiązania oraz
                    # wyczyścić jego listę poprzedników
                    if prev_point != start:
                        solution.points.remove(prev_point.coordinates)
                        next_point.previous_points.remove(prev_point.coordinates)
                        prev_point.previous_points = []
                        # Jeśli dodatkowo punkt jest węzłem, trzeba usunąć go z listy węzłów oraz wyczyścić jego
                        # informacje o węźle
                        if prev_point.is_knot.keys():
                            solution.knots.remove(prev_point.coordinates)
                            prev_point.is_knot = {}
                    # W następnej iteracji pierwszym wierzchołkiem będzie obecny drugi wierzchołek usuwanej krawędzi
                    prev_point = next_point
            if "in" in prev_point.is_knot.keys() and len(prev_point.previous_points) == 1:
                solution.knots.remove(prev_point.coordinates)
                prev_point.is_knot = {}
            solution.update_flow((0, 0))


def change_random_edge(solution: ip.Solution, iteration: int = 0):
    """
    Funkcja zmieniająca losową krawędź w rozwiązaniu na zbiór 3 krawędzi zastępujących ją,
    np.:    .           .__
            |  ->         |
            '           '--
    :param solution: modyfikowane rozwiązanie
    :param iteration: ilość powtórzeń wywołania funkcji, jeśli nie uda się wykonać zmiany dla pierwszej losowo wybranej
    krawędzi
    """
    P1: ip.Point_coordinates = random.choice(list(solution.solution_graph.keys()))
    P2: ip.Point_coordinates
    direction: str
    # Określenie orientacji P2 względem P1 i utworzenie punktów, przez które zostaną poprowadzone zastępcze krawędzie
    P2, direction = random.choice([(edge[0], edge[1]) for edge in solution.solution_graph[P1]])
    if direction == "up":
        change = P1[1] - 1 if P1[1] - 1 >= 0 else P1[1] + 1
        middle_1: ip.Point = solution.point_matrix[P1[0]][change]
        middle_2: ip.Point = solution.point_matrix[P2[0]][change]
    elif direction == "down":
        change = P1[1] + 1 if P1[1] + 1 < len(solution.point_matrix) else P1[1] - 1
        middle_1: ip.Point = solution.point_matrix[P1[0]][change]
        middle_2: ip.Point = solution.point_matrix[P2[0]][change]
    elif direction == "right":
        change = P1[0] - 1 if P1[0] - 1 >= 0 else P1[0] + 1
        middle_1: ip.Point = solution.point_matrix[change][P1[1]]
        middle_2: ip.Point = solution.point_matrix[change][P2[1]]
    else:
        change = P1[0] + 1 if P1[0] + 1 < len(solution.point_matrix) else P1[0] - 1
        middle_1: ip.Point = solution.point_matrix[change][P1[1]]
        middle_2: ip.Point = solution.point_matrix[change][P2[1]]
    # Sprawdzenie czy da się utworzyć wszystkie 3 krawędzie na podstawie wyników z funkcji sprawdzającej poprawność
    # Jeśli tak, to krawędzie są dodawane (chyba, że już takie istnieją)
    sol_copy: ip.Solution = solution.copy()  # Kopia rozwiązania pomocniczo, aby ułatwić sprawdzenie
    check_edge_1: int = solution.check_if_edge_correct(P1, middle_1.coordinates)
    if check_edge_1 in [0, 4]:
        # usunięcie krawędzi P1-P2 z kopii, aby nie powstały błędy pętli
        sol_copy.solution_graph[P1].pop([edge[0] for edge in sol_copy.solution_graph[P1]].index(P2))
        if check_edge_1 == 0:
            sol_copy.add_edge(P1, middle_1.coordinates)
        check_edge_2: int = sol_copy.check_if_edge_correct(middle_1.coordinates, middle_2.coordinates)
        if check_edge_2 in [0, 4]:
            if check_edge_2 == 0:
                sol_copy.add_edge(middle_1.coordinates, middle_2.coordinates)
            check_edge_3: int = sol_copy.check_if_edge_correct(middle_2.coordinates, P2)
            if check_edge_3 in [0, 4]:
                for i in range(len(solution.solution_graph[P1])):
                    edge: Tuple[ip.Point_coordinates, str, float, float] = solution.solution_graph[P1][i]
                    if P2 in edge:
                        solution.costs_sum -= edge[2]
                        solution.times_sum -= edge[3]
                        solution.solution_graph[P1].pop(i)
                        break
                if check_edge_1 == 0:
                    solution.add_edge(P1, middle_1.coordinates)
                if check_edge_2 == 0:
                    solution.add_edge(middle_1.coordinates, middle_2.coordinates)
                if check_edge_3 == 0:
                    solution.add_edge(middle_2.coordinates, P2)
                # Jeśli P1 był węzłem wychodzącym, możliwe, że została zmieniona ilość jego krawędzi wychodzących,
                # trzeba więc zmienić jego stosunki
                P1_point: ip.Point = solution.point_matrix[P1[0]][P1[1]]
                if "out" in P1_point.is_knot.keys():
                    # Z racji tego, że jedna krawędź została usunięta, węzeł może mieć teraz maksymalnie 2 krawędzi
                    # wychodzące
                    if len(solution.solution_graph[P1]) == 2:
                        P1_point.is_knot["out"] = ip.knot_kinds[2][0]
                    else:
                        P1_point.is_knot.pop("out")
                solution.update_flow(P1)
                return
    if iteration < 10:
        change_random_edge(solution, iteration + 1)


def SA(initial_solution: ip.Solution, t0: float, alfa: float, max_it_number: int, it_number_in_one_temp: int,
       change_knot: bool = True, f_cost_parameters: Optional[List[float]]=None) -> Tuple[ip.Solution, int]:
    """
    Funkcja wyznaczająca rozwiązanie problemu metodą Symulowanego Wyżarzania
    :param initial_solution: rozwiązanie początkowe
    :param t0: temperatura początkowa
    :param alfa: liniowa zmiana temperatury, alfa należy do (0, 1)
    :param max_it_number: maksymalna liczba iteracji algorytmu
    :param it_number_in_one_temp: liczba iteracji w jednej temperaturze
    :param change_knot: jeśli True, sąsiedztwo to zmiana stosunków któregoś węzła, jeśli nie, będzie nim zmiana
    krawędzi
    :param f_cost_parameters: parametry funkcji celu:
        waga kosztu położenia krawędzi w funkcji celu,
        waga czasu położenia krawędzi w funkcji celu,
        waga kary za niedostarczenie wody do węzła w funkcji celu
    """
    if f_cost_parameters is None:
        f_cost_parameters = [0.1, 0.1, 1]
    sol_best: ip.Solution = initial_solution.copy()  # początkowo najlepsze rozwiązanie to rozwiązanie początkowe
    it_best: int = 0  # iteracja, w której znaleziono najlepsze rozwiązanie
    it_number: int = 0  # aktualny numer iteracji
    while it_number < max_it_number and t0 > 0:
        for i in range(it_number_in_one_temp):
            s_prim = initial_solution.copy()
            if change_knot:
                try:
                    change_random_knot(s_prim)
                except ValueError:
                    pass
            else:
                change_random_edge(s_prim)
            if ip.objective_function(s_prim, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]) < \
                    ip.objective_function(sol_best, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]):
                sol_best = s_prim.copy()
                it_best = it_number
            delta = ip.objective_function(s_prim, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]) - \
                    ip.objective_function(initial_solution, f_cost_parameters[0], f_cost_parameters[1],
                                          f_cost_parameters[2])
            if delta < 0:
                initial_solution = s_prim.copy()
            else:
                x = random.uniform(0, 1)
                if x < np.exp(- delta / t0):
                    initial_solution = s_prim.copy()
        it_number += 1
        t0 = alfa * t0
    return sol_best, it_best
