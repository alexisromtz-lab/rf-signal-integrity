# Fe de erratas: rutas del entorno de ejecucion en registros historicos

<!-- HUELLA-ERRATA-RUTAS-RF_SIGNAL_INTEGRITY-20261022 -->

## Alcance

La auditoria de fuga publica (`fuga-publica/1`) reporta **5 referencias** al
entorno de ejecucion original en **2 archivos** de este repositorio: **2**
lineas de registro de corrida (salida literal de los instrumentos) y **3** lineas en
documentos fechados. Una misma linea puede portar mas de una referencia.

Detalle medido:

- `PREREGISTRO_RF_SI_20261012.md` — 3 linea(s) · documento
- `registros/20261013/rf_b2_ref_hammerstad_20261013T024127Z.txt` — 2 linea(s) · crudo

Ninguna vive en codigo ejecutable: el codigo publico de este repositorio no depende de
ninguna de estas rutas.

## Determinacion de inmutabilidad

Estos archivos son el registro de lo que ocurrio: pre-registros escritos antes de la
corrida y volcados crudos de los medidores. Reescribirlos cambiaria el contenido sobre el
que se sostienen las conclusiones publicadas y romperia la identidad de las sumas de
verificacion ya emitidas. Por eso **no se editan**: la discordancia se resuelve aqui, no
en el archivo.

## Correspondencia canonica

Toda referencia a `/Users/<usuario>/rf-signal-integrity` equivale operacionalmente a la raiz del arbol
reproducido localmente, conservando el sufijo relativo de cada referencia. La equivalencia
documenta la portabilidad del contexto; no garantiza por si sola la existencia de cada
archivo citado.

## Menciones al arbol de custodia

**1 lineas** de estos registros nombran el arbol privado donde viven el instrumento de
pre-vuelo y el catalogo interno. Designan el **origen de la custodia**, no una
dependencia: ningun archivo publico de este repositorio lo importa, lo ejecuta ni lo
necesita para medir. Se conservan por la misma razon que las rutas —son la transcripcion
de lo que se ejecuto— y quedan adjudicadas por huella con las demas.

## Registro

Las lineas afectadas quedan adjudicadas en el libro tipado de la auditoria
(`fuga_allow.txt`) bajo `RUTA_HISTORICA_SELLADA`, en dos categorias:
`REGISTRO_DE_CORRIDA` (crudos) y `PREREGISTRO_O_ACTA_FECHADA` (documentos). La adjudicacion
va firmada por la huella de la linea: si alguien edita el registro, la huella caduca y el
hallazgo vuelve a abrirse. Esa es la garantia de que esta errata no es una exencion: es
una custodia.
