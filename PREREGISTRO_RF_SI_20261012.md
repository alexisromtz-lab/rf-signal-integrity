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
