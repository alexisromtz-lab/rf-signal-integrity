"""Aparato semántico Nivel 6 para los invariantes FDTD de RF.

HUELLA-TEST-SEMANTICA-RF-NV6-20261022
"""

import re
from pathlib import Path

import numpy as np

from sim import solver_escalon_s as solver

RAIZ = Path(__file__).resolve().parents[1]
CRUDO_EXTRA = RAIZ / "registros" / "20261012" / "rf_b1_crudo_extra_20261012T205836Z.txt"


def _c11_por_malla():
    if not CRUDO_EXTRA.is_file():
        raise FileNotFoundError("CRUDO_AUSENTE: %s" % CRUDO_EXTRA)

    salida = {}
    dx = None
    patron_dx = re.compile(r"^\s*dx=([0-9.eE+-]+) m\s*$")
    patron_c11 = re.compile(
        r"^\s*C1\.1 medido \|potencia-1\|=([0-9.eE+-]+)\s+"
        r"umbral ([0-9.eE+-]+)\s+-> (PASA|FALLA)\s*$"
    )
    for linea in CRUDO_EXTRA.read_text(encoding="utf-8").splitlines():
        m_dx = patron_dx.match(linea)
        if m_dx:
            dx = float(m_dx.group(1))
            continue
        m_c11 = patron_c11.match(linea)
        if m_c11 and dx is not None:
            salida[dx] = (float(m_c11.group(1)), float(m_c11.group(2)), m_c11.group(3))
    return salida


def test_cfl_respeta_la_cota_de_estabilidad():
    for dx in (1.0e-3, 1.25e-4, 6.25e-5):
        dt = solver.paso_temporal(dx)
        courant = solver.C0 * dt / dx
        assert 0.0 < courant <= 1.0, "CFL_INESTABLE: dx=%g S=%r" % (dx, courant)
        assert courant == solver.S_CFL, "CFL_NO_DERIVA_DEL_SOLVER: %r" % courant


def test_c11_cruza_la_tolerancia_al_refinar_la_malla():
    mediciones = _c11_por_malla()
    gruesa, fina = mediciones[1.25e-4], mediciones[6.25e-5]

    assert gruesa[1] == solver.C11_TOL_ABS
    assert gruesa[0] > solver.C11_TOL_ABS and gruesa[2] == "FALLA", (
        "C11_GRUESA_DEBIA_FALLAR: residuo=%r estado=%s" % (gruesa[0], gruesa[2])
    )
    assert fina[1] == solver.C11_TOL_ABS
    assert fina[0] <= solver.C11_TOL_ABS and fina[2] == "PASA", (
        "C11_FINA_DEBIA_PASAR: residuo=%r estado=%s" % (fina[0], fina[2])
    )
    assert 1.25e-4 / 6.25e-5 == 2.0, "REFINAMIENTO_NO_ES_UN_FACTOR_DOS"


def test_esponja_reduce_energia_reflejada_frente_a_control_pec():
    dx = 1.0e-3
    n = 600
    i_fuente, i_monitor = 200, 250
    n_pasos = 3500
    dt = solver.paso_temporal(dx)
    epsr = np.ones(n, dtype=float)

    traza_esponja, _ = solver.corrida(
        dx, epsr, i_fuente, i_monitor, i_monitor, n_pasos, dt
    )
    traza_pec, _ = solver.corrida(
        dx, epsr, i_fuente, i_monitor, i_monitor, n_pasos, dt, frontera_derecha="pec"
    )

    tiempos = np.arange(n_pasos, dtype=float) * dt
    ventana_reflejada = (tiempos >= 2.7e-9) & (tiempos <= 4.0e-9)
    energia_esponja = float(np.dot(traza_esponja[ventana_reflejada], traza_esponja[ventana_reflejada]))
    energia_pec = float(np.dot(traza_pec[ventana_reflejada], traza_pec[ventana_reflejada]))

    assert energia_pec > 0.0, "CONTROL_PEC_SIN_REFLEXION: falsador ineficaz"
    assert energia_esponja < energia_pec * 1.0e-3, (
        "ABSORCION_INSUFICIENTE: energia esponja=%g PEC=%g"
        % (energia_esponja, energia_pec)
    )
