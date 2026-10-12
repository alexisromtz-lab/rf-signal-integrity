# SOLVER FDTD RF BENCHMARK 1: SALTO DE IMPEDANCIA Y PARAMETROS S
# -*- coding: utf-8 -*-
"""
Benchmark 1 del pre-registro PREREGISTRO_RF_SI_20261012.md (seccion 4).

OBJETO MEDIBLE
  Extraer S11 y S21 de una discontinuidad TEM (salto de impedancia) con FDTD 1D
  y contrastarlos contra las formas cerradas congeladas en la seccion 4:

      S11 = (Z2 - Z1) / (Z2 + Z1)
      S21 = 2 * sqrt(Z1 * Z2) / (Z2 + Z1)
      |S11|^2 + |S21|^2 = 1

PROCEDIMIENTO CONGELADO (dos corridas, para no circular)
  Corrida A: linea homogenea de impedancia Z1. El monitor de entrada registra la
             onda INCIDENTE.
  Corrida B: la misma linea con el escalon eps1 -> eps2 en i_esc. El monitor de
             entrada registra la onda TOTAL y el monitor de salida la TRANSMITIDA.
  Onda reflejada = total (B) menos incidente (A). La resta es exacta mientras la
  reflexion no ha regresado al monitor de entrada, porque la fuente y la region
  entre la fuente y ese monitor son identicas en A y en B.

EXTRACCION EN LA FRECUENCIA DECLARADA f0 (seccion 6)
  S11 = DFT{V_ref}(f0) / DFT{V_inc}(f0)
  S21 = DFT{V_trans}(f0) / DFT{V_inc}(f0) * sqrt(Z1 / Z2)
  La DFT se evalua en un unico tono, f0, declarado abajo.

CRITERIOS SELLADOS (seccion 4; NO se mueven despues de ver una salida)
  C1.1  |S11|^2 + |S21|^2 = 1.0 con tolerancia absoluta 1e-4
  C1.2  error relativo de |S11| contra la formula <= 1.0 por ciento
  C1.3  error relativo de |S21| contra la formula <= 1.0 por ciento
  C1.4  cola absorbida por debajo de -60 dB del pico de la onda incidente

GUARDAS
  G1  cero filas medidas -> CONTRATO ROTO (no VERDE)
  G2  cada caso reporta la causa ademas del codigo
  G5  cero notacion monetaria en este archivo y en su crudo

UNIDADES DECLARADAS
  longitud: metro     celda: celda     campo: normalizado al pico de la incidente
  frecuencia: hertz   parametro S: adimensional (ondas de potencia)

DISPOSICION DECLARADA (de izquierda a derecha, en celdas)
  [esponja izquierda][fuente][monitor 1 (entrada)][escalon][monitor 2 (salida)][esponja derecha]
  Las distancias fisicas se fijan en longitudes de onda en el vacio a f0, de modo
  que la geometria NO cambia al refinar la malla; solo cambia el numero de celdas.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time

import numpy as np

# ------------------------------------------------------------------ constantes
C0 = 299792458.0
ETA0 = 376.730313668
MU0 = ETA0 / C0
EPS0 = 1.0 / (ETA0 * C0)

EPS1 = 1.0
EPS2 = 4.0
F0_HZ = 10.0e9
LAM0_M = C0 / F0_HZ

S_CFL = 0.5
N_ABS = 40
M_ESP = 3
R0_ESP = 1.0e-9

Z1 = ETA0 / math.sqrt(EPS1)
Z2 = ETA0 / math.sqrt(EPS2)
S11_ANA = (Z2 - Z1) / (Z2 + Z1)
S21_ANA = 2.0 * math.sqrt(Z1 * Z2) / (Z1 + Z2)

C11_TOL_ABS = 1.0e-4
C12_REL = 1.0e-2
C13_REL = 1.0e-2
C14_DB = -60.0

T_TOTAL_S = 8.0e-9
TAU_FRAC = 1.5
DX_POR_DEFECTO = (1.0e-3, 0.5e-3, 0.25e-3)
FREC_CONTROL = (0.5, 0.7, 0.85, 1.0, 1.15, 1.3, 1.5)

MOTOR = "python3 -B sim/solver_escalon_s.py"
UNIVERSO = (
    "dos corridas FDTD 1D por resolucion (A homogenea, B con escalon); "
    "fuera del universo: los picos vecinos del espectro, el arbol .git y "
    "cualquier otra pieza del repositorio"
)


# --------------------------------------------------------------------- perfil
def perfil_sigma(n: int, epsr: np.ndarray, dx: float) -> np.ndarray:
    """Conductividad graduada (esponja) para absorcion terminal, en siemens por metro."""
    sigma = np.zeros(n, dtype=float)
    L = N_ABS * dx
    for i in range(N_ABS):
        frac = (N_ABS - i) / float(N_ABS)
        eta = ETA0 / math.sqrt(epsr[i])
        smax = -2.0 * (M_ESP + 1) * math.log(R0_ESP) / (eta * L)
        sigma[i] = smax * frac ** M_ESP
    for i in range(n - N_ABS, n):
        frac = (i - (n - N_ABS - 1)) / float(N_ABS)
        eta = ETA0 / math.sqrt(epsr[i])
        smax = -2.0 * (M_ESP + 1) * math.log(R0_ESP) / (eta * L)
        sigma[i] = smax * frac ** M_ESP
    return sigma


# -------------------------------------------------------------------- corrida
def corrida(dx, epsr, i_fuente, i_mon1, i_mon2, n_pasos, dt, f0, tau, td):
    """FDTD 1D (Ez en nodos, Hy en seminodos). Devuelve los dos monitores y el campo final."""
    n = int(epsr.size)
    eps = epsr * EPS0
    sigma = perfil_sigma(n, epsr, dx)
    ca = (1.0 - sigma * dt / (2.0 * eps)) / (1.0 + sigma * dt / (2.0 * eps))
    cb = (dt / (eps * dx)) / (1.0 + sigma * dt / (2.0 * eps))
    ch = dt / (MU0 * dx)

    ez = np.zeros(n, dtype=float)
    hy = np.zeros(n, dtype=float)
    m1 = np.zeros(n_pasos, dtype=float)
    m2 = np.zeros(n_pasos, dtype=float)

    for paso in range(n_pasos):
        hy[:-1] -= ch * (ez[1:] - ez[:-1])
        ez[1:] = ca[1:] * ez[1:] + cb[1:] * (hy[1:] - hy[:-1])
        t = paso * dt
        ez[i_fuente] += -math.exp(-((t - td) / tau) ** 2) * math.sin(2.0 * math.pi * f0 * (t - td))
        m1[paso] = ez[i_mon1]
        m2[paso] = ez[i_mon2]
    return m1, m2, ez


def dft_tono(x: np.ndarray, dt: float, f: float) -> complex:
    """DFT de x evaluada en el tono unico f, con el factor dt."""
    n = np.arange(x.size, dtype=float)
    return complex(np.sum(x * np.exp(-2j * math.pi * f * n * dt)) * dt)


def correr_resolucion(dx: float) -> dict:
    n_lam = LAM0_M / dx
    i_fuente = N_ABS + int(round(2.0 * n_lam))
    i_mon1 = N_ABS + int(round(3.5 * n_lam))
    i_esc = N_ABS + int(round(20.0 * n_lam))
    i_mon2 = i_esc + int(round(5.0 * n_lam))
    n = i_mon2 + int(round(10.0 * n_lam)) + N_ABS + 1

    v_max = C0 / math.sqrt(min(EPS1, EPS2))
    dt = S_CFL * dx / v_max
    n_pasos = int(math.ceil(T_TOTAL_S / dt))
    tau = TAU_FRAC / F0_HZ
    td = 4.0 * tau

    epsr_a = np.full(n, EPS1, dtype=float)
    epsr_b = np.full(n, EPS1, dtype=float)
    epsr_b[i_esc:] = EPS2

    m1a, _m2a, _fin_a = corrida(dx, epsr_a, i_fuente, i_mon1, i_mon2, n_pasos, dt, F0_HZ, tau, td)
    m1b, m2b, ez_fin = corrida(dx, epsr_b, i_fuente, i_mon1, i_mon2, n_pasos, dt, F0_HZ, tau, td)

    v_inc = m1a
    v_tot = m1b
    v_ref = v_tot - v_inc
    v_tra = m2b

    a_inc = dft_tono(v_inc, dt, F0_HZ)
    a_ref = dft_tono(v_ref, dt, F0_HZ)
    a_tra = dft_tono(v_tra, dt, F0_HZ)

    s11 = a_ref / a_inc
    s21 = (a_tra / a_inc) * math.sqrt(Z1 / Z2)

    s11_med = abs(s11)
    s21_med = abs(s21)
    s11_ana = abs(S11_ANA)
    s21_ana = abs(S21_ANA)

    e11 = abs(s11_med - s11_ana) / s11_ana
    e21 = abs(s21_med - s21_ana) / s21_ana
    pot = s11_med ** 2 + s21_med ** 2
    d_pot = abs(pot - 1.0)

    pico_inc = float(np.max(np.abs(v_inc)))
    cola_dom = float(np.max(np.abs(ez_fin)))
    cola_mon = float(np.max(np.abs(v_inc[n_pasos // 2:])))
    cola = max(cola_dom, cola_mon)
    cola_db = 20.0 * math.log10(cola / pico_inc) if cola > 0.0 else -999.0

    c11 = bool(d_pot <= C11_TOL_ABS)
    c12 = bool(e11 <= C12_REL)
    c13 = bool(e21 <= C13_REL)
    c14 = bool(cola_db <= C14_DB)

    # espectro de control: el mismo instrumento fuera del tono declarado
    espectro = []
    for k in FREC_CONTROL:
        f = k * F0_HZ
        ai = dft_tono(v_inc, dt, f)
        ar = dft_tono(v_ref, dt, f)
        at = dft_tono(v_tra, dt, f)
        if abs(ai) == 0.0:
            continue
        espectro.append({
            "f_hz": f,
            "f_sobre_f0": k,
            "s11_abs": abs(ar / ai),
            "s21_abs": abs(at / ai) * math.sqrt(Z1 / Z2),
        })

    return {
        "dx_m": dx,
        "n_celdas": n,
        "celdas_por_lambda_vacio": LAM0_M / dx,
        "celdas_por_lambda_dielectrico": LAM0_M / (dx * math.sqrt(EPS2)),
        "celulas_por_lambda_elegida": LAM0_M / dx,
        "dt_s": dt,
        "n_pasos": n_pasos,
        "t_total_s": n_pasos * dt,
        "i_fuente": i_fuente,
        "i_mon1": i_mon1,
        "i_esc": i_esc,
        "i_mon2": i_mon2,
        "a_inc_abs": abs(a_inc),
        "a_ref_abs": abs(a_ref),
        "a_tra_abs": abs(a_tra),
        "s11_med_abs": s11_med,
        "s11_med_fase_deg": math.degrees(math.atan2(s11.imag, s11.real)),
        "s21_med_abs": s21_med,
        "s21_med_fase_deg": math.degrees(math.atan2(s21.imag, s21.real)),
        "s11_ana_abs": s11_ana,
        "s21_ana_abs": s21_ana,
        "e11_rel": e11,
        "e21_rel": e21,
        "potencia": pot,
        "d_potencia": d_pot,
        "pico_inc": pico_inc,
        "cola_abs": cola,
        "cola_db": cola_db,
        "c11": c11,
        "c12": c12,
        "c13": c13,
        "c14": c14,
        "pasa": bool(c11 and c12 and c13 and c14),
        "espectro_control": espectro,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Benchmark 1: escalon de impedancia y parametros S")
    ap.add_argument("--dx", type=float, nargs="+", default=list(DX_POR_DEFECTO))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    t_ini = time.time()
    ventana = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    resoluciones = [correr_resolucion(dx) for dx in args.dx]
    filas = len(resoluciones)

    # G1: guarda de cero entradas
    if filas == 0:
        veredicto = "CONTRATO ROTO"
    elif all(r["pasa"] for r in resoluciones):
        veredicto = "PASA EN TODAS LAS RESOLUCIONES"
    elif any(r["pasa"] for r in resoluciones):
        veredicto = "PASA EN ALGUNA RESOLUCION"
    else:
        veredicto = "NO PASA"

    blob = {
        "pieza": "sim/solver_escalon_s.py",
        "benchmark": 1,
        "universo_declarado": UNIVERSO,
        "motor": MOTOR,
        "unidad": "celda / muestra temporal / metro / hertz",
        "ventana_utc": ventana,
        "f0_hz": F0_HZ,
        "eps1": EPS1,
        "eps2": EPS2,
        "z1_ohm": Z1,
        "z2_ohm": Z2,
        "s11_ana": S11_ANA,
        "s21_ana": S21_ANA,
        "s11_ana_abs": abs(S11_ANA),
        "s21_ana_abs": abs(S21_ANA),
        "c11_tol_abs": C11_TOL_ABS,
        "c12_rel": C12_REL,
        "c13_rel": C13_REL,
        "c14_db": C14_DB,
        "filas_medidas": filas,
        "resoluciones": resoluciones,
        "veredicto": veredicto,
        "segundos_reloj": time.time() - t_ini,
    }

    if args.json:
        print(json.dumps(blob, indent=2, ensure_ascii=False))
        return 0

    print("BENCHMARK 1 - SALTO DE IMPEDANCIA Y PARAMETROS S")
    print("UNIVERSO DECLARADO: %s" % UNIVERSO)
    print("MOTOR: %s" % MOTOR)
    print("UNIDAD: celda / muestra temporal / metro / hertz")
    print("VENTANA: %s" % ventana)
    print("TOTAL_LINEAS_ENCABEZADO = 6")
    print("")
    print("GEOMETRIA Y CONSTANTES")
    print("  eps1 = %.17g   eps2 = %.17g" % (EPS1, EPS2))
    print("  Z1_ohm = %.12f   Z2_ohm = %.12f" % (Z1, Z2))
    print("  S11_analitico = %.17g   |S11| = %.17g" % (S11_ANA, abs(S11_ANA)))
    print("  S21_analitico = %.17g   |S21| = %.17g" % (S21_ANA, abs(S21_ANA)))
    print("  f0_hz = %.6e   lambda_vacio_m = %.6e   S_CFL = %.3f   N_ABS = %d" % (F0_HZ, LAM0_M, S_CFL, N_ABS))
    print("")
    print("FILAS MEDIDAS = %d" % filas)
    print("")
    cab = "dx_m".ljust(9) + "celdas".rjust(8) + "c/lambda".rjust(10) + "n_pasos".rjust(9) + "S11_abs".rjust(14) + "S21_abs".rjust(14) + "potencia".rjust(14) + "e11_rel".rjust(12) + "e21_rel".rjust(12) + "cola_dB".rjust(10)
    print(cab)
    for r in resoluciones:
        print(
            ("%.4g" % r["dx_m"]).ljust(9)
            + ("%d" % r["n_celdas"]).rjust(8)
            + ("%.2f" % r["celdas_por_lambda_vacio"]).rjust(10)
            + ("%d" % r["n_pasos"]).rjust(9)
            + ("%.10f" % r["s11_med_abs"]).rjust(14)
            + ("%.10f" % r["s21_med_abs"]).rjust(14)
            + ("%.10f" % r["potencia"]).rjust(14)
            + ("%.6f" % r["e11_rel"]).rjust(12)
            + ("%.6f" % r["e21_rel"]).rjust(12)
            + ("%.2f" % r["cola_db"]).rjust(10)
        )
    print("")
    print("CRITERIOS, RESOLUCION POR RESOLUCION (valor medido y umbral sellado)")
    for r in resoluciones:
        print("  dx_m = %.4g" % r["dx_m"])
        print("    C1.1  |S11|^2+|S21|^2 = %.12f   esperado 1.0  desvio %.3e  umbral %.1e  -> %s"
              % (r["potencia"], r["d_potencia"], C11_TOL_ABS, "PASA" if r["c11"] else "FALLA"))
        print("    C1.2  error relativo |S11| = %.6f   umbral %.4f  -> %s"
              % (r["e11_rel"], C12_REL, "PASA" if r["c12"] else "FALLA"))
        print("    C1.3  error relativo |S21| = %.6f   umbral %.4f  -> %s"
              % (r["e21_rel"], C13_REL, "PASA" if r["c13"] else "FALLA"))
        print("    C1.4  cola absorbida = %.2f dB   umbral %.1f dB  -> %s"
              % (r["cola_db"], C14_DB, "PASA" if r["c14"] else "FALLA"))
        print("    fase de S11 medida = %.4f grados (plano de referencia = monitor de entrada)"
              % r["s11_med_fase_deg"])
        print("    fase de S21 medida = %.4f grados" % r["s21_med_fase_deg"])
    print("")
    print("ESPECTRO DE CONTROL (misma corrida de la resolucion mas gruesa; no es el criterio)")
    base = resoluciones[0]
    print("  dx_m = %.4g" % base["dx_m"])
    print("  f_sobre_f0".rjust(12) + "|S11|".rjust(14) + "|S21|".rjust(14) + "potencia".rjust(14))
    for e in base["espectro_control"]:
        print(
            ("%.2f" % e["f_sobre_f0"]).rjust(12)
            + ("%.10f" % e["s11_abs"]).rjust(14)
            + ("%.10f" % e["s21_abs"]).rjust(14)
            + ("%.10f" % (e["s11_abs"] ** 2 + e["s21_abs"] ** 2)).rjust(14)
        )
    print("")
    print("VEREDICTO: %s" % veredicto)
    print("SEGUNDOS_RELOJ = %.2f" % (time.time() - t_ini))
    return 0


if __name__ == "__main__":
    sys.exit(main())
