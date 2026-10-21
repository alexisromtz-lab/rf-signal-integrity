# HUELLA-EJECUTOR-B2-MICROSTRIP-RF-20261021
"""Ejecutor directo del solver electrostatico de microstrip B2."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sim import b2_microstrip_2d as solver  # noqa: E402


@pytest.fixture(scope="module")
def par_medido():
    vacio = solver.correr(40, 1.0, 20.0, tol=1e-8, chk=20, maxbar=20000)
    dielectrico = solver.correr(40, 4.2, 20.0, tol=1e-8, chk=20, maxbar=20000)
    return vacio, dielectrico, solver.par(vacio, dielectrico)


def test_solver_converge_y_sostiene_el_par_de_magnitudes(par_medido):
    vacio, dielectrico, (eps_eff, z0) = par_medido

    for resultado in (vacio, dielectrico):
        assert resultado["convergido"] is True
        assert resultado["ra"] <= 1e-8
        assert resultado["ndir"] == 3
        assert resultado["Vmax"] == 1.0
        assert resultado["Cq"] > 0.0
        assert resultado["Ce"] > 0.0
        assert abs(float(resultado["Cq"] / resultado["Ce"]) - 1.0) < 1e-8

    assert math.isclose(float(eps_eff), 3.1076822266665194, abs_tol=1e-9)
    assert math.isclose(float(z0), 61.30927386492423, abs_tol=1e-8)


def test_dx_mayor_que_h_falla_cerrado_con_rc_2(capsys):
    with pytest.raises(SystemExit) as salida:
        solver.correr(10, 4.2, 20.0, tol=1e-8, chk=20, maxbar=20000)

    assert salida.value.code == 2
    assert "CONTRATO ROTO: dx > h" in capsys.readouterr().out
