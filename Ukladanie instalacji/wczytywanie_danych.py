import implementacja_problemu as ip
from typing import List
import pandas


def separate(string: str, ntype='float', separator: str = ',', empty_chars: List[str] = None):
    """
    Funkcja pomocnicza do wczytywania danych. Konwertuje ciąg znaków na listę liczb.
    :param string: Ciąg znaków do przekonwertowania.
    :param ntype: Typ liczb na jakie mają być przekonwertowane dane. Dopuszczalne typy to "float" oraz "int" zapisane jako typ str.
    :param separator: Znak oddzielający od siebie liczby w parametrze "string".
    :param empty_chars: Lista znaków, które mają być potraktowane jako znaki puste. Jeśli None używane są znaki: " ", "(", ")".
    """
    if empty_chars is None:
        empty_chars = [' ', '(', ')']
    # Rozdzielanie
    lst = []
    temp = ''
    for el in string:
        if el == separator:
            lst.append(temp)
            temp = ''
        elif el in empty_chars:
            pass
        else:
            temp += el
    if temp != '':
        lst.append(temp)
    # Konwersja typów
    for i in range(len(lst)):
        if lst[i] == 'None':
            lst[i] = None
        elif ntype == 'int':
            lst[i] = int(lst[i])
        elif ntype == 'float':
            lst[i] = float(lst[i])
        else:
            raise ValueError('Parameter ntype must be either \'int\' or \'float\'.')
    return lst


def read_from_file(filename: str):
    """
    Funkcja do wczytywania danych z pliku do struktur danych
    :param filename: ścieżka do pliku
    """
    # global source_capacity
    # global point_matrix
    # global extraction_points
    # global max_time
    # global max_cost
    # global knot_kinds
    # global knot_dx
    # global knot_dy

    koszty = pandas.read_excel(filename, 0, header=0, index_col=0).values.tolist()
    czasy = pandas.read_excel(filename, 1, header=0, index_col=0).values.tolist()
    pobor = pandas.read_excel(filename, 2, header=None, index_col=0).values.tolist()
    wezly = pandas.read_excel(filename, 3, header=None, index_col=None).values.tolist()
    ip.source_capacity = float(pandas.read_excel(filename, 4, header=None, index_col=None).values.tolist()[0][0])
    ip.knot_dx = int(pandas.read_excel(filename, 5, header=None, index_col=0).values.tolist()[0][0])
    ip.knot_dy = int(pandas.read_excel(filename, 5, header=None, index_col=0).values.tolist()[1][0])

    # Obsługa wczytywania macierzy punktów
    if len(koszty) != len(czasy) or len(koszty[0]) != len(czasy[0]):
        raise ValueError('Cost and/or time matrices are not valid.')
    ip.point_matrix = [[None for _ in range(len(koszty[0]))] for _ in range(len(koszty))]
    for i in range(len(koszty)):
        for j in range(len(koszty[0])):
            temp_k = separate(koszty[i][j])
            temp_c = separate(czasy[i][j])
            ip.point_matrix[i][j] = ip.Point((i, j), temp_c[0], temp_c[1], temp_c[2], temp_c[3], temp_k[0], temp_k[1],
                                             temp_k[2], temp_k[3])
            # Szukanie największego kosztu i czasu
            max_cost_temp = max([it for it in temp_k if it])  # Usuwa None i wyznacza max
            max_time_temp = max([it for it in temp_c if it])
            if ip.max_cost is None or ip.max_cost < max_cost_temp:
                ip.max_cost = max_cost_temp
            if ip.max_time is None or ip.max_time < max_time_temp:
                ip.max_time = max_time_temp

    # Obsługa wczytywania punktów poboru
    pobor = list(map(list, zip(*pobor)))  # Transpozycja listy list
    ip.extraction_points = [None for _ in range(len(pobor))]
    for i in range(len(pobor)):
        coord = tuple(separate(pobor[i][0], 'int'))
        ip.extraction_points[i] = ip.ExtractionPoint(coord, float(pobor[i][1]))

    # Obsługa wczytywania węzłów
    for rodzaj in wezly:
        key = int(rodzaj[0][0])
        if key not in (2, 3):
            raise ValueError('Knots can have only 2 or 3 outputs.')
        temp_lst = []
        for i in range(1, len(rodzaj)):
            temp_lst.append(separate(rodzaj[i]))
        ip.knot_kinds[key] = temp_lst

    # Obsługa wczytywania odległości między węzłami już jest zrobiona przy wczytaniu z excela
    # Obsługa wczytywania źródła już jest zrobiona przy wczytaniu z excela

    # Ustawienie punktu (0,0) w macierzy jako źródła
    ip.point_matrix[0][0].flow = ip.source_capacity
