import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.patches as patches
from scipy.optimize import fsolve

# Funkcja obliczająca pozycje punktów kolinearnych (L1, L2, L3) na osi X
def oblicz_l1_l2_l3(mu):
    x_s, x_z = -mu, 1 - mu

    # Równanie bilansu sił: odśrodkowa - grawitacja m1 - grawitacja m2 = 0
    def rownanie(x):
        return x - (1 - mu) * (x - x_s) / abs(x - x_s) ** 3 - mu * (x - x_z) / abs(x - x_z) ** 3

    # Szukanie miejsc zerowych za pomocą fsolve
    l1 = fsolve(rownanie, x_z - (mu / 3) ** (1 / 3))[0]
    l2 = fsolve(rownanie, x_z + (mu / 3) ** (1 / 3))[0]
    l3 = fsolve(rownanie, x_s - 1)[0]
    return l1, l2, l3

# Paleta kolorów (motyw ciemnego kosmosu)
TLO = '#0b0e1a'
TLO_PANEL = '#141a2e'
SIATKA = '#243056'
TEKST = '#e6e9f0'
SLONCE = '#ffd24a'
ZIEMIA = '#4aa3ff'
L123 = '#ff5c7a'
L45 = '#36d39a'

# Tworzy ciało niebieskie z efektem poświaty (kilka nałożonych na siebie warstw)
def _stworz_cialo(ax, x, y, kolor, rozmiar_rdzenia, warstwy=4):
    halo = []
    for i in range(warstwy):
        frac = (warstwy - i) / warstwy
        s = rozmiar_rdzenia * (1 + 7 * frac ** 2)
        a = 0.13 * frac
        halo.append(ax.scatter([x], [y], s=s, color=kolor, alpha=a, edgecolors='none', zorder=4))
    rdzen = ax.scatter([x], [y], s=rozmiar_rdzenia, color=kolor, edgecolors='white', linewidths=0.7, zorder=6)
    return {'halo': halo, 'rdzen': rdzen, 'warstwy': warstwy}

# Aktualizuje fizyczną pozycję i rozmiar ciała podczas przesuwania suwaka
def _aktualizuj_cialo_pozycje(cialo, x, y, rozmiar_rdzenia):
    w = cialo['warstwy']
    for i, h in enumerate(cialo['halo']):
        frac = (w - i) / w
        h.set_offsets(np.c_[[x], [y]])
        h.set_sizes([rozmiar_rdzenia * (1 + 7 * frac ** 2)])
    cialo['rdzen'].set_offsets(np.c_[[x], [y]])
    cialo['rdzen'].set_sizes([rozmiar_rdzenia])

# Zmienia kolor ciała (używane w przyciskach ze scenariuszami)
def _aktualizuj_cialo_kolor(cialo, kolor):
    for h in cialo['halo']:
        h.set_facecolor(kolor)
    cialo['rdzen'].set_facecolor(kolor)

# Przelicza względną masę na piksele wyświetlane na ekranie
def _rozmiar_ciala(masa_wzgledna):
    return 40 + 1200 * masa_wzgledna

# Oblicza, jak nisko pod planetą dać tekst, żeby poświata go nie zasłaniała
def _oblicz_offset_tekstu(rozmiar_rdzenia):
    return 0.04 + 0.0055 * np.sqrt(rozmiar_rdzenia)

# Główna funkcja programu
def uruchom_wizualizacje():
    # Ustawienia czcionki i kolorów okna
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': TEKST, 'axes.labelcolor': TEKST})
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.canvas.manager.set_window_title("Punkty Lagrange'a — CR3BP")
    fig.patch.set_facecolor(TLO)
    ax.set_facecolor(TLO)
    
    # Marginesy, żeby zmieścić UI na dole
    plt.subplots_adjust(bottom=0.22, left=0.06, right=0.96, top=0.92)

    mu_start = 0.05

    # Generowanie tła z losowo rozsypanymi, półprzezroczystymi gwiazdami
    rng = np.random.default_rng(42)
    n = 450
    gx = rng.uniform(-1.6, 1.6, n)
    gy = rng.uniform(-1.15, 1.15, n)
    gs = rng.uniform(0.3, 6.0, n)
    gkolor = np.ones((n, 4))
    gkolor[:, 3] = rng.uniform(0.15, 0.9, n)
    ax.scatter(gx, gy, s=gs, c=gkolor, linewidths=0, zorder=0)

    # Obliczenia pozycji początkowych
    xs, xz = -mu_start, 1 - mu_start
    l1, l2, l3 = oblicz_l1_l2_l3(mu_start)
    l4x, l4y = 0.5 - mu_start, np.sqrt(3) / 2
    l5x, l5y = 0.5 - mu_start, -np.sqrt(3) / 2

    # Rysowanie przerywanych orbit dla obu ciał
    orbita_m2 = patches.Circle((0, 0), 1 - mu_start, fill=False, lw=1.2, ls=(0, (6, 6)), ec=ZIEMIA, alpha=0.35, zorder=1)
    orbita_m1 = patches.Circle((0, 0), mu_start, fill=False, lw=1.2, ls=(0, (6, 6)), ec=SLONCE, alpha=0.45, zorder=1)
    ax.add_patch(orbita_m2)
    ax.add_patch(orbita_m1)

    # Rysowanie ramion trójkątów dla L4 i L5
    linia_l4, = ax.plot([xs, l4x, xz, xs], [0, l4y, 0, 0], color=L45, lw=1.1, alpha=0.4, zorder=2)
    linia_l5, = ax.plot([xs, l5x, xz, xs], [0, l5y, 0, 0], color=L45, lw=1.1, alpha=0.4, zorder=2)

    # Inicjalizacja głównych mas (planet)
    rozm_m1_start = _rozmiar_ciala(1 - mu_start)
    rozm_m2_start = _rozmiar_ciala(mu_start)
    cialo_m1 = _stworz_cialo(ax, xs, 0, SLONCE, rozm_m1_start)
    cialo_m2 = _stworz_cialo(ax, xz, 0, ZIEMIA, rozm_m2_start)

    # Rysowanie punktów Lagrange'a (znacznik 'X' i mała poświata)
    halo_123 = ax.scatter([l1, l2, l3], [0, 0, 0], s=420, color=L123, alpha=0.18, edgecolors='none', zorder=4)
    pkt_123 = ax.scatter([l1, l2, l3], [0, 0, 0], marker='X', s=130, color=L123, edgecolors='white', linewidths=0.6, zorder=7, label='L1, L2, L3')
    halo_45 = ax.scatter([l4x, l5x], [l4y, l5y], s=420, color=L45, alpha=0.18, edgecolors='none', zorder=4)
    pkt_45 = ax.scatter([l4x, l5x], [l4y, l5y], marker='X', s=130, color=L45, edgecolors='white', linewidths=0.6, zorder=7, label='L4, L5')

    # Podpisy L1-L5
    etykiety = ['L1', 'L2', 'L3', 'L4', 'L5']
    napisy = []
    wsp_x = [l1, l2, l3, l4x, l5x]
    wsp_y = [0, 0, 0, l4y, l5y]
    for i in range(5):
        t = ax.text(wsp_x[i], wsp_y[i] + 0.07, etykiety[i], fontsize=11, fontweight='bold', ha='center', color=TEKST, zorder=8)
        napisy.append(t)

    # Podpisy ciał niebieskich (np. "Słońce", "Jowisz") z dynamicznym odstępem
    offset_m1_start = _oblicz_offset_tekstu(rozm_m1_start)
    offset_m2_start = _oblicz_offset_tekstu(rozm_m2_start)
    napis_m1 = ax.text(xs, -offset_m1_start, 'Masa 1', fontsize=10, ha='center', color=SLONCE, zorder=8)
    napis_m2 = ax.text(xz, -offset_m2_start, 'Masa 2', fontsize=10, ha='center', color=ZIEMIA, zorder=8)

    # Okienko ze statystykami w prawym górnym rogu
    info = ax.text(0.985, 0.97, '', transform=ax.transAxes, ha='right', va='top', fontsize=10, family='monospace', color=TEKST, bbox=dict(boxstyle='round,pad=0.6', fc=TLO_PANEL, ec=SIATKA, alpha=0.9))

    # Formatowanie wartości tekstowych do okienka
    def _tekst_info(mu, a, b, c):
        return (f"μ = {mu:6.3f}\nL1 = {a:6.3f}\nL2 = {b:6.3f}\nL3 = {c:6.3f}")

    info.set_text(_tekst_info(mu_start, l1, l2, l3))

    # Dekoracja osi współrzędnych i siatki
    ax.axhline(0, color=SIATKA, lw=0.8, ls='--', zorder=1)
    ax.axvline(0, color=SIATKA, lw=0.8, ls='--', zorder=1)
    ax.grid(True, color=SIATKA, ls=':', alpha=0.4)
    ax.set_axisbelow(True)
    
    # Zapewnienie, że okręgi nie będą spłaszczone w elipsy
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.15, 1.15)
    for s in ax.spines.values(): s.set_color(SIATKA)
    ax.tick_params(colors='#8893b5', labelsize=9)
    ax.set_title("Punkty Lagrange'a i orbity  •  problem trzech ciał (CR3BP)", fontsize=15, fontweight='bold', color=TEKST, pad=16)

    # Stylizacja legendy
    leg = ax.legend(loc='upper left', framealpha=0.9, fontsize=10)
    leg.get_frame().set_facecolor(TLO_PANEL)
    leg.get_frame().set_edgecolor(SIATKA)
    for txt in leg.get_texts(): txt.set_color(TEKST)

    # --- ELEMENTY INTERFEJSU UI ---
    
    # Pasek suwaka
    os_suwaka = plt.axes([0.25, 0.13, 0.5, 0.03], facecolor=TLO_PANEL)
    suwak_mu = Slider(os_suwaka, r'Parametr masy ($\mu$)', 0.001, 0.5, valinit=mu_start, valfmt='%.3f', color=L45)
    suwak_mu.label.set_color(TEKST)
    suwak_mu.label.set_fontsize(11)
    suwak_mu.valtext.set_color(TEKST)

    # Trzy przyciski scenariuszy (presetów)
    ax_btn1 = plt.axes([0.20, 0.05, 0.18, 0.04])
    ax_btn2 = plt.axes([0.41, 0.05, 0.18, 0.04])
    ax_btn3 = plt.axes([0.62, 0.05, 0.18, 0.04])

    btn1 = Button(ax_btn1, 'Słońce-Jowisz', color=TLO_PANEL, hovercolor=SIATKA)
    btn2 = Button(ax_btn2, 'Ziemia-Księżyc', color=TLO_PANEL, hovercolor=SIATKA)
    btn3 = Button(ax_btn3, 'Układ Podwójny', color=TLO_PANEL, hovercolor=SIATKA)

    for b in [btn1, btn2, btn3]:
        b.label.set_color(TEKST)
        b.label.set_fontsize(10)

    # Uniwersalna funkcja nakładająca wybrane parametry po kliknięciu
    def zastosuj_preset(mu, kol_1, kol_2, nazwa_1, nazwa_2):
        suwak_mu.set_val(mu) # To polecenie automatycznie wywoła podaną niżej funkcję `aktualizacja`
        _aktualizuj_cialo_kolor(cialo_m1, kol_1)
        _aktualizuj_cialo_kolor(cialo_m2, kol_2)
        orbita_m1.set_edgecolor(kol_1)
        orbita_m2.set_edgecolor(kol_2)
        napis_m1.set_text(nazwa_1)
        napis_m1.set_color(kol_1)
        napis_m2.set_text(nazwa_2)
        napis_m2.set_color(kol_2)
        fig.canvas.draw_idle()

    # Zdarzenia kliknięcia konkretnych przycisków
    def set_jowisz(event):
        zastosuj_preset(0.001, '#ffd24a', '#d4a373', 'Słońce', 'Jowisz')

    def set_ksiezyc(event):
        zastosuj_preset(0.012, '#4aa3ff', '#b0bec5', 'Ziemia', 'Księżyc')

    def set_podwojny(event):
        zastosuj_preset(0.500, '#ffd24a', '#4aa3ff', 'Ciało A', 'Ciało B')

    btn1.on_clicked(set_jowisz)
    btn2.on_clicked(set_ksiezyc)
    btn3.on_clicked(set_podwojny)

    # Główna pętla logiczna - odpala się przy każdym drgnięciu suwaka
    def aktualizacja(_):
        mu = suwak_mu.val
        
        # 1. Przeliczamy nowe pozycje z matematyki
        ns, nz = -mu, 1 - mu
        a, b, c = oblicz_l1_l2_l3(mu)
        n4x, n4y = 0.5 - mu, np.sqrt(3) / 2
        n5x, n5y = 0.5 - mu, -np.sqrt(3) / 2

        # 2. Skalujemy ciała wg nowej masy
        rozm_m1_nowy = _rozmiar_ciala(1 - mu)
        rozm_m2_nowy = _rozmiar_ciala(mu)
        _aktualizuj_cialo_pozycje(cialo_m1, ns, 0, rozm_m1_nowy)
        _aktualizuj_cialo_pozycje(cialo_m2, nz, 0, rozm_m2_nowy)

        # 3. Przesuwamy na wykresie punkty L1-L5
        halo_123.set_offsets(np.c_[[a, b, c], [0, 0, 0]])
        pkt_123.set_offsets(np.c_[[a, b, c], [0, 0, 0]])
        halo_45.set_offsets(np.c_[[n4x, n5x], [n4y, n5y]])
        pkt_45.set_offsets(np.c_[[n4x, n5x], [n4y, n5y]])

        # 4. Zwężamy/rozszerzamy orbity ciał
        orbita_m2.set_radius(1 - mu)
        orbita_m1.set_radius(mu)

        # 5. Aktualizujemy wierzchołki trójkątów
        linia_l4.set_data([ns, n4x, nz, ns], [0, n4y, 0, 0])
        linia_l5.set_data([ns, n5x, nz, ns], [0, n5y, 0, 0])

        # 6. Aktualizujemy położenie etykiet tekstowych
        wx = [a, b, c, n4x, n5x]
        wy = [0, 0, 0, n4y, n5y]
        for i in range(5):
            napisy[i].set_position((wx[i], wy[i] + 0.07))

        offset_m1_nowy = _oblicz_offset_tekstu(rozm_m1_nowy)
        offset_m2_nowy = _oblicz_offset_tekstu(rozm_m2_nowy)
        napis_m1.set_position((ns, -offset_m1_nowy))
        napis_m2.set_position((nz, -offset_m2_nowy))

        # Odświeżenie danych w panelu numerycznym
        info.set_text(_tekst_info(mu, a, b, c))
        fig.canvas.draw_idle()

    # Zarejestrowanie funkcji do suwaka
    suwak_mu.on_changed(aktualizacja)

    # Utrzymanie referencji w pamięci, aby UI nie zniknęło
    ax._suwak = suwak_mu
    ax._buttons = [btn1, btn2, btn3]

    plt.show()

# Zabezpieczenie wymagane przy imporcie modułu
if __name__ == '__main__':
    uruchom_wizualizacje()
