#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# b2_microstrip_2d.py -- driver 2D electrostatico del Benchmark 2 (microstrip cuasi-TEM).
# PIEZA NUEVA del frente Benchmark 2 (PREREGISTRO_RF_SI_20261012.md, seccion 13, G13.2).
# No edita ni reescribe el motor base de B1 (N2/N3): es pieza aparte.
#
# Objeto: SOLO dos cantidades, las de la seccion 13.1:
#   M1 = permitividad efectiva  eps_eff  (adimensional)
#   M2 = impedancia caracteristica Z0    (ohm)
# Extractor: metodo capacitivo de DOS corridas, congelado en 13.5.
#   C = Q / V  con V = 1.0 V ;  eps_eff = C_D / C_V ;  Z0 = 1 / (c0 * sqrt(C_V * C_D))
#   (L identica con y sin dielectrico: no hay material magnetico.)
# La carga Q sale del flujo por la cinta. Se imprime TAMBIEN la capacidad por energia
# (2W/V^2) como control de metodo C13.3: si las dos no coinciden, el emparejamiento de
# coeficientes del operador y del funcional esta roto.
#
# UNIVERSO DECLARADO: caja de calculo 20h x 20h (nominal, 13.5) y 40h x 40h (control de
#   dominio C13.4), con h = 1.000 mm, w/h = 1.0 exacto, eps_r = 4.2 (corrida D) contra
#   vacio eps_r = 1.0 (corrida V), sobre plano de masa Dirichlet.
# MOTOR: python3 -B + numpy (SOR de caja cuadrada, omega = 2/(1+sqrt(1-rho^2)),
#   rho = cos(pi/nc); barrido por paridad de (i+j); residuo L2 absoluto impreso).
# UNIDAD: F/m, adimensional, ohm, celda, s, linea, byte.
# VENTANA: se imprime al arrancar.

import math, sys, time
import numpy as np

C0   = 299792458.0
ETA0 = 376.730313668
EPS0 = 1.0 / (ETA0 * C0)
H    = 1.0e-3

REF_E  = 3.0437601569801833
REF_Z  = 72.522341968959097
ERR_REL_Z0_MAX   = 1.5e-2   # C13.1 (== C2.1 sellado, NO se mueve; 13.7)
ERR_REL_EEFF_MAX = 2.0e-2   # C13.2 (sello nuevo)
CTRL_METODO_MAX  = 1.0e-2   # C13.3
CTRL_CAJA_MAX    = 5.0e-3   # C13.4
TOL_RES          = 1.0e-12  # 13.5 (malla nominal)


def correr(nc, epsr, boxh, tol=TOL_RES, chk=100, maxbar=400000):
    L  = boxh * H
    dx = L / nc
    nd = nc + 1
    ncd = int(round(H / dx))          # celdas por h ; paso dx = h/ncd
    an  = ncd                         # w = h  -> w/dx = ncd
    jc  = ncd                         # cinta sobre y = h
    ic0 = nc // 2 - an // 2
    if ncd < 1:
        print("CONTRATO ROTO: dx > h"); sys.exit(2)
    eps_cell = np.where(np.arange(nc) < ncd, epsr, 1.0)
    ex  = np.empty(nd); ex[1:nc] = 0.5*(eps_cell[0:nc-1]+eps_cell[1:nc])
    ex[0] = eps_cell[0]; ex[nc] = eps_cell[nc-1]
    eyd = np.empty(nd); eyd[1:] = eps_cell[0:nc]; eyd[0] = eps_cell[0]
    eyu = np.empty(nd); eyu[0:nc] = eps_cell[:];  eyu[nc] = eps_cell[nc-1]
    i = np.arange(1, nc)
    I, J = np.meshgrid(i, i, indexing='ij')
    idx = (I*nd + J).ravel()
    par = ((I + J) % 2).ravel()
    nb = np.stack([(I-1)*nd+J, (I+1)*nd+J, I*nd+(J-1), I*nd+(J+1)], 0).reshape(4, -1)
    w  = np.stack([eyd[I], eyu[I], ex[I], ex[I]], 0).reshape(4, -1)
    s  = w.sum(0)
    dm = ((I == jc) & (J >= ic0) & (J <= ic0 + an)).ravel()
    ndir = int(dm.sum())
    if ndir < 1:
        print("CONTRATO ROTO: conjunto Dirichlet vacio (banda fuera de la caja)"); sys.exit(2)
    V = np.zeros(nd*nd); V[idx[dm]] = 1.0
    rho = math.cos(math.pi/nc)
    om  = 2.0/(1.0 + math.sqrt(1.0 - rho*rho))
    pA = (par == 0) & (~dm); pB = (par == 1) & (~dm)
    A = idx[pA]; B = idx[pB]
    nA = nb[:, pA]; nB = nb[:, pB]
    wA = w[:, pA];  wB = w[:, pB]
    sA = s[pA];     sB = s[pB]
    t0 = time.time(); it = 0; ra = float('nan')
    while it < maxbar:
        for _ in range(chk):
            it += 1
            V[A] = (1.0-om)*V[A] + om*(wA*V[nA]).sum(0)/sA
            V[B] = (1.0-om)*V[B] + om*(wB*V[nB]).sum(0)/sB
        d  = np.concatenate([V[A]-(wA*V[nA]).sum(0)/sA, V[B]-(wB*V[nB]).sum(0)/sB])
        ra = math.sqrt(float((d*d).sum()))
        if ra <= tol:
            break
    el = time.time() - t0
    V2 = V.reshape(nd, nd)
    qs = 0.0
    for c in range(ic0, ic0 + an + 1):
        qs += (eyd[jc]*(V2[jc, c]-V2[jc-1, c]) + eyu[jc]*(V2[jc, c]-V2[jc+1, c])
               + ex[jc]*(V2[jc, c]-V2[jc, c-1]) + ex[jc]*(V2[jc, c]-V2[jc, c+1]))
    dv  = V2[:, 1:] - V2[:, 0:-1]
    dhh = V2[1:, :] - V2[0:-1, :]
    W = 0.5*(float((ex[:, None]*dv**2).sum()) + float((eps_cell[:, None]*dhh**2).sum()))
    return dict(nc=nc, epsr=epsr, boxh=boxh, dx=dx, jc=jc, an=an, ic0=ic0, ndir=ndir,
                om=om, it=it, el=el, ra=ra, convergido=bool(ra <= tol),
                Vmax=float(V2.max()), nact=int(A.size+B.size), Cq=EPS0*qs, Ce=2.0*W*EPS0)


def imprime(tag, r):
    rel = abs(r['Cq']/r['Ce'] - 1.0)
    print("  [%s] nc=%d caja=%.0fh eps_r=%.1f dx=%.6e jc=%d an=%d ndir=%d om=%.8f" % (
        tag, r['nc'], r['boxh'], r['epsr'], r['dx'], r['jc'], r['an'], r['ndir'], r['om']))
    print("     celdas_activas=%d  iter=%d  reloj=%.2f s  Vmax=%.12f" % (
        r['nact'], r['it'], r['el'], r['Vmax']))
    print("     residuo_l2=%.6e  convergido=%s" % (r['ra'], r['convergido']))
    print("     C_charge =%.12e F/m   C_energia=%.12e F/m   |Cc/Ce-1|=%.3e" % (
        r['Cq'], r['Ce'], rel))
    if not r['convergido'] or rel > CTRL_METODO_MAX:
        print("     *** CONTRATO ROTO: residuo fuera de tolerancia o control de metodo fuera de C13.3 ***")


def par(V, D):
    ee = D['Cq'] / V['Cq']
    z0 = 1.0 / (C0 * math.sqrt(V['Cq'] * D['Cq']))
    return ee, z0


def main():
    print("FECHA_UTC = %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("MOTOR: python3 -B + numpy %s (SOR caja cuadrada)" % np.__version__)
    print("REFERENCIA (13.3): eps_eff=%.17g  Z0=%.17g" % (REF_E, REF_Z))
    print("UMBRALES: ERR_REL_Z0_MAX=%.3e  ERR_REL_EEFF_MAX=%.3e  CTRL_METODO_MAX=%.3e  CTRL_CAJA_MAX=%.3e" % (
        ERR_REL_Z0_MAX, ERR_REL_EEFF_MAX, CTRL_METODO_MAX, CTRL_CAJA_MAX))
    print("")

    print("=== MALLA NOMINAL (13.5): caja 20h x 20h, dx = h/40 = 25.0 um, nc = 800 ===")
    nV = correr(800, 1.0, 20.0)
    nD = correr(800, 4.2, 20.0)
    imprime("nominal-V", nV)
    imprime("nominal-D", nD)
    ee_n, z0_n = par(nV, nD)
    d_ee_n = abs(ee_n/REF_E - 1.0)
    d_z0_n = abs(z0_n/REF_Z - 1.0)
    print("  >> eps_eff = %.17g   desv_rel = %.6e" % (ee_n, d_ee_n))
    print("  >> Z0      = %.17g   desv_rel = %.6e" % (z0_n, d_z0_n))
    print("  C13.1 (Z0  <= %.1e): %s" % (ERR_REL_Z0_MAX, "PASA" if d_z0_n <= ERR_REL_Z0_MAX else "FALLA"))
    print("  C13.2 (eeff<= %.1e): %s" % (ERR_REL_EEFF_MAX, "PASA" if d_ee_n <= ERR_REL_EEFF_MAX else "FALLA"))
    print("")
    print("  TRAMPA (G13.4): corrida V contra V (eps_r=1 en ambas) da eps_eff = 1.0 EXACTO")
    print("                  por construccion. Una salida que no puede diferir no es evidencia.")
    print("")

    print("=== CONTROL DE DOMINIO C13.4: caja duplicada 40h x 40h, mismo dx = 25.0 um, nc = 1600 ===")
    bV = correr(1600, 1.0, 40.0)
    bD = correr(1600, 4.2, 40.0)
    imprime("doble-V", bV)
    imprime("doble-D", bD)
    ee_b, z0_b = par(bV, bD)
    m_ee = abs(ee_b/ee_n - 1.0)
    m_z0 = abs(z0_b/z0_n - 1.0)
    print("  >> eps_eff = %.17g   movimiento_rel = %.6e" % (ee_b, m_ee))
    print("  >> Z0      = %.17g   movimiento_rel = %.6e" % (z0_b, m_z0))
    print("  C13.4 (mov <= %.1e en cada magnitud): %s" % (
        CTRL_CAJA_MAX, "PASA" if (m_ee <= CTRL_CAJA_MAX and m_z0 <= CTRL_CAJA_MAX) else "FALLA"))
    print("")
    print("=== RESUMEN (las cinco cifras juntas, C13.5) ===")
    print("  C_V = %.12e F/m   C_D = %.12e F/m" % (nV['Cq'], nD['Cq']))
    print("  eps_eff = %.17g   Z0 = %.17g ohm" % (ee_n, z0_n))
    print("  residuo_Laplace = %.6e (V) / %.6e (D)" % (nV['ra'], nD['ra']))
    print("  C13.3 (|Cc/Ce-1| max) = %.3e   -> %s" % (
        max(abs(nV['Cq']/nV['Ce']-1), abs(nD['Cq']/nD['Ce']-1)),
        "PASA" if max(abs(nV['Cq']/nV['Ce']-1), abs(nD['Cq']/nD['Ce']-1)) <= CTRL_METODO_MAX else "FALLA"))
    ok = (d_z0_n <= ERR_REL_Z0_MAX and d_ee_n <= ERR_REL_EEFF_MAX
          and max(abs(nV['Cq']/nV['Ce']-1), abs(nD['Cq']/nD['Ce']-1)) <= CTRL_METODO_MAX
          and m_ee <= CTRL_CAJA_MAX and m_z0 <= CTRL_CAJA_MAX
          and nV['convergido'] and nD['convergido'])
    print("  VEREDICTO (C13.1 a C13.4 en la malla nominal): %s" % ("PASA" if ok else "NO PASA"))


if __name__ == "__main__":
    main()
