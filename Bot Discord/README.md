# Opis
Celem projektu było stworzenie automatycznego bota do komunikatora Discord, ułatwiającego pewne aspekty moderacji serwera. Głównym jego zadaniem jest wyszukiwanie użytkowników, którzy nie posiadają wymaganych przez zasady danego serwera ról. Bot jest dalej rozwijany i dodawane są kolejne funkcjonalności, ułatwiające moderację lub po prostu rekreacyjne.
Funkcjonalności bota są aktywowane przez wywoływanie na jednym z kanałów danego serwera komend, na które w odpowiedni sposób reaguje bot.
Obecne funkcjonalności bota:
- wyszukiwanie użytkowników bez zdefiniowanych dla danego serwera ról
- generowanie listy poleceń wyrzucenia użytkowników (dla innego bota) znalezionych za pomocą funkcji wyszukującej
- wyświetlenie informacji o ilości czasu, jaka upłynęła od kiedy ostatnio użytkownik dołączył do serwera
- wyświetlenie obecnie zapamiętanych przez bota roli na serwerze
- dodawanie kolejnych grup roli (lub pojedynczych roli)
- wyświetlanie listy komend z instrukcją wywołań
- wyświetlenie ostatnich zmian w działaniu bota (cała lista w pliku Changelog.txt)
- zapisywanie pliku z logami dotyczącymi działania bota (do diagnostyki ewentualnych błędów)
- wysłanie jednego z wielu zapisanych gifów, na podstawie odpowiedniego tytułu
- wysyłanie predefiniowanej wiadomości co określony okres czasu

Do uruchomienia bota potrzebny jest, poza umieszczonymi tu plikami, plik .env z tokenem bota, który ze względów bezpieczeństwa nie jest udostępniony, a także pliki z danymi o serwerze, na którym działa - także niedostępne w repozytorium.

# Pliki
- cogs/ - folder z plikami zawierającymi komendy bota:
  - cog_fun.py - komendy rekreacyjne
  - cog_logging.py - komendy związane z logowaniem łączenia się bota z serwerami Discorda
  - cog_moderation.py - komendy związane z moderacją serwera
  - cog_self_checking.py - komendy związane z samym botem i jego działaniem, pomoc do komend
- Changelog.txt - plik ze zmianami w kodzie bota w poszczególnych wersjach (oznaczających większe zmiany w działaniu lub dodanie nowych funkcji)
- Wraith_bot.py - główny plik uruchamiający bota i ładujący pliki z komendami
