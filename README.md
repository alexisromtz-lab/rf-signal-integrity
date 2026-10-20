# rf-signal-integrity — parámetros S y Z₀ con el umbral sellado *antes* de la primera cifra

> **EN —** RF signal integrity metrology: one solver, one Hammerstad reference, one sealed
> threshold (`C11_TOL_ABS = 1.0e-4`), and the verdicts **exactly as they came out** — including the
> ones that fail. The criterion that adjudicates never moved; when the mesh could not deliver, the
> **domain** was declared defective, not the criterion.

Este repositorio es un **pre-registro metrológico** y su evidencia. El archivo
[`PREREGISTRO_RF_SI_20261012.md`](PREREGISTRO_RF_SI_20261012.md) se sella **antes** de la primera
cifra: todo umbral y toda ventana quedan fijos ahí. Ninguna cifra de ese archivo se mueve después de
ver una salida.

```
T_UTC_SELLADO = 2026-10-12T16:46:49Z
SEED_COMMIT   = 4456a70d8851ddf8dfda6a0610841c1d834c7c1e
BLOB_PRE      = e69de29bb2d1d6434b8b29ae775ad8c2e48c5391   (blob vacío: el archivo no existía)
GATE_NOMINAL  = RC 0
CONTROLES     = blob_mal=12 · lineas_mal=15 · tupla_vacia=20 · sentinela_ausente=0
```

## Qué se mide

Cuatro piezas, declaradas como **objeto único medible** (§1 del pre-registro): el solucionador de
escalón en parámetros S, el microstrip 2D, la referencia analítica de Hammerstad, y los crudos de
cada corrida. Todo lo demás —narrativa, intención, calidad del código— **está excluido** por el
propio pre-registro.

## Criterios sellados

| criterio | umbral sellado | qué adjudica |
|---|---|---|
| `C1.1` | `C11_TOL_ABS = 1.0e-4` sobre el residuo `\|S11\|² + \|S21\|² − 1` | conservación de energía en el escalón |
| `C1.2` | — | pasa a partir de `0.5 mm` de malla |
| `C1.3`, `C1.4` | — | pasan en las tres mallas selladas |
| `ERR_REL_EEFF_MAX` | `2.0e-2` | error relativo de `eps_eff` contra Hammerstad |

Referencia con obligación de imprimir: `sim/ref_hammerstad.py` **debe** imprimir
`3.0437601569801833` y `72.522341968959097`. Si imprime otra cosa, la discrepancia **se declara y no
se adjudica**; la referencia no se mueve.

## Veredictos, tal como resultaron

- **Las cuatro mallas nominales FALLAN `C1.1`.** N4 declarado: el umbral `1.0e-4` **no se mueve**; el
  defecto es de **dominio** (dispersión numérica de la malla), no del criterio. La malla necesaria se
  declara aparte: `dx ≤ 8.25e-5 m` (~360 celdas/λ₀), y **no sustituye** al criterio.
- **Barrido sellado:** `VEREDICTO: NO PASA / CONTROL NO DISCRIMINA`.
- **Corrida extra:** `VEREDICTO: PASA EN ALGUNA RESOLUCION / CONTROL NO DISCRIMINA`. El pase **no** se
  obtiene aflojando el umbral: se obtiene sobre una malla declarada, con el umbral intacto. El cruce
  observado cae entre `1.25e-4 m` (FALLA) y `6.25e-5 m` (PASA), consistente con la malla requerida.
- **El control pierde potencia ~factor 4 por refinamiento** (misma ley que el residuo) ⇒ el sufijo
  `CONTROL NO DISCRIMINA` es correcto y se imprime **por resolución**, no sólo para la primera fila.

Esto es un control negativo publicado como resultado: el criterio se conserva, el instrumento se
declara mudo donde se vuelve mudo, y ninguna cifra se publica sin su comando.

## Mapa

```
PREREGISTRO_RF_SI_20261012.md        el sello: umbrales, ventanas, criterios, veredictos por corrida
sim/solver_escalon_s.py              solucionador de escalón en parámetros S
sim/b2_microstrip_2d.py              microstrip 2D
sim/ref_hammerstad.py                referencia analítica (obligación de impresión declarada)
registros/20261012/                  crudos sellados + el instrumento L128 (rf_b1_crudo_*)
registros/20261013/                  crudos b2 + las dos pasadas de la referencia Hammerstad
```

## Reproducir

```sh
python3 -B sim/ref_hammerstad.py                 # debe imprimir 3.0437601569801833 y 72.522341968959097
python3 -B sim/solver_escalon_s.py --help        # flags del solucionador (emite crudo con --json)
```

Los crudos de `registros/` son **capturas fechadas**: se conservan como se capturaron y no se
reeditan. Una cifra que no pueda diferir no es evidencia.

## Límites declarados

- El criterio `C1.1` **no pasa** en las mallas nominales: el repositorio publica el rojo, no lo
  maquilla.
- El control negativo **deja de discriminar** conforme la malla converge; se declara con su cifra.
- `dx ≤ 8.25e-5 m` es una **malla requerida declarada**, no medida todavía en esta pieza.

## Licencia y citación

MIT — ver [`LICENSE`](LICENSE). Al usar el solucionador, los crudos o su geometría, cite el artefacto
completo (`PREREGISTRO_RF_SI_20261012.md`) con su `T_UTC_SELLADO` y su `SEED_COMMIT`.

**Parte del archivo de instrumentos de [alexisromtz-lab](https://github.com/alexisromtz-lab)** — la
regla es la misma desde la física hasta el software: *un número que no puede diferir no es evidencia.*
