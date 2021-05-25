# Raport covidowy dla Allegro SUMMER E-XPERIENCE
## Rekrutacja: Intern - Business Application Administrator

Table of Contents

    * Przygotowanie danych
        * Lista wszystkich państw
        * Lista państw z danymi
        * Lista państw bez danych
        * Tabela danych dla wskazanych państw

    * TOP 10 państw z największą liczbą wyzdrowień ...
    * TOP 10 państw z największą liczbą potwierdzonych nowych przypadków ...
    * TOP 10 państw z największą liczbą przypadków śmiertelnych ...
    * Statystyki ... dla Polski za ostatni miesiąc
    * Miesięczny przyrost wyzdrowień w ostatnim miesiącu

* API: https://api.covid19api.com/
* Dokumentacja: https://documenter.getpostman.com/view/10808728/SzS8rjbc#intro

#### PROBLEM 1: Pozyskanie danych z API pozwalających na odpowiedź na zadane pytania.
#### ROZWIĄZANIE: Wydobycie listy krajów przez konkretne zapytanie. Zautomatyzowanie jednego z zapytań do pozyskania wszystkich potrzebnych danych
#### USPRAWNIENIE: Sprawniejsze zapoznanie się z dokumentacją API, szybsze zidentyfikowanie problemu wymagającego automatyzacji.

#### PROBLEM 2: Powiadomienie o łańcuchowym przypisywaniu zmiennych
#### ROZWIĄZANIE: Wyciszenie powiadomień: pd.set_option('mode.chained_assignment', None)
#### USPRAWNIENIE: Dla poprawienia czystości kodu zastosowałbym metodę: .copy(), (.deepcopy() - dla list)

#### PROBLEM 3: API nie odpowiada na wszystkie requesty w prawidłowy sposób. Informacja o przekroczeniu limitu dla darmowego użytkownika.
#### ROZWIĄZANIE: Zmniejszenie częstotliwości zapytań dzieki modułowi time i metodzie sleep.
#### USPRAWNIENIE: ? 

#### PROBLEM 4: Zbyt długi czas uruchomienia kodu przy ręcznym debuggowaniu
#### ROZWIĄZANIE: Obejście pętli polegającej na module requests i odpowiedziach API, przez zapis i wczytanie danych bezprośrednio do i z pliku csv
#### USPRAWNIENIE: Podzielenie kodu na moduły by zwiekszyć niezależność między częściami kodu. 

#### PROBLEM 5: API zwraca błąd o zbyt dlugim przedziale czasowym dla zapytania o USA.
#### ROZWIĄZANIE: Stworzenie dwóch list służących za jednodniowy przedział dla zapytania kierowanego do API. Wykorzystanie równoległej iteracji.
#### USPRAWNIENIE: ?

#### PROBLEM 6: API nie zwraca danych dla pewnych państw. Prawdopodobnie brak danych dla tych krajów.
#### ROZWIĄZANIE: Brak.
#### USPRAWNIENIE: ?

#### PROBLEM 7: Wartości w kolumnach są wartościami względnymi. Każdy następny dzień jest sumą wartości przyrostu i wartości dnia poprzedniego.
#### ROZWIĄZANIE: Uzyskanie bezwzględnej liczby wzrostu argumentu w danym miesiącu przez implementację poniższej logiki.
#### USPRAWNIENIE: ?

#### PROBLEM 8: Wartość odstająca w jednym z rekordów
#### ROZWIĄZANIE: Ręczne przeliczenie na podstawie innych kolumn
#### USPRAWNIENIE: W przypadku innego typu outlier'a można zastosować inne sposoby wyznaczenia wartości

#### PROBLEM 9: Wyeksportowanie jupyternotebooka do pdf
#### ROZWIĄZANIE: Użycie LaTeX'a
#### USPRAWNIENIE: Bardziej czysty export do pdf (bez kodu, pustych stron, tabel podzielonych na dwie stony)

# USPRAWNIENIA OGÓLNE:
    # Obudowanie kodu w funkcje
    # Rozdzielenie funkcji na moduły rozwiązujące pomniejsze problemy
    # Zastosowanie modułu 'logging' do śledzenia działania kodu
    # Zastosowanie modułu 'pdb' do debugowania kodu 
    # Zastosowanie modułu 'unittest' do jednostkowego testowania kodu
    # Zaimportowanie modułów i dokończenie raportu w Jupyter Lab'ie
    # Zbudowanie responsywnego spisu treści
    # Komentarze i wnioski do każdego wykresu