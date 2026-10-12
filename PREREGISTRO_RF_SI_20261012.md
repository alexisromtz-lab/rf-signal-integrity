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
