from datetime import datetime
import random
from typing import Dict, List, Tuple

import pandas as pd
import sqlalchemy_utils as sql_u
from sqlalchemy import CheckConstraint, Column, create_engine, Double, DateTime, Integer, select, \
    Sequence, String, Table
from sqlalchemy.orm import declarative_base


def generate_data(df: pd.DataFrame, names_hours_dict: Dict[str, Tuple[float, float, int]]) -> pd.DataFrame:
    for key, value in names_hours_dict.items():
        units: float = random.uniform(value[0], value[1])
        units = round(units * 2) / 2.0
        df.loc[len(df)] = [datetime.today(), key, units, "h", value[2], units * value[2]]
    return df


input("Enter, by rozpocząć")
names_hours_zo: Dict[str, Tuple[float, float, int]] = {
    "FORMIERNIA ROBOCZOGODZINA": (26.6, 40, 190), "MODELARNIA-ROBOCIZNA": (2.8, 3.5, 195),
    "OCZYSZCZ.I WYKAŃCZ.-ROBOCZ.": (23.0, 25.0, 175), "TOPIALNIA PIEC INDUKCYJNY": (14.0, 16.5, 170),
    "WYBIJANIE-ROBOCZOGODZINA": (9.5, 10.5, 135)}
names_hours_zbm: Dict[str, Tuple[float, float, int]] = {
    "CNC": (11.5, 13.0, 150), "FREZARKA BRAMOWA TBI": (13.5, 17.5, 370), "KONSTRUKCJE": (14.5, 19.5, 140),
    "MALOWANIE I ŚRUTOWANIE": (1.2, 1.5, 140), "MONTAŻ": (10.0, 13.5, 140), "OBRÓBKA LEKKA": (10.2, 11.5, 150),
    "PRZYGOTOWANIE": (6.5, 7.1, 140), "SKJ": (2.6, 10, 150), "SPAWANIE": (23.3, 32.5, 150),
    "TOKARKI, WYTACZARKI, FREZARKI": (36.6, 46.6, 150), "TRASOWANIE": (4.8, 6.0, 140)
}

data104: pd.DataFrame = pd.DataFrame(columns=["data_wprowadzenia", "nazwa_asortymentu", "ilosc_jednostek", "jednostki",
                                              "srednia_cena_zakupu", "wartosc_zakupu"])
data204: pd.DataFrame = pd.DataFrame(columns=["data_wprowadzenia", "nazwa_asortymentu", "ilosc_jednostek", "jednostki",
                                              "srednia_cena_zakupu", "wartosc_zakupu"])
data104 = generate_data(data104, names_hours_zo)
data204 = generate_data(data204, names_hours_zbm)

db_string = "mysql://marcinp1:pbJ16eaz1PFRzKzS@mysql.agh.edu.pl:3306/marcinp1"
engine = create_engine(db_string)
Base = declarative_base()


class Tabela(object):
    __tablename__ = None
    __table_args__ = (
        CheckConstraint('length(nazwa_asortymentu) > 0'),
        CheckConstraint('ilosc_jednostek > 0'),
        CheckConstraint('length(jednostki) > 0')
    )
    id = None
    data_wprowadzenia = Column(DateTime, nullable=False)
    nazwa_asortymentu = Column(String(100), nullable=False)
    ilosc_jednostek = Column(Double, nullable=False)
    jednostki = Column(String(10), nullable=False)
    srednia_cena_zakupu = Column(Double, nullable=False)
    wartosc_zakupu = Column(Double, nullable=False)


class ZO(Tabela, Base):
    __tablename__ = "ZO_Robocizna_104"
    id = Column(Integer, Sequence("seq_zo_id"), primary_key=True, autoincrement=True)


class ZBM(Tabela, Base):
    __tablename__ = "ZBM_Robocizna_204"
    id = Column(Integer, Sequence("seq_zbm_id"), primary_key=True, autoincrement=True)


if not sql_u.database_exists(engine.url):
    sql_u.create_database(engine.url)
db_con = engine.connect()
metadata_db = declarative_base().metadata
metadata_db.reflect(engine)
if metadata_db.tables.keys() != Base.metadata.tables.keys():
    Base.metadata.create_all(engine)
    print("Created")
    metadata_db = Base.metadata
zo_tab = Table("ZO_Robocizna_104", metadata_db, autoload=True, autoload_with=engine)
zbm_tab = Table("ZBM_Robocizna_204", metadata_db, autoload=True, autoload_with=engine)

# TEST
# smt = select(zo_tab.c).select_from(zo_tab)
# results = db_con.execute(smt)
# df = pd.DataFrame(results.fetchall())
# if not df.empty:
#     df.columns = results.keys()
# print(df)
# db_con.close()

input("\nEnter, by kontynuować...")
dane: List[Tuple[pd.DataFrame, Table]] = [(data104, zo_tab), (data204, zbm_tab)]
for i in range(len(dane)):
    try:
        last_id = pd.DataFrame(db_con.execute(
            select(dane[i][1].c.id).select_from(dane[i][1]).order_by(dane[i][1].c.id.desc()).limit(1)
        ).fetchall())
        if not last_id.empty:
            last_id = last_id.iloc[0, 0]
        else:
            last_id = 0
        dane[i][0].insert(0, "id", range(last_id + 1, last_id + 1 + dane[i][0].shape[0]))
        print(f"Wysyłanie danych - {dane[i][1].name}")
        print(dane[i][0])
        print("\nInsert\n")
        for j, row in dane[i][0].iterrows():
            insert_smt = dane[i][1].insert().values(row)
            print(insert_smt)
            db_con.execute(insert_smt)
    except Exception as e:
        with open("ERROR.log", "w") as f:
            f.write(e.__str__())
        input()
        exit()

db_con.commit()
db_con.close()

print("Skończone")
input("Enter, by zakończyć...")
