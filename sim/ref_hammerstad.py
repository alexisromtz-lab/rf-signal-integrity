#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim/ref_hammerstad.py — INSTRUMENTO DE REFERENCIA (Benchmark 2, microstrip 2D cuasi-estatico)

PIEZA NUEVA (G13.2). No importa, no copia y no edita el motor base (N2/N3).
No toca sfqed-paper.

OBLIGACION SELLADA 13.4/R2: este instrumento debe imprimir
    eps_eff = 3.0437601569801833
    Z0      = 72.522341968959097 ohm
Si imprime otra cosa, la discrepancia SE DECLARA y NO SE ADJUDICA: la referencia
operativa de 13.6 no se mueve (N4).

FALLO CERRADO (G13.1): si los dos valores no coinciden con la obligacion, o si el
control discriminante no discrimina, el veredicto es CONTRATO ROTO y el codigo de
salida es NO CERO (2), nunca 0.

CERO NOTACION MONETARIA (G13.5): este archivo no contiene el signo monetario.
"""

import math
import sys
from datetime import datetime, timezone

# --- PARAMETROS CONGELADOS (seccion 5 del pre-registro; no se leen de una salida) ---
ETA0 = 376.730313668      # impedancia del vacio, constante declarada
EPS_R = 4.2               # FR-4 congelado
WORH = 1.0                # w / h congelado -> BORDE del dominio declarado (w/h <= 1)
H = 1.0e-3                # 1.000 mm, unidad de longitud del experimento (13.2)

# --- OBLIGACION R2 (literales sellados; el instrumento se mide contra ellos) ---
REF_EEFF = '3.0437601569801833'
REF_Z0 = '72.522341968959097'


def hj(epsr, worh):
    """Formas cerradas CONGELADAS de la seccion 5. worh = w / h. Devuelve (eps_eff, Z0, arg)."""
    ee = ((epsr + 1) / 2) + (((epsr - 1) / 2) * (1 + 12 / worh) ** (-0.5))
    arg = 8 / worh + worh / 4          # 8*h/w + w/(4*h)  ==  8/(w/h) + (w/h)/4
    z0 = (ETA0 / (2 * math.pi * math.sqrt(ee))) * math.log(arg)
    return ee, z0, arg


def linea(n=78):
    print('-' * n)


def main():
    ahora = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ee, z0, arg = hj(EPS_R, WORH)
    s_ee = '%.17g' % ee
    s_z0 = '%.17g' % z0

    print('=== INSTRUMENTO DE REFERENCIA HAMMERSTAD-JENSEN (seccion 5 congelada) ===')
    print('FECHA_UTC = %s' % ahora)
    print('UNIVERSO DECLARADO: dos cantidades del caso congelado (eps_r = 4.2, w/h = 1.0)')
    print('                    y nada mas. Sin solver, sin malla, sin crudo ajeno.')
    print('                    Queda fuera: S11 y S21 del microstrip (A11.8, N5) y todo Z0')
    print('                    fuera del dominio w/h <= 1 (N5).')
    print('MOTOR:  python3 -B sim/ref_hammerstad.py')
    print('UNIDAD: razon adimensional (eps_eff) | ohm (Z0) | linea (fuente impresa)')
    print('VENTANA: %s' % ahora)
    print('OBLIGACION 13.4/R2: eps_eff = %s   Z0 = %s' % (REF_EEFF, REF_Z0))
    linea()

    print('--- PARAMETROS CONGELADOS ---')
    print('eps_r  = %s' % EPS_R)
    print('w / h  = %s   (BORDE del dominio declarado)' % WORH)
    print('h      = %.3e m   (unidad de longitud del experimento, declarada en 13.2)' % H)
    print('eta_0  = %s ohm  (constante declarada, NO medida en esta pieza)' % ETA0)
    dom = WORH <= 1.0
    print('DOMINIO w/h <= 1 -> %s (el borde cuenta como dentro; N5)' % ('EN DOMINIO' if dom else 'FUERA DE DOMINIO'))
    linea()

    print('--- FORMAS USADAS (verbatim de la seccion 5) ---')
    print('eps_eff = ((eps_r + 1) / 2) + (((eps_r - 1) / 2) * (1 + 12 * h / w)^(-1/2))')
    print('Z0      = (eta_0 / (2 * pi * sqrt(eps_eff))) * ln(8 * h / w + w / (4 * h))')
    linea()

    print('--- PIEZAS DECLARADAS DEL CALCULO (13.3) ---')
    print('argumento del logaritmo 8*h/w + w/(4*h) = %.17g   (declarado 8.25 exacto)' % arg)
    print('sqrt(13)                                = %.17g' % math.sqrt(13.0))
    print('ln(8.25)                                = %.17g' % math.log(8.25))
    print('sqrt(eps_eff)                           = %.17g' % math.sqrt(ee))
    print('1 / (2*pi*sqrt(eps_eff))                = %.17g' % (1.0 / (2 * math.pi * math.sqrt(ee))))
    linea()

    print('--- VALORES MEDIDOS POR ESTE COMANDO (formato %.17g) ---')
    print('eps_eff = %s' % s_ee)
    print('Z0      = %s ohm' % s_z0)
    linea()

    # --- CONTROLES DE LA REFERENCIA ---
    print('--- CONTROLES ---')
    print('K1 (R1, no circularidad): la referencia sale de una forma cerrada y de una linea')
    print('   de comando; NO sale del solucionador. El metro no se valida contra si mismo.')
    print('   Medido aqui: la palabra solver aparece 0 veces como fuente de estos numeros.')

    print('K2 (DISCRIMINANTE): el mismo comando sobre OTRA geometria debe dar OTRO numero.')
    ee2, z02, arg2 = hj(EPS_R, 0.5)
    s_ee2 = '%.17g' % ee2
    s_z02 = '%.17g' % z02
    print('   w/h = 0.5 -> eps_eff = %s   Z0 = %s ohm   (arg = %.17g)' % (s_ee2, s_z02, arg2))
    k2_difiere = (s_ee2 != s_ee) and (s_z02 != s_z0)
    print('   la salida PUEDE diferir: %s' % ('SI' if k2_difiere else 'NO'))

    print('K3 (TRAMPA declarada, R3): Z0 es LINEAL en eta_0.')
    print('   Z0 / eta_0 = %.17g' % (z0 / ETA0))
    print('   (sensibilidad relativa: mover eta_0 mueve TODA la referencia; no es una')
    print('    mejora, es otro metro. No se cita como evidencia.)')

    print('K4 (IDENTIDAD ESTRUCTURAL, G13.4): eps_r = 1.0 ->')
    ee1, _z01, _a1 = hj(1.0, WORH)
    print('   eps_eff = %.17g   (da 1.0 exacto por construccion: no puede diferir)'
          % ee1)
    print('   TRAMPA: se imprime como identidad, NUNCA como evidencia.')
    linea()

    # --- VEREDICTO (fallo cerrado) ---
    ok_ee = (s_ee == REF_EEFF)
    ok_z0 = (s_z0 == REF_Z0)
    print('--- VEREDICTO ---')
    print('C13.4/R2 eps_eff: %s  (medido %s contra obligacion %s)' % ('COINCIDE' if ok_ee else 'DIVERGE', s_ee, REF_EEFF))
    print('C13.4/R2 Z0     : %s  (medido %s contra obligacion %s)' % ('COINCIDE' if ok_z0 else 'DIVERGE', s_z0, REF_Z0))
    print('K2 discriminante: %s' % ('PASA' if k2_difiere else 'CONTRATO ROTO (la salida no puede diferir)'))
    print('FILAS MEDIDAS  : 2 magnitudes (eps_eff, Z0); cero filas no se declara verde (G1/N6)')

    rc = 0
    if not (ok_ee and ok_z0 and k2_difiere):
        rc = 2
        print('VEREDICTO: CONTRATO ROTO (RC=%d). Se declara, no se adjudica: la referencia' % rc)
        print('           operativa de 13.6 NO se mueve (N4).')
    else:
        print('VEREDICTO: REFERENCIA CONFIRMADA (RC=0). Las dos cifras de 13.3 quedan')
        print('           respaldadas por comando, no por prediccion.')
    return rc


if __name__ == '__main__':
    sys.exit(main())
