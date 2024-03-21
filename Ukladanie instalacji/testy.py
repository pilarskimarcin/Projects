from datetime import time
import implementacja_problemu as ip
import wczytywanie_danych as wd
import algorytm_konstrukcyjny as ak
import SA
import algorytm_genetyczny as ag
from typing import List
from wyrysowywanie_rozwiązania import draw_solution
import numpy as np


def test_read_from_file(filename: str = None, line_len: int = 200):
    """
    Wypisanie wszystkich wczytanych danych na konsolę.
    :param filename: Nazwa pliku do wczytania danych. Jeśli nie podano to funkcja nie wywołuje wczytywania danych.
    :param line_len: Długość kreski oddzielającej na początku i na końcu wypisywania.
    """
    if filename is not None:
        wd.read_from_file(filename)

    print()
    print('-' * line_len)
    print('WCZYTYWANIE DANYCH Z PLIKU (test)\n')
    print("Macierz kosztów:")
    for i in range(len(ip.point_matrix)):
        for j in range(len(ip.point_matrix[0])):
            print((ip.point_matrix[i][j].cost_left, ip.point_matrix[i][j].cost_up, ip.point_matrix[i][j].cost_right,
                   ip.point_matrix[i][j].cost_down), end='  ')
        print()

    print("\nMacierz czasów:")
    for i in range(len(ip.point_matrix)):
        for j in range(len(ip.point_matrix[0])):
            print((ip.point_matrix[i][j].time_left, ip.point_matrix[i][j].time_up, ip.point_matrix[i][j].time_right,
                   ip.point_matrix[i][j].time_down), end='  ')
        print()

    print('\nRodzaje węzłów:\n', ip.knot_kinds)
    print('\nOdległość między węzłami w poziomie: ', ip.knot_dx)
    print('Odległość między węzłami w pionie: ', ip.knot_dy)

    print('\nPunkty poboru:')
    for i in range(len(ip.extraction_points)):
        print((ip.extraction_points[i].coordinates, ip.extraction_points[i].extraction_value), end='  ')
    print()

    print('\nPojemność źródła: ', ip.source_capacity)

    print('\nMaksymalny koszt w macierzy: ', ip.max_cost)
    print('Maksymalny czas w macierzy: ', ip.max_time)
    print('-' * line_len)
    print()


def test_point_comparison():
    """
    Funkcja sprawdzająca poprawność metody magicznej __eq__ w klasie Point. Poprawne wyniki to: True True False False
    """
    point1: ip.ExtractionPoint = ip.extraction_points[0]  # Punkt poboru
    point2: ip.Point = ip.point_matrix[point1.coordinates[0]][point1.coordinates[1]]  # Poprawny punkt w macierzy
    point3: ip.Point = ip.point_matrix[point1.coordinates[0] + 1][point1.coordinates[1] + 1]  # Błędny punkt w macierzy

    print('Punkt poboru == Poprawny punkt w macierzy: ', point1 == point2)
    print('Poprawny punkt w macierzy == Punkt poboru: ', point2 == point1)
    print('Punkt poboru == Błędny punkt w macierzy: ', point1 == point3)
    print('Błędny punkt w macierzy == Punkt poboru: ', point3 == point1)
    print()


def test_knots():
    """
    Funkcja sprawdzająca poprawność dodawania węzłów - wchodzącego i wychodzącego
    """
    solution: ip.Solution = ak.initial_solution_with_knots()
    draw_solution(solution.return_solution(), extractions_coord)
    old_flow: float = ip.point_matrix[4][7].flow
    solution.add_edge((4, 3), (3, 3))
    solution.add_edge((3, 3), (3, 4))
    solution.add_edge((3, 4), (3, 5))
    solution.add_edge((3, 5), (3, 6))
    solution.add_edge((3, 6), (4, 6))
    solution.add_edge((3, 4), (4, 4))
    draw_solution(solution.return_solution(), extractions_coord)
    print(f"Czy przepływ w ostatnim punkcie jest taki sam jak wcześniej: {ip.point_matrix[4][7].flow == old_flow}")


def test_random_route():
    """
    Test do funkcji random_route - po prostu czy działa i nie wyskakują błędy
    """
    solution: ip.Solution = ip.Solution()
    print(extractions_coord[0])
    ak.random_route(solution, (0, 0), extractions_coord[0])
    solution = ak.random_initial_solution()
    draw_solution(solution.return_solution(), extractions_coord)


def test_SA(t0: float = 10, alfa: float = 0.5, max_it_number: int = 100, it_number_in_one_temp: int = 10,
            knot_neighbourhood: bool = True, random_solution: bool = False, write_to_file: bool = False):
    """
    Algorytm symulowanego wyżarzania - testowanie, parametry podać w listach
    UWAGA! parametr write_to_file to test dla różnych parametrów, wykonuje się ok.30min
    :param t0: temperatura początkowa
    :param alfa: liniowa zmiana temperatury, alfa należy do (0, 1)
    :param max_it_number: maksymalna liczba iteracji algorytmu
    :param it_number_in_one_temp: liczba iteracji w jednej temperaturze
    :param knot_neighbourhood: czy sąsiedztwo to zmiana stosunków węzła, czy zmiana krawędzi
    :param random_solution: czy losowe rozwiązanie początkowe
    """
    if random_solution:
        solution: ip.Solution = ak.random_initial_solution()
    else:
        solution: ip.Solution = ak.initial_solution_with_knots()
    if write_to_file:
        results = []
        for t0 in [5, 10, 20]:
            for alfa in [0.1, 0.5, 0.9]:
                for max_it_number in [10, 100, 500, 1000]:
                    for it_number_in_one_temp in [5, 10, 20]:
                        best_sol, it = SA.SA(solution, t0, alfa, max_it_number, it_number_in_one_temp,
                                             knot_neighbourhood)
                        results.append(
                            [t0, alfa, max_it_number, it_number_in_one_temp, knot_neighbourhood,
                             ip.objective_function(solution), ip.objective_function(best_sol), it])
        df = wd.pandas.DataFrame(results, columns=["t0", "alfa", "max_it", "it_one_temp", "knot_or_not", "Initial",
                                                   "Result", "iteration"])
        df.to_excel("Results.xlsx")
        return
    best_sol, it = SA.SA(solution, t0, alfa, max_it_number, it_number_in_one_temp, knot_neighbourhood)
    draw_solution(solution.return_solution(), extractions_coord)
    print(f"Początkowe rozwiązanie: {ip.objective_function(solution)}")
    print(f"Najlepsze rozwiązanie: {ip.objective_function(best_sol)}, znalezione w iteracji {it}")
    print()
    proportions = solution.return_knots_proportions()
    print("Początkowe stosunki w węzłach:")
    for key, value in proportions.items():
        print("     ", key, " : ", value)
    proportions = best_sol.return_knots_proportions()
    print("Końcowe stosunki w węzłach:")
    for key, value in proportions.items():
        print("     ", key, " : ", value)


def test_cross_solutions():
    S1 = ak.random_initial_solution()
    S2 = ak.random_initial_solution()
    draw_solution(S1.return_solution(), extractions_coord)
    draw_solution(S2.return_solution(), extractions_coord)
    SA.change_random_knot(S1)
    SA.change_random_knot(S2)
    S3, S4 = ag.cross_solutions(S1, S2)
    draw_solution(S3.return_solution(), extractions_coord)
    draw_solution(S4.return_solution(), extractions_coord)


def test_delete_edges():
    """
    Test delete_edges - czy zatrzymuje się na punktach poboru i węzłach, usuwa tylko krawędzie zerowe
    """
    solution: ip.Solution = ak.initial_solution_with_knots()
    print("TYLKO DLA PORÓWNANIA")
    draw_solution(solution.return_solution(), extractions_coord)
    for ex in solution.extraction_points:
        print(ex.coordinates, end=' - ')
        print(ex.extraction_satisfied, end='/')
        print(ex.extraction_value)
    print(f"Wartość funkcji celu przed dodaniem krawędzi - {ip.objective_function(solution)}")
    print("TYLKO DLA PORÓWNANIA\n\n")
    solution.add_edge((6, 3), (6, 4))
    solution.add_edge((6, 4), (6, 5))
    solution.add_edge((6, 5), (6, 6))
    solution.add_edge((6, 6), (5, 6))
    solution.add_edge((4, 3), (3, 3))
    solution.add_edge((3, 3), (3, 4))
    solution.add_edge((3, 4), (4, 4))
    draw_solution(solution.return_solution(), extractions_coord)
    print(f"Wartość funkcji celu przed usunięciem krawędzi - {ip.objective_function(solution)}")
    # Powinno usunąć wszystkie dodatkowe krawędzie - zostanie tak jak było normalnie przed dodaniem
    SA.delete_edges(solution)
    print(f"\nPo usunięciu zbędnych krawędzi: {ip.objective_function(solution)}")
    draw_solution(solution.return_solution(), extractions_coord)
    for ex in solution.extraction_points:
        print(ex.coordinates, end=' - ')
        print(ex.extraction_satisfied, end='/')
        print(ex.extraction_value)


def test_change_random_edge():
    sol = ak.random_initial_solution()
    for _ in range(10):
        SA.change_random_edge(sol)
        draw_solution(sol.return_solution(), extractions_coord)


def test_EA():
    sol, it = ag.EA(10, 10, max_it_num=5)
    draw_solution(sol.return_solution(), extractions_coord)
    print(ip.objective_function(sol))
    print(it)


def changing_knot_bf():
    """
    Funkcja realizująca przeszukiwanie wszystkich rozwiązań dla różnych rodzajów węzłów i initial_solution_with_knots
    """
    new_knot_kind = [0, 1]
    new_knot_kind2 = [1, 0]
    sol: ip.Solution = ak.initial_solution_with_knots()
    for knot_kind in ip.knot_kinds[2]:
        SA.change_knot(sol, (4, 3), knot_kind)
        for knot_kind2 in ip.knot_kinds[2]:
            SA.change_knot(sol, (4, 6), knot_kind2)
            print("(4, 3) ", knot_kind, " (4, 6) ", knot_kind2, " funkcja ", ip.objective_function(sol))
            for i in range(2):
                new_knot_kind2[i] = knot_kind2[i - 1]
            SA.change_knot(sol, (4, 6), new_knot_kind2)
            print("(4, 3) ", knot_kind, " (4, 6) ", new_knot_kind2, " funkcja ", ip.objective_function(sol))
        for i in range(2):
            new_knot_kind[i] = knot_kind[i - 1]
        SA.change_knot(sol, (4, 3), new_knot_kind)
        for knot_kind2 in ip.knot_kinds[2]:
            SA.change_knot(sol, (4, 6), knot_kind2)
            print("(4, 3) ", new_knot_kind, " (4, 6) ", knot_kind2, " funkcja ", ip.objective_function(sol))
            for i in range(2):
                new_knot_kind2[i] = knot_kind2[i - 1]
            SA.change_knot(sol, (4, 6), new_knot_kind2)
            print("(4, 3) ", new_knot_kind, " (4, 6) ", new_knot_kind2, " funkcja ", ip.objective_function(sol))

# def EA(population_num: int, mutation_prob: int = 10, crossing_prob: int = 90, destination: str = "min",
#        max_it_num=100, cost_weight: float = 0.1, time_weight: float = 0.1,
#        penalty_severity: float = 10, mutation_kind_knots: bool = True) -> Tuple[ip.Solution, int]:
def test_EA_with_file(filename: str, repeats = 10, population_num: int = 10, mutation_prob: int = 10, crossing_prob: int = 90, destination: str = "min", max_it_num=100, cost_weight: float = 0.1, time_weight: float = 0.1, penalty_severity: float = 10, mutation_kind_knots: bool = True):
    print("Tworzenie pliku")
    try:
        open(filename+".txt", 'x')
                # print(os.listdir('Dane'))
    except (FileExistsError, FileNotFoundError):
        pass
    file = open(filename+".txt", "r+")
    file.truncate(0)
    ###
    results_sol = []
    results_it = []
    for i in range(repeats):
        sol, it = ag.EA(population_num, mutation_prob, crossing_prob, destination, max_it_num, cost_weight, time_weight, penalty_severity, mutation_kind_knots)
        # try:
        #     sol, it = ag.EA(population_num, mutation_prob, crossing_prob, destination, max_it_num, cost_weight, time_weight, penalty_severity, mutation_kind_knots)
        # except:
        #     i -= 1
        #     continue
        results_sol.append(ip.objective_function(sol))
        results_it.append(it)
        print("Liczba uruchomień algorytmu: ", i+1, " / ", repeats)
    ###
    mean_sol = np.mean(results_sol)
    median_sol = np.median(results_sol)
    deviation_sol = np.std(results_sol)
    mean_it = np.mean(results_it)
    median_it = np.median(results_it)
    deviation_it = np.std(results_it)
    ###
    print("Zapisywanie do pliku")  
    output = "WYNIKI ALGORYTMU GENETYCZNEGO"
    output += "\n\n--INFORMACJE OGÓLNE--"
    output += "\nLiczba prób: " + str(repeats)
    output += "\nWielkość populacji: " + str(population_num)
    output += "\nPrawdopodobieństwo mutacji: " + str(mutation_prob) + "%"
    output += "\nPrawdopodobieństwo krzyżowania: " + str(crossing_prob) + "%"
    if destination == "min":
        output += "\nMinimalizacja funkcji celu"
    elif destination == "max":
        output += "\nMaksymalizacja funkcji celu"
    output += "\nMaksymalna dopuszczalna liczba iteracji: " + str(max_it_num)
    output += "\nWaga kosztów w funkcji celu: " + str(cost_weight)
    output += "\nWaga czasów w funkcji celu: " + str(time_weight)
    output += "\nWspółczynnik dotkliwości funkcji kary: " + str(penalty_severity)
    if mutation_kind_knots:
        output += "\nMutacja poprzez zmianę stosunków w węzłach"
    else:
        output += "\nMutacja poprzez zmianę krawędzi"
    ###
    output += "\n\n--NAJLEPSZY WYNIK--"
    best = None
    pos = None
    if destination == 'min':
        best = min(results_sol)
        pos = np.argmin(results_sol)
    elif destination == "max":
        best = max(results_sol)
        pos = np.argmax(results_sol)
    output += "\nNajlepsza wartość funkcji celu: " + str(best)
    output += "\nLiczba wykonanych iteracji: " + str(results_it[pos])
    ###
    output += "\n\n--STATYSTYKA--"
    output += "\nŚrednia wartość funkcji celu: " + str(mean_sol)
    output += "\nŚrednia wartość liczby iteracji: " + str(mean_it)
    output += "\nMediana funkcji celu: " + str(median_sol)
    output += "\nMediana liczby iteracji: " + str(median_it)
    output += "\nOdchylenie standardowe funkcji celu: " + str(deviation_sol)
    output += "\nOdchylenie standardowe liczby iteracji: " + str(deviation_it)
    ###
    output += "\n\n--PRÓBY--"
    output += "\nWartość funkcji celu : Liczba iteracji"
    for i in range(len(results_sol)):
        output += "\n" + str(results_sol[i]) + " : " + str(results_it[i])
    ###
    file.writelines(output)
    file.close()
    print('GOTOWE')


if __name__ == '__main__':
    # INSTRUKCJA UŻYWANIA TESTÓW:
    # Odkomentuj wiersz z danym testem, uruchom plik (ale nie jako pytest!), skonsultuj wyniki z opisem funkcji
    # testującej

    # test_read_from_file()
    # POZOSTAWIĆ TE 2 LINIJKI ODKOMENTOWANE
    wd.read_from_file('DANE.xlsx')
    extractions_coord: List[ip.Tuple[int, int]] = [el.coordinates for el in ip.extraction_points]

    # test_point_comparison()
    # test_knots()
    # test_random_route()
    # test_SA(knot_neighbourhood=True)
    # draw_solution(ak.random_initial_solution().return_solution(), extractions_coord)
    # test_delete_edges()  # NIE UŻYWAĆ - nie jest naprawione
    # test_cross_solutions()
    # test_change_random_edge()
    # test_EA()
    # sol = changing_knot_bf()

    #--TWORZENIE TESTÓW EA--

    # test_EA_with_file(filename="EA_BasicTest_MutationByKnots", repeats=100, population_num=20, max_it_num=20)
    # test_EA_with_file(filename="EA_BasicTest_MutationByEdges", repeats=100, population_num=20, max_it_num=20, mutation_kind_knots=False)
    
    # test_EA_with_file(filename="EA_MutationVeryImportant_MutationByKnots", repeats=100, population_num=20, max_it_num=20, mutation_prob=70)
    # test_EA_with_file(filename="EA_MutationVeryImportant_MutationByEdges", repeats=100, population_num=20, max_it_num=20, mutation_prob=70, mutation_kind_knots=False)

    # test_EA_with_file(filename="EA_LowPopulation_MutationByKnots", repeats=100, population_num=10, max_it_num=20)
    # test_EA_with_file(filename="EA_LowPopulation_MutationByEdges", repeats=100, population_num=10, max_it_num=20, mutation_kind_knots=False)
    # test_EA_with_file(filename="EA_HighPopulation_MutationByKnots", repeats=100, population_num=30, max_it_num=20)
    # test_EA_with_file(filename="EA_HighPopulation_MutationByEdges", repeats=100, population_num=30, max_it_num=20, mutation_kind_knots=False)

    test_EA_with_file(filename="EA_LowPenalty_MutationByKnots", repeats=100, population_num=20, max_it_num=20, penalty_severity=1)
    test_EA_with_file(filename="EA_LowPenalty_MutationByEdges", repeats=100, population_num=20, max_it_num=20, penalty_severity=1, mutation_kind_knots=False)