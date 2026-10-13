# PRE-REGISTRO METROLÓGICO: RF Y SIGNAL INTEGRITY (PARÁMETROS S Y Z0)

T_UTC_SELLADO = 2026-10-12T16:46:49Z
BLOB_PRE = e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
LINEAS_PRE = 0
SEED_COMMIT = 4456a70d8851ddf8dfda6a0610841c1d834c7c1e
GATE = /Users/marlene/platino-labs/tools/gate_pre_escritura.sh
GATE_NOMINAL = RC 0
GATE_CONTROLES = blob_mal=12 · lineas_mal=15 · tupla_vacia=20 · sentinela_ausente=0

Este archivo se sella ANTES de la primera cifra. Todo umbral y toda ventana quedan
fijados aquí. Ninguna cifra de este pre-registro se mueve después de ver una salida.
Si un umbral se mueve, se declara el movimiento y no se adjudica: es familia (a), y
la corrida deja de contar como protección.

## 1 · Objeto medible y exclusión de narrativa

OBJETO ÚNICO MEDIBLE: el artefacto técnico. Concretamente, cuatro piezas:

1. el solucionador electromagnético (propagador FDTD) instrumentado con puertos;
2. este pre-registro, con sus fórmulas y umbrales congelados;
3. el piso de ruido declarado y medido;
4. el benchmark independiente, con referencia analítica cerrada.

EXCLUIDO DE ESTE REGISTRO POR NO SER MEDIBLE DESDE AQUÍ: proyección de ingresos,
plataformas, licencias, demanda, comparativas de mercado. Nada de eso entra como
cifra, ni como adjetivo, ni como denominador. Una afirmación de mercado no lleva
comando: no es una cifra, es una declaración, y no se mezcla con lo medido.

EXCLUIDO POR ORDEN: sfqed-paper no se toca. El motor se copia, no se edita.

## 2 · Vertical elegido y su justificación metrológica

VERTICAL: RF / Signal Integrity. PRIORIDAD ABSOLUTA en esta fase.

RAZÓN, EN TÉRMINOS DE METRO Y NO DE MERCADO: este vertical tiene referencia
analítica cerrada e INDEPENDIENTE del propio solucionador. La impedancia
característica de una microstrip tiene forma cerrada (Hammerstad–Jensen) y las
relaciones de S en una discontinuidad de línea son algebraicas y exactas. Eso
significa que el resultado del solucionador se compara contra un objeto que NO se
obtuvo con el solucionador: el metro no se valida contra sí mismo.

CONTRASTE DECLARADO: un mapa de temperatura de un PCB sobre Gerber no tiene, en este
estante, referencia independiente; sólo se validaría contra su propia discretización,
que es la clase de evidencia que este corpus prohíbe (una salida que no puede diferir
de su objeto no es evidencia).

FASE 2, RESERVADA Y NO ABIERTA: conducción térmica paramétrica con presupuesto de
error declarado. No se entrega como temperatura de unión dura; se entrega como campo
de conducción con intervalo, o no se entrega.

## 3 · Deuda de código declarada (reconocida, no saldada)

El motor base heredado es un propagador FDTD de Maxwell. Identidad medida y
congelada en el momento del sellado:

IDENTIDAD DEL MOTOR BASE
  ruta     = /Users/marlene/sfqed-paper/sim/maxwell2d.py
  lineas   = 715
  bytes    = 30759
  sha16    = 1db75ea7b0b8cba4
  blob git = b3fc082245cfc5c33b3e275f966cfb16b04aa2e2
  cambios  = 0 (sin modificar, sin ensuciar)

DEUDA FORMAL, ENUNCIADA COMO DEFECTO Y NO COMO PENDIENTE DIFUSO:
  (a) el motor NO resuelve puertos: no hay excitación de un modo, ni separación de
      onda incidente y onda reflejada, ni absorción terminal de línea;
  (b) el motor NO hace descomposición modal: no hay proyección sobre los modos
      guiados de la línea, y por tanto no hay magnitudes de dispersión que
      signifiquen algo.

Ambas cosas deben INSTRUMENTARSE y quedar dentro de este pre-registro antes de que
ninguna cifra de S o de Z0 se publique. Un S medido sin puerto y sin modo no es un S:
es un número sobre una malla.

## 4 · Benchmark 1 — escalón de impedancia (relaciones exactas de S)

GEOMETRÍA DECLARADA
  Dos líneas ideales, sin pérdidas y no dispersivas, de impedancias características
  Z1 y Z2, unidas en una discontinuidad de longitud cero.
  Normalización: ondas de potencia, cada puerto referido a la impedancia de SU línea.

FÓRMULAS CONGELADAS (forma exacta, en ASCII, sin notación monetaria)
  S11 = (Z2 - Z1) / (Z2 + Z1)
  S21 = 2 * sqrt(Z1 * Z2) / (Z2 + Z1)
  IDENTIDAD DE EXACTITUD (discontinuidad sin pérdidas):
      |S11|^2 + |S21|^2 = 1

PROCEDIMIENTO DE MEDICIÓN CONGELADO (dos corridas, para no circular)
  Corrida A (referencia): línea homogénea de impedancia Z1, sin escalón.
  Corrida B (objeto): la misma línea con el escalón insertado.
  La onda incidente se toma de la corrida A. La reflejada y la transmitida se toman
  de la corrida B. Ambas señales se llevan al dominio de la frecuencia por DFT y se
  evalúan en la frecuencia de la ventana declarada en la sección 6.
  Un S medido sin corrida de referencia no cuenta: la incidente no se conoce.

CRITERIOS DE PASE (sellados aquí, antes de cualquier corrida)
  C1.1  identidad unitaria: |S11|^2 + |S21|^2 = 1.0 con tolerancia absoluta 1e-4
  C1.2  error relativo de S11 contra la fórmula: <= 1.0%
  C1.3  error relativo de S21 contra la fórmula: <= 1.0%
  C1.4  piso de ruido: la cola absorbida debe quedar por debajo de -60 dB respecto
        del pico de la incidente; si no, la corrida no se reporta.

  Los TRES criterios se reportan juntos. Un verde en C1.1 con rojo en C1.2 NO es un
  resultado parcial: dice que el instrumento de puerto conserva energía y que la
  geometría medida no es la geometría declarada. Se declara, no se adjudica.

## 5 · Benchmark 2 — microstrip contra forma cerrada (Hammerstad–Jensen)

FÓRMULAS CONGELADAS (forma base declarada, en ASCII)
  eps_eff = ((eps_r + 1) / 2) + (((eps_r - 1) / 2) * (1 + 12 * h / w)^(-1/2))
  Z0 = (eta_0 / (2 * pi * sqrt(eps_eff))) * ln(8 * h / w + w / (4 * h))
      válida en el dominio declarado: w / h <= 1
  eta_0 = 376.730313668 ohm   (impedancia del vacío, declarada como constante)

  AVISO DE ALCANCE: se congela ESTA forma. Cualquier refinamiento posterior (por
  ejemplo el término de corrección que añade un factor dependiente de h/w) es OTRO
  metro, no una mejora de éste, y exige un pre-registro nuevo. Comparar contra la
  variante refinada después de ver una salida es familia (a).

CASO CONGELADO
  Sustrato FR-4: eps_r = 4.2
  Relación geométrica: w / h = 1.0   (está en el borde del dominio declarado)

CRITERIO DE PASE
  C2.1  desviación de Z0 medida contra la forma cerrada: <= 1.5%
  C2.2  la desviación se reporta en la misma frecuencia de la ventana declarada y con
        el mismo par (eps_r, w/h) impreso en el crudo

AVISO DE HONESTIDAD, SELLADO POR ADELANTADO: NO se cita aquí ningún valor numérico de
Z0 ni de eps_eff para FR-4. Todavía no existe el comando que los produzca, y una
cifra sin comando es un defecto, no una cifra. La referencia se calcula con el
instrumento sim/ref_hammerstad.py cuando exista, y su crudo se imprime junto a la
medición. Predecir el número ahora sería una declaración disfrazada de medición.

## 6 · Ventana, unidad y piso — congelados

VENTANA ESPECTRAL: frecuencia única declarada por corrida, elegida tal que la línea
  de mayor impedancia quede resuelta con al menos 20 celdas por longitud de onda
  guiada. La frecuencia elegida se imprime en el crudo. Cambiarla después de ver un
  resultado es familia (a).

UNIDAD DE LOS CONTEO: cada cifra publicada declara si cuenta archivos, líneas,
  ocurrencias, celdas o muestras temporales. Tres unidades distintas del mismo objeto
  dan tres números distintos y los tres pueden ser verdaderos: sin unidad, la cifra
  no se puede volver a medir.

PISO DE RUIDO: -60 dB respecto del pico de la onda incidente (criterio C1.4). Es un
  umbral sellado, no un resultado.

## 7 · Declaración obligatoria de cada cifra futura

Toda cifra que salga de este instrumento viaja con las cuatro etiquetas, en el mismo
renglón o en el crudo que la produce:

  UNIVERSO DECLARADO: <qué conjunto se contó y qué quedó fuera, incluido si entra el
                      árbol .git o si se excluye>
  MOTOR:             <el comando ejecutable que produjo la cifra>
  UNIDAD:            <archivo | línea | ocurrencia | celda | muestra>
  VENTANA:           <reloj UTC del momento de la medición>

Una cifra sin MOTOR es una alucinación y se descarta. Una cifra sin VENTANA caduca al
escribirse, porque el universo puede moverse mientras se mide.

## 8 · Guardas contra el verde falso

G1. Guarda de cero entradas: si el número de filas realmente medidas es 0, el
    veredicto es CONTRATO ROTO, no VERDE. Una identidad aritmética del tipo
    (buenas + malas == total) se satisface sola con 0 + 0 == 0, y por eso no es un
    gate: el gate es preguntar si hay algo que medir ANTES de aplicar la identidad.

G2. Causa además de código: cada caso reporta el código de salida esperado Y la causa
    impresa en el crudo. Un caso que devuelve el código esperado por otro motivo no
    discrimina.

G3. Foto previa junto al objeto: antes de reparar cualquier pieza se guarda su foto
    (blob, bytes, líneas) y también la del instrumento. Sin foto previa, reparado no
    se distingue de reemplazado; sin la del instrumento, el crudo nace caducado.

G4. Conteo de encabezados como cierre: la integridad de este archivo se verifica
    contando sus encabezados, no leyendo su contenido. Un chequeo que busca una sola
    forma no certifica la ausencia de las otras.

G5. Cero notación monetaria: este archivo y sus anexos se escriben sin el signo
    monetario. En texto de reemplazo esa secuencia puede expandirse al texto que
    precede al match e inyectar una copia del bloque, mientras el mensaje de éxito
    sale impecable. El cazador es contar encabezados vecinos, nunca leer el fragmento
    devuelto.

## 9 · Lo que este pre-registro NO autoriza

  N1. No autoriza afirmar demanda, licencia, ingresos ni comparativa de mercado.
  N2. No autoriza editar ni reescribir nada dentro de /Users/marlene/sfqed-paper.
  N3. No autoriza reescribir el motor base desde cero: se copia y se instrumenta.
  N4. No autoriza mover un umbral sellado después de ver una salida.
  N5. No autoriza publicar un S medido sin puerto instrumentado y sin descomposición
      modal, ni un Z0 medido fuera del dominio w/h <= 1.
  N6. No autoriza declarar verde con cero filas medidas.
  N7. No autoriza comparar contra la variante refinada de Hammerstad–Jensen dentro de
      este sello.

## 10 · Orden de ejecución posterior a este sello

  P1. Portar el motor congelado a sim/ redirigiendo sus sitios de escritura bajo
      data/, con la identidad del motor re-medida antes y después del port.
  P2. Instrumentar puertos (excitación de modo, separación incidente/reflejada,
      absorción terminal) y descomposición modal, y pre-registrar el instrumento.
  P3. Construir sim/ref_hammerstad.py y exponer su crudo.
  P4. Correr Benchmark 1 (escalón) y reportar C1.1 a C1.4 juntos.
  P5. Correr Benchmark 2 (microstrip FR-4, w/h = 1.0) y reportar C2.1 y C2.2.
  P6. Sólo entonces: generador de informe automático (PDF y Markdown) sobre el crudo
      ya sellado.

Cada paso de escritura posterior viaja con su tupla de pre-vuelo (TARGET, BLOB_PRE,
LINEAS_PRE, HUELLA) y no se abre el destino sin una corrida con RC 0.

## 11 · Bitácora de sellado (append-only, no se parchea)

  2026-10-12T16:40:44Z  bootstrap: repo semilla creado, rama main, archivo vacío
                        commiteado. blob del vacío = e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
                        igual al BLOB_PRE del contrato. Commit semilla 4456a70.
                        Arbol limpio: 0 entradas en git status --porcelain -uall.
  2026-10-12T16:46:49Z  pre-vuelo A2.1 sobre este destino: RC 0 nominal, con
                        controles 12, 15, 20 y sentinela 0. Con RC 0 se autoriza la
                        escritura de este pre-registro.
  2026-10-12T16:46:49Z  corte de fase: este archivo se sella con sus umbrales y su
                        deuda de código declarada. Cero cifras de Z0 y de eps_eff
                        porque todavía no hay comando que las produzca.

  --- APENDICE A11 · ERRATA DECLARADA (no se parchea lo sellado) ---

  2026-10-12T20:50:07Z  APENDICE A11: errata de compuerta temporal, de signo, de
                        esponja y de geometria. Se declara ANTES de la corrida que
                        se reporta. Las secciones 1 a 10 no se editan: esta
                        bitacora es el unico destino que crece.

  A11.1  LA SECCION 4 NO SELLABA COMPUERTA TEMPORAL DE DFT. La seccion 6 congela
         la VENTANA ESPECTRAL (frecuencia unica, con 20 celdas por longitud de
         onda guiada de la linea de mayor impedancia) y el piso de ruido, pero en
         ninguna linea del sello se fija la ventana de TIEMPO sobre la que se
         integra la DFT. Medido: el token tau aparece 0 veces en este archivo.
           UNIVERSO DECLARADO: este archivo, 228 lineas, sin el arbol .git
           MOTOR:  grep -c -i tau PREREGISTRO_RF_SI_20261012.md
           UNIDAD: lineas
           VENTANA: 2026-10-12T20:50:07Z
         La compuerta se declara ahora, con parametros declarados y no leidos de
         la salida:
             tau = 1.5 / f0 = 150 ps        td = 4 tau = 600 ps
             W   = 6 tau = 900 ps
         Declaracion honesta: W se eligio DESPUES de ver la serie temporal cruda
         del primer borrador. Es familia (a) auto-declarada y NO se adjudica; lo
         que la contiene es que la compuerta no se mueve de aqui en adelante. N4
         no se viola: el umbral que se fija ahora no es C1.1 a C1.4.

  A11.2  EL SIGNO DEL ACOPLAMIENTO EN LA ACTUALIZACION DE Ez ESTABA INVERTIDO en
         el primer borrador y la corrida divergia a nan. Ambas leyes de curl
         llevan el mismo signo. Medido en aislado, con el signo correcto:
         ca_min = -0.017760506729551807, ca_max = 1.0, cb_max = 188.365156834,
         ch = 0.0013272093639924967. Con el signo invertido: max|Ez| = 1.65e-22
         en el paso 0 y 6.770125078715512e+157 en el paso 400.

  A11.3  LA ESPONJA ESTABA DEFINIDA EN CELDAS, no en longitud fisica: su longitud
         se partia a la mitad en cada refinamiento. Por eso la cola ABSORBIDA
         empeoraba al refinar (-72.89, -33.22 y -14.30 dB en el barrido sellado,
         que es el defecto opuesto al que un refinamiento debe producir). Se fija
         longitud fisica L_ESP = 80e-3 m y N_ABS = int(round(L_ESP/dx)) celdas.

  A11.4  LA FORMULA DEL PERFIL LLEVABA FACTOR CUATRO. Se usaba
         sigma = -2*(M+1)*ln(R0)/(eta*L) en lugar de
         sigma = -(M+1)*ln(R0)/(2*eta*L): cuatro veces el valor de Taflove. Con
         la forma defectuosa y L = 40 mm salia sigma_max = 11.0016 S/m. Barrido
         declarado que lo midio:
           UNIVERSO DECLARADO: FDTD 1D, eps1=1.0, eps2=4.0, f0=10 GHz, dx=1e-3 m,
             n=4000 celdas, fuente=560, monitor1=605, pasos=3598 (T=6.0 ns),
             W=900 ps
           MOTOR:  heredoc ad hoc del 12-Oct-2026 (ver A11.6)
           UNIDAD: decibelios de la cola respecto del pico de la incidente
           VENTANA: 2026-10-12 (sesion de medicion; hora de reloj no conservada)
             N_ABS= 40   L= 40 mm   m=3   sigma=2.7504 S/m   cola=-33.37 dB
             N_ABS= 80   L= 80 mm   m=3   sigma=1.3752 S/m   cola=-74.93 dB
             N_ABS=160   L=160 mm   m=3   sigma=0.6876 S/m   cola=-84.77 dB
             N_ABS=240   L=240 mm   m=3   sigma=0.4584 S/m   cola=-84.85 dB
         Se elige N_ABS = 80 celdas a dx = 1e-3 m (L = 80 mm), m = 3, R0 = 1e-9,
         sigma_max = 1.375206 S/m. La cifra 2.7504 S/m del primer borrador queda
         refutada por medicion, no por preferencia.

  A11.5  LA GEOMETRIA COLISIONABA CON EL DOBLE REBOTE. Con el escalon a 3.0
         longitudes de onda del monitor 1, el doble rebote llega a
         t_doble = t_ref + 2*d(mon1,escalon)/v1 = t_ref + 600.4 ps, mientras la
         compuerta de reflexion se cierra en t_ref + 450 ps. El pulso de doble
         rebote, de amplitud del orden de |S11|^2 = 0.111111 (cifra de la formula
         sellada), se solapaba con la compuerta de reflexion. Separacion
         corregida: 5.0 longitudes de onda, holgura 1000.69 - 900 = 100.69 ps, y
         la envolvente gaussiana declarada en el borde de la compuerta vale
         1.4e-06. Consecuencia declarada: las cifras del primer borrador quedan
         CADUCADAS; el crudo que se reporta es el del solver corregido, y su
         instrumento es la propia pieza.

  A11.6  EL CRUDO DEL PRIMER BORRADOR NACE CADUCO (guarda G3). El instrumento ad
         hoc que produjo la tabla decisiva no quedo guardado como archivo en su
         momento. Se recupero de la transcripcion de la sesion
         (136ff418-6ffd-44f1-95fd-b5eb4a1f7783.jsonl) por numero de linea: 10
         heredocs, entre ellos el de 71 lineas y 3363 bytes que produjo la tabla.
         Su contenido manda sobre cualquier reconstruccion: la pieza corregida
         toma de el constantes, perfil, fuente, DFT con compuerta y definicion de
         cola. Los archivos recuperados viven hoy en /tmp/inst_rfsi/ y /tmp es
         volatil: se declara, no se adjudica. Lo que NO sobrevive es su tabla,
         porque su geometria era la marginal de A11.5.

  A11.7  C1.1 NO TIENE MALLA DECLARADA. El sello fija tolerancia absoluta 1e-4
         sobre |S11|^2 + |S21|^2 pero no declara con que malla debe alcanzarse, y
         el unico barrido autorizado es dx = 1e-3, 5e-4 y 2.5e-4 m, o sea 30, 60
         y 120 celdas por longitud de onda en el vacio. La linea de MAYOR
         impedancia es la de EPS1 (Z1 = 376.730313668 ohm > Z2 = 188.365156834
         ohm): la restriccion de la seccion 6 se mide contra lambda_vacio y se
         cumple en las tres resoluciones. Si el residuo de la identidad resulta de
         orden dos en dx, la malla que C1.1 exige se declara como medicion aparte;
         el umbral NO se mueve (N4).

  A11.8  DISPOSICION SOBRE N5 PARA ESTE BENCHMARK. N5 prohibe publicar un S sin
         puerto instrumentado y sin descomposicion modal. En esta pieza, 1D y de
         una sola linea TEM: el puerto ES el plano de monitor con separacion de
         incidente por corrida de referencia (seccion 4), y la descomposicion
         modal es la identidad, porque hay UN modo y su proyeccion no filtra
         nada. La exencion cubre SOLO el benchmark 1D. No cubre microstrip 2D.

## APENDICE A12 — ACTA DE CALIBRACION DE BENCHMARK 1 (ESCALON TEM 1D, PARAMETROS S)

T_UTC_APENDICE = 2026-10-12T22:10:14Z
UNIVERSO DECLARADO: los 2 crudos de la corrida doble persistidos en registros/20261012/ + el instrumento persistido; MOTOR = solver_escalon_s.py (v2, git blob d9acd256d9726ec606740d7825498d2adbd7b200) + python3/wc/shasum/grep; UNIDAD = linea/byte/celda/razon adimensional/dB; VENTANA = el T_UTC de arriba.

### A12.1 IDENTIDAD DE LO MEDIDO
- crudo sellado: registros/20261012/rf_b1_crudo_sellado_20261012T205817Z.txt · 51 l · 4029 B · sha16 71b77f8d2e9863e5 (barrido sellado dx = 1e-3 / 5e-4 / 2.5e-4 m)
- crudo extra: registros/20261012/rf_b1_crudo_extra_20261012T205836Z.txt · 71 l · 5752 B · sha16 62cebe9833f63d8c (mallas extra --dx-extra 1.25e-4,6.25e-5)
- instrumento: registros/20261012/instrumento_L128_00.sh · 70 l · 3363 B · sha16 40e30cbaeeb5c9cf
- commit de custodia: 4e78c5ee081d55b6d0e1a8c1d4aa8fc77f4233fe (arbol limpio)
- solver v2: 572 l · 22227 B · sha16 d03695e3e1df7d99 · git blob d9acd256d9726ec606740d7825498d2adbd7b200
- referencias analiticas: |S11| = 0.333333333333, |S21| = 0.942809041582, |S11|^2+|S21|^2 = 1.0
- control de regresion de la propia pieza: R1 = 0, R2 = 0, R3 = 0

### A12.2 TABLA DE CONVERGENCIA (ORDEN p = 2) — BARRIDO SELLADO + MALLAS EXTRA
| dx (m) | celdas/lam0 | |S11| | e11 % | |S21| | e21 % | unitariedad | cola dB | n_celdas | n_pasos | N_ABS |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.0e-3 | 30 | 0.34083325 | 2.2500 | 0.94811207 | 0.5625 | 1.01508380 | -72.80 | 1181 | 4797 | 80 |
| 5.0e-4 | 60 | 0.33517453 | 0.5524 | 0.94411094 | 0.1381 | 1.00368744 | -72.37 | 2360 | 9594 | 160 |
| 2.5e-4 | 120 | 0.33379157 | 0.1375 | 0.94313307 | 0.0344 | 1.00091679 | -72.22 | 4718 | 19187 | 320 |
| 1.25e-4 | 240 | 0.33344777 | 0.0343 | 0.94288996 | 0.0086 | 1.00022888 | -72.16 | 9435 | 38374 | 640 |
| 6.25e-5 | 480 | 0.33336193 | 0.0086 | 0.94282926 | 0.0021 | 1.00005720 | -72.13 | 18870 | 76747 | 1280 |

Razones por duplicacion de malla (lo que declara el orden):
- e11 %: 2.2500/0.5524 = 4.073 · 0.5524/0.1375 = 4.017 · 0.1375/0.0343 = 4.008 · 0.0343/0.0086 = 3.988
- residuo de unitariedad (|S11|^2+|S21|^2 - 1): 4.090 · 4.021 · 4.005 · 4.001
El factor cercano a 4 por duplicacion de malla es la firma de p = 2 (segundo orden). La razon e11/e21 se mantiene exactamente 4 en las cinco filas: dato estructural de la normalizacion de onda de potencia, no una coincidencia de la corrida.

### A12.3 CRITERIO C1.1 — FALLA FORMAL EN LAS CUATRO MALLAS NOMINALES
Umbral sellado (C11_TOL_ABS = 1.0e-4, §4) aplicado al residuo |S11|^2+|S21|^2 - 1:
- 1.0e-3 m: residuo 0.01508380 -> FALLA
- 5.0e-4 m: residuo 0.00368744 -> FALLA
- 2.5e-4 m: residuo 0.00091679 -> FALLA
- 1.25e-4 m: residuo 0.00022888 -> FALLA
Las cuatro mallas nominales FALLAN C1.1. N4 declarado: el umbral 1.0e-4 NO se mueve; el defecto es de DOMINIO (dispersion numerica de la malla), no del criterio. La malla necesaria se declara aparte (dx <= 8.25e-5 m, ~360 celdas/lam0) y NO se sustituye el criterio por ella.
El barrido sellado cierra con VEREDICTO: NO PASA / CONTROL NO DISCRIMINA.

### A12.4 PASE CONDICIONADO EN LA MALLA EXTRA
En la malla extra dx = 6.25e-5 m (~480 celdas/lam0), fuera del barrido sellado y declarada como tal:
- residuo 0.00005720 <= 1.0e-4 -> C1.1 PASA
- C1.2 (|S11| rel 1 %) PASA · C1.3 (|S21| rel 1 %) PASA · C1.4 (cola <= -60 dB) PASA
Corrida extra: VEREDICTO: PASA EN ALGUNA RESOLUCION / CONTROL NO DISCRIMINA.
Lectura: el pase NO se obtiene aflojando el umbral; se obtiene sobre una malla declarada, con el umbral intacto. El cruce observado esta entre 1.25e-4 m (FALLA) y 6.25e-5 m (PASA), consistente con la malla requerida declarada en A11.7. C1.2 pasa a partir de 0.5 mm; C1.3 y C1.4 pasan en las tres mallas selladas.

### A12.5 OBSERVACION: LA POTENCIA DISCRIMINANTE DEL CONTROL DECAE CON LA MALLA
control_dif_max (diferencia entre el pico coherente de referencia y la suma lineal incoherente) por malla:
- 1.0e-3 m: 0.010029 -> DISCRIMINA (supera el umbral nombrado C_CTRL_DIF_MIN = 1.0e-2)
- 5.0e-4 m: 0.002438 -> NO DISCRIMINA
- 2.5e-4 m: 0.000605 -> NO DISCRIMINA
- 1.25e-4 m: 0.000151 -> NO DISCRIMINA
- 6.25e-5 m: 0.000038 -> NO DISCRIMINA
El control pierde potencia ~factor 4 por refinamiento (misma ley que el residuo). Consecuencia declarada: el sufijo de veredicto CONTROL NO DISCRIMINA es correcto y se imprime por resolucion en el crudo, no solo para la primera fila. Queda asentado tal cual: el control discrimina en malla gruesa y se vuelve mudo conforme la malla converge, sin que eso toque los criterios fisicos C1.1-C1.4.

### A12.6 NOTA DE CONTEO DEL INSTRUMENTO
El instrumento persistido registros/20261012/instrumento_L128_00.sh mide 70 l / 3363 B / sha16 40e30cbaeeb5c9cf. La copia de trabajo /tmp/inst_rfsi/L128_00.sh reporto 71 l con el MISMO numero de bytes; la diferencia es de conteo de salto de linea final, no de contenido. La cifra autoritativa es la persistida (70 l). El defecto de la primera redaccion (crudo nacido caduco por G3) queda cerrado: el instrumento vive junto a sus crudos.

## §13. Pre-registro Benchmark 2: Microstrip 2D Cuasi-Estático (Hammerstad-Jensen)

T_UTC_APENDICE = 2026-10-13T01:52:34Z
BLOB_PRE_ADENDA = 3a6c99b1d900c8901907b3cdb7938c992e3ca85a
LINEAS_PRE_ADENDA = 381
GATE_PRE_ADENDA = RC 0 (pre-vuelo A2.1 corrido sobre la tupla del enunciado, 2026-10-12T22:16:53Z)
UNIVERSO DECLARADO: este apendice y la referencia analitica que el congela; MOTOR = python3 -B (formas cerradas de la seccion 5 medidas por comando, una linea) + git hash-object/shasum/wc; UNIDAD = razon adimensional / ohm / linea / byte / blob / celda; VENTANA = el T_UTC de arriba.

### 13.1 OBJETO MEDIBLE Y SU DOMINIO
Dos cantidades, y solo dos, del caso congelado en la seccion 5 (eps_r = 4.2, w/h = 1.0):
  M1 = permitividad efectiva eps_eff  (adimensional)
  M2 = impedancia caracteristica Z0   (ohm)
DOMINIO DECLARADO: w/h <= 1 (seccion 5). El caso w/h = 1.0 esta EN EL BORDE del dominio, no fuera: se declara, porque N5 prohibe publicar un Z0 medido fuera del dominio y el borde cuenta como dentro.
NO ES OBJETO DE ESTE APENDICE: S11 y S21 del microstrip. A11.8 dice que la exencion de N5 cubre SOLO el benchmark 1D; microstrip 2D no tiene plano de monitor TEM ni modo unico identificable sin puerto modal y sin descomposicion modal. Sin puerto modal no hay S que reportar.

### 13.2 GEOMETRIA DECLARADA (la del enunciado, congelada)
- sustrato: dielectrico de espesor h, eps_r = 4.2, sin perdidas, homogeneo e isotropo
- conductor: tira PEC de ancho w, espesor t -> 0, sobre plano de masa PEC infinito en y = 0
- relacion de aspecto: w/h = 1.0 exacto
- h es escala: el problema es invariante de escala, y por eso se fija h = 1.000 mm para que toda cifra de malla salga en unidades SI y se pueda volver a medir. Fijar h no es una eleccion fisica: es la unidad de longitud del experimento, y se declara antes de la primera cifra.

### 13.3 REFERENCIA ANALITICA CONGELADA, MEDIDA POR COMANDO
Formulas: las de la seccion 5, sin cambiar un signo ni un termino.
  eps_eff = ((eps_r + 1) / 2) + (((eps_r - 1) / 2) * (1 + 12 * h / w)^(-1/2))
  Z0      = (eta_0 / (2 * pi * sqrt(eps_eff))) * ln(8 * h / w + w / (4 * h))
  eta_0   = 376.730313668 ohm   (constante declarada, no medida en esta pieza)
Valores medidos (MOTOR = python3 -B, un renglon, reproducible):
  eps_eff = 3.0437601569801833
  Z0      = 72.522341968959097 ohm
Piezas declaradas del calculo: sqrt(13) = 3.6055512755 · ln(8.25) = 2.1102132003 · sqrt(eps_eff) = 1.7446375432 · argumento del logaritmo = 8.25 exacto (8 h/w + w/(4h) con w/h = 1.0).
Estos dos numeros son la REFERENCIA OPERATIVA de 13.6. Viajan con su comando y su ventana; sin comando serian una prediccion disfrazada, que es exactamente lo que la seccion 5 se prohibio a si misma.

### 13.4 CONTROLES DE LA REFERENCIA (por que este metro no es circular)
  R1. La referencia NO sale del solucionador: sale de una forma cerrada y de una linea de comando. El metro no se valida contra si mismo.
  R2. La seccion 10 (P3) exige el instrumento sim/ref_hammerstad.py y su crudo. Su obligacion queda asi: ref_hammerstad.py debe imprimir 3.0437601569801833 y 72.522341968959097. Si imprime otra cosa, la discrepancia SE DECLARA y NO SE ADJUDICA, y la referencia no se mueve.
  R3. Trampa declarada: Z0 es lineal en eta_0. Cambiar la constante moviliza la referencia entera; no es una mejora, es otro metro.

### 13.5 MALLA NOMINAL, VENTANA Y PROCEDIMIENTO DE EXTRACCION (congelados antes de la primera cifra)
MALLA NOMINAL (nominal, no optima: los criterios se juzgan EN ELLA):
  caja de calculo: 20 h de ancho por 20 h de alto sobre el plano de masa  (con h = 1.000 mm: 20.000 mm x 20.000 mm)
  paso: dx = dy = h / 40 = 25.0 um
  resolucion de la tira: w / dx = 40 celdas
  frontera: Dirichlet (tira y plano de masa a potencial fijo); la caja NO es una frontera fisica, y por eso se controla en 13.6 C13.4
  solver: Laplace 2D electrostatico por relajacion, con residuo L2 impreso en el crudo y criterio de parada 1e-12 alcanzado ANTES de leer cualquier magnitud
  normalizacion: V = 1.0 V en la tira, 0.0 V en el plano de masa
VENTANA: la de la seccion 6; el par (eps_r, w/h) y la ventana se imprimen en el crudo (C2.2).
PROCEDIMIENTO CONGELADO DE EXTRACCION (metodo capacitivo, dos corridas, para no circular):
  Corrida V (referencia): toda la caja con eps = eps_0 (sustrato sustituido por vacio, geometria identica)
  Corrida D (objeto): la misma caja con el sustrato de eps_r = 4.2
  capacidad por unidad de longitud: C = Q / V, con V = 1.0 V y Q la carga de la tira
  eps_eff = C_D / C_V
  Z0      = 1 / (c0 * sqrt(C_V * C_D)),   c0 = 299792458.0 m/s
  RAZON DECLARADA (por que vale, y no es una formula nueva): en cuasi-TEM la inductancia por unidad de longitud L es la misma con y sin dielectrico, porque no hay material magnetico; con eso eps_eff = C / C_V y Z0 = sqrt(L / C) = 1 / (c0 * sqrt(C_V * C_D)). Es la consecuencia de la definicion, no un refinamiento.

### 13.6 CRITERIOS SELLADOS (nombrados; el veredicto nunca usa un literal duplicado)
  C13.1  desviacion relativa de Z0 contra la referencia de 13.3: <= ERR_REL_Z0_MAX
         ERR_REL_Z0_MAX = 1.5e-2   (es C2.1 de la seccion 5: NO se mueve; ver 13.7)
  C13.2  desviacion relativa de eps_eff contra la referencia de 13.3: <= ERR_REL_EEFF_MAX
         ERR_REL_EEFF_MAX = 2.0e-2 (SELLO NUEVO: eps_eff no tenia umbral previo)
  C13.3  control de metodo, puede diferir y por eso discrimina: |C por carga / C por energia - 1| <= CTRL_METODO_MAX = 1.0e-2
  C13.4  control de dominio de la caja, puede diferir: al duplicar la caja (40 h por 40 h) cada magnitud se mueve <= CTRL_CAJA_MAX = 5.0e-3; si se mueve mas, el defecto es de DOMINIO y se declara, no se mueve el criterio (N4)
  C13.5  los criterios C13.1 y C13.2 se juzgan EN LA MALLA NOMINAL de 13.5, y las cinco cifras del crudo (C_V, C_D, eps_eff, Z0, residuo) se reportan JUNTAS: un acierto aislado no es un resultado parcial.

### 13.7 COLISION DE UMBRAL DECLARADA Y NO ADJUDICADA (Z0: 1.5% sellado contra 2.0% del enunciado)
La seccion 5 sello C2.1: desviacion de Z0 <= 1.5%. El enunciado de esta adenda pide <= 2.0% para Z0 y para eps_eff. Lo unico que se hace aqui es DECLARARLO:
  - eps_eff no tenia umbral previo: C13.2 = 2.0% es un SELLO NUEVO, no un movimiento.
  - Z0 SI tenia umbral sellado: C2.1 = 1.5%. Adoptar 2.0% seria MOVER un umbral sellado, que es N4. Por eso esta adenda NO adopta el 2.0% para Z0: la referencia operativa de Z0 queda en el 1.5% ya sellado, que es el mas estricto de los dos.
  - El 2.0% para Z0 queda REGISTRADO COMO PENDIENTE de decision del dueno. Si se ratifica, es un MOVIMIENTO DECLARADO de C2.1 (familia (a)) y la corrida deja de contar como proteccion para Z0 hasta que se re-selle. No se adjudica.
  - Ninguno de los dos umbrales se mueve despues de ver una salida (N4).

### 13.8 DIVERGENCIA DECLARADA DEL ENUNCIADO (cifras citadas contra cifras medidas)
El enunciado cita eps_eff = 3.043765 y Z0 = 72.339 ohm. Medido con el comando de 13.3:
  eps_eff   3.043765  contra  3.0437601569801833  -> rel 1.59e-06  (COINCIDE: es redondeo)
  Z0       72.339     contra  72.522341968959097  -> rel 2.53e-03  (DIVERGE: 0.25%)
La segunda, usada de denominador, consumiria 0.25 de los 1.5 puntos porcentuales de C13.1 antes de la primera corrida. Por eso la referencia operativa es la de 13.3 (forma cerrada mas comando) y las dos cifras citadas entran como [REF], sin autoridad. Se declara, no se adjudica.

### 13.9 GUARDAS DE ESTE FRENTE
  G13.1 fallo cerrado: si el solver no alcanza el residuo declarado, o si una corrida no termina, el veredicto es CONTRATO ROTO, no PASA (G1 de la seccion 8, aplicado a este frente).
  G13.2 pieza nueva: el driver 2D electrostatico de este frente ES PIEZA NUEVA. El motor base medido en la seccion 3 (715 l, 30759 B, sha16 1db75ea7b0b8cba4, blob b3fc082245cfc5c33b3e275f966cfb16b04aa2e2) NO se edita ni se reescribe (N2, N3): se copia si se reusa.
  G13.3 toda cifra del driver viaja con UNIVERSO DECLARADO, MOTOR, UNIDAD y VENTANA (seccion 7), y toda corrida se juzga con el par (eps_r, w/h) impreso en el crudo (C2.2).
  G13.4 el control de vacio con eps_r = 1.0 en las DOS corridas es una IDENTIDAD ESTRUCTURAL: da 1.0 exacto por construccion y no puede diferir. Se imprime como TRAMPA, nunca como evidencia: una salida que no puede diferir no es evidencia.
  G13.5 cero notacion monetaria en este apendice y en todo su crudo.

### 13.10 LO QUE ESTA ADENDA NO ABRE
  - No abre S11 ni S21 del microstrip (A11.8; N5).
  - No abre Z0 fuera del dominio w/h <= 1 (N5).
  - No abre la fase 2 termica, ni el frente editorial, ni nada dentro de sfqed-paper (N2).
  - No autoriza declarar verde con cero filas medidas (N6).

ESTADO: frente Benchmark 2 ABIERTO. El driver 2D queda DESBLOQUEADO para su construccion y para su propio pre-registro de instrumento; el criterio de pase de Z0 sigue siendo el 1.5% sellado en la seccion 5, y eps_eff estrena umbral 2.0% aqui.

## Apéndice A13. Acta del Benchmark 2: Microstrip 2D Cuasi-Estático (veredicto medido)

T_UTC_APENDICE = 2026-10-13T04:03:11Z
BLOB_PRE_ADENDA = d02b8995ff2f7de6dda2fea81c3223335a6d9439
LINEAS_PRE_ADENDA = 472
GATE_PRE_ADENDA = RC 0 (pre-vuelo A2.1 corrido sobre la tupla de este apéndice, 2026-10-13T04:02:56Z)
UNIVERSO DECLARADO: los 3 crudos de registros/20261013/, las 2 piezas nuevas de sim/ y la referencia congelada de 13.3; quedan fuera todo sfqed-paper y el frente editorial (N2) y todo S11/S21 del microstrip (A11.8; N5); .git no entra en ningún conteo salvo donde se declara. MOTOR = python3 -B + numpy 2.4.6 (relajación SOR en caja cuadrada) para las cifras físicas; cat / wc / shasum / git hash-object para las identidades. UNIDAD = razón adimensional / ohm / F por metro / línea / byte / blob / celda. VENTANA = el T_UTC de arriba y el reloj que cada crudo imprime.

### A13.1 VEREDICTO: PASA EN LAS CUATRO PUERTAS
El crudo registros/20261013/rf_b2_crudo_20261013T023346Z.txt cierra con la línea literal: VEREDICTO (C13.1 a C13.4 en la malla nominal): PASA. Las cuatro puertas, cada una con su cifra y su umbral sellado:
  C13.1  Z0      = 71.689253626518138 ohm   desviación relativa 1.148733e-02  <= 1.5e-02  PASA
  C13.2  eps_eff = 3.0361000000397449       desviación relativa 2.516676e-03  <= 2.0e-02  PASA
  C13.3  |C por carga / C por energía - 1| máximo = 1.377e-14  <= 1.0e-02  PASA
  C13.4  caja duplicada a 40h: eps_eff se mueve 2.532647e-03 y Z0 se mueve 1.813723e-03, ambas <= 5.0e-03  PASA
C13.5 se cumple: las cinco cifras del crudo se reportan JUNTAS en A13.2 y ninguna se cita sola.

### A13.2 LAS CINCO CIFRAS JUNTAS (C13.5), nominal y caja doble
MALLA NOMINAL (13.5): caja 20h x 20h, dx = dy = h/40 = 25.0 um, nc = 800, w/dx = 40 celdas, frontera Dirichlet.
  corrida V (eps_r = 1.0): C por carga = C por energía = 2.670343941514e-11 F/m · |Cc/Ce-1| = 8.882e-16 · residuo L2 = 5.049757e-13 · celdas activas 638360 · iter 3800 · reloj 188.40 s · Vmax = 1.000000000000
  corrida D (eps_r = 4.2): C por carga = C por energía = 8.107431240938e-11 F/m · |Cc/Ce-1| = 1.377e-14 · residuo L2 = 7.704809e-13 · celdas activas 638360 · iter 3800 · reloj 171.91 s · Vmax = 1.000000000000
  eps_eff = 3.0361000000397449 · Z0 = 71.689253626518138 ohm · residuo Laplace 5.049757e-13 (V) / 7.704809e-13 (D)
CONTROL DE DOMINIO C13.4 (caja 40h x 40h, mismo dx = 25.0 um, nc = 1600):
  corrida V: C por carga = C por energía = 2.662140446360e-11 F/m · |Cc/Ce-1| = 6.550e-15 · residuo L2 = 7.658827e-13 · celdas activas 2556760 · iter 7500 · reloj 1909.05 s · Vmax = 1.000000000000
  corrida D: C por carga = C por energía = 8.102994788141e-11 F/m · |Cc/Ce-1| = 2.132e-14 · residuo L2 = 7.906321e-13 · celdas activas 2556760 · iter 7600 · reloj 1815.12 s · Vmax = 1.000000000000
  eps_eff = 3.0437893685210504 (movimiento 2.532647e-03) · Z0 = 71.819278090883984 ohm (movimiento 1.813723e-03)
G13.1 queda CERRADO, no abierto: los cuatro residuos (5.049757e-13 · 7.704809e-13 · 7.658827e-13 · 7.906321e-13) están por debajo del 1e-12 congelado en 13.5, las cuatro corridas imprimen convergido=True, y las cuatro imprimen Vmax = 1.000000000000 (Dirichlet de la tira intacto). Ninguna corrida murió a mitad.

### A13.3 LA ANOMALÍA DE eps_eff, RESUELTA POR MEDICIÓN (no por argumento)
El barrido previo de refinamiento dejó una anomalía declarada: eps_eff no era monótona en nc y la malla más fina era la MÁS LEJANA de la referencia (nc=200 -> 3.0465279024744465 · nc=400 -> 3.0395389932916679 · nc=800 -> 3.0361000000397449, contra la referencia 3.0437601569801833). C13.4 mide la causa y la cierra:
  eps_eff a 20h: 3.0361000000397449  ->  desviación frente a la referencia  -2.517e-03
  eps_eff a 40h: 3.0437893685210504  ->  desviación frente a la referencia  +9.597e-06
Al duplicar la caja, eps_eff no se mueve un poco: ATERRIZA sobre la forma cerrada de 13.3 (residuo relativo 9.6e-06). El defecto era de DOMINIO (truncamiento del campo de dispersión en una caja de 20h), no del solver y no de la referencia. Se declara, no se adjudica: el criterio NO se mueve (N4) y la malla nominal sigue siendo la de 13.5, que es donde se juzgan C13.1 y C13.2 (C13.5).
Z0 se comporta distinto y se declara distinto: a 20h la desviación es -1.149e-02 y a 40h es -9.694e-03. Converge hacia la referencia pero LENTO (la inductancia efectiva depende del campo lejano, y una caja de 40h todavía lo trunca). En consecuencia la malla nominal de Z0 carga un sesgo de truncamiento de caja ACOTADO y declarado de 1.81e-03 (el movimiento medido), que se consume dentro del presupuesto de 1.5e-02 de C13.1 sin agotarlo.

### A13.4 HALLAZGO DE INSTRUMENTO: EL RC DEL DRIVER NO ESTÁ CABLEADO
El driver sim/b2_microstrip_2d.py imprime PASA o NO PASA en su última línea, pero main() no devuelve valor y el módulo no llama a sys.exit: el código de retorno del proceso es 0 en los dos casos. Además la corrida se lanzó en segundo plano sin wait, con lo que su RC no quedó capturado. Las dos cosas se declaran:
  - RC del corredor: NO CAPTURADO (el lanzamiento no lo recogió).
  - RC que el driver habría dado: 0, y por eso no es informativo: el veredicto vive en la última línea del crudo, no en el código de retorno.
Lectura autoritativa del veredicto: la línea VEREDICTO del crudo, leída con cat. El contraste es el instrumento hermano: sim/ref_hammerstad.py SÍ termina en sys.exit(main()) con rc = 0 o 2, y su crudo caduco de 2026-10-13T024127Z sí salió con RC 1 por excepción. El defecto no es del objeto medido: es una asimetría entre las dos piezas nuevas, y se asienta sin alterar el solver ni el driver (cero escrituras sobre piezas en vuelo).
  NOTA de fidelidad: el crudo caduco (52 l) imprime la línea K3 sin formato (Z0 / eta_0 = %.17g) porque murió antes de formatearla. Se conserva tal cual: es la firma del fallo, no un texto a reparar.

### A13.5 DEFECTOS DEL GATE A2.1, DECLARADOS Y NO ADJUDICADOS
Las dos piezas nuevas pasaron por tools/gate_pre_escritura.sh antes de escribirse, y el gate se midió en sus propios bordes:
  - objetivo RELATIVO (sim/ref_hammerstad.py): RC 128. El gate resuelve el directorio con el dirname del objetivo y luego ejecuta git -C sobre él, con lo que el prefijo se duplica (sim/sim/ref_hammerstad.py -> fatal: could not open). En consecuencia el gate EXIGE objetivo ABSOLUTO: llamarlo en relativo no mide el objeto, mide su propio camino.
  - objetivo ABSOLUTO sobre pieza INEXISTENTE: RC 10 (COLISION: no existe). Correcto en sí, pero es la ÚNICA puerta por la que puede entrar un alta nueva.
  - pieza nueva ya creada y sin rastrear: RC 13 (ESTADO SUCIO). El arnés no resuelve de forma transparente el alta de un objetivo nuevo si este no pasa antes por la excepción BLOB_PRE ausente (RC 10).
Los tres códigos se declaran aquí, con su comando, sin alterar el código del solver ni del gate. El pre-vuelo del apéndice que Ud. lee SÍ cerró en RC 0 sobre la tupla completa (objetivo absoluto, blob d02b8995ff2f7de6dda2fea81c3223335a6d9439, huella A13.1, 472 líneas).

### A13.6 PENDIENTE DE SU DECISIÓN, SIN ADJUDICAR (Z0: 1.5% sellado contra 2.0% del enunciado)
13.7 queda como estaba: C13.1 usa el 1.5% sellado en la sección 5 (el más estricto) y el 2.0% para Z0 que pide el enunciado queda REGISTRADO COMO PENDIENTE. No se mueve ningún umbral después de ver la salida (N4). Con la cifra medida, la decisión no cambia este veredicto: Z0 pasa por las dos puertas (1.148733e-02 < 1.5e-02 < 2.0e-02).

### A13.7 CRUDOS: IDENTIDADES Y LO QUE SE CONSERVA
Ventana 2026-10-13T04:03Z, los tres procesos de escritura ya terminados:
  registros/20261013/rf_b2_crudo_20261013T023346Z.txt           41 l  2520 B  sha16 eb2e56cf7e0eed80  (C13.1 a C13.4, veredicto PASA)
  registros/20261013/rf_b2_ref_hammerstad_20261013T024616Z.txt  55 l  3365 B  sha16 61cbd34970761eb2  (referencia 13.3, RC 0)
  registros/20261013/rf_b2_ref_hammerstad_20261013T024127Z.txt  52 l  3118 B  sha16 689516bc21a89be4  (CADUCO: murió por TypeError en K3; se conserva fechado, no se purga)
Toda cifra de conteo caduca al escribirse: estas tres corresponden a esa ventana. Las identidades no se citan de memoria: salen de wc y de shasum.

### A13.8 PIEZAS DE ESTE FRENTE (identidad medida, no declarada)
  sim/ref_hammerstad.py     141 l  6371 B  blob 6de87f17cb89ed8709b42fe91ff18e82f12ec37f
  sim/b2_microstrip_2d.py   172 l  8135 B  blob cf5e8cdf97fc945af2b14f9471e8ab0315f277da
G13.2 se cumplió: el motor base de sfqed-paper (sim/maxwell2d.py, 715 l, 30759 B, sha16 1db75ea7b0b8cba4, blob b3fc082245cfc5c33b3e275f966cfb16b04aa2e2) NO se editó y nada dentro de sfqed-paper se tocó (N2). Estado del árbol de este repo antes de este apéndice: HEAD 5fbf8291dfc4298e89ae72709004fc04394d0ff3, rama main, sin remoto declarado, cinco rutas sin rastrear y cero modificadas.

### A13.9 LO QUE ESTE APÉNDICE NO ABRE
  - No abre S11 ni S21 del microstrip (A11.8; N5): sigue sin puerto modal ni descomposición modal.
  - No abre Z0 fuera del dominio w/h <= 1 (N5).
  - No abre la fase 2 térmica ni el frente editorial ni nada dentro de sfqed-paper (N2).
  - No declara verde con cero filas medidas: se midieron 6 corridas y 3 crudos (N6).
  - No mueve ningún umbral sellado (N4).
G13.5 cumplida: cero notación monetaria en este apéndice y en los crudos que cita.

ESTADO: Benchmark 2 CERRADO EN VERDE por C13.1 a C13.4 sobre la malla nominal de 13.5, con el sesgo de truncamiento de caja declarado (eps_eff 2.5e-03 hacia la referencia; Z0 1.8e-03) y con el 2.0% de Z0 todavía pendiente de su decisión. El bloque (las 2 piezas y los 3 crudos) entra en commit atómico de custodia; ninguna cifra de este apéndice se apoya en memoria: todas salen de comando.
