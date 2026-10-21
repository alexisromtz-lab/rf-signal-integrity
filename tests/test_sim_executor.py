# HUELLA-EJECUTOR-SIM-RF-20261020
"""Ejecutor del instrumento — rf-signal-integrity.

`sim/solver_escalon_s.py` importa numpy y produce el crudo sellado del
Benchmark 1 (escalon de impedancia, parametros S) que el README publica, pero
hasta hoy ningun test ni paso del aparato lo abria: el censo
`censo_numpy_dependencia_20261020.py` lo clasifico `SIN_EJECUTOR`
(2 portadores, 0 ejecutados). Un import que nadie ejecuta no puede fallar, y
por tanto no era una dependencia: era una suposicion.

Este test corre el instrumento por su propia puerta (`main --json`, en proceso)
y **asierte sobre su salida**: las S analiticas se recalculan desde las
impedancias que el crudo declara, la potencia medida desde sus propias S, los
errores relativos desde las S medidas, y el veredicto desde sus filas. El
veredicto publicado de este repo es un ROJO (`NO PASA / CONTROL NO DISCRIMINA`)
y el test lo exige **derivado**, no citado.

Falsador declarado (lo que hace rojo a este test):

  1. numpy ausente -> `from sim import solver_escalon_s` levanta
     `ModuleNotFoundError` en la coleccion: el test no puede ni empezar.
  2. el crudo cambia de forma (faltan filas o claves) -> cae el test del crudo.
  3. una S analitica deja de salir de las impedancias -> cae el test 2.
  4. la potencia medida deja de ser la suma de las S -> cae el test 3.
  5. el veredicto se escribe a mano y deja de derivarse de las filas -> cae el
     test del veredicto (se recalcula desde `pasa` y `control_discrimina`).
  6. numpy 1.x activo -> cae el test del piso: el manifiesto declara 2.0.
"""

from __future__ import annotations

import contextlib
import io
import json
import math
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sim import solver_escalon_s as instrumento  # noqa: E402

TOL = 1e-12


def _crudo():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = instrumento.main(["--json"])
    return rc, json.loads(buf.getvalue())


def _cerrado(a, b, tol=TOL):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def test_el_instrumento_corre_y_emite_su_crudo():
    rc, crudo = _crudo()
    assert rc == 0, rc
    for clave in ("resoluciones", "filas_medidas", "veredicto", "control_ok",
                  "z1_ohm", "z2_ohm", "s11_ana", "s21_ana"):
        assert clave in crudo, clave
    assert crudo["filas_medidas"] == len(crudo["resoluciones"])
    assert crudo["resoluciones"], "sin filas no hay medida"


def test_las_s_analiticas_salen_de_las_impedancias():
    _, crudo = _crudo()
    z1, z2 = crudo["z1_ohm"], crudo["z2_ohm"]
    s11 = (z2 - z1) / (z2 + z1)
    assert _cerrado(crudo["s11_ana"], s11), (crudo["s11_ana"], s11)
    s21 = math.sqrt(1.0 - s11 * s11)
    assert _cerrado(crudo["s21_ana"], s21), (crudo["s21_ana"], s21)
    assert _cerrado(crudo["s11_ana_abs"], abs(s11))
    assert _cerrado(crudo["s21_ana_abs"], s21)


def test_la_potencia_medida_es_la_suma_de_sus_s():
    _, crudo = _crudo()
    for fila in crudo["resoluciones"]:
        suma = fila["s11_med_abs"] ** 2 + fila["s21_med_abs"] ** 2
        assert _cerrado(fila["potencia"], suma), (fila["dx_m"], fila["potencia"], suma)
        assert _cerrado(fila["d_potencia"], fila["potencia"] - 1.0)


def test_los_errores_relativos_se_recomputan():
    _, crudo = _crudo()
    for fila in crudo["resoluciones"]:
        e11 = abs(fila["s11_med_abs"] - fila["s11_ana_abs"]) / fila["s11_ana_abs"]
        e21 = abs(fila["s21_med_abs"] - fila["s21_ana_abs"]) / fila["s21_ana_abs"]
        assert _cerrado(fila["e11_rel"], e11), (fila["dx_m"], fila["e11_rel"], e11)
        assert _cerrado(fila["e21_rel"], e21), (fila["dx_m"], fila["e21_rel"], e21)


def test_el_veredicto_se_deriva_de_sus_filas():
    """El titular publicado es un rojo: se exige derivado, no citado."""
    _, crudo = _crudo()
    filas = crudo["resoluciones"]
    pasa_alguna = any(fila["pasa"] for fila in filas)
    discrimina_todas = all(fila["control_discrimina"] for fila in filas)
    derivado = ("PASA EN ALGUNA RESOLUCION" if pasa_alguna else "NO PASA")
    if not discrimina_todas:
        derivado += " / CONTROL NO DISCRIMINA"
    assert crudo["veredicto"] == derivado, (crudo["veredicto"], derivado)
    assert crudo["control_ok"] is discrimina_todas, (crudo["control_ok"], discrimina_todas)


def test_numpy_cargado_cumple_el_piso_declarado():
    version = instrumento.np.__version__
    assert re.fullmatch(r"\d+\.\d+\.\d+.*", version), version
    assert int(version.split(".")[0]) >= 2, version
