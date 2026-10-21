# -*- coding: utf-8 -*-
"""Test de cifras publicadas — rf-signal-integrity.

Mide que cada cifra del README tenga portador en los crudos sellados de
``registros/`` y que cada veredicto impreso sea **recomputable** a partir de la
cifra medida y del umbral sellado (§4 del pre-registro). No compara prosa
contra prosa: recalcula la identidad, el veredicto y el cruce.

El aparato es el que discrimina: se incluye un falsificador propio
(``test_el_verificador_sabe_fallar``) que muta el crudo en memoria y exige que
el motor lo detecte. Si el motor no caza una mutación, el test falla.

HUELLA-RF-TEST-CIFRAS-20261020

Falla cerrado: si un crudo falta o está vacío, el test falla. No se inventa la
cifra que el portador no trae.
"""

import inspect
import json
import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REG = RAIZ / "registros"
README = RAIZ / "README.md"

CRUDO_SELLADO = REG / "20261012" / "rf_b1_crudo_sellado_20261012T205817Z.txt"
CRUDO_EXTRA = REG / "20261012" / "rf_b1_crudo_extra_20261012T205836Z.txt"
CRUDO_B2 = REG / "20261013" / "rf_b2_crudo_20261013T023346Z.txt"
REF_B2_A = REG / "20261013" / "rf_b2_ref_hammerstad_20261013T024127Z.txt"
REF_B2_B = REG / "20261013" / "rf_b2_ref_hammerstad_20261013T024616Z.txt"

C_LUZ = 299792458.0
F0_HZ = 1.0e10
LAM0_M = C_LUZ / F0_HZ

# Tolerancias declaradas: 3e-8 cubre el redondeo a 8 decimales de la columna
# `potencia`; 0.1 cubre el redondeo a 1 decimal de `celdas/lambda_vacio`.
TOL_POTENCIA_ABS = 3.0e-8
TOL_REDONDEO_DP1 = 0.1
TOL_DESV_REL = 1.0e-6
TOL_TEXTO = 1e-11

FILA = re.compile(
    r"^([0-9.eE+-]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+"
    r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s*$",
    re.M,
)
BLOQUE_DX = re.compile(r"^\s*dx=([0-9.eE+-]+) m\s*$", re.M)
CRITERIO = re.compile(r"^\s*C1\.([1-4]) medido (.+?)\s+umbral (.+?)\s+-> (PASA|FALLA)\s*$", re.M)
CONTROL = re.compile(
    r"^\s*dx=([0-9.eE+-]+) m\s+max\|S11_control-S11_f0\|/S11_f0 = ([\d.]+)\s+"
    r"umbral ([\d.]+)\s+-> (DISCRIMINA|NO DISCRIMINA)\s*$",
    re.M,
)
VEREDICTO = re.compile(r"^VEREDICTO: (.+?)\s*$", re.M)
ANALITICO = re.compile(
    r"^ANALITICO: .*\|S11\|=([\d.]+) \|S21\|=([\d.]+) \|S11\|\^2\+\|S21\|\^2=([\d.]+)", re.M
)

REF_B2 = re.compile(r"REFERENCIA \(13\.3\): eps_eff=([\d.]+)\s+Z0=([\d.]+)")
UMBRALES_B2 = re.compile(r"UMBRALES: ERR_REL_Z0_MAX=([\d.eE+-]+)\s+ERR_REL_EEFF_MAX=([\d.eE+-]+)")
DESV_B2 = re.compile(r">> (eps_eff|Z0)\s+= ([\d.]+)\s+desv_rel = ([\d.eE+-]+)")
PUERTA_B2 = re.compile(r"C13\.([124]) \(.*?<= ([\d.eE+-]+).*?\): (PASA|FALLA)")
CCCE_B2 = re.compile(r"\|Cc/Ce-1\|=([\d.eE+-]+)")
C133_B2 = re.compile(r"C13\.3 \(\|Cc/Ce-1\| max\) = ([\d.eE+-]+)\s+-> (PASA|FALLA)")
RESUMEN_B2 = re.compile(r"^\s+eps_eff = ([\d.]+)\s+Z0 = ([\d.]+) ohm", re.M)
MOV_B2 = re.compile(r"movimiento_rel = ([\d.eE+-]+)")
OBLIGACION = re.compile(r"OBLIGACION 13\.4/R2: eps_eff = ([\d.]+)\s+Z0 = ([\d.]+)")
COINCIDE = re.compile(r"C13\.4/R2 (eps_eff|Z0)\s*: COINCIDE\s+\(medido ([\d.]+) contra obligacion ([\d.]+)\)")


def leer(ruta):
    """Lee un portador; si falta o está vacío, falla cerrado."""
    if not ruta.is_file():
        raise FileNotFoundError(
            "CRUDO_AUSENTE: falta %s — sin el crudo no hay cifra que medir" % ruta
        )
    texto = ruta.read_text(encoding="utf-8")
    if not texto.strip():
        raise ValueError("CRUDO_VACIO: %s no trae ninguna linea" % ruta)
    return texto


def filas(texto):
    """Tabla de convergencia del barrido TEM 1D."""
    return [
        {
            "dx": float(m.group(1)),
            "celdas_lam0": float(m.group(2)),
            "s11": float(m.group(7)),
            "s21": float(m.group(9)),
            "potencia": float(m.group(11)),
            "cola_db": float(m.group(12)),
        }
        for m in FILA.finditer(texto)
    ]


def criterios(texto):
    """C1.1..C1.4 por malla, tal como los imprime el crudo."""
    salida = {}
    dx = None
    for linea in texto.splitlines():
        m = BLOQUE_DX.match(linea)
        if m:
            dx = float(m.group(1))
            salida.setdefault(dx, {})
            continue
        m = CRITERIO.match(linea)
        if m and dx is not None:
            medido = float(m.group(2).split("=")[-1].split()[0])
            umbral = float(m.group(3).split()[0])
            salida[dx]["C1." + m.group(1)] = (medido, umbral, m.group(4))
    return salida


def controles(texto):
    """Control por resolucion: (dx, valor, umbral, veredicto)."""
    return [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4))
        for m in CONTROL.finditer(texto)
    ]


def veredicto(texto):
    m = VEREDICTO.search(texto)
    return m.group(1) if m else None


def inconsistencias(texto):
    """Motor: devuelve la lista de discrepancias recomputables del crudo.

    Vacía significa que cada cifra impresa se reconstruye desde las columnas
    del propio crudo y desde el umbral que el propio crudo declara.
    """
    fallos = []
    rs = filas(texto)
    cs = criterios(texto)
    ct = controles(texto)
    if len(rs) < 2:
        fallos.append("FILAS_INSUFICIENTES: %d filas medidas" % len(rs))
    if not cs:
        fallos.append("SIN_CRITERIOS: el crudo no imprime los C1.x")
    if not ct:
        fallos.append("SIN_CONTROL: el crudo no imprime el control por resolucion")

    potencia = {}
    for r in rs:
        recom = r["s11"] ** 2 + r["s21"] ** 2
        if abs(recom - r["potencia"]) > TOL_POTENCIA_ABS:
            fallos.append(
                "UNITARIEDAD: dx=%g |S11|^2+|S21|^2=%r y la columna potencia dice %r"
                % (r["dx"], recom, r["potencia"])
            )
        calc = LAM0_M / r["dx"]
        if abs(calc - r["celdas_lam0"]) > TOL_REDONDEO_DP1:
            fallos.append(
                "CELDAS_LAMBDA: dx=%g imprime %r y lambda0/dx = %.4f"
                % (r["dx"], r["celdas_lam0"], calc)
            )
        potencia[r["dx"]] = r["potencia"]

    for dx in sorted(cs):
        if dx not in potencia:
            fallos.append("CRITERIO_SIN_FILA: dx=%g no aparece en la tabla" % dx)
            continue
        for nombre in sorted(cs[dx]):
            medido, umbral, impreso = cs[dx][nombre]
            if nombre == "C1.1" and abs(medido - abs(potencia[dx] - 1.0)) > TOL_POTENCIA_ABS:
                fallos.append(
                    "C11_NO_DERIVA_DE_POTENCIA: dx=%g medido=%r y |potencia-1|=%r"
                    % (dx, medido, abs(potencia[dx] - 1.0))
                )
            esperado = "PASA" if medido <= umbral else "FALLA"
            if impreso != esperado:
                fallos.append(
                    "VEREDICTO_NO_SE_RECOMPUTA: dx=%g %s medido=%r umbral=%r imprime %s y toca %s"
                    % (dx, nombre, medido, umbral, impreso, esperado)
                )

    for nombre in ("C1.1", "C1.2", "C1.3", "C1.4"):
        umbrales = {round(c[nombre][1], 15) for c in cs.values() if nombre in c}
        if len(umbrales) > 1:
            fallos.append("UMBRAL_NO_HOMOGENEO: %s declara %s" % (nombre, sorted(umbrales)))

    falla = sorted(dx for dx, c in cs.items() if c.get("C1.1", (0, 0, ""))[2] == "FALLA")
    pasa = sorted(dx for dx, c in cs.items() if c.get("C1.1", (0, 0, ""))[2] == "PASA")
    if falla and pasa:
        fino, grueso = min(falla), max(pasa)
        if grueso >= fino:
            fallos.append(
                "CRUCE_SIN_SENTIDO: el PASA mas grueso (%g) no es mas fino que el FALLA mas fino (%g)"
                % (grueso, fino)
            )
        elif abs(fino / grueso - 2.0) > 1e-9:
            fallos.append(
                "CRUCE_NO_ES_UN_PASO: %g/%g = %.6f (un paso de refinamiento es 2)"
                % (fino, grueso, fino / grueso)
            )

    for dx, valor, umbral, impreso in ct:
        esperado = "DISCRIMINA" if valor > umbral else "NO DISCRIMINA"
        if impreso != esperado:
            fallos.append(
                "CONTROL_NO_SE_RECOMPUTA: dx=%g valor=%r umbral=%r imprime %s y toca %s"
                % (dx, valor, umbral, impreso, esperado)
            )
    valores = [c[1] for c in ct]
    for grueso, fino in zip(valores, valores[1:]):
        razon = grueso / fino if fino else float("inf")
        if not 3.5 <= razon <= 4.5:
            fallos.append("CONTROL_NO_DECA_FACTOR_4: razon %.4f" % razon)

    impreso = veredicto(texto)
    if impreso is None:
        fallos.append("SIN_VEREDICTO: el crudo no cierra con VEREDICTO:")
    else:
        prefijo = "PASA EN ALGUNA RESOLUCION" if pasa else "NO PASA"
        sufijo = (
            "CONTROL NO DISCRIMINA"
            if any(c[3] == "NO DISCRIMINA" for c in ct)
            else "CONTROL DISCRIMINA"
        )
        recomputado = "%s / %s" % (prefijo, sufijo)
        if impreso != recomputado:
            fallos.append(
                "VEREDICTO_GLOBAL_NO_SE_RECOMPUTA: imprime %r y toca %r" % (impreso, recomputado)
            )
    return fallos


def inconsistencias_b2(texto):
    """Motor del benchmark 2: desviaciones y puertas recomputadas."""
    fallos = []
    ref = REF_B2.search(texto)
    umbrales = UMBRALES_B2.search(texto)
    if not ref or not umbrales:
        return ["B2_SIN_ENCABEZADO: falta REFERENCIA (13.3) o UMBRALES"]
    eps_ref, z0_ref = float(ref.group(1)), float(ref.group(2))
    umbral_z0, umbral_eeff = float(umbrales.group(1)), float(umbrales.group(2))

    medidos = {}
    for m in DESV_B2.finditer(texto):
        medidos[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    for nombre, referencia in (("eps_eff", eps_ref), ("Z0", z0_ref)):
        if nombre not in medidos:
            fallos.append("B2_SIN_MEDIDA: falta '>> %s'" % nombre)
            continue
        medido, desv = medidos[nombre]
        recom = abs(medido / referencia - 1.0)
        if abs(recom - desv) > TOL_DESV_REL:
            fallos.append(
                "DESV_NO_SE_RECOMPUTA: %s medido=%r ref=%r desv=%r y toca %.9e"
                % (nombre, medido, referencia, desv, recom)
            )

    puertas = {"1": ("Z0", umbral_z0), "2": ("eps_eff", umbral_eeff)}
    for numero in ("1", "2"):
        nombre, umbral = puertas[numero]
        m = re.search(r"C13\.%s \(.*?<= ([\d.eE+-]+).*?\): (PASA|FALLA)" % numero, texto)
        if not m:
            fallos.append("B2_SIN_PUERTA: falta C13.%s" % numero)
            continue
        if abs(float(m.group(1)) - umbral) > 1e-15:
            fallos.append(
                "B2_UMBRAL_DIVERGENTE: C13.%s declara %r y UMBRALES %r"
                % (numero, float(m.group(1)), umbral)
            )
        if nombre not in medidos:
            continue
        desv = medidos[nombre][1]
        esperado = "PASA" if desv <= umbral else "FALLA"
        if m.group(2) != esperado:
            fallos.append(
                "B2_PUERTA_NO_SE_RECOMPUTA: C13.%s desv=%r umbral=%r imprime %s y toca %s"
                % (numero, desv, umbral, m.group(2), esperado)
            )

    mov = [float(x) for x in MOV_B2.findall(texto)]
    puerta4 = PUERTA_B2.search(texto)
    if not mov or not puerta4:
        fallos.append("B2_SIN_C134: falta el control de dominio")
    else:
        umbral4 = float(puerta4.group(2))
        esperado = "PASA" if max(mov) <= umbral4 else "FALLA"
        if puerta4.group(3) != esperado:
            fallos.append(
                "B2_C134_NO_SE_RECOMPUTA: max movimiento_rel=%r umbral=%r imprime %s y toca %s"
                % (max(mov), umbral4, puerta4.group(3), esperado)
            )

    ccce = [float(x) for x in CCCE_B2.findall(texto)]
    c133 = C133_B2.search(texto)
    if len(ccce) < 2 or not c133:
        fallos.append("B2_SIN_C133: faltan las cifras |Cc/Ce-1|")
    else:
        max_nominal = max(ccce[:2])
        if abs(max_nominal - float(c133.group(1))) > 1e-18:
            fallos.append(
                "B2_C133_NO_ES_EL_MAX_NOMINAL: imprime %r y la malla nominal da %r"
                % (float(c133.group(1)), max_nominal)
            )

    resumen = RESUMEN_B2.search(texto)
    if not resumen or "eps_eff" not in medidos or "Z0" not in medidos:
        fallos.append("B2_SIN_RESUMEN: el resumen no repite las dos cifras")
    elif float(resumen.group(1)) != medidos["eps_eff"][0] or float(resumen.group(2)) != medidos["Z0"][0]:
        fallos.append(
            "B2_RESUMEN_DIVERGENTE: resumen (%s, %s) vs medido (%r, %r)"
            % (resumen.group(1), resumen.group(2), medidos["eps_eff"][0], medidos["Z0"][0])
        )
    return fallos


def cifra_readme(patron, texto):
    m = re.search(patron, texto)
    assert m, "README_SIN_CIFRA: no aparece /%s/" % patron
    return float(m.group(1))


# ---------------------------------------------------------------- portadores


def test_los_cinco_crudos_existen_y_no_estan_vacios():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA, CRUDO_B2, REF_B2_A, REF_B2_B):
        texto = leer(ruta)
        assert len(texto.splitlines()) > 20, "CRUDO_TRUNCADO: %s" % ruta


def test_el_barrido_tiene_tres_y_cinco_filas():
    sellado = [r["dx"] for r in filas(leer(CRUDO_SELLADO))]
    extra = [r["dx"] for r in filas(leer(CRUDO_EXTRA))]
    assert sellado == [0.001, 0.0005, 0.00025], "BARRIDO_SELLADO: %r" % sellado
    assert extra == [0.001, 0.0005, 0.00025, 0.000125, 6.25e-05], "BARRIDO_EXTRA: %r" % extra


def test_el_barrido_es_internamente_consistente():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        fallos = inconsistencias(leer(ruta))
        assert not fallos, "%s: %s" % (ruta.name, "; ".join(fallos))


def test_la_identidad_analitica_del_encabezado():
    sellado = leer(CRUDO_SELLADO)
    m = ANALITICO.search(sellado)
    assert m, "ANALITICO_AUSENTE"
    s11, s21, suma = float(m.group(1)), float(m.group(2)), float(m.group(3))
    assert abs(s11 - 1.0 / 3.0) < TOL_TEXTO, "|S11| analitico no es 1/3: %r" % s11
    assert abs(s21 - math.sqrt(8.0) / 3.0) < TOL_TEXTO, "|S21| analitico no es sqrt(8)/3: %r" % s21
    assert abs(suma - 1.0) < TOL_TEXTO, "unitariedad analitica != 1: %r" % suma
    assert abs(s11 ** 2 + s21 ** 2 - suma) < TOL_TEXTO, "la suma impresa no sale de |S11| y |S21|"


def test_las_celdas_por_lambda_se_recomputan():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        for fila in filas(leer(ruta)):
            assert abs(LAM0_M / fila["dx"] - fila["celdas_lam0"]) <= TOL_REDONDEO_DP1, (
                "CELDAS_LAMBDA: dx=%g imprime %r y lambda0/dx=%.4f"
                % (fila["dx"], fila["celdas_lam0"], LAM0_M / fila["dx"])
            )


def test_el_umbral_c11_es_unico_en_los_dos_crudos():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        umbrales = {round(c["C1.1"][1], 15) for c in criterios(leer(ruta)).values() if "C1.1" in c}
        assert len(umbrales) == 1, "UMBRAL_C11_NO_HOMOGENEO en %s: %r" % (ruta.name, umbrales)


def test_el_umbral_c11_es_el_del_readme():
    readme = leer(README)
    del_readme = cifra_readme(r"C11_TOL_ABS\s*=\s*([0-9.]+e[+-]?\d+)", readme)
    del_crudo = criterios(leer(CRUDO_SELLADO))[0.001]["C1.1"][1]
    assert del_readme == del_crudo, (
        "UMBRAL_DIVERGENTE: README dice %r y el crudo adjudica con %r" % (del_readme, del_crudo)
    )


def test_cuatro_mallas_fallan_y_el_readme_lo_dice():
    falla = [
        dx
        for dx, c in criterios(leer(CRUDO_EXTRA)).items()
        if c.get("C1.1", (0, 0, ""))[2] == "FALLA"
    ]
    assert len(falla) == 4, "MALLAS_QUE_FALLAN: %d (%r)" % (len(falla), sorted(falla))
    assert re.search(r"cuatro mallas nominales FALLAN", leer(README)), (
        "README_NO_DECLARA_EL_CONTEO: el crudo da %d mallas en FALLA" % len(falla)
    )


def test_el_cruce_cae_entre_dos_mallas_consecutivas():
    cs = criterios(leer(CRUDO_EXTRA))
    falla = sorted(dx for dx, c in cs.items() if c["C1.1"][2] == "FALLA")
    pasa = sorted(dx for dx, c in cs.items() if c["C1.1"][2] == "PASA")
    assert min(falla) == 0.000125, "FALLA_MAS_FINO: %r" % min(falla)
    assert max(pasa) == 6.25e-05, "PASA_MAS_GRUESO: %r" % max(pasa)
    assert min(falla) / max(pasa) == 2.0, "EL_CRUCE_NO_ES_UN_PASO_DE_REFINAMIENTO"
    readme = leer(README)
    assert re.search(r"1\.25e-4 m[`\s]*\(FALLA\)", readme), "README_SIN_EL_EXTREMO_QUE_FALLA"
    assert re.search(r"6\.25e-5 m[`\s]*\(PASA\)", readme), "README_SIN_EL_EXTREMO_QUE_PASA"


def test_la_malla_requerida_cae_en_el_cruce():
    readme = leer(README)
    declaradas = re.findall(r"dx ≤ ([0-9.]+e[-+]?\d+) m", readme)
    assert len(set(declaradas)) == 1, "MALLA_REQUERIDA_AMBIGUA: %r" % (declaradas,)
    requerida = cifra_readme(r"dx ≤ ([0-9.]+e[-+]?\d+) m", readme)
    cs = criterios(leer(CRUDO_EXTRA))
    falla = min(dx for dx, c in cs.items() if c["C1.1"][2] == "FALLA")
    pasa = max(dx for dx, c in cs.items() if c["C1.1"][2] == "PASA")
    assert pasa < requerida <= falla, (
        "MALLA_REQUERIDA_FUERA_DEL_CRUCE: %r no cae en (%r, %r] medido en %s"
        % (requerida, pasa, falla, CRUDO_EXTRA.name)
    )
    celdas = LAM0_M / requerida
    assert 355.0 <= celdas <= 365.0, "CELDAS_DECLARADAS_FALSAS: lambda0/dx = %.2f" % celdas
    assert abs(celdas - 360.0) <= 5.0, "CELDAS_DECLARADAS_FALSAS: %.2f vs 360" % celdas
    assert "360" in readme, "README_NO_DECLARA_LAS_CELDAS"


def test_el_control_decae_factor_4():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        valores = [c[1] for c in controles(leer(ruta))]
        for grueso, fino in zip(valores, valores[1:]):
            razon = grueso / fino
            assert 3.5 <= razon <= 4.5, "CONTROL_NO_DECA_FACTOR_4: %.4f en %s" % (razon, ruta.name)
    assert re.search(r"factor 4", leer(README)), "README_NO_DECLARA_EL_FACTOR"


def test_el_veredicto_de_cada_puerta_se_recomputa():
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        for dx, crits in criterios(leer(ruta)).items():
            for nombre, (medido, umbral, impreso) in crits.items():
                esperado = "PASA" if medido <= umbral else "FALLA"
                assert impreso == esperado, (
                    "%s: dx=%g %s medido=%r umbral=%r imprime %s y toca %s"
                    % (ruta.name, dx, nombre, medido, umbral, impreso, esperado)
                )


def test_el_veredicto_global_se_recomputa():
    readme = leer(README)
    for ruta in (CRUDO_SELLADO, CRUDO_EXTRA):
        texto = leer(ruta)
        cs = criterios(texto)
        pasa = any(c["C1.1"][2] == "PASA" for c in cs.values() if "C1.1" in c)
        prefijo = "PASA EN ALGUNA RESOLUCION" if pasa else "NO PASA"
        sufijo = (
            "CONTROL NO DISCRIMINA"
            if any(c[3] == "NO DISCRIMINA" for c in controles(texto))
            else "CONTROL DISCRIMINA"
        )
        assert veredicto(texto) == "%s / %s" % (prefijo, sufijo), (
            "VEREDICTO_GLOBAL: %s imprime %r" % (ruta.name, veredicto(texto))
        )
        assert veredicto(texto) in readme, "README_NO_CITA_EL_VEREDICTO: %r" % veredicto(texto)


def test_c12_pasa_desde_medio_milimetro():
    cs = criterios(leer(CRUDO_SELLADO))
    assert cs[0.001]["C1.2"][2] == "FALLA", "C12_DEBERIA_FALLAR_EN_MALLA_GRUESA"
    for dx in (0.0005, 0.00025):
        assert cs[dx]["C1.2"][2] == "PASA", "C12_DEBERIA_PASAR_EN_%g" % dx


def test_c13_y_c14_pasan_en_las_tres_mallas_selladas():
    cs = criterios(leer(CRUDO_SELLADO))
    assert len(cs) == 3, "MALLAS_SELLADAS: %d" % len(cs)
    for dx, crits in cs.items():
        assert crits["C1.3"][2] == "PASA", "C13_NO_PASA_EN_%g" % dx
        assert crits["C1.4"][2] == "PASA", "C14_NO_PASA_EN_%g" % dx


# ------------------------------------------------------------- benchmark 2


def test_la_referencia_hammerstad_esta_en_crudo_referencias_y_readme():
    ref_crudo = REF_B2.search(leer(CRUDO_B2))
    assert ref_crudo, "B2_SIN_REFERENCIA"
    eps, z0 = ref_crudo.group(1), ref_crudo.group(2)
    for ruta in (REF_B2_A, REF_B2_B):
        m = OBLIGACION.search(leer(ruta))
        assert m, "B2_SIN_OBLIGACION en %s" % ruta.name
        assert (m.group(1), m.group(2)) == (eps, z0), (
            "B2_OBLIGACION_DIVERGENTE en %s: %r" % (ruta.name, m.groups())
        )
    readme = leer(README)
    assert eps in readme, "README_SIN_EPS_DE_LA_REFERENCIA: %r" % eps
    assert z0 in readme, "README_SIN_Z0_DE_LA_REFERENCIA: %r" % z0


def test_la_primera_pasada_se_conserva_con_su_fallo():
    """El crudo de la primera pasada se conserva tal cual: cayo y no adjudica."""
    primera = leer(REF_B2_A)
    assert "Traceback (most recent call last)" in primera, "PRIMERA_PASADA_SIN_SU_FALLO"
    assert "TypeError: not all arguments converted" in primera, "PRIMERA_PASADA_SIN_LA_CAUSA"
    assert not re.search(r"^VEREDICTO:", primera, re.M), (
        "CORRIDA_CAIDA_ADJUDICA: un crudo con Traceback no puede firmar veredicto"
    )


def test_la_segunda_pasada_confirma_las_dos_magnitudes():
    segunda = leer(REF_B2_B)
    pares = COINCIDE.findall(segunda)
    assert len(pares) == 2, "REF_SIN_LAS_DOS_COINCIDENCIAS: %r" % (pares,)
    for magnitud, medido, obligacion in pares:
        assert medido == obligacion, "REF_NO_COINCIDE: %s" % magnitud
    assert re.search(r"^VEREDICTO: REFERENCIA CONFIRMADA", segunda, re.M), "REF_SIN_VEREDICTO"
    assert re.search(r"^FILAS MEDIDAS\s*: 2 magnitudes", segunda, re.M), "REF_SIN_CONTEO_DE_FILAS"


def test_el_crudo_b2_es_internamente_consistente():
    fallos = inconsistencias_b2(leer(CRUDO_B2))
    assert not fallos, "; ".join(fallos)


def test_el_umbral_de_eeff_del_readme_es_el_del_crudo():
    readme = leer(README)
    del_readme = cifra_readme(r"ERR_REL_EEFF_MAX`?\s*\|\s*`?([0-9.]+e[+-]?\d+)", readme)
    del_crudo = float(UMBRALES_B2.search(leer(CRUDO_B2)).group(2))
    assert del_readme == del_crudo, (
        "UMBRAL_EEFF_DIVERGENTE: README %r vs crudo %r" % (del_readme, del_crudo)
    )


def test_la_trampa_v_contra_v_esta_declarada():
    crudo = leer(CRUDO_B2)
    assert "TRAMPA (G13.4)" in crudo, "LA_TRAMPA_NO_SE_DECLARA"
    assert re.search(r"eps_eff = 1\.0 EXACTO", crudo), "LA_TRAMPA_NO_DECLARA_SU_CIFRA"


# ------------------------------------------------------------- falsificadores


def test_falla_cerrado_sin_crudo():
    inexistente = REG / "20261013" / "crudo_que_no_existe.txt"
    try:
        leer(inexistente)
    except FileNotFoundError as exc:
        assert "CRUDO_AUSENTE" in str(exc)
    else:
        raise AssertionError("LEE_UN_CRUDO_INEXISTENTE: el portador no existe y el test no fallo")


def test_el_verificador_sabe_fallar():
    """Falsificador propio: cada mutacion del crudo tiene que ser detectada."""
    texto = leer(CRUDO_EXTRA)
    assert not inconsistencias(texto), "el crudo sano no debe dar discrepancias"

    mutaciones = {
        "veredicto_mentido": texto.replace(
            "C1.1 medido |potencia-1|=0.000228884  umbral 1.0e-04  -> FALLA",
            "C1.1 medido |potencia-1|=0.000228884  umbral 1.0e-04  -> PASA",
        ),
        "residuo_mentido": texto.replace(
            "C1.1 medido |potencia-1|=0.000057201", "C1.1 medido |potencia-1|=0.000057901"
        ),
        "umbral_movido": texto.replace(
            "C1.1 medido |potencia-1|=0.000916794  umbral 1.0e-04",
            "C1.1 medido |potencia-1|=0.000916794  umbral 1.0e-03",
        ),
        "malla_del_cruce_movida": texto.replace("0.000125", "0.00015"),
        "control_mentido": texto.replace("0.010029", "0.004029"),
        "columna_potencia_mentida": texto.replace("1.00005720   -72.13", "1.00015720   -72.13"),
    }
    for nombre, mutado in mutaciones.items():
        assert mutado != texto, "MUTACION_NO_APLICADA: %s" % nombre
        cazado = inconsistencias(mutado)
        assert cazado, "MUTACION_NO_CAZADA: %s — el verificador no discrimina" % nombre
    assert inconsistencias(""), "CRUDO_VACIO_NO_CAZADO"


# ------------------------------------------------------------- testigo de claims
# HUELLA-RF-CLAIMS-WITNESS-20261020
#
# El claims.json deja de ser prosa: cada claim tiene que nombrar un portador que
# existe, una funcion de este modulo que lo lea, y una prosa que cita la cifra.
# Si alguno de los tres eslabones falta, el testigo falla cerrado.

CLAIMS = RAIZ / ".github" / "claims.json"
DERIVA = re.compile(r"^parser:(?P<ruta>[^:]+)::(?P<funcion>[A-Za-z_][A-Za-z0-9_]*)$")
CAMPOS_CLAIM = ("id", "afirma", "dato", "deriva", "polaridad", "prosa")


def cargar_claims(ruta=CLAIMS):
    """Lee el claims.json; si falta o no parsea, falla cerrado."""
    if not ruta.is_file():
        raise FileNotFoundError("CLAIMS_INVALIDO: falta %s" % ruta)
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError("CLAIMS_INVALIDO: %s no parsea (%s)" % (ruta.name, exc))


def portadores(dato):
    """Constantes de este modulo que fijan el portador declarado."""
    objetivo = (RAIZ / dato).resolve()
    return [n for n, v in globals().items() if isinstance(v, Path) and v.resolve() == objetivo]


def inconsistencias_claims(obj):
    """Devuelve las mentiras medibles del claims.json (vacio = contrato cumplido)."""
    fallos = []
    if not isinstance(obj, dict):
        return ["CLAIMS_INVALIDO: la raiz no es un objeto"]
    if obj.get("clase") != "A":
        fallos.append("CLAIMS_INVALIDO: clase %r no es mecanizable" % (obj.get("clase"),))
    lista = obj.get("claims")
    if not isinstance(lista, list) or not lista:
        return fallos + ["CLAIMS_VACIO: un claims.json sin claims no declara nada"]

    for i, c in enumerate(lista):
        faltan = [k for k in CAMPOS_CLAIM if not isinstance(c, dict) or not c.get(k)]
        if faltan:
            fallos.append("CLAIMS_INVALIDO: claim %d sin %s" % (i, ",".join(faltan)))
            continue
        nombre = c["id"]

        portador = RAIZ / c["dato"]
        fijado = portadores(c["dato"])
        if not portador.is_file() or not fijado:
            fallos.append(
                "DATO_SIN_PORTADOR: %s declara %s y no hay crudo ni constante que lo fije"
                % (nombre, c["dato"])
            )

        m = DERIVA.match(c["deriva"])
        funcion = globals().get(m.group("funcion")) if m else None
        if not m or m.group("ruta") != "tests/test_cifras_publicadas.py" or not callable(funcion):
            fallos.append(
                "PARSER_AUSENTE: %s deriva %r no nombra una funcion de este modulo"
                % (nombre, c["deriva"])
            )
        elif fijado and not any(p in inspect.getsource(funcion) for p in fijado):
            fallos.append(
                "DERIVACION_CIEGA: %s deriva en %s, que no lee %s"
                % (nombre, funcion.__name__, "/".join(fijado))
            )

        prosa = RAIZ / c["prosa"]
        if not prosa.is_file():
            fallos.append("PROSA_AUSENTE: %s cita %s" % (nombre, c["prosa"]))
        elif c["afirma"] not in prosa.read_text(encoding="utf-8"):
            fallos.append(
                "README_DESALINEADO: %s afirma %r y %s no lo dice" % (nombre, c["afirma"], c["prosa"])
            )
    return fallos


def test_el_claims_declara_solo_lo_que_el_parser_mide():
    """Portador real, derivacion nombrada que lo lee, prosa que cita la cifra."""
    fallos = inconsistencias_claims(cargar_claims())
    assert not fallos, "; ".join(fallos)


def test_el_testigo_de_claims_sabe_fallar():
    """Falsificador del testigo: cada mentira del claims.json tiene que ser cazada."""
    sano = cargar_claims()
    assert not inconsistencias_claims(sano), "EL_CLAIMS_SANO_YA_FALLA"

    def mutar(indice, campo, valor):
        copia = json.loads(json.dumps(sano))
        copia["claims"][indice][campo] = valor
        return copia

    mutaciones = {
        "DATO_SIN_PORTADOR": mutar(0, "dato", "registros/20261012/crudo_que_no_existe.txt"),
        "PARSER_AUSENTE": mutar(
            0, "deriva", "parser:tests/test_cifras_publicadas.py::test_que_no_existe"
        ),
        "DERIVACION_CIEGA": mutar(
            0,
            "deriva",
            "parser:tests/test_cifras_publicadas.py::test_la_trampa_v_contra_v_esta_declarada",
        ),
        "README_DESALINEADO": mutar(0, "afirma", "9.99e-9"),
    }
    for esperado, roto in mutaciones.items():
        cazado = inconsistencias_claims(roto)
        assert any(f.startswith(esperado + ":") for f in cazado), (
            "MUTACION_NO_CAZADA: %s — el testigo no discrimina (%r)" % (esperado, cazado)
        )

    vacio = {"clase": "A", "claims": []}
    assert any(f.startswith("CLAIMS_VACIO") for f in inconsistencias_claims(vacio)), (
        "CLAIMS_VACIO_NO_CAZADO"
    )
    assert any(f.startswith("CLAIMS_INVALIDO") for f in inconsistencias_claims({"clase": "B"})), (
        "CLASE_NO_MECANIZABLE_NO_CAZADA"
    )

    roto = Path("/tmp/rf_claims_roto.json")
    roto.write_text("{ esto no es json", encoding="utf-8")
    try:
        try:
            cargar_claims(roto)
        except ValueError as exc:
            assert "CLAIMS_INVALIDO" in str(exc), "CLAIMS_INVALIDO_SIN_CAUSA"
        else:
            raise AssertionError("CLAIMS_ROTO_PARSEA")
    finally:
        roto.unlink(missing_ok=True)
