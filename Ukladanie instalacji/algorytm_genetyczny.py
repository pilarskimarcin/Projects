from typing import Tuple, Set, List
import random
import SA
import implementacja_problemu as ip
import algorytm_konstrukcyjny as ak


def cross_solution_create_return(sol1: ip.Solution, sol2: ip.Solution,
                                 cross_point: ip.Point_coordinates) -> ip.Solution:
    """
    Funkcja pomocnicza tworząca nowe skrzyżowane rozwiązanie
    """
    # print(cross_point)
    ret_sol1: ip.Solution = ip.Solution()
    point1: ip.Point_coordinates = (0, 0)
    # Pobranie krawędzi z sol1:
    stack1: List[ip.Point_coordinates] = [point1]
    while stack1:
        point1 = stack1.pop()
        if point1 in sol1.solution_graph.keys() and point1 != cross_point:
            for edge_end in sol1.solution_graph[point1]:
                indicator = ret_sol1.check_if_edge_correct(point1, edge_end[0])
                if indicator == 0:
                    stack1.append(edge_end[0])
                    P1 = sol1.point_matrix[point1[0]][point1[1]]
                    knot_kind = P1.is_knot['out'] if 'out' in P1.is_knot.keys() else None
                    ret_sol1.add_edge(point1, edge_end[0], knot_kind)
    # pobranie krawędzi z sol2 - pobieram krawędzie prowadzące tylko do tych punktów, które nie znalazły się jeszcze w rozwiązaniu:
    point1 = cross_point
    stack1 = [point1]
    while stack1:
        point1 = stack1.pop()
        if point1 in sol2.solution_graph.keys():
            for edge_end in sol2.solution_graph[point1]:
                indicator = ret_sol1.check_if_edge_correct(point1, edge_end[0])
                P1 = sol1.point_matrix[point1[0]][point1[1]]
                if indicator in [0, 4]:
                    stack1.append(edge_end[0])
                    if indicator == 0:
                        knot_kind = P1.is_knot['out'] if 'out' in P1.is_knot.keys() else None
                        ret_sol1.add_edge(point1, edge_end[0], knot_kind)
                if indicator == 7:
                    return sol1
                elif indicator not in [0, 4] and (
                        'out' not in P1.is_knot.keys() or P1 not in ret_sol1.extraction_points):
                    return sol1
    return ret_sol1


def cross_solutions(sol1: ip.Solution, sol2: ip.Solution, max_it_number: int = 10) -> Tuple[ip.Solution, ip.Solution]:
    """
    Operator krzyżowania
    :param sol1: pierwsze rozwiązanie
    :param sol2: drugie rozwiązanie
    :param max_it_number: maksymalna liczba prób wyboru punktu krzyżowania
    :return: krotka zawierająca dwa nowe rozwiązania
    """
    common_points: Set[ip.Point_coordinates] = {point for point in sol1.points if point in sol2.points and point != (
        0, 0)}  # zbiór punktów wspólnych obu rozwiązań, nie będących źródłem
    cross_point: ip.Point_coordinates = (0, 0)
    if len(common_points) == 0:
        return sol1, sol2
    for i in range(max_it_number):
        cross_point = random.sample(common_points, 1)[0]  # wybór losowy punktu krzyżowania
        if cross_point in sol1.solution_graph.keys() and cross_point in sol2.solution_graph.keys():
            break
    if cross_point == (0, 0):
        # raise ValueError("Nie można wybrać punktu krzyżowania")
        return sol1, sol2
    # Utworzenie nowych rozwiązań:
    ret_sol1 = cross_solution_create_return(sol1, sol2, cross_point)
    ret_sol2 = cross_solution_create_return(sol2, sol1, cross_point)
    return ret_sol1, ret_sol2


# -----------------------------------------------------------------------------------------------------------------------------------


def crossing(solutions: List[ip.Solution], children_num: int, probability: int) -> List[ip.Solution]:
    """
    Funkcja zwracająca listę wyników krzyżowania
    :param solutions: Rodzice, na których będzie zastosowane krzyżowanie
    :param children_num: Liczba dzieci jaka ma powstać przez krzyżowanie
    :param probability: prawdopodobieństwo wykonania krzyżowania na danej parze rodziców
    :return: Lista zawierająca dzieci (wyniki krzyżowania)
    """
    return_list: List[ip.Solution] = []
    tabu_index: List[Tuple[int, int]] = []  # Lista wyorzystanych już par rodziców do krzyżowania
    solutions_len = len(solutions)
    while len(return_list) < children_num:
        sol1_index = random.randint(0, solutions_len - 1)
        sol2_index = random.randint(0, solutions_len - 1)
        while sol2_index == sol1_index:
            sol2_index = random.randint(0, solutions_len - 1)
        if (sol1_index, sol2_index) not in tabu_index and (sol1_index, sol2_index) not in tabu_index:
            tabu_index.append((sol1_index, sol2_index))
            do_crossing = random.randint(0, 100)
            if do_crossing <= probability:  # czy na danej parze rodziców wykonujemy krzyżowanie
                ret_sol1, ret_sol2 = cross_solutions(solutions[sol1_index], solutions[sol2_index])
                return_list.append(ret_sol1)
                return_list.append(ret_sol2)
    return return_list


def mutation(solutions: List[ip.Solution], probability: int, change_knot: bool) -> List[ip.Solution]:
    """
    Funkcja zwracająca listę rozwiązań po mutacji
    :param solutions: Rozwiązania, które mogą zostać poddane mutacji z pewnym prawdopodobieństwem
    :param probability: Prawdopodobieństwo wystąpienia mutacji u danego rozwiązania (0 - 100) [%]
    :param change_knot: Rodzaj wykonywanej mutacji
    :return: Lista rozwiązań, gdzie część może być po mutacji
    """
    for sol in solutions:
        do_mutation = random.randint(0, 100)
        if do_mutation <= probability:  # czy wykonujemy mutację na danym rozwiązaniu
            if change_knot:  # mutacja to zmiana węzła
                try:
                    SA.change_random_knot(sol)
                except ValueError:
                    continue
            else:  # mutacja to zmiana krawędzi
                SA.change_random_edge(sol)
    return solutions


def selection(solutions: List[ip.Solution], cost_weight: float, time_weight: float, penalty_severity: float,
              destination: str = "min") -> List[ip.Solution]:
    """
    Funkcja zwracająca listę wyników selekcji poprzez turniej
    :param solutions: Rozwiązania, które zostaną poddane selekcji
    :param cost_weight: waga kosztu położenia krawędzi w funkcji celu
    :param time_weight: waga czasu położenia krawędzi w funkcji celu
    :param penalty_severity: waga kary za niedostarczenie wody do węzła w funkcji celu
    :param destination: Określenie czy chcemy maksymalizować czy minimalizować funkcję celu ("max", "min")
    :return: Lista rozwiązań po selekcji
    """
    result: List[ip.Solution] = []
    solutions_id: List[int] = [i for i in range(len(solutions))]
    for _ in range(int(len(solutions) / 2)):
        sol1 = random.choice(solutions_id)
        solutions_id.remove(sol1)
        sol2 = random.choice(solutions_id)
        solutions_id.remove(sol2)
        if destination == "min":
            better = solutions[sol1].copy() if ip.objective_function(solutions[sol1], cost_weight, time_weight,
                                                                     penalty_severity) < ip.objective_function(
                solutions[sol2], cost_weight, time_weight, penalty_severity) else solutions[sol2].copy()
        elif destination == "max":
            better = solutions[sol1].copy() if ip.objective_function(solutions[sol1], cost_weight, time_weight,
                                                                     penalty_severity) > ip.objective_function(
                solutions[sol2], cost_weight, time_weight, penalty_severity) else solutions[sol2].copy()
        result.append(better)
    return result


def best_solution_idx(solutions: List[ip.Solution], cost_weight: float, time_weight: float, penalty_severity: float,
                      destination: str = "min") -> int:
    """
    Funkcja zwracająca indeks najlepszego rozwiązania w liście rozwiązań
    :param solutions: Rozwiązania, z których będzie wybrane najlepsze rozwiązanie
    :param cost_weight: waga kosztu położenia krawędzi w funkcji celu
    :param time_weight: waga czasu położenia krawędzi w funkcji celu
    :param penalty_severity: waga kary za niedostarczenie wody do węzła w funkcji celu
    :param destination: Określenie czy chcemy maksymalizować czy minimalizować funkcję celu ("max", "min")
    :return: Indeks najlepszego rozwiązania w liście
    """
    best: int = None
    for idx in range(len(solutions)):
        if best is None:
            best = idx
        elif destination == "min" and ip.objective_function(solutions[best], cost_weight, time_weight,
                                                            penalty_severity) > ip.objective_function(solutions[idx],
                                                                                                      cost_weight,
                                                                                                      time_weight,
                                                                                                      penalty_severity):
            best = idx
        elif destination == "max" and ip.objective_function(solutions[best], cost_weight, time_weight,
                                                            penalty_severity) < ip.objective_function(solutions[idx],
                                                                                                      cost_weight,
                                                                                                      time_weight,
                                                                                                      penalty_severity):
            best = idx
    return best


def EA(population_num: int, mutation_prob: int = 10, crossing_prob: int = 90, destination: str = "min",
       max_it_num=100, cost_weight: float = 0.1, time_weight: float = 0.1,
       penalty_severity: float = 10, mutation_kind_knots: bool = True) -> Tuple[ip.Solution, int]:
    """
    Algorytm Ewolucyjny
    :param population_num: Liczebność populacji
    :param mutation_prob: Prawdopodobieństwo wystąpienia mutacji (w procentach)
    :param crossing_prob: Prawdopodobieństwo wystąpienia krzyżowania (w procentach)
    :param destination: Określenie czy chcemy maksymalizować czy minimalizować funkcję celu ("max", "min")
    :param max_it_num: kryterium stopu - maksymalna liczba iteracji
    :param cost_weight: waga kosztu położenia krawędzi w funkcji celu
    :param time_weight: waga czasu położenia krawędzi w funkcji celu
    :param penalty_severity: waga kary za niedostarczenie wody do węzła w funkcji celu
    :param mutation_kind_knots: rodzaj mutacji (domyślnie zmiana stosunków w węzłach)
    :return: Najlepsze rozwiązanie i w której iteracji zostało uzyskane
    """
    # Stworzenie N początkowych rozwiązań za pomocą random_initial_solution
    solutions: List[ip.Solution] = []
    for i in range(population_num):
        solutions.append(ak.random_initial_solution())
    # Wybranie najlepszego rozwiązania
    best_solution: ip.Solution = solutions[
        best_solution_idx(solutions, cost_weight, time_weight, penalty_severity, destination)].copy()
    best_sol_it = 0
    # W PĘTLI:
    it_num: int = 1
    while True:
        # Krzyżowanie
        children: List[ip.Solution] = crossing(solutions, population_num, crossing_prob)
        # Mutacja
        children = mutation(children, mutation_prob, mutation_kind_knots)
        # Dodanie dzieci do listy rozwiązań
        solutions.extend(children)
        # Wybranie najlepszego
        idx: int = best_solution_idx(solutions, cost_weight, time_weight, penalty_severity, destination)
        if destination == "min" and ip.objective_function(solutions[idx], cost_weight, time_weight,
                                                          penalty_severity) < ip.objective_function(best_solution,
                                                                                                    cost_weight,
                                                                                                    time_weight,
                                                                                                    penalty_severity):
            best_solution = solutions[idx].copy()
            best_sol_it = it_num
        elif destination == "max" and ip.objective_function(solutions[idx], cost_weight, time_weight,
                                                            penalty_severity) > ip.objective_function(best_solution,
                                                                                                      cost_weight,
                                                                                                      time_weight,
                                                                                                      penalty_severity):
            best_solution = solutions[idx].copy()
            best_sol_it = it_num
        # Selekcja
        solutions = selection(solutions, cost_weight, time_weight, penalty_severity, destination)
        # Kryteria stopu
        if it_num >= max_it_num:
            return best_solution, best_sol_it
        it_num += 1
