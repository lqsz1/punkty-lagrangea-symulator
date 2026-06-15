# Ograniczony Kołowy Problem Trzech Ciał (CR3BP) - Symulator

Wizualny i interaktywny symulator układów grawitacyjnych, napisany w języku Python. Program numerycznie wyznacza położenie punktów libracyjnych (Lagrange'a L1-L5) za pomocą biblioteki SciPy i prezentuje je w czasie rzeczywistym na obracającym się układzie odniesienia.

## Funkcjonalności
* Interaktywny suwak parametru masy (od 0.001 do 0.5) aktualizujący pozycje w czasie rzeczywistym.
* Trzy wbudowane scenariusze astronomiczne: Układ Słońce-Jowisz, Układ Ziemia-Księżyc, Idealny Układ Podwójny.
* Automatyczne zapobieganie nakładaniu się etykiet i skalowanie rozmiarów ciał w zależności od zadanej masy.
* Numeryczne obliczanie punktów kolinearnych (L1, L2, L3) algorytmem `fsolve`.

## Wymagania i uruchomienie
Aby uruchomić symulację, upewnij się, że posiadasz zainstalowanego Pythona (wersja 3.x) oraz wymagane biblioteki:

```bash
pip install numpy scipy matplotlib
