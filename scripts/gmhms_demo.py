#!/usr/bin/env python3
"""
GMHMS Demo — Guasti Multi-Harmonic Modular Spectrum
====================================================
Script de démonstration du cadre GMHMS.
Calcule les spectres multi-harmoniques de Guasti et visualise les résultats.

Auteur : Alexandre Guasti (Lyon, France)
Licence : MIT
Date : 18 février 2026

Usage :
    pip install numpy matplotlib
    python gmhms_demo.py
"""

import numpy as np
import matplotlib.pyplot as plt
from math import gcd

# =============================================================================
# 1. FONCTIONS DE BASE — Diviseurs et angles Guasti
# =============================================================================

def diviseurs(n):
    """Retourne la liste des diviseurs de n."""
    divs = []
    for d in range(1, int(n**0.5) + 1):
        if n % d == 0:
            divs.append(d)
            if d != n // d:
                divs.append(n // d)
    return sorted(divs)


def angle_guasti(d, n):
    """
    Angle Guasti : θ(d,n) = arctan(n / d²)
    Encode la position géométrique du diviseur d dans la Grille de Guasti.
    """
    return np.arctan2(n / d, d)  # equivalent à arctan((n/d) / d) = arctan(n/d²)


def tau(n):
    """Nombre de diviseurs de n (fonction τ)."""
    return len(diviseurs(n))


# =============================================================================
# 2. MODES HARMONIQUES GUASTI — G_m(n)
# =============================================================================

def G_m(n, m):
    """
    Mode harmonique Guasti d'ordre m pour l'entier n.

    G_m(n) = (1 / √τ(n)) * Σ_{d|n} e^{i·m·θ(d,n)}

    Chaque entier est un "résonateur" dont les diviseurs sont les harmoniques.
    Pour un premier p : seulement 2 diviseurs → signature minimale.
    Pour un composite : nuage riche d'angles → interférences complexes.
    """
    divs = diviseurs(n)
    t = len(divs)
    if t == 0:
        return 0.0
    somme = sum(np.exp(1j * m * angle_guasti(d, n)) for d in divs)
    return somme / np.sqrt(t)


# =============================================================================
# 3. POLYNÔME DE DIRICHLET — P_m(t)
# =============================================================================

def spectre_dirichlet(N, m, t_values):
    """
    Calcule le polynôme de Dirichlet Guasti :
    P_m(t) = Σ_{n=1}^{N} G_m(n) · n^{-it}

    C'est l'objet spectral qui parle le langage de Guth-Maynard.
    """
    P = np.zeros(len(t_values), dtype=complex)
    for n in range(1, N + 1):
        coeff = G_m(n, m)
        for i, t in enumerate(t_values):
            P[i] += coeff * n ** (-1j * t)
    return P


# =============================================================================
# 4. ANALYSE MODULAIRE — S_{m,k}(r;N)
# =============================================================================

def analyse_modulaire(N, m, k):
    """
    Réponse spectrale moyenne par résidu modulo k.
    S_{m,k}(r;N) = moyenne de G_m(n) sur les n ≡ r mod k.
    """
    resultats = {}
    for r in range(k):
        valeurs = []
        for n in range(1, N + 1):
            if n % k == r:
                valeurs.append(G_m(n, m))
        if valeurs:
            moyenne = np.mean(np.abs(valeurs))
            resultats[r] = {
                "amplitude_moyenne": moyenne,
                "nb_termes": len(valeurs),
                "valeurs": valeurs
            }
    return resultats


# =============================================================================
# 5. FONCTIONS CLASSIQUES — Pour calibration
# =============================================================================

def mobius(n):
    """Fonction de Möbius μ(n)."""
    if n == 1:
        return 1
    facteurs = []
    temp = n
    for p in range(2, int(temp**0.5) + 1):
        if temp % p == 0:
            count = 0
            while temp % p == 0:
                count += 1
                temp //= p
            if count > 1:
                return 0  # n a un facteur carré
            facteurs.append(p)
    if temp > 1:
        facteurs.append(temp)
    return (-1) ** len(facteurs)


def est_premier(n):
    """Test de primalité simple."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# =============================================================================
# 6. VISUALISATION PRINCIPALE
# =============================================================================

def demo_spectres(N=200, nb_frequences=500):
    """
    Démonstration principale : calcule et affiche les spectres
    pour les modes m=0, 1, 2, 4, 8.
    """
    print(f"=" * 60)
    print(f"  GMHMS Demo — N={N}, {nb_frequences} fréquences")
    print(f"=" * 60)

    t_values = np.linspace(0.1, 40, nb_frequences)
    modes = [0, 1, 2, 4, 8]
    couleurs = ["#2E5090", "#3A6BA5", "#E74C3C", "#27AE60", "#8E44AD"]
    labels = ["m=0 (masse brute)", "m=1 (forme globale)",
              "m=2 (ANNULATION ?)", "m=4 (irrégularités)", "m=8 (symétrie 45°)"]

    fig, axes = plt.subplots(len(modes), 1, figsize=(12, 14), sharex=True)
    fig.suptitle(f"Spectre Guasti Multi-Harmonique — GMHMS (N={N})",
                 fontsize=16, fontweight="bold", color="#2E5090")

    resultats = {}

    for idx, m in enumerate(modes):
        print(f"\n  Calcul du mode m={m}...", end=" ", flush=True)
        P = spectre_dirichlet(N, m, t_values)
        amplitude = np.abs(P)
        max_amp = np.max(amplitude)
        moyenne = np.mean(amplitude)

        resultats[m] = {
            "max": max_amp,
            "moyenne": moyenne,
            "ratio": max_amp / np.sqrt(N) if N > 0 else 0
        }

        print(f"Max |P(t)| = {max_amp:.1f}, Moyenne = {moyenne:.1f}")

        axes[idx].plot(t_values, amplitude, color=couleurs[idx], linewidth=1.2)
        axes[idx].set_title(f"{labels[idx]} | Max |P| = {max_amp:.1f}",
                           fontsize=11, fontweight="bold")
        axes[idx].set_ylabel("|P(t)|")
        axes[idx].grid(True, alpha=0.3)

    axes[-1].set_xlabel("t (fréquence spectrale)", fontsize=12)
    plt.tight_layout()
    plt.savefig("gmhms_spectre_demo.png", dpi=150, bbox_inches="tight")
    print(f"\n  → Figure sauvegardée : gmhms_spectre_demo.png")

    # Résumé
    print(f"\n{'=' * 60}")
    print(f"  RÉSUMÉ DES RÉSULTATS")
    print(f"{'=' * 60}")
    print(f"  {'Mode':<10} {'Max |P|':<12} {'Moyenne':<12} {'Max/√N':<10}")
    print(f"  {'-' * 44}")
    for m in modes:
        r = resultats[m]
        flag = " ★ ANNULATION" if r["max"] < 1.0 else ""
        print(f"  m={m:<7} {r['max']:<12.1f} {r['moyenne']:<12.1f} {r['ratio']:<10.2f}{flag}")

    print(f"\n  √N = {np.sqrt(N):.1f}")
    print(f"{'=' * 60}")

    return resultats


def demo_modulaire(N=200, m=2, k=6):
    """
    Démonstration de l'analyse modulaire pour un mode et un modulus donnés.
    """
    print(f"\n{'=' * 60}")
    print(f"  ANALYSE MODULAIRE — m={m}, k={k}, N={N}")
    print(f"{'=' * 60}")

    res = analyse_modulaire(N, m, k)

    print(f"\n  {'Résidu r':<12} {'Amplitude moy.':<18} {'Nb termes':<12} {'Coprime à k?':<14}")
    print(f"  {'-' * 56}")
    for r in sorted(res.keys()):
        coprime = "OUI" if gcd(r, k) == 1 and r > 0 else "non"
        premier_friendly = " ← premiers" if coprime == "OUI" else ""
        print(f"  r={r:<9} {res[r]['amplitude_moyenne']:<18.4f} {res[r]['nb_termes']:<12} {coprime}{premier_friendly}")

    # Comparaison coprimes vs non-coprimes
    amp_coprimes = [res[r]["amplitude_moyenne"] for r in res if gcd(r, k) == 1 and r > 0]
    amp_non = [res[r]["amplitude_moyenne"] for r in res if gcd(r, k) != 1 or r == 0]

    if amp_coprimes and amp_non:
        ratio = np.mean(amp_coprimes) / np.mean(amp_non) if np.mean(amp_non) > 0 else float("inf")
        print(f"\n  Amplitude moyenne coprimes : {np.mean(amp_coprimes):.4f}")
        print(f"  Amplitude moyenne autres   : {np.mean(amp_non):.4f}")
        print(f"  Ratio coprime/autre        : {ratio:.2f}")

    print(f"{'=' * 60}")


def demo_calibration_mobius(N=200, nb_frequences=500):
    """
    Calibration avec Möbius : vérifie que les pics correspondent
    aux zéros non triviaux de ζ(s).
    """
    print(f"\n{'=' * 60}")
    print(f"  CALIBRATION MÖBIUS — N={N}")
    print(f"{'=' * 60}")

    t_values = np.linspace(0.1, 40, nb_frequences)

    # Calcul du spectre Möbius
    P = np.zeros(len(t_values), dtype=complex)
    for n in range(1, N + 1):
        mu = mobius(n)
        if mu != 0:
            for i, t in enumerate(t_values):
                P[i] += mu * n ** (-1j * t)

    amplitude = np.abs(P)

    # Positions connues des premiers zéros non triviaux de ζ
    zeros_riemann = [14.13, 21.02, 25.01, 30.42, 32.94, 37.59]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(t_values, amplitude, color="#2E5090", linewidth=1.2, label="Möbius |P(t)|")

    for z in zeros_riemann:
        ax.axvline(x=z, color="#E74C3C", alpha=0.5, linestyle="--", linewidth=0.8)

    ax.set_title(f"Calibration Möbius vs. zéros de ζ (N={N})", fontsize=14, fontweight="bold")
    ax.set_xlabel("t (fréquence spectrale)")
    ax.set_ylabel("|P(t)|")
    ax.legend(["Möbius |P(t)|", "Zéros de ζ (14.13, 21.02, ...)"])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("gmhms_calibration_mobius.png", dpi=150, bbox_inches="tight")
    print(f"  → Figure sauvegardée : gmhms_calibration_mobius.png")
    print(f"{'=' * 60}")


# =============================================================================
# 7. POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  GMHMS — Guasti Multi-Harmonic Modular Spectrum ║")
    print("  ║  Démonstration v1.0                             ║")
    print("  ║  Alexandre Guasti — Lyon, France — 2026         ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

    # Paramètres (ajustables)
    N = 200              # Nombre d'entiers à analyser
    NB_FREQ = 500        # Nombre de fréquences spectrales

    # 1. Spectres multi-harmoniques
    resultats = demo_spectres(N=N, nb_frequences=NB_FREQ)

    # 2. Calibration Möbius
    demo_calibration_mobius(N=N, nb_frequences=NB_FREQ)

    # 3. Analyse modulaire (m=2, k=6)
    demo_modulaire(N=N, m=2, k=6)

    # 4. Analyse modulaire (m=2, k=30)
    demo_modulaire(N=N, m=2, k=30)

    print()
    print("  Terminé ! Consultez les figures générées :")
    print("  - gmhms_spectre_demo.png")
    print("  - gmhms_calibration_mobius.png")
    print()
    print("  « Les nombres premiers ne sont plus des points rares,")
    print("    mais des résonateurs privilégiés dans un espace")
    print("    multi-harmonique discret. »")
    print()
    print("  — Alexandre Guasti & TriadIA, 2026")
    print()
