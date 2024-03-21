import csv
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from sqlalchemy import create_engine
import pandas as pd
import datetime
from sqlalchemy import Table, MetaData, select
from sqlalchemy_utils import Timestamp


def pobierz_dane_z_bazy(connection_string, zapytanie):
    engine = create_engine(connection_string)
    with engine.connect() as connection:
        result = connection.execute(zapytanie)
        dane = pd.DataFrame(result.fetchall(), columns=result.keys())
    return dane


def generuj_strone_tytulowa(pdf_pages):
    fig = plt.figure(figsize=(11, 8.5))
    plt.axis('off')

    tytul = "Raport danych"
    data = datetime.date.today()

    plt.text(0.5, 0.7, tytul, fontsize=24, ha='center')
    plt.text(0.5, 0.6, data, fontsize=18, ha='center')

    pdf_pages.savefig(fig, bbox_inches='tight')


# def odczytaj_dane_z_csv(dane_csv):
#     dane = []
#     with open(dane_csv, 'r', encoding='utf-8') as plik_csv:
#         czytnik_csv = csv.DictReader(plik_csv)
#         for wiersz in czytnik_csv:
#             dane.append(wiersz)
#     return dane

def generuj_raport(dane, pdf_pages, nazwa_tabeli):
    print("Generowanie raportu")
    ilosc_jednostek = {}
    for _, wiersz in dane.iterrows():
        asortyment = wiersz['nazwa_asortymentu']
        ilosc = float(wiersz['ilosc_jednostek'])
        if asortyment in ilosc_jednostek:
            ilosc_jednostek[asortyment] += ilosc
        else:
            ilosc_jednostek[asortyment] = ilosc

    plt.style.use('ggplot')

    fig = plt.figure(figsize=(10, 7))

    bars = plt.bar(range(len(ilosc_jednostek)), list(ilosc_jednostek.values()), tick_label=list(ilosc_jednostek.keys()))
    plt.xlabel('Asortyment')
    plt.ylabel('Ilość jednostek')
    plt.title(f'Analiza całkowitej ilości jednostek - {nazwa_tabeli}')
    plt.xticks(rotation=45, ha="right")
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.05, round(yval, 2), ha='center', va='bottom')
    plt.tight_layout()
    pdf_pages.savefig(fig, bbox_inches="tight")

    wartosc_zakupu = {}
    for _, wiersz in dane.iterrows():
        asortyment = wiersz['nazwa_asortymentu']
        ilosc = float(wiersz['ilosc_jednostek'])
        cena = float(wiersz['srednia_cena_zakupu'])
        wartosc = ilosc * cena
        if asortyment in wartosc_zakupu:
            wartosc_zakupu[asortyment] += wartosc
        else:
            wartosc_zakupu[asortyment] = wartosc

    fig = plt.figure(figsize=(10, 5))

    wedges, texts, autotexts = plt.pie(list(wartosc_zakupu.values()), autopct='%1.1f%%')
    plt.title(f'Analiza wartości zakupu - {nazwa_tabeli}')
    plt.axis('equal')

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="->", color='red'), bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        plt.annotate(list(wartosc_zakupu.keys())[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                     horizontalalignment=horizontalalignment, **kw)
    pdf_pages.savefig(fig, bbox_inches="tight")

    wartosc_dzien = {}
    for _, wiersz in dane.iterrows():

        date_string: Timestamp = wiersz['data_wprowadzenia']
        datetime_object = datetime.datetime.strptime(date_string.__str__(), "%Y-%m-%d %H:%M:%S")
        dzien = str(datetime_object.date())

        ilosc_1 = float(wiersz['ilosc_jednostek'])
        cena_1 = float(wiersz['srednia_cena_zakupu'])
        wartosc_1 = ilosc_1 * cena_1
        if dzien in wartosc_dzien:
            wartosc_dzien[dzien] += wartosc_1
        else:
            wartosc_dzien[dzien] = wartosc_1

    last_keys = list(wartosc_dzien.keys())[-30:]
    last_values = [wartosc_dzien[key] for key in last_keys]

    # print(wartosc_dzien)

    fig = plt.figure(figsize=(12, 5))
    plt.plot(last_keys, last_values, marker='o')
    plt.xlabel('Ostatnie 30 dni')
    plt.ylabel('Wartość')
    plt.title(f'Wartość zakupu w ostatnich 30 dniach - {nazwa_tabeli}')
    plt.xticks(rotation=90)

    pdf_pages.savefig(fig, bbox_inches="tight")


# dane_csv = 'ZBM_Robocizna_204.csv'
# dane = odczytaj_dane_z_csv(dane_csv)

# connection_string = "mysql://marcinp1:pbJ16eaz1PFRzKzS@mysql.agh.edu.pl:3306/marcinp1"
# dane = create_engine(connection_string)

# zapytanie = "SELECT * FROM ZBM_Robocizna_204"

# dane = pobierz_dane_z_bazy(connection_string, zapytanie)

connection_string = "mysql://marcinp1:pbJ16eaz1PFRzKzS@mysql.agh.edu.pl:3306/marcinp1"
engine = create_engine(connection_string)
metadata = MetaData()

zbm_robocizna_204 = Table('ZBM_Robocizna_204', metadata, autoload_with=engine)
zo_robocizna_104 = Table("ZO_Robocizna_104", metadata, autoload_with=engine)
# zapytanie = select(zbm_robocizna_204)
# dane = pobierz_dane_z_bazy(connection_string, zapytanie)

with PdfPages(f'{os.path.dirname(os.path.abspath(sys.argv[0]))}/raport-{datetime.date.today().strftime("%Y-%m-%d")}.pdf') as pdf_pages:
    generuj_strone_tytulowa(pdf_pages)
    for tabela in [zbm_robocizna_204, zo_robocizna_104]:
        zapytanie = select(tabela)
        dane = pobierz_dane_z_bazy(connection_string, zapytanie)
        generuj_raport(dane, pdf_pages, tabela.name)
print("Raport wygenerowany")
input()
