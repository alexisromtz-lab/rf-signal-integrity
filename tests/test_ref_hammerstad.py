# HUELLA-EJECUTOR-REF-HAMMERSTAD-RF-20261021
# HUELLA-CORRECCION-IMPORT-REF-HAMMERSTAD-20261021
"""Ejecutor directo de la referencia cerrada Hammerstad-Jensen."""

from __future__ import annotations

import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sim import ref_hammerstad as referencia  # noqa: E402


def test_caso_congelado_reproduce_las_dos_magnitudes_y_el_argumento():
    eps_eff, z0, argumento = referencia.hj(4.2, 1.0)

    assert math.isclose(eps_eff, 3.0437601569801833, abs_tol=1e-14)
    assert math.isclose(z0, 72.5223419689591, abs_tol=1e-12)
    assert argumento == 8.25


def test_control_discriminante_cambia_ambas_magnitudes():
    eps_eff, z0, argumento = referencia.hj(4.2, 1.0)
    eps_eff_control, z0_control, argumento_control = referencia.hj(4.2, 0.5)

    assert eps_eff_control == 2.92
    assert math.isclose(z0_control, 97.5578008130055, abs_tol=1e-12)
    assert argumento_control == 16.125
    assert eps_eff_control != eps_eff
    assert z0_control != z0


def test_main_emite_veredicto_confirmado_y_rc_cero(capsys):
    rc = referencia.main()
    salida = capsys.readouterr().out

    assert rc == 0
    assert "K2 discriminante: PASA" in salida
    assert "VEREDICTO: REFERENCIA CONFIRMADA (RC=0)" in salida
