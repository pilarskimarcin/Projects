from __future__ import annotations

import copy
from typing import List, Tuple, Optional, Dict, Union

Point_coordinates = Tuple[int, int]  # współrzędne punktów
Edge = Tuple[Point_coordinates, Point_coordinates]

# Dane (globalne) do wczytania z pliku:
source_capacity: Optional[float] = None  # pojemność źródła
point_matrix: List[List[Optional[Point]]] = [[]]  # Macierz wszystkich punktów
extraction_points: List[ExtractionPoint] = []  # Lista punktów poboru
max_time: Optional[float] = None  # maksymalny czas położenia kawałka instalacji między sąsiednimi punktami
max_cost: Optional[float] = None  # maksymalny koszt położenia kawałka instalacji między sąsiednimi punktami
knot_kinds: Dict[int, List[List[float]]] = {}  # słownik możliwych rozgałęzień w postaci {2: [lst1, lst2..], 3: [lst1,
#   lst2...]}, gdzie lst1, lst2 to listy możliwych ułamków przepływu w poszczególnych gałęziach rozgałęzienia
knot_dx: Optional[int] = None  # Minimalna wymagana odległość między węzłami w poziomie
knot_dy: Optional[int] = None  # Minimalna wymagana odległość między węzłami w pionie


class Point:
    coordinates: Point_coordinates
    time_left: Optional[float]
    time_up: Optional[float]
    time_right: Optional[float]
    time_down: Optional[float]
    cost_left: Optional[float]
    cost_up: Optional[float]
    cost_right: Optional[float]
    cost_down: Optional[float]
    flow: float  # przepływ w danym punkcie
    is_knot: Dict[str, Optional[List[float]]]  # czy punkt jest węzłem - np. {"out": [0.5, 0.5], "in": None}
    previous_points: List[Point_coordinates]

    def __init__(self, coordinates: Tuple[int, int], time_left: Optional[float], time_up: Optional[float],
                 time_right: Optional[float], time_down: Optional[float], cost_left: Optional[float],
                 cost_up: Optional[float], cost_right: Optional[float], cost_down: Optional[float], flow: float = 0):
        self.coordinates = coordinates
        self.time_left = time_left
        self.time_up = time_up
        self.time_right = time_right
        self.time_down = time_down
        self.cost_left = cost_left
        self.cost_up = cost_up
        self.cost_right = cost_right
        self.cost_down = cost_down
        self.flow = flow
        self.is_knot = {}
        self.previous_points = []

    def __eq__(self, other: Union[Point, ExtractionPoint]):
        if self.coordinates == other.coordinates:
            return True
        return False

    def __hash__(self):
        return hash(self.coordinates)

    def __str__(self):
        return str(self.coordinates)

    def copy(self):
        copy_point = Point(self.coordinates, self.time_left, self.time_up, self.time_right, self.time_down,
                           self.cost_left, self.cost_up, self.cost_right, self.cost_down, self.flow)
        copy_point.is_knot = copy.deepcopy(self.is_knot)
        copy_point.previous_points = copy.deepcopy(self.previous_points)
        return copy_point

    def knot_proportions(self):
        if not self.is_knot or "out" not in self.is_knot.keys():
            return False
        return self.is_knot["out"]


class ExtractionPoint:  # punkty poboru
    coordinates: Point_coordinates
    extraction_value: float  # wartość poboru
    extraction_satisfied: float  # wartość poboru, która została już zaspokojona

    def __init__(self, coordinates: Point_coordinates, extraction_value: float):
        self.coordinates = coordinates
        self.extraction_value = extraction_value
        self.extraction_satisfied = 0

    def __str__(self):
        return str(self.coordinates)

    def __eq__(self, other: Union[Point, ExtractionPoint]):
        if self.coordinates == other.coordinates:
            return True
        return False


class Solution:
    solution_graph: Dict[Point_coordinates, List[Tuple[Point_coordinates, str, float, float]]]  # rozwiązanie w formie
    # grafu (lista sąsiedztwa - słownik: {Punkt startowy: [[Punkt końcowy, kierunek krawędzi, koszt, czas]]})
    costs_sum: float  # suma wszystkich kosztów w rozwiązaniu
    times_sum: float  # suma wszystkich czasów w rozwiązaniu
    points: List[Point_coordinates]  # Lista punktów dodanych do rozwiązania
    knots: List[Point_coordinates]  # Lista węzłów w danym rozwiązaniu
    extraction_points: List[ExtractionPoint]  # Lista punktów poboru w danym rozwiązaniu
    point_matrix: List[List[Point]]

    def __init__(self):
        self.solution_graph = {(0, 0): []}
        self.costs_sum = 0
        self.times_sum = 0
        self.points = [(0, 0)]
        self.knots = []
        self.extraction_points = copy.deepcopy(extraction_points)
        self.point_matrix = copy.deepcopy(point_matrix)

    def copy(self):
        copy_solution = Solution()
        copy_solution.solution_graph = copy.deepcopy(self.solution_graph)
        copy_solution.costs_sum = self.costs_sum
        copy_solution.times_sum = self.times_sum
        copy_solution.points = copy.deepcopy(self.points)
        copy_solution.knots = copy.deepcopy(self.knots)
        copy_solution.extraction_points = copy.deepcopy(self.extraction_points)
        copy_solution.point_matrix = copy.deepcopy(self.point_matrix)
        return copy_solution

    def update_extraction_point(self, possible_ex_point_coordinates: Point_coordinates, is_add_knot: bool = False):
        """
        Pomocnicza funkcja do aktualizacji zapełnienia punktów poboru
        :param possible_ex_point_coordinates: współrzędne badanego punktu
        :param is_add_knot: parametr określający w jaki sposób dostaliśmy badany punkt - potrzebny do ustalenia w jaki
        sposób ustalić extraction_satisfied, jeśli True, dostaliśmy z funkcji dodającej węzeł
        """
        possible_ex_point: Point = self.point_matrix[possible_ex_point_coordinates[0]][possible_ex_point_coordinates[1]]
        # Sprawdzenie czy punkt jest punktem poboru
        for extraction_point in self.extraction_points:
            if extraction_point.coordinates == possible_ex_point.coordinates:
                if is_add_knot:
                    extraction_point.extraction_satisfied = possible_ex_point.flow
                else:
                    extraction_point.extraction_satisfied += possible_ex_point.flow
                if extraction_point.extraction_satisfied > extraction_point.extraction_value:
                    possible_ex_point.flow = extraction_point.extraction_satisfied - \
                                             extraction_point.extraction_value
                    extraction_point.extraction_satisfied = extraction_point.extraction_value
                else:
                    possible_ex_point.flow = 0
                break

    def update_flow(self, point_coord: Point_coordinates, dflow: float = None):
        """
        Funkcja aktualizująca przepływ w punktach
        :param point_coord: obecny punkt, z którego aktualizujemy przepływ
        :param dflow: różnica pomiędzy nowym przepływem punktu a poprzednim
        """
        # Jeśli nie został podany dflow
        if point_coord not in self.solution_graph.keys():
            return
        point = self.point_matrix[point_coord[0]][point_coord[1]]
        if dflow is None:
            for i in range(len(self.solution_graph[point_coord])):
                edge = self.solution_graph[point_coord][i]
                next_point: Point = self.point_matrix[edge[0][0]][edge[0][1]]
                old_flow: float = next_point.flow
                # Aktualizacja przepływu następnego punktu na podstawie obecnego
                next_point.flow = point.is_knot["out"][i] * point.flow if "out" in point.is_knot.keys() else point.flow
                # Jeśli następny punkt jest węzłem wchodzącym, trzeba będzie dodać przepływy z jego innych poprzedników
                if "in" in next_point.is_knot:
                    for prev_of_next_point_coord in next_point.previous_points:
                        prev_of_next_point: Point = self.point_matrix[prev_of_next_point_coord[0]][
                            prev_of_next_point_coord[1]]
                        # Pominięcie punktu, dla którego już to zostało obliczone
                        if prev_of_next_point == point:
                            continue
                        # Jeśli poprzednik następnego punktu jest węzłem wychodzącym, trzeba znaleźć punkt wśród
                        # krawędzi wychodzących i obliczyć składową przepływu next_point na podstawie procentu
                        if "out" in prev_of_next_point.is_knot:
                            for j in range(len(self.solution_graph[prev_of_next_point_coord])):
                                edge = self.solution_graph[prev_of_next_point_coord][j]
                                if next_point.coordinates in edge:
                                    new_flow: float = prev_of_next_point.flow * prev_of_next_point.is_knot["out"][j]
                        # Jeśli jednak poprzednikiem jest zwykły punkt, składową będzie przepływ tego punktu
                        else:
                            new_flow: float = point.flow
                        next_point.flow += new_flow
                # Jeśli następny punkt jest punktem poboru, trzeba zaktualizować jego zapełnienie
                self.update_extraction_point(next_point.coordinates)
                # Jeśli następny punkt jest w kluczach słownika, ma kolejny/e punkt/y za sobą, trzeba dla niego wywołać
                # funkcję rekurencyjnie
                if next_point.coordinates in self.solution_graph.keys() and next_point.flow != old_flow:
                    self.update_flow(next_point.coordinates, next_point.flow - old_flow)
            return
        # Aktualizacja dla węzłów wychodzących
        if "out" in point.is_knot.keys():
            # Musimy zaktualizować przepływ każdego jednego punktu, do którego wychodzą krawędzie z point
            out_list: List[Point_coordinates] = [v[0] for v in self.solution_graph[point_coord]]
            # Sprawdzamy jak rozdziela węzeł
            knot_type: List[float] = point.is_knot["out"]
            for i in range(len(out_list)):
                next_point: Point = self.point_matrix[out_list[i][0]][out_list[i][1]]
                # nowy przepływ next_point wyliczony na podstawie procentu z knot_type
                dflow_next_point = knot_type[i] * dflow
                next_point.flow += dflow_next_point
                # Jeśli następny punkt jest punktem poboru, trzeba zaktualizować jego zapełnienie
                self.update_extraction_point(next_point.coordinates)
                if next_point.flow < 0:
                    next_point.flow = 0
                # Jeśli następny punkt jest w kluczach słownika, ma kolejny/e punkt/y za sobą, trzeba dla niego wywołać
                # funkcję rekurencyjnie
                if next_point.coordinates in self.solution_graph.keys():
                    self.update_flow(next_point.coordinates, dflow_next_point)
        # Aktualizacja przepływu dla punktów, które nie są węzłami wychodzącymi
        else:
            # Do następnego punktu dodajemy zmianę wartości przepływu
            next_point_coord: Point_coordinates = self.solution_graph[point_coord][0][0]
            next_point: Point = self.point_matrix[next_point_coord[0]][next_point_coord[1]]
            old_flow: float = next_point.flow
            next_point.flow += dflow
            # Jeśli następny punkt jest punktem poboru, trzeba zaktualizować jego zapełnienie
            self.update_extraction_point(next_point.coordinates)
            if next_point.flow < 0:
                next_point.flow = 0
            # Jeśli następny punkt jest w kluczach słownika, ma kolejny/e punkt/y za sobą, trzeba dla niego wywołać
            # funkcję rekurencyjnie
            if next_point_coord in self.solution_graph.keys():
                self.update_flow(next_point_coord, next_point.flow - old_flow)

    def add_knot_out(self, point_coord: Point_coordinates, out_list: List[Point_coordinates],
                     knot_kind: List[float]) -> bool:
        """
        Funkcja dodająca rozgałęzienia
        :param point_coord: Punkt, w którym dodajemy rozgałęzienie
        :param out_list: lista punktów - końców krawędzi wychodzących z rozgałęzienia
        :param knot_kind: rodzaj węzła
        :return: czy operacja się powiodła
        """
        # Sprawdzenie czy węzeł może powstać
        if not self.check_knots_distances(point_coord):
            return False
        # Dodanie punktu do węzłów, ustawienie informacji o tym, że jest węzłem wychodzącym, aktualizacja przepływów
        if point_coord not in self.knots:
            self.knots.append(point_coord)
        point: Point = self.point_matrix[point_coord[0]][point_coord[1]]
        point.is_knot["out"] = knot_kind
        # Przepływ trzeba zaktualizować w każdej z wychodzących krawędzi
        for i in range(len(out_list)):
            out_point_coord: Point_coordinates = out_list[i]
            out_point: Point = self.point_matrix[out_point_coord[0]][out_point_coord[1]]
            dflow: float
            if "in" in out_point.is_knot.keys():
                old_flow: float = 0  # Suma przepływów w węźle wchodzącym, poza krawędzią wychodzącą z point
                for key in self.solution_graph.keys():
                    # Ominięcie węzła point
                    if key == point_coord:
                        continue
                    for j in range(len(self.solution_graph[key])):
                        edge: Tuple[Point_coordinates, str, float, float] = self.solution_graph[key][j]
                        if out_point_coord == edge[0]:
                            # Skoro out_point jest połączony z innym punktem krawędzią, zostaje dodany do zmiennej
                            # przepływ z tego punktu
                            key_point: Point = self.point_matrix[key[0]][key[1]]
                            if "out" in key_point.is_knot.keys():
                                old_flow += key_point.flow * key_point.is_knot["out"][j]
                            else:
                                old_flow += key_point.flow
                # Różnica między nowym przepływem, a starym to różnica sumy nowego przepływu z węzła point oraz starych
                # przepływów z innych punktów oraz starej wartości przepływu w out_point
                old_out_point_flow = out_point.flow
                out_point.flow = point.flow * knot_kind[i] + old_flow
                self.update_extraction_point(out_point_coord, is_add_knot=True)
                dflow = out_point.flow - old_out_point_flow
                if out_point_coord in self.solution_graph.keys():
                    self.update_flow(out_point_coord, dflow)
            else:
                old_flow = out_point.flow
                out_point.flow = point.flow * knot_kind[i]
                self.update_extraction_point(out_point_coord, is_add_knot=True)
                dflow = out_point.flow - old_flow
                if out_point_coord in self.solution_graph.keys():
                    self.update_flow(out_point_coord, dflow)
        return True

    def add_knot_in(self, point_cord: Point_coordinates, flow: float) -> bool:
        """
        Metoda ustalająca przepływ w punkcie w przypadku węzła, do którego wchodzi kilka krawędzi
        :param point_cord: punkt będący węzłem
        :param flow: wartość przepływu z krawędzi, którą dodajemy
        :return: czy operacja się powiodła
        """
        point = self.point_matrix[point_cord[0]][point_cord[1]]
        # Sprawdzenie czy węzeł może powstać
        if not self.check_knots_distances(point_cord):
            return False
        # Dodanie punktu do węzłów, ustawienie informacji o tym, że jest węzłem wchodzącym, aktualizacja przepływu
        if point_cord not in self.knots:
            self.knots.append(point_cord)
        point.is_knot["in"] = None
        point.flow += flow
        self.update_extraction_point(point.coordinates)
        self.update_flow(point_cord, flow)
        return True

    def add_knot_in_out(self, P2: Point_coordinates, point_cord: Point_coordinates, out_list: List[Point_coordinates],
                        knot_kind: List[float]) -> bool:
        """
        Metoda dodająca węzeł wchodzący i ychodzący (gdy dodanie kawędzi powoduje dodanie dwóch węzłów)
        """
        old_flow = self.point_matrix[P2[0]][P2[1]].flow
        is_node_added = self.add_knot_out(point_cord, out_list, knot_kind)
        if not is_node_added:
            return False
        return self.add_knot_in(P2, old_flow)

    def check_cycle_dfs(self, start: Point_coordinates, end: Point_coordinates, visited: List[Point_coordinates],
                        cycle: List[int]):
        """
        Metoda pomocnicza sprawdzająca, czy po dodaniu krawędzi powstanie cykl:
        :param start: punkt, od którego startujemy
        :param end: punkt, jeśli do niego dojdziemy to znaczy, że po dodaniu krawędzi powstanie cykl
        :param visited: odwiedzone wierzchołki
        :param cycle: czy powstaje cykl - jeśli tak, dodaję liczbę do listy
        :return: czy powstaje cykl: True - tak, False - nie
        """
        if start not in visited:
            visited.append(start)  # dodanie punktu startowego do visited
            if start in self.solution_graph.keys():
                for edge in self.solution_graph[start]:
                    if edge[0] == end:
                        cycle.append(
                            1)  # jeśli powstaje cykl, dodaję element do listy - odpowiedź dot. istnienia cyklu zwracam na podstawie długości listy
                    self.check_cycle_dfs(edge[0], end, visited, cycle)

    def check_cycle(self, P1: Point_coordinates, P2: Point_coordinates):
        """
        Metoda sprawdzająca, czy po dodaniu krawędzi powstanie cykl: True - powstanie, False - nie powstanie
        :param P1: pierwszy punkt badanej krawędzi
        :param P2: drugi punkt badanej krawędzi
        """
        cycle = []
        visited = []
        self.check_cycle_dfs(P2, P1, visited, cycle)
        return bool(len(cycle))

    def check_if_edge_correct(self, P1: Point_coordinates, P2: Point_coordinates) -> int:
        """
        Metoda sprawdzająca, czy może istnieć krawędź o podanych wierzchołkach
        :param P1: pierwszy punkt
        :param P2: drugi punkt
        :return: 0 - krawędź jest poprawna, 1 - błędne współrzędne - nie może istnieć taka krawędź, 2 - początkowy punkt
        nie został jeszcze dodany do rozwiązania, 3 - początkowy punkt ma zerowy przepływ, 4 - podana krawędź istnieje,
        5 - istnieje przeciwna krawędź, 6 - powstaje pętla
        """
        # Sprawdzenie, czy może istnieć krawędź o podanych punktach:
        if (P1[0] != P2[0] and P1[1] != P2[1]) or (P1[0] == P2[0] and P1[1] == P2[1]):
            # print("Nie istnieje taka krawędź")
            return 1
        # Sprawdzenie czy krawędź jest ciągłym przedłużeniem rozwiązania:
        if P1 not in self.points:
            # print("Krawędź nie jest przedłużeniem rozwiązania")
            return 2
        # Sprawdzenie czy krawędź nie wychodzi z punktu, w którym nie ma wody (przez to, że jest punktem poboru):
        if self.point_matrix[P1[0]][P1[1]].flow == 0:
            # print("Zerowy przepływ")
            return 3
        # sprawdzenie czy podana krawędź już istnieje w grafie:
        if P1 in self.solution_graph.keys():
            for v in self.solution_graph[P1]:
                if v[0] == P2:
                    return 4
        if P2 in self.solution_graph.keys():
            for v in self.solution_graph[P2]:
                if v[0] == P1:
                    return 5
        # jeśli P2 nie będzie równocześnie początkiem jakiejś krawędzi to powstanie pętla i nie będzie co zrobić z tą wodą
        # for v in self.solution_graph.values():  # v - listy będące wartościami w słowniku
        #     for p in v:  # p - poszczególne punkty w listach
        #         if p[0] == P2:
        #             if P2 not in self.solution_graph.keys() and P2 not in [p.coordinates for p in
        #                                                                    self.extraction_points]:
        #                 return 7
        if self.check_cycle(P1, P2):
            return 6
        return 0

    def add_edge_to_solution(self, P1: Point_coordinates, P2: Point_coordinates, direction: str, cost: float,
                             time: float):
        """
        Funkcja pomocnicza do add_edge
        :param time: czas montażu rury między punktami
        :param cost: koszt montażu rury między punktami
        :param direction: kierunek, w którym znajduje się drugi punkt, względem pierwszego punktu
        :param P2: drugi punkt
        :param P1: pierwszy punkt
        """
        self.solution_graph[P1].append((P2, direction, cost, time))
        self.point_matrix[P2[0]][P2[1]].previous_points.append(P1)
        if P2 not in self.points:  # dodanie punktu P2 do listy punktów w rozwiązaniu
            self.points.append(P2)
        self.costs_sum += cost
        self.times_sum += time

    def add_edge(self, P1: Point_coordinates, P2: Point_coordinates, knot_kind: Optional[List[float]]= None):
        """
        Funkcja dodająca krawędź do rozwiązania
        :param P1: pierwszy punkt
        :param P2: drugi punkt
        :param knot_kind: rodzaj węzła wychodzącego (ważne przy krzyżowaniu)
        """
        if bool(self.check_if_edge_correct(P1, P2)):  # Krawędź poprawna, gdy funkcja zwróci 0
            raise ValueError("Niepoprawna krawędź")
        # jeśli możemy dodać krawędź do rozwiązania - ustalamy jej kierunek, koszt i czas:
        else:
            P1_point = self.point_matrix[P1[0]][P1[1]]
            P2_point = self.point_matrix[P2[0]][P2[1]]
            if P2[0] > P1[0]:
                cost = P1_point.cost_down
                time = P1_point.time_down
                direction = 'down'
            elif P2[0] < P1[0]:
                cost = P1_point.cost_up
                time = P1_point.time_up
                direction = 'up'
            elif P2[1] > P1[1]:
                cost = P1_point.cost_right
                time = P1_point.time_right
                direction = 'right'
            else:
                cost = P1_point.cost_left
                time = P1_point.time_left
                direction = 'left'
            # Ustalenie, czy będziemy musieli dodać węzeł:
            is_node_out = False
            is_node_in = False
            if P1 in self.solution_graph.keys():
                if len(self.solution_graph[P1]) > 0:
                    is_node_out = True
            for v in self.solution_graph.values():  # v - listy będące wartościami w słowniku
                for p in v:  # p - poszczególne punkty w listach
                    if p[0] == P2:
                        is_node_in = True
                        break
            dx_minus: int = P1[0] - knot_dx
            dx_plus: int = P1[0] + knot_dx
            dy_minus: int = P1[1] - knot_dy
            dy_plus: int = P1[1] + knot_dy
            if is_node_in and is_node_out and dx_minus < P2[0] < dx_plus and dy_minus < P2[1] < dy_plus:
                raise ValueError("Nie można dodać węzła")
            # ustalenie wartości przepływu w punktach i dodanie krawędzi do rozwiązania:
            # jeśli P1 jest kluczem w grafie to znaczy, że jakaś krawędź już z niego wychodzi, więc punkt ten staje się
            # rozgałęzieniem
            if P1 in self.solution_graph.keys():
                if is_node_out:
                    outs = [v[0] for v in self.solution_graph[P1]]  # punkty końcowe krawędzi wychodzących
                    # z rozgałęzienia
                    outs.append(P2)
                    # Wybór rodzaju węzła:
                    if knot_kind and len(outs) == len(knot_kind):
                        chosen_kind = knot_kind
                    else:
                        chosen_kind = knot_kinds[len(outs)][0]
                    # Dodanie węzła:
                    if is_node_in:
                        is_node_added = self.add_knot_in_out(P2, P1, outs, chosen_kind)
                    else:
                        is_node_added = self.add_knot_out(P1, outs, chosen_kind)
                    if is_node_added:  # jeśli można poprawnie dodać węzeł
                        self.add_edge_to_solution(P1, P2, direction, cost, time)
                    elif not is_node_added:
                        raise ValueError("Nie można dodać węzła")
                else:
                    P2_point.flow = P1_point.flow
                    self.add_edge_to_solution(P1, P2, direction, cost, time)
            # jeśli P2 jest którąś z wartości w grafie to znaczy, że jest węzłem wchodzącym - do wartości przepływu
            # w punkcie P2 trzeba będzie dodać wartość przepływu z P1
            elif is_node_in:
                is_node_added = self.add_knot_in(P2, P1_point.flow)
                if is_node_added:
                    self.solution_graph[P1] = []
                    self.add_edge_to_solution(P1, P2, direction, cost, time)
                else:
                    raise ValueError("Nie można dodać węzła")
            # jeśli P2 ani P1 nie są węzłami to normalnie dodajemy krawędź, a wartość przepływu w P2 jest równa
            # wartości przepływu w P1
            else:
                P2_point.flow = P1_point.flow
                self.solution_graph[P1] = []
                self.add_edge_to_solution(P1, P2, direction, cost, time)
            # Obsługa punktów poboru - jeśli nie była wykonana pzy okazji dodawania węzła wychodzącego
            if not is_node_out and not is_node_in:
                for extraction_point in self.extraction_points:
                    if extraction_point.coordinates == P2:
                        if P2_point.flow < extraction_point.extraction_value:
                            extraction_point.extraction_satisfied = P2_point.flow
                            P2_point.flow = 0
                        else:
                            extraction_point.extraction_satisfied = extraction_point.extraction_value
                            P2_point.flow -= extraction_point.extraction_value
                        break

    def check_knots_distances(self, candidate: Point_coordinates) -> bool:
        """
        Funkcja sprawdzająca czy potencjalny węzeł jest w odpowiedniej odległości od pozostałych węzłów. Jeśli węzeł ma
        takie współrzędne jak inny, już istniejący, może zostać utworzony, aby umożliwić dodanie kolejnego rozgałęzienia
        :param candidate: potencjalny węzeł
        :return: czy węzeł może powstać
        """
        global knot_dx
        global knot_dy
        for knot in self.knots:
            if knot == candidate:
                return True
            dx_minus: int = knot[0] - knot_dx
            dx_plus: int = knot[0] + knot_dx
            dy_minus: int = knot[1] - knot_dy
            dy_plus: int = knot[1] + knot_dy
            if dx_minus < candidate[0] < dx_plus and dy_minus < candidate[1] < dy_plus:
                return False
        return True

    def return_solution(self) -> List[Edge]:
        """
        Funkcja zwracająca listę krawędzi, zawartych w rozwiązaniu
        :return: lista krawędzi
        """
        to_return: List[Edge] = []
        for out_point in self.solution_graph.keys():
            for in_point in self.solution_graph[out_point]:
                to_return.append((out_point, in_point[0]))
        return to_return

    def return_knots_proportions(self):
        knot_proportions = {}
        for knot in self.knots:
            x = knot[0]
            y = knot[1]
            proportions = self.point_matrix[x][y].knot_proportions()
            if proportions:
                temp = []
                for it in range(len(proportions)):
                    temp.append((proportions[it], self.solution_graph[(x, y)][it][1]))
                knot_proportions[(knot[0], knot[1])] = temp
        return knot_proportions


def objective_function(solution: Solution, cost_weight: float = 0.1, time_weight: float = 0.1,
                       penalty_severity: float = 1) -> float:
    """
    Funkcja celu
    :param cost_weight: waga kosztów montażu instalacji
    :param time_weight: waga czasów montażu instalacji
    :param penalty_severity: dotkliwość kary
    :param solution: rozwiązanie
    :return: wartość funkcji celu
    """
    value: float = solution.costs_sum * cost_weight / max_cost + solution.times_sum * time_weight / max_time + sum([
        point.extraction_value - point.extraction_satisfied for point in
        solution.extraction_points]) * penalty_severity / sum(
        [point.extraction_value for point in solution.extraction_points])
    return value


