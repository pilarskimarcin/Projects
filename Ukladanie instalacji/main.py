from typing import Dict
from wczytywanie_danych import *
from algorytm_genetyczny import *
import algorytm_konstrukcyjny as ak
from wyrysowywanie_rozwiązania import draw_solution
import PySimpleGUI as sg


def layout_main():
    layout: List[List[sg.Element]] = [
        [sg.T()],
        [sg.Column([[sg.T("Problem układania instalacji wodociągowej", font="Arial 16")]], justification='center')],
        [sg.T("Parametry funkcji celu:")],
        [sg.T("Waga kosztów:"), sg.In("0.1", size=7, key="cost_w"),
         sg.T("Waga czasów:"), sg.In("0.1", size=7, key="time_w")],
        [sg.T("Dotkliwość kary za niezaspokojenie punktów poboru:"), sg.In("1", size=7, key="penalty")],
        [sg.Column([
            [sg.Button("Algorytm SA", enable_events=True, key="SA", size=(22, 7))],
            [sg.Button("Algorytm Genetyczny", enable_events=True, key="AG", size=(22, 7))]
        ], justification='center')],
        [sg.T()],
        [sg.Exit("Wyjdź")]
    ]
    return sg.Window("Projekt - Badania Operacyjne", layout, finalize=True)


def layout_SA():
    layout: List[List[sg.Element]] = [
        [sg.Column([[sg.T("Parametry algorytmu SA:", font="Helvetica 13")]], justification='center')],
        [sg.T("Temperatura początkowa:"), sg.In("5", size=7, key='T0'),
         sg.T("Współczynnik liniowej zmiany temperatury (0 < alfa < 1):"), sg.In("0.1", size=7, key='alfa')],
        [sg.T("Maksymalna liczba iteracji:"), sg.In("100", size=7, key='max_it'),
         sg.T("Liczba iteracji w jednej temperaturze:"), sg.In("10", size=7, key='n_it_temp')],
        [sg.T("Sposób określenia sąsiedztwa:"),
         sg.Radio("Zmiana stosunków węzła", "neighbourhood", default=True, key="knot"),
         sg.Radio("Zmiana krawędzi", "neighbourhood")],
        [sg.Submit("Start"), sg.T(expand_x=True), sg.Button('Powrót'), sg.Exit("Wyjdź")],
        [sg.T()],
        [sg.Multiline(do_not_clear=False, reroute_stdout=True, size=(60, 21), font='Courier 12')]
    ]
    return sg.Window("Algorytm Symulowanego Wyżarzania", layout, finalize=True)


def layout_AG():
    layout: List[List[sg.Element]] = [
        [sg.Column([[sg.T("Parametry algorytmu AG:", font="Helvetica 13")]], justification='center')],
        [sg.T("Liczebność populacji:"), sg.In("20", size=7, key="population_num"),
         sg.T("Cel optymalizacji:"), sg.Combo(["min", "max"], "min", key="destination"),
         sg.T("Maksymalna liczba iteracji:"), sg.In("100", size=7, key="max_it")],
        [sg.T("Prawdopodobieństwo mutacji:"), sg.In("10", size=7, key="mutation_prob"), sg.T("%"), sg.T(" "),
         sg.T("Prawdopodobieństwo krzyżowania:"), sg.In("90", size=7, key="crossing_prob"), sg.T("%")],
        [sg.T("Sposób mutacji:"), sg.Radio("Zmiana stosunków węzła", "mutation", default=True, key="knot"),
         sg.Radio("Zmiana krawędzi", "mutation")],
        [sg.Submit("Start"), sg.T(expand_x=True), sg.Button('Powrót'), sg.Exit("Wyjdź")],
        [sg.T()],
        [sg.Multiline(do_not_clear=False, reroute_stdout=True, size=(60, 21), font='Courier 12')]
    ]
    return sg.Window("Algorytm Genetyczny", layout, finalize=True)


def SA_main(t0: float, alfa: float, max_it_number: int, it_number_in_one_temp: int, neighbourhood_changing_knots: bool,
            f_cost_parameters: List[float]):
    """
    Algorytm symulowanego wyżarzania
    :param t0: temperatura początkowa
    :param alfa: liniowa zmiana temperatury, alfa należy do (0, 1)
    :param max_it_number: maksymalna liczba iteracji algorytmu
    :param it_number_in_one_temp: liczba iteracji w jednej temperaturze
    :param neighbourhood_changing_knots: czy sąsiedztwo to zmiana stosunków węzła, czy zmiana krawędzi
    :param f_cost_parameters: parametry funkcji celu:
        waga kosztu położenia krawędzi w funkcji celu,
        waga czasu położenia krawędzi w funkcji celu,
        waga kary za niedostarczenie wody do węzła w funkcji celu
    """
    solution: ip.Solution = ak.random_initial_solution()
    # solution = ak.initial_solution_with_knots()
    best_sol: ip.Solution
    it_best: int
    best_sol, it_best = SA.SA(solution, t0, alfa, max_it_number, it_number_in_one_temp, neighbourhood_changing_knots,
                              f_cost_parameters)
    global extractions_coord
    print()
    draw_solution(solution.return_solution(), extractions_coord)
    print(f"Początkowe rozwiązanie: {ip.objective_function(solution, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]):.4f}")
    print(f"Najlepsze rozwiązanie: {ip.objective_function(best_sol, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]):.4f}, znalezione w iteracji {it_best}")
    print()
    if neighbourhood_changing_knots and len(solution.knots) != 0:
        proportions = solution.return_knots_proportions()
        print("Początkowe stosunki w węzłach:")
        for key, value in proportions.items():
            print("     ", key, " : ", value)
        proportions = best_sol.return_knots_proportions()
        print("Końcowe stosunki w węzłach:")
        for key, value in proportions.items():
            print("     ", key, " : ", value)


def AG_main(population_num: int, mutation_prob: int, crossing_prob: int, destination: str, max_it_num: int,
            f_cost_parameters: List[float], mutation_kind_knots: bool):
    """
    Alsgorytm genetyczny
    :param population_num: Liczebność populacji
    :param mutation_prob: Prawdopodobieństwo wystąpienia mutacji (w procentach)
    :param crossing_prob: Prawdopodobieństwo wystąpienia krzyżowania (w procentach)
    :param destination: Określenie czy chcemy maksymalizować czy minimalizować funkcję celu ("max", "min")
    :param max_it_num: kryterium stopu - maksymalna liczba iteracji
    :param f_cost_parameters: parametry funkcji celu:
        waga kosztu położenia krawędzi w funkcji celu,
        waga czasu położenia krawędzi w funkcji celu,
        waga kary za niedostarczenie wody do węzła w funkcji celu
    :param mutation_kind_knots: czy mutacja to zmiana stosunków w węzłach
    """
    best_sol: ip.Solution
    it_best: int
    best_sol, it_best = EA(population_num, mutation_prob, crossing_prob, destination, max_it_num, f_cost_parameters[0],
                           f_cost_parameters[1], f_cost_parameters[2], mutation_kind_knots)
    print()
    draw_solution(best_sol.return_solution(), extractions_coord)
    print(f"Najlepsze rozwiązanie: {ip.objective_function(best_sol, f_cost_parameters[0], f_cost_parameters[1], f_cost_parameters[2]):.4f}, znalezione w iteracji {it_best}")
    if mutation_kind_knots and len(best_sol.knots) != 0:
        proportions = best_sol.return_knots_proportions()
        print("Końcowe stosunki w węzłach:")
        for key, value in proportions.items():
            print("     ", key, " : ", value)


if __name__ == '__main__':
    read_from_file('DANE.xlsx')
    extractions_coord: List[ip.Tuple[int, int]] = [el.coordinates for el in ip.extraction_points]
    mode: str = 'main'
    cost_f_params: List[float] = []
    window = layout_main()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Wyjdź":
            break
        # main
        elif event == 'SA' or event == 'AG':
            cost_f_params = [float(values["cost_w"]), float(values["time_w"]), float(values["penalty"])]
            window.close()
            if event == 'SA':
                mode = 'SA'
                window = layout_SA()
            else:
                mode = 'AG'
                window = layout_AG()
        # SA
        elif event == 'Start' and mode == 'SA':
            SA_main(float(values["T0"]), float(values["alfa"]), int(values["max_it"]), int(values["n_it_temp"]),
                    values["knot"], cost_f_params)
        elif event == 'Powrót':
            mode = 'main'
            window.close()
            window = layout_main()
        # AG
        elif event == 'Start' and mode == 'AG':
            AG_main(int(values["population_num"]), int(values["mutation_prob"]), int(values["crossing_prob"]),
                    values["destination"], int(values["max_it"]), cost_f_params, values["knot"])


