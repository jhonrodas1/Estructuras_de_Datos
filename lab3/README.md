# Sistema de búsqueda de estudiantes

Este trabajo parte del código que hicimos en el taller de la clase. La idea era
tener un sistema que guardara estudiantes y permitiera buscarlos por ID,
insertar nuevos, y listarlos en orden. En el taller ya estaban las tres
estructuras (lista, ABB y B+), pero faltaba medir cómo se comportaban cuando
los datos crecen.

Lo que hice fue adaptar ese código para convertirlo en un experimento: agregué
medición de tiempos, varias repeticiones por caso, y un script aparte que
genera las gráficas a partir de los datos que se guardan en CSV.

---

## Qué se implementó

Tres formas de guardar los estudiantes:

**Lista normal.** Un arreglo donde se guardan los estudiantes. Para buscar uno
toca recorrerlos todos hasta encontrarlo. Es lo más simple pero lo más lento
cuando hay muchos datos.

**ABB (árbol binario de búsqueda).** Los IDs menores van a la izquierda y los
mayores a la derecha. Si los datos llegan en orden aleatorio funciona muy bien.
El problema es cuando llegan ordenados: el árbol se va hacia un solo lado y
termina comportándose como una lista.

**B+.** Los nodos internos solo guardan claves, los datos van en las hojas, y
las hojas están conectadas entre sí. Eso último es lo que hace que buscar un
rango sea muy rápido, porque no hay que subir y bajar por el árbol.

---

## Cómo se hicieron las pruebas

**Datos.** Se generan N estudiantes con IDs del 1 al N. Hay dos modos: los IDs
llegan ordenados, o llegan mezclados (aleatorios).

**Búsquedas.** Se hacen M búsquedas con IDs al azar. En el experimento
principal M queda fijo en 1000, y en un segundo experimento se prueba con
M = 100, 500, 1000 y 5000.

**Medición.** Cada operación se cronometra por separado. Se corre 5 veces cada
caso y se reportan el promedio, la desviación estándar, la mediana y el mínimo.
La razón de reportar mediana y mínimo es que con pocas repeticiones un valor
raro (por ejemplo el sistema operativo interrumpiendo) puede dañar el promedio.

Antes de medir se apaga el recolector de basura de Python para que no se meta
en medio, y se enciende otra vez después. También se hace una corrida de
calentamiento que se descarta.

**Tamaños probados.** N = 10, 30, 100, 300, 1000, 5000, 10000 y 30000. Los
tamaños pequeños se incluyeron para ver en qué punto exacto las estructuras
empiezan a diferenciarse.

**Equipo donde corrí esto.** Windows 10, Python 3.10, procesador [COMPLETAR],
[COMPLETAR] GB de RAM.

---

## Resultados y gráficas

Todas las gráficas están en la carpeta `graficas/`. Las más importantes son:

- `comparacion_busqueda.png`: comparación lado a lado entre datos aleatorios y
  ordenados. En la mitad de la izquierda (aleatorios) el ABB y el B+ le ganan
  claramente a la lista. En la mitad de la derecha (ordenados) el ABB se pega
  a la lista, mientras que el B+ sigue abajo solo.
- `alturas.png`: aquí se ve clarísimo cómo la altura del ABB ordenado crece
  igual que N, o sea el árbol se degenera. Las demás alturas se mantienen
  bajas.
- `construccion_ordenado.png`: el ABB ordenado tarda muchísimo más en
  construirse que las otras dos. Es porque cada inserción recorre toda la rama
  derecha.

---

## Lo que encontré

**1. La lista no distingue el orden.** Da casi lo mismo si los datos llegan
ordenados o mezclados, porque siempre recorre todo. Su tiempo crece de forma
lineal con N.

**2. El ABB sí depende del orden.** Cuando los datos llegan ordenados el árbol
se convierte en una lista (la altura queda igual a N), y la búsqueda se vuelve
lenta. Con N = 30000 la altura del ABB ordenado fue 30000, mientras que en modo
aleatorio fue apenas 36. La búsqueda del ABB ordenado terminó siendo incluso
más lenta que la de la lista normal.

**3. El B+ se mantiene estable.** En todos los tamaños y en ambos modos su
altura se quedó entre 1 y 3. Su tiempo de búsqueda es prácticamente el mismo
sin importar si los datos llegaron ordenados o no. Además es el más rápido
haciendo búsquedas por rango: en N = 30000 tardó unos 43 microsegundos, contra
1476 de la lista y 1345 del ABB.

**4. Con datos muy pequeños la lista gana.** Con N = 10 la lista fue la más
rápida. Tiene sentido: el ABB y el B+ tienen más costos fijos (crear objetos,
seguir punteros), y cuando hay poquitos datos esos costos pesan más que la
ventaja de la búsqueda logarítmica. El cruce donde el ABB empieza a ganar
aparece alrededor de N = 30.

**5. La lista es más rápida listando datos ya ordenados.** Esto me llamó la
atención al principio, pero no es un error. Python usa un algoritmo llamado
Timsort que detecta cuando los datos ya vienen ordenados y los recorre mucho
más rápido. Es una propiedad del lenguaje, no del algoritmo.

**6. El B+ fue el mejor en general.** Búsqueda puntual, búsqueda por rango,
listar todos y construcción: en ninguno de esos casos el B+ quedó mal parado.
Es el único que no se afecta por el orden en que llegan los datos.

---

## Qué se puede y qué no se puede concluir

Cosas que sí se pueden concluir con este experimento:

- El ABB sin balanceo es peligroso si los datos llegan ordenados.
- El B+ es más robusto y por eso las bases de datos lo usan.
- La notación O grande describe bien el comportamiento cuando N es grande,
  pero con N pequeño los costos fijos hacen que estructuras teóricamente
  mejores no sean las más rápidas.

Cosas que no se pueden concluir:

- Los tiempos exactos no sirven para otras máquinas, solo las proporciones.
- No se midió uso de memoria, solo tiempo.
- El B+ está en memoria, no en disco. En un caso real las páginas del disco
  cambian el número óptimo de claves por nodo.
- Con 5 repeticiones la desviación estándar es una estimación limitada.

---

## Cómo volver a correr esto

Instalar dependencias:

```
py -m pip install -r requirements.txt
```

Correr el experimento (tarda entre 6 y 10 minutos):

```
py lab3.py
```

Generar las gráficas:

```
py graficar.py
```

Los resultados quedan en `resultados/` y las gráficas en `graficas/`. El
experimento usa una semilla fija, así que los datos y los tiempos son
reproducibles en el mismo equipo.

---

## Estructura del repositorio

```
proyecto/
├── lab3.py
├── graficar.py
├── requirements.txt
├── README.md
├── CODIGO_DE_HONOR.md
├── resultados/
│   ├── resultados_lab3.csv
│   ├── resultados_M.csv
│   └── entorno.json
└── graficas/
    ├── alturas.png
    ├── busqueda_aleatorio.png
    ├── busqueda_ordenado.png
    ├── comparacion_busqueda.png
    ├── construccion_aleatorio.png
    ├── construccion_ordenado.png
    ├── experimento_M.png
    ├── rango_aleatorio.png
    ├── rango_ordenado.png
    ├── todos_aleatorio.png
    └── todos_ordenado.png
```

## entorno
- Procesador	Intel(R) Core(TM) i3-1005G1 CPU @ 1.20GHz   1.19 GHz
- RAM instalada	16,0 GB (15,8 GB usable)
- Almacenamiento	1.86 TB SSD FIKWOT FS810 2TB, 477 GB SSD NVMe ADATA LEGEND 700
- Tarjeta gráfica	Intel(R) UHD Graphics (128 MB)

# Código de Honor

1. El código presentado en este repositorio es una adaptación del trabajodesarrollado durante el taller de la clase, complementado con lasmediciones y análisis experimental aquí documentados.

2. Utilicé herramientas de inteligencia artificial como apoyo para:
   - Diseño del experimento y estructura de las mediciones.
   - Ayuda para adaptar el código base, esto llevando a recomendacion de unas librerias muy interesantes como platform.
   - Revisión metodológica y detección de bugs (de los cuales si hubieron bastantes)
   - Sugerencias para la redacción del README.

3. Todos los datos, gráficas y análisis estadísticos provienen de ejecucionesreales del código en mi equipo. Los valores no fueron inventados ni estimados sin verificación.

4. Comprendo:
   - El funcionamiento de cada una de las tres estructuras implementadas.
   - El diseño experimental y las decisiones metodológicas tomadas.
   - El significado de cada estadística reportada.
   - Las conclusiones y su relación con los resultados obtenidos.
