# Laboratorio 1: Matriz de 100,000 x 100,000 en Disco Duro

**Estudiante:** Jhon Deivy Rodas Morales
**Materia:** Estructuras de Datos  

---

## Archivos contenidos en esta carpeta para la solucion del problema

* `matriz_laboratorio1.cpp`: Código fuente en C++ con la solución estructurada para intentar solucionar todas las problematicas planteadas.
* `.gitignore`: Archivo de configuración de Git para omitir la subida de ejecutables.

---

## Solución a las problemáticas planteadas

### 1. Consumo excesivo de RAM
**Problema:** Cargar una matriz de 10,000,000,000 de datos colapsa la memoria RAM de cualquier equipo convencional.
**Solución:** Se implementó la librería `<fstream>` para abrir un canal de lectura/escritura directo al disco duro. El programa **nunca** carga el archivo completo. Mediante la función `seekg()`, el código salta matemáticamente al byte exacto que se necesita. Cuando se extrae una fila, solo se cargan a la RAM 100,000 bytes (~100 KB), protegiendo la memoria del sistema.

### 2. Escritura lenta a disco
**Problema:** Escribir 10 mil millones de ceros byte por byte tomaría horas siendo terriblemente ineficiente.
**Solución:** Se utilizó el concepto de **archivos dispersos (Sparse Files)**. El programa salta a la última posición del archivo (byte 10,000,100,128) y escribe un solo byte. El sistema operativo (Windows) reserva el tamaño lógico instantáneamente sin tener que escribir físicamente los ceros. Luego, solo se escriben en disco los metadatos y los separadores de fila, reduciendo el tiempo de creación a milisegundos.

### 3. Optimización general
* **Manipulación y Almacenamiento:** Se utilizó el tipo de dato primitivo `char` (1 byte) en lugar de `int` (4 bytes). Esto ya que las demas eran inviables, podrian llegar a pesar 40 gigas por lo que vi
**Lectura de datos:** El acceso es de complejidad $O(1)$. No se itera sobre el archivo buscando datos. Se usa la fórmula `Posición = Header + (Fila * Ancho_Fila) + Columna` para encontrar coordenadas instantáneamente.

---

## Forma de verificar el contenido
El código cuenta con un algoritmo de verificación que realiza lo siguiente:
1. Comprueba si el archivo ya existe para evitar recrearlo.
2. Genera dos coordenadas aleatorias robustas (Fila y Columna entre 0 y 99,999) usando `<random>`.
3. Navega por el disco duro y extrae únicamente la fila sorteada, llevándola a un vector en RAM.
4. Muestra la cantidad de bytes consumidos y extrae de esa memoria la coordenada solicitada, demostrando que la estructura bidimensional funciona correctamente sin leer todo el documento.
*(Existe un bloque comentado en el código que permite imprimir la fila completa en consola si se desea para que puedas comprar que se tiene toda la fila de la matriz).*

## Uso

Se debe abrir el cmd en la carpeta que posee la solucion y ejecutar g++ -o matriz matriz_laboratorio1.cpp y despues utilizar matriz.exe.

Al hacerlo se vera como se genera la matriz (por lo general el menos de un minuto) y se toma una fila aleatoria apra cargar en ram y realizar una bsuqueda aleatoria, tras esto se mostrara el contenido de esa busqueda aleatoria.