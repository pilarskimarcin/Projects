import implementacja_problemu as ip
from typing import List
from random import randint, choice


# _________________________________________________________________________________________________________
# DO ALGORYTMU SA


def initial_solution():
    """
    Funkcja tworząca rozwiązanie początkowe (algorytm konstrukcyjny)
    """
    extractions: List[ip.Point_coordinates] = [el.coordinates for el in ip.extraction_points]
    extractions.sort(key=lambda x: x[0])  # Sort by 'x'
    # extractions.sort(key = lambda x: [x[0], x[1]]) # Sort by 'x', if equal sort by 'y'

    # Printowanie posortowanej listy współrzędnych (test)
    #
    # for el in extractions:
    #     print(el, end='  ')
    # print()

    to_right: bool = True  # Czy idziemy w rozwiązaniu w prawo czy w lewo
    cur: List[int, int] = [0, 0]  # Współrzędne aktualnego punktu w rozwiązaniu
    ep: int = 0  # Indeks aktualnego punktu poboru
    sol: ip.Solution = ip.Solution()

    # Plan działania:
    # A) Jeśli idziemy w prawo:
    #       1) Idź po y-ach w lewo aż do lewego y
    #       2) Idź po x-ach w dół aż do docelowego x
    #       3) Idź po y-ach w prawo aż do prawego y
    #       4) Zmień kierunek z prawego na lewy
    # B) Jeśli idziemy w lewo:
    #       1) Idź po y-ach w prawo aż do prawego y
    #       2) Idź po x-ach w dół aż do docelowego x
    #       3) Idź po y-ach w lewo aż do lewego y
    #       4) Zmień kierunek z lewego na prawy
    #
    # Wszytko powtarzaj aż do wyczerpania x-ów docelowych

    while ep < len(extractions):
        all_y_in_x: List[int] = [extractions[ep][1]]  # Zbiór wszystkich 'y' dla danego 'x'
        for i in range(ep + 1, len(extractions)):
            if extractions[ep][0] == extractions[i][0]:
                all_y_in_x.append(extractions[i][1])
            else:
                break
        right_y: int = max(all_y_in_x)  # Najbardziej prawy 'y' dla danego 'x'
        left_y: int = min(all_y_in_x)  # Najbardziej lewy 'y' dla danego 'x'
        if to_right:
            while cur[1] > left_y:
                sol.add_edge((cur[0], cur[1]), (cur[0], cur[1] - 1))
                cur[1] -= 1
            while cur[0] < extractions[ep][0]:
                sol.add_edge((cur[0], cur[1]), (cur[0] + 1, cur[1]))
                cur[0] += 1
            while cur[1] < right_y:
                sol.add_edge((cur[0], cur[1]), (cur[0], cur[1] + 1))
                cur[1] += 1
            to_right = False
        else:
            while cur[1] < right_y:
                sol.add_edge((cur[0], cur[1]), (cur[0], cur[1] + 1))
                cur[1] += 1
            while cur[0] < extractions[ep][0]:
                sol.add_edge((cur[0], cur[1]), (cur[0] + 1, cur[1]))
                cur[0] += 1
            while cur[1] > left_y:
                sol.add_edge((cur[0], cur[1]), (cur[0], cur[1] - 1))
                cur[1] -= 1
            to_right = True
        ep += len(all_y_in_x)
    return sol


def initial_solution_with_knots():
    """
    Funkcja tworząca rozwiązanie początkowe z węzłami
    """
    extractions: List[ip.Point_coordinates] = [el.coordinates for el in ip.extraction_points]
    extractions.sort(key=lambda x: [x[0], x[1]])  # Sort by 'x', if equal sort by 'y'
    cur: List[int, int] = [0, 0]  # Współrzędne aktualnego punktu w rozwiązaniu
    max_x = 0  # maksymalna współrzędna x występująca w rozwiązaniu
    max_y = 0  # maksymalna współrzędna y występująca w rozwiązaniu
    sol: ip.Solution = ip.Solution()
    for ep in extractions:
        it = 0
        while ep[0] > max_x:
            if it == 0:
                if ep[1] >= max_y:
                    cur = [max_x, max_y]
                else:
                    for p in sol.points:
                        if p[1] == ep[1]:
                            cur = [p[0], p[1]]
                            break
            sol.add_edge((cur[0], cur[1]), (cur[0] + 1, cur[1]))
            cur[0] += 1
            max_x = cur[0] if cur[0] > max_x else max_x
            it += 1
        it = 0
        while ep[1] > max_y:
            if it == 0:
                if ep[0] >= max_x:
                    cur = [max_x, max_y]
                else:
                    for p in sol.points:
                        if p[0] == ep[0]:
                            cur = [p[0], p[1]]
                            break
            sol.add_edge((cur[0], cur[1]), (cur[0], cur[1] + 1))
            cur[1] += 1
            max_y = cur[1] if cur[1] > max_y else max_y
            it += 1
    return sol


# _________________________________________________________________________________________________________
# DO ALGORYTMU EA


def random_route(solution: ip.Solution, start: ip.Point_coordinates, end: ip.Point_coordinates):
    """
    Funkcja tworząca "zygzakowatą" drogę z jednego punktu do drugiego
    :param sol: Obiekt klasy Solution
    :param start: Punkt startowy
    :param end: Punkt końcowy
    """
    sol: ip.Solution = solution.copy()
    cur: ip.Point_coordinates = start
    done: bool = True  # Czy wykonano już akcję w ramach pętli
    while done:
        done = False
        random: int = randint(0, 1)  # "0" oznacza ruch prawo-lewo, a "1" góra-dół
        # ruch w poziomie
        if not random or end[0] == cur[0]:
            # ruch w prawo
            if end[1] > cur[1]:
                dest = (cur[0], cur[1] + 1)
                indicator = sol.check_if_edge_correct(cur, dest)
                if not indicator:
                    sol.add_edge(cur, dest)
                    cur = dest
                    done = True
                elif indicator == 4:
                    cur = dest
                    done = True
                elif indicator not in (0, 4):
                    raise ValueError("Wrong indicator")
            # ruch w lewo
            elif end[1] < cur[1]:
                dest = (cur[0], cur[1] - 1)
                indicator = sol.check_if_edge_correct(cur, dest)
                if not indicator:
                    sol.add_edge(cur, dest)
                    cur = dest
                    done = True
                elif indicator == 4:
                    cur = dest
                    done = True
                elif indicator not in (0, 4):
                    raise ValueError("Wrong indicator")
        # ruch w pionie
        # elif random or not done or end[1] == cur[1]:
        if not done:
            # ruch w dół
            if end[0] > cur[0]:
                dest = (cur[0] + 1, cur[1])
                indicator = sol.check_if_edge_correct(cur, dest)
                if not indicator:
                    sol.add_edge(cur, dest)
                    cur = dest
                    done = True
                elif indicator == 4:
                    cur = dest
                    done = True
                elif indicator not in (0, 4):
                    raise ValueError("Wrong indicator")
            # ruch w górę
            elif end[0] < cur[0]:
                dest = (cur[0] - 1, cur[1])
                indicator = sol.check_if_edge_correct(cur, dest)
                if not indicator:
                    sol.add_edge(cur, dest)
                    cur = dest
                    done = True
                elif indicator == 4:
                    cur = dest
                    done = True
                elif indicator not in (0, 4):
                    raise ValueError("Wrong indicator")
    return sol


def random_initial_solution():
    """
    Funkcja tworząca losowe rozwiązanie początkowe z uwzględnieniem węzłów
    """
    # UWAGA!! Funkcja jest wysoce niestabilna - będzie się wykonywała aż zwróci poprawny wynik! - (można to minimalnie poprawić jak coś)
    # try-except sprawdzający błąd przekroczenia dopuszczalnej ilości rekurencji
    try:
        extractions: List[ip.Point_coordinates] = [el.coordinates for el in ip.extraction_points]
        sol: ip.Solution = ip.Solution()
        while extractions:
            start: ip.Point_coordinates = choice(sol.points)
            end: ip.Point_coordinates = choice(extractions)
            # try-except sprawdzający ValueError-y z random_route i z dodawania węzłów -> jeśli nie możemy dodać węzła, musimy spróbować dodać trasę do punktu w inny sposób
            try:
                solu = random_route(sol, start, end)
                to_remove = []
                for extr in extractions:
                    if extr in solu.points:
                        to_remove.append(extr)
                for extr in to_remove:
                    extractions.remove(extr)
            except ValueError:
                continue
            # solu = random_route(sol, start, end)
            # for extr in extractions:
            #     if extr in solu.points:
            #         extractions.remove(extr)
            sol = solu  # Nadpisanie rozwiązania nowym rozwiązaniem z dopuszczalną ścieżką
        return sol
    except RecursionError:
        return random_initial_solution()

