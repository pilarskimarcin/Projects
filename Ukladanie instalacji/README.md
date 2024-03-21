# Opis
Projekt polegający na implementacji oraz próbie rozwiązania problemu ułożenia sieci wodociągowej na siatce reprezentującej pewien teren. Rozwiązanie problemu wykorzystuje algorytm symulowanego wyżarzania oraz algorytm genetyczny.
Szczegóły dotyczące uruchomienia oraz dokładnego działania projektu znajdują się w pliku Dokumentacja.pdf.

# Pliki
- algorytm_genetyczny.py - implementacja algorytmu genetycznego
- algorytm_konstrukcyjny.py - funkcje służące do generowania rowiązań początkowych
- DANE.xlsx - przykładowe dane wejściowe do programu, użycie innych danych wejściowych jest możliwe pod warunkiem zachowania dokładnej nazwy pliku
- Dokumentacja.pdf - dokumentacja projektu
- EA_tests - wyniki testów dla różnych parametrów algorytmu genetycznego
- implementacja_problemu.py - implementacja klas potrzebnych do reprezentacji rozwiązania oraz funkcji celu
- main.py - plik służący do uruchomienia programu, zawierający GUI
- SA.py - implementacja algorytmu symulowanego wyżarzania (także mutacji alg. genetycznego - jest ona tożsama z sąsiedztwem w przypadku alg. SA)
- testy.py - testowanie obu algorytmów, a także wielu pojedynczych funkcjonalności całego programu
- wczytywanie_danych.py - funkcje konieczne do wczytania danych z pliku
- wyrysowywanie_rozwiązania.py - funkcje umożliwiające wizualizację rozwiązania w GUI