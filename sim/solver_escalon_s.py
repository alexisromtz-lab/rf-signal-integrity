# SOLVER FDTD RF BENCHMARK 1: SALTO DE IMPEDANCIA Y PARAMETROS S
# -*- coding: utf-8 -*-
"""Benchmark 1 TEM: escalon de impedancia. Extractor de parametros S.

OBJETO MEDIBLE
  El par (S11, S21) medido por el instrumento, contrastado contra la forma
  algebraica exacta de una discontinuidad de linea sin perdidas, y la identidad
  de exactitud |S11|^2 + |S21|^2 = 1. Es el contraste contra los coeficientes
  analiticos de Fresnel en la discontinuidad, con el metro FUERA del solucionador:
  las formulas de las secciones 4 y 5 del pre-registro no se obtuvieron aqui.

GEOMETRIA DECLARADA (en longitudes de onda, no en celdas)
  n_lam    = LAM0_M / dx
  n_abs    = int(round(L_ESP_M / dx))            esponja, longitud fisica fija
  i_fuente = n_abs + int(round(GEOM_FUENTE_LAM * n_lam))
  i_mon1   = n_abs + int(round(GEOM_MON1_LAM * n_lam))
  i_esc    = n_abs + int(round(GEOM_ESC_LAM * n_lam))
  i_mon2   = i_esc + int(round(GEOM_ESC_MON2_LAM * n_lam))
  n        = i_mon2 + int(round(GEOM_COLA_LAM * n_lam)) + n_abs + 1
  Declarar la geometria en longitudes de onda y no en celdas hace que los arribos
  del pulso sean los mismos en toda la escalera de resoluciones: lo unico que
  cambia con dx es la dispersion de malla. La separacion fuente-monitor1-escalon
  se elige para que el doble rebote y el eco de la esponja caigan FUERA de toda
  compuerta temporal, y esa condicion se verifica por corrida (campo
  geometria_limpia), no se supone.

ESPONJA DECLARADA (absorcion terminal)
  sigma_max = -(M_ESP + 1) * ln(R0_ESP) / (2 * ETA0 * L_ESP_M)
  Perfil polinomial de grado M_ESP, simetrico en los dos extremos, con L_ESP_M
  FIJO: no se define en celdas. Definirla en celdas partia su longitud fisica a la
  mitad en cada refinamiento y por eso la cola empeoraba al refinar (errata A11.3).
  La forma anterior llevaba el factor 2*(M_ESP+1) en el numerador, cuatro veces el
  valor de Taflove (errata A11.4).

PROCEDIMIENTO CONGELADO (dos corridas, seccion 4 del pre-registro)
  Corrida A (referencia): linea homogenea EPS1, sin escalon.
  Corrida B (objeto):     la misma linea con el escalon EPS1 | EPS2.
  Incidente:   monitor 1 de la corrida A.
  Reflejada:   monitor 1 de la corrida B menos monitor 1 de la corrida A.
  Transmitida: monitor 2 de la corrida B.
  Un S medido sin corrida de referencia no cuenta: la incidente no se conoce.

EXTRACCION EN f0 CON COMPUERTA TEMPORAL
  La seccion 4 sella la frecuencia pero NO sella compuerta temporal de DFT. Eso
  queda declarado en la errata A11.1. Aqui la compuerta se declara antes de la
  corrida y deriva de parametros declarados, no de cifras observadas:
      tau   = TAU_FRAC / F0_HZ        td = 4 * tau        W = 6 * tau
      t_inc = td + (i_mon1   - i_fuente) * dx / v1
      t_ref = td + (i_esc    - i_fuente) * dx / v1 + (i_esc - i_mon1) * dx / v1
      t_tra = td + (i_esc    - i_fuente) * dx / v1 + (i_mon2 - i_esc) * dx / v2
  con v1 = C0 y v2 = C0 / sqrt(EPS2). Los arribos son geometricos: no se leen de
  la salida. La comparacion contra la forma sellada es de MAGNITUDES; la fase
  medida incluye el retardo de ida y vuelta y se imprime como diagnostico.

CRITERIOS SELLADOS (seccion 4, verbatim; no se mueven: N4)
  C1.1  |S11|^2 + |S21|^2 = 1.0 con tolerancia absoluta 1e-4
  C1.2  error relativo de S11 contra la formula <= 1.0 por ciento
  C1.3  error relativo de S21 contra la formula <= 1.0 por ciento
  C1.4  cola absorbida por debajo de -60 dB respecto del pico de la incidente
  Los TRES criterios se reportan juntos. Un verde en C1.1 con rojo en C1.2 dice
  que el puerto conserva energia y que la geometria medida no es la declarada.

GUARDAS
  G1      cero filas medidas -> veredicto CONTRATO ROTO, nunca verde.
  G2      cada criterio imprime su valor medido Y su umbral: el codigo solo no
          discrimina la causa.
  G_GEOM  si el eco de la esponja o el doble rebote caen dentro o al borde de una
          compuerta, el veredicto es CONTRATO ROTO: la geometria declarada
          dejaria de ser la geometria medida.
  G_CTRL  el espectro de control debe PODER diferir del valor en f0; si todos los
          controles coinciden, la salida no es evidencia y el veredicto lo dice.
  G4 y G5 son de archivo, no de corrida: los encabezados del pre-registro se
          cuentan fuera; aqui se cuenta y se imprime el encabezado de la tabla.

UNIDADES DECLARADAS
  Ez en V/m en nodo entero (Ez en nodo, Hy en semipaso). Celdas, muestras
  temporales, segundos, hertz y ohm se declaran en el encabezado de la tabla.

DISPOSICION DECLARADA SOBRE N5
  N5 prohibe publicar un S sin puerto instrumentado y sin descomposicion modal.
  En esta pieza, 1D y de una sola linea TEM, el puerto ES el plano de monitor con
  separacion de incidente por corrida de referencia (seccion 4), y la
  descomposicion modal es la identidad: hay UN modo y su proyeccion no filtra
  nada. La exencion cubre SOLO este benchmark 1D. No cubre microstrip 2D.

TRAMPA DECLARADA
  Una identidad impresa DENTRO de la pieza describe su version anterior. Este
  archivo no imprime su propia huella: la identidad se mide fuera, en terminal,
  con git hash-object y sha16.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time

import numpy as np

# --- constantes declaradas ---------------------------------------------------

C0 = 299792458.0
ETA0 = 376.730313668
MU0 = ETA0 / C0
EPS0 = 1.0 / (ETA0 * C0)

F0_HZ = 10.0e9
LAM0_M = C0 / F0_HZ

EPS1 = 1.0
EPS2 = 4.0
Z1_OHM = ETA0 / math.sqrt(EPS1)
Z2_OHM = ETA0 / math.sqrt(EPS2)
S11_ANA = (Z2_OHM - Z1_OHM) / (Z2_OHM + Z1_OHM)
S21_ANA = 2.0 * math.sqrt(Z1_OHM * Z2_OHM) / (Z1_OHM + Z2_OHM)

TAU_FRAC = 1.5
TAU_S = TAU_FRAC / F0_HZ
TD_S = 4.0 * TAU_S
W_COMPUERTA_S = 6.0 * TAU_S
S_CFL = 0.5

L_ESP_M = 80.0e-3
M_ESP = 3
R0_ESP = 1.0e-9
SIGMA_MAX = -(M_ESP + 1) * math.log(R0_ESP) / (2.0 * ETA0 * L_ESP_M)

T_TOTAL_S = 8.0e-9

C11_TOL_ABS = 1.0e-4
C12_REL = 1.0e-2
C13_REL = 1.0e-2
C14_DB = -60.0

# Umbral de DISCRIMINACION DEL CONTROL: el control es el barrido de frecuencia
# con las mismas compuertas. Se declara discriminante si la variacion relativa de
# |S11| dentro del barrido supera el 1 % (la misma tolerancia de C1.2/C1.3).
# NO es un criterio sellado del pre-registro: es la exigencia de que el control
# PUEDA diferir. Se nombra aqui para que el umbral no viva duplicado sin nombre.
C_CTRL_DIF_MIN = 1.0e-2

DX_SELLADAS = (1.0e-3, 0.5e-3, 0.25e-3)
FREC_CONTROL = (8.0e9, 9.0e9, 10.0e9, 11.0e9, 12.0e9)

GEOM_FUENTE_LAM = 15.0     # n_abs        -> fuente
GEOM_MON1_LAM = 16.5       # n_abs        -> monitor 1
GEOM_ESC_LAM = 21.5        # n_abs        -> escalon
GEOM_ESC_MON2_LAM = 2.5    # escalon      -> monitor 2
GEOM_COLA_LAM = 10.0       # monitor 2    -> inicio de la esponja lejana

# La linea de MAYOR impedancia es la de EPS1 (Z1 > Z2), luego la restriccion de la
# seccion 6 (20 celdas por longitud de onda guiada) se mide contra lambda_vacio.


def paso_temporal(dx):
    """Devuelve el paso temporal estable fijado por S_CFL."""
    if dx <= 0.0:
        raise ValueError("dx debe ser positivo")
    return S_CFL * dx / C0


def perfil_sigma(n, dx):
    """Absorbedor en los dos extremos: grado M_ESP, longitud fisica L_ESP_M."""
    n_abs = int(round(L_ESP_M / dx))
    if 2 * n_abs >= n:
        raise ValueError("la esponja no cabe en el dominio: n_abs=%d n=%d" % (n_abs, n))
    sigma = np.zeros(n, dtype=float)
    for i in range(n_abs):
        f = (n_abs - i) / float(n_abs)
        s = SIGMA_MAX * (f ** M_ESP)
        sigma[i] = s
        sigma[n - 1 - i] = s
    return sigma, n_abs


def corrida(dx, epsr, i_fuente, i_mon1, i_mon2, n_pasos, dt, frontera_derecha="esponja"):
    """Un Yee 1D; ``pec`` habilita el control reflectivo del borde derecho.

    HUELLA-RF-FRONTERA-DERECHA-PEC-CONTROL-20261022
    """
    if frontera_derecha not in ("esponja", "pec"):
        raise ValueError("frontera_derecha debe ser 'esponja' o 'pec'")
    n = int(epsr.size)
    eps = epsr * EPS0
    sigma, n_abs = perfil_sigma(n, dx)
    if frontera_derecha == "pec":
        sigma[n - n_abs :] = 0.0
    ca = (1.0 - sigma * dt / (2.0 * eps)) / (1.0 + sigma * dt / (2.0 * eps))
    cb = (dt / (eps * dx)) / (1.0 + sigma * dt / (2.0 * eps))
    ch = dt / (MU0 * dx)
    ez = np.zeros(n, dtype=float)
    hy = np.zeros(n, dtype=float)
    m1 = np.zeros(n_pasos, dtype=float)
    m2 = np.zeros(n_pasos, dtype=float)
    for p in range(n_pasos):
        hy[:-1] -= ch * (ez[1:] - ez[:-1])
        ez[1:] = ca[1:] * ez[1:] - cb[1:] * (hy[1:] - hy[:-1])
        t = p * dt
        ez[i_fuente] -= math.exp(-(((t - TD_S) / TAU_S) ** 2)) * math.sin(
            2.0 * math.pi * F0_HZ * (t - TD_S)
        )
        if frontera_derecha == "pec":
            ez[-1] = 0.0
        m1[p] = ez[i_mon1]
        m2[p] = ez[i_mon2]
    return m1, m2


def dft_tono(x, dt, f, t0, t1):
    """DFT de un solo tono sobre la compuerta de tiempo [t0, t1] declarada."""
    n0 = max(int(math.floor(t0 / dt)), 0)
    n1 = min(int(math.ceil(t1 / dt)), int(x.size))
    if n1 <= n0:
        return 0j
    nn = np.arange(n0, n1, dtype=float)
    return complex(np.sum(x[n0:n1] * np.exp(-2j * math.pi * f * nn * dt)) * dt)


def correr_resolucion(dx):
    """Mide (S11, S21) en f0 y aplica los criterios sellados a una resolucion."""
    n_lam = LAM0_M / dx
    n_abs = int(round(L_ESP_M / dx))
    i_fuente = n_abs + int(round(GEOM_FUENTE_LAM * n_lam))
    i_mon1 = n_abs + int(round(GEOM_MON1_LAM * n_lam))
    i_esc = n_abs + int(round(GEOM_ESC_LAM * n_lam))
    i_mon2 = i_esc + int(round(GEOM_ESC_MON2_LAM * n_lam))
    n = i_mon2 + int(round(GEOM_COLA_LAM * n_lam)) + n_abs + 1

    dt = paso_temporal(dx)
    n_pasos = int(math.ceil(T_TOTAL_S / dt))
    t_total = n_pasos * dt

    v1 = C0
    v2 = C0 / math.sqrt(EPS2)
    t_inc = TD_S + (i_mon1 - i_fuente) * dx / v1
    t_ref = TD_S + (i_esc - i_fuente) * dx / v1 + (i_esc - i_mon1) * dx / v1
    t_tra = TD_S + (i_esc - i_fuente) * dx / v1 + (i_mon2 - i_esc) * dx / v2
    t_doble = t_ref + 2.0 * (i_esc - i_mon1) * dx / v1
    t_eco_cota = t_inc + 2.0 * (n - 1 - i_mon1) * dx / v1

    medio = W_COMPUERTA_S / 2.0
    sep_rebote = t_doble - medio - (t_ref + medio)
    sep_eco = t_eco_cota - medio - (t_tra + medio)
    geometria_limpia = bool((sep_rebote > 0.0) and (sep_eco > 0.0))

    eps_a = np.full(n, EPS1, dtype=float)
    eps_b = np.full(n, EPS1, dtype=float)
    eps_b[i_esc:] = EPS2

    m1a, _ = corrida(dx, eps_a, i_fuente, i_mon1, i_mon2, n_pasos, dt)
    m1b, m2b = corrida(dx, eps_b, i_fuente, i_mon1, i_mon2, n_pasos, dt)

    ai = dft_tono(m1a, dt, F0_HZ, t_inc - medio, t_inc + medio)
    ar = dft_tono(m1b - m1a, dt, F0_HZ, t_ref - medio, t_ref + medio)
    at = dft_tono(m2b, dt, F0_HZ, t_tra - medio, t_tra + medio)
    if abs(ai) == 0.0:
        raise ValueError("la incidencia medida es nula en dx=%.4g: no hay cociente que medir" % dx)

    s11 = ar / ai
    s21 = (at / ai) * math.sqrt(Z1_OHM / Z2_OHM)
    s11_med = abs(s11)
    s21_med = abs(s21)
    e11 = abs(s11_med - abs(S11_ANA)) / abs(S11_ANA)
    e21 = abs(s21_med - abs(S21_ANA)) / abs(S21_ANA)
    pot = s11_med * s11_med + s21_med * s21_med
    d_pot = abs(pot - 1.0)

    pico_inc = float(np.max(np.abs(m1a)))
    i0 = min(max(int((t_inc + medio) / dt), 0), n_pasos)
    if i0 < n_pasos:
        cola_abs = float(np.max(np.abs(m1a[i0:])))
        t_pico_cola = (i0 + int(np.argmax(np.abs(m1a[i0:])))) * dt
    else:
        cola_abs = 0.0
        t_pico_cola = 0.0
    if cola_abs > 0.0 and pico_inc > 0.0:
        cola_db = 20.0 * math.log10(cola_abs / pico_inc)
    else:
        cola_db = -999.0

    control = []
    for f in FREC_CONTROL:
        aic = dft_tono(m1a, dt, f, t_inc - medio, t_inc + medio)
        arc = dft_tono(m1b - m1a, dt, f, t_ref - medio, t_ref + medio)
        if abs(aic) == 0.0:
            continue
        control.append((f, abs(arc / aic)))
    dif_max = 0.0
    if s11_med > 0.0 and control:
        dif_max = max(abs(v - s11_med) / s11_med for _, v in control)
    control_discrimina = bool(control) and (dif_max > C_CTRL_DIF_MIN)

    c11 = bool(d_pot <= C11_TOL_ABS)
    c12 = bool(e11 <= C12_REL)
    c13 = bool(e21 <= C13_REL)
    c14 = bool(cola_db <= C14_DB)

    return {
        "dx_m": dx,
        "n_celdas": n,
        "celdas_por_lambda_vacio": n_lam,
        "celdas_por_lambda_dielectrico": n_lam * math.sqrt(EPS2),
        "celulas_por_lambda_elegida": n_lam,  # clave conservada de la foto defectuosa
        "n_abs": n_abs,
        "dt_s": dt,
        "n_pasos": n_pasos,
        "t_total_s": t_total,
        "i_fuente": i_fuente,
        "i_mon1": i_mon1,
        "i_esc": i_esc,
        "i_mon2": i_mon2,
        "t_inc_s": t_inc,
        "t_ref_s": t_ref,
        "t_tra_s": t_tra,
        "t_doble_s": t_doble,
        "t_eco_cota_s": t_eco_cota,
        "sep_rebote_s": sep_rebote,
        "sep_eco_s": sep_eco,
        "geometria_limpia": geometria_limpia,
        "a_inc_abs": abs(ai),
        "a_ref_abs": abs(ar),
        "a_tra_abs": abs(at),
        "s11_med_abs": s11_med,
        "s11_med_fase_deg": math.degrees(math.atan2(s11.imag, s11.real)),
        "s21_med_abs": s21_med,
        "s21_med_fase_deg": math.degrees(math.atan2(s21.imag, s21.real)),
        "s11_ana_abs": abs(S11_ANA),
        "s21_ana_abs": abs(S21_ANA),
        "e11_rel": e11,
        "e21_rel": e21,
        "potencia": pot,
        "d_potencia": d_pot,
        "pico_inc": pico_inc,
        "cola_abs": cola_abs,
        "cola_db": cola_db,
        "t_pico_cola_s": t_pico_cola,
        "c11": c11,
        "c12": c12,
        "c13": c13,
        "c14": c14,
        "pasa": bool(c11 and c12 and c13 and c14),
        "control_dif_max": dif_max,
        "control_discrimina": control_discrimina,
        "espectro_control": [{"f_hz": f, "s11_abs": v} for f, v in control],
    }


def _cabecera():
    return [
        "UNIVERSO DECLARADO: Benchmark 1 TEM 1D, eps1=1.0 eps2=4.0, f0=1.0e10 Hz, "
        "geometria declarada en lambda_vacio, L_ESP=0.08 m, esponja en los dos extremos",
        "MOTOR: FDTD 1D Yee (Ez en nodo, Hy en semipaso), S_CFL=0.5, "
        "sigma_max=-(m+1)*ln(R0)/(2*eta0*L_ESP)=%.6f S/m, m=%d, R0=%.0e"
        % (SIGMA_MAX, M_ESP, R0_ESP),
        "UNIDAD: Ez en V/m en nodo; celdas / muestras temporales / s / Hz / ohm "
        "declarados en el encabezado de la tabla",
        "VENTANA: %s | espectral f0=1.0e10 Hz con celdas por lambda_vacio en la tabla "
        "| temporal W=6*tau=%.0f ps | barrido sellado dx=1.0e-3 5.0e-4 2.5e-4 m"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), W_COMPUERTA_S * 1e12),
        "ANALITICO: Z1=%.9f ohm Z2=%.9f ohm S11=%.12f |S11|=%.12f |S21|=%.12f "
        "|S11|^2+|S21|^2=%.12f"
        % (
            Z1_OHM,
            Z2_OHM,
            S11_ANA,
            abs(S11_ANA),
            abs(S21_ANA),
            abs(S11_ANA) ** 2 + abs(S21_ANA) ** 2,
        ),
        "dx_m  celdas/lambda_vacio  celdas/lambda_eps2  N_ABS  n_celdas  n_pasos  "
        "|S11|  e11_por_ciento  |S21|  e21_por_ciento  potencia  cola_dB",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Benchmark 1 TEM: escalon de impedancia y parametros S."
    )
    ap.add_argument("--json", action="store_true", help="emite solo el crudo JSON")
    ap.add_argument(
        "--dx-extra",
        default="",
        help="dx adicionales separados por coma, fuera del barrido sellado",
    )
    args = ap.parse_args(argv)

    reloj0 = time.time()
    ventana_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    dx_lista = list(DX_SELLADAS)
    dx_extra = []
    for tok in args.dx_extra.split(","):
        tok = tok.strip()
        if tok:
            dx_extra.append(float(tok))
    dx_lista.extend(dx_extra)

    cabecera = _cabecera()
    assert len(cabecera) == 6, "el encabezado declarado no mide seis lineas"

    filas = []
    fallo = None
    for dx in dx_lista:
        try:
            filas.append(correr_resolucion(dx))
        except ValueError as exc:
            fallo = "dx=%.4g: %s" % (dx, exc)
            break

    if not filas:
        veredicto = "CONTRATO ROTO"
        if fallo is None:
            fallo = "cero filas medidas: no hay identidad que aplicar (G1)"
    elif any(not r["geometria_limpia"] for r in filas):
        veredicto = "CONTRATO ROTO"
        fallo = "geometria no limpia: un eco de la esponja o el doble rebote cae " \
                "dentro o al borde de una compuerta (G_GEOM)"
    elif all(r["pasa"] for r in filas):
        veredicto = "PASA EN TODAS LAS RESOLUCIONES"
    elif any(r["pasa"] for r in filas):
        veredicto = "PASA EN ALGUNA RESOLUCION"
    else:
        veredicto = "NO PASA"

    control_ok = bool(filas) and all(r["control_discrimina"] for r in filas)
    if (not control_ok) and (not veredicto.startswith("CONTRATO ROTO")):
        veredicto = veredicto + " / CONTROL NO DISCRIMINA"

    segundos = time.time() - reloj0

    crudo = {
        "pieza": "sim/solver_escalon_s.py",
        "benchmark": "Benchmark 1 TEM: escalon de impedancia",
        "universo_declarado": "FDTD 1D TEM, eps1=1.0 eps2=4.0, f0=1.0e10 Hz, "
                              "esponja de longitud fisica L_ESP=0.08 m en los dos extremos",
        "motor": "python3 -B sim/solver_escalon_s.py",
        "unidad": "Ez en V/m en nodo; celdas / muestras / s / Hz / ohm declarados por cifra",
        "ventana_utc": ventana_utc,
        "f0_hz": F0_HZ,
        "eps1": EPS1,
        "eps2": EPS2,
        "z1_ohm": Z1_OHM,
        "z2_ohm": Z2_OHM,
        "s11_ana": S11_ANA,
        "s21_ana": S21_ANA,
        "s11_ana_abs": abs(S11_ANA),
        "s21_ana_abs": abs(S21_ANA),
        "c11_tol_abs": C11_TOL_ABS,
        "c12_rel": C12_REL,
        "c13_rel": C13_REL,
        "c14_db": C14_DB,
        "tau_s": TAU_S,
        "w_compuerta_s": W_COMPUERTA_S,
        "td_s": TD_S,
        "l_esp_m": L_ESP_M,
        "m_esp": M_ESP,
        "r0_esp": R0_ESP,
        "sigma_max_s_m": SIGMA_MAX,
        "frec_control_hz": list(FREC_CONTROL),
        "dx_selladas_m": list(DX_SELLADAS),
        "dx_extra_m": dx_extra,
        "errata_declarada": [
            "A11.1 la seccion 4 no sellaba compuerta temporal de DFT: se declara aqui",
            "A11.2 el signo del acoplamiento en la actualizacion de Ez estaba invertido",
            "A11.3 la esponja se definia en celdas y cambiaba de longitud al refinar",
            "A11.4 sigma_max llevaba el factor 2*(m+1): cuatro veces el valor de Taflove",
            "A11.5 la geometria colisionaba con el doble rebote y con el eco de la esponja",
            "A11.7 C1.1 no tiene malla declarada: el umbral no se mueve",
        ],
        "filas_medidas": len(filas),
        "resoluciones": filas,
        "control_ok": control_ok,
        "fallo": fallo,
        "veredicto": veredicto,
        "segundos_reloj": segundos,
    }

    if args.json:
        print(json.dumps(crudo, indent=2, ensure_ascii=False))
        return 2 if veredicto.startswith("CONTRATO ROTO") else 0

    for linea in cabecera:
        print(linea)
    print("TOTAL_LINEAS_ENCABEZADO = %d" % len(cabecera))

    for r in filas:
        print(
            "%-8.4g %8.1f %8.1f %5d %8d %8d %.8f %12.4f %.8f %12.4f %.8f %8.2f"
            % (
                r["dx_m"],
                r["celdas_por_lambda_vacio"],
                r["celdas_por_lambda_dielectrico"],
                r["n_abs"],
                r["n_celdas"],
                r["n_pasos"],
                r["s11_med_abs"],
                100.0 * r["e11_rel"],
                r["s21_med_abs"],
                100.0 * r["e21_rel"],
                r["potencia"],
                r["cola_db"],
            )
        )
        print(
            "         arribos declarados en ps: t_inc=%.1f t_ref=%.1f t_tra=%.1f "
            "t_doble=%.1f t_eco_cota=%.1f"
            % (
                r["t_inc_s"] * 1e12,
                r["t_ref_s"] * 1e12,
                r["t_tra_s"] * 1e12,
                r["t_doble_s"] * 1e12,
                r["t_eco_cota_s"] * 1e12,
            )
        )
        print(
            "         separaciones en ps: rebote_vs_compuerta_ref=%.1f "
            "eco_vs_compuerta_tra=%.1f | geometria_limpia=%s | pico de cola medido en "
            "t=%.1f ps"
            % (
                r["sep_rebote_s"] * 1e12,
                r["sep_eco_s"] * 1e12,
                r["geometria_limpia"],
                r["t_pico_cola_s"] * 1e12,
            )
        )
        print(
            "         fases medidas en grados: s11=%.3f s21=%.3f (incluyen el retardo "
            "de ida y vuelta; la comparacion sellada es de magnitudes)"
            % (r["s11_med_fase_deg"], r["s21_med_fase_deg"])
        )

    print("")
    print("CRITERIOS SELLADOS (seccion 4 del pre-registro; los cuatro se reportan juntos)")
    for r in filas:
        print("  dx=%.4g m" % r["dx_m"])
        print(
            "    C1.1 medido |potencia-1|=%.9f  umbral %.1e  -> %s"
            % (r["d_potencia"], C11_TOL_ABS, "PASA" if r["c11"] else "FALLA")
        )
        print(
            "    C1.2 medido e11=%.6f  umbral %.6f  -> %s"
            % (r["e11_rel"], C12_REL, "PASA" if r["c12"] else "FALLA")
        )
        print(
            "    C1.3 medido e21=%.6f  umbral %.6f  -> %s"
            % (r["e21_rel"], C13_REL, "PASA" if r["c13"] else "FALLA")
        )
        print(
            "    C1.4 medido cola=%.6f dB  umbral %.1f dB  -> %s"
            % (r["cola_db"], C14_DB, "PASA" if r["c14"] else "FALLA")
        )

    if filas:
        print("")
        print(
            "ESPECTRO DE CONTROL sobre dx=%.4g m, mismas compuertas (una salida que no "
            "puede diferir no es evidencia)" % filas[0]["dx_m"]
        )
        for it in filas[0]["espectro_control"]:
            print("  f=%.4e Hz  |S11_control|=%.9f" % (it["f_hz"], it["s11_abs"]))
        print("")
        print(
            "CONTROL POR RESOLUCION (el veredicto sufija NO DISCRIMINA si ALGUNA fila "
            "no discrimina; por eso se imprimen TODAS, no solo la primera)"
        )
        for r in filas:
            print(
                "  dx=%.4g m  max|S11_control-S11_f0|/S11_f0 = %.6f  umbral %.2f  -> %s"
                % (
                    r["dx_m"],
                    r["control_dif_max"],
                    C_CTRL_DIF_MIN,
                    "DISCRIMINA" if r["control_discrimina"] else "NO DISCRIMINA",
                )
            )

    print("")
    if fallo is not None:
        print("CAUSA DECLARADA: %s" % fallo)
    print("VEREDICTO: %s" % veredicto)
    print("SEGUNDOS_RELOJ = %.3f" % segundos)
    return 2 if veredicto.startswith("CONTRATO ROTO") else 0


if __name__ == "__main__":
    sys.exit(main())
