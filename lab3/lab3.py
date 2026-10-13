import random
import time
import statistics
import csv
import os
import gc
import platform
import json

MAX_CLAVES = 50
REPETICIONES = 5
M_BUSQUEDAS = 1000
BASE_SEED = 42

TAMANOS_N = [10, 30, 100, 300, 1000, 5000, 10000, 30000]

N_FIJO_PARA_M = 10000
VALORES_M = [100, 500, 1000, 5000]


def generar_estudiantes(n, ordenado=False):
    ids = list(range(1, n + 1))
    if not ordenado:
        random.shuffle(ids)
    return [{"id": i,
             "nombre": f"Estudiante_{i}",
             "edad": random.randint(17, 30),
             "promedio": round(random.uniform(0, 10), 1)} for i in ids]


def posicion_izquierda(claves, id_):
    izq, der = 0, len(claves)
    while izq < der:
        medio = (izq + der) // 2
        if claves[medio] < id_:
            izq = medio + 1
        else:
            der = medio
    return izq


def posicion_derecha(claves, id_):
    izq, der = 0, len(claves)
    while izq < der:
        medio = (izq + der) // 2
        if claves[medio] <= id_:
            izq = medio + 1
        else:
            der = medio
    return izq


class Lista:
    def __init__(self):
        self.datos = []

    def insertar(self, est):
        self.datos.append(est)

    def buscar(self, id_):
        for est in self.datos:
            if est["id"] == id_:
                return est
        return None

    def listar_rango(self, a, b):
        en_rango = [e for e in self.datos if a <= e["id"] <= b]
        return sorted(en_rango, key=lambda e: e["id"])

    def listar_todos(self):
        return sorted(self.datos, key=lambda e: e["id"])


class NodoABB:
    def __init__(self, est):
        self.est = est
        self.izq = None
        self.der = None


class ABB:
    def __init__(self):
        self.raiz = None
        self.altura = 0

    def insertar(self, est):
        if self.raiz is None:
            self.raiz = NodoABB(est)
            self.altura = 1
            return

        actual = self.raiz
        nivel = 1
        while True:
            nivel += 1
            if est["id"] < actual.est["id"]:
                if actual.izq is None:
                    actual.izq = NodoABB(est)
                    break
                actual = actual.izq
            else:
                if actual.der is None:
                    actual.der = NodoABB(est)
                    break
                actual = actual.der

        if nivel > self.altura:
            self.altura = nivel

    def buscar(self, id_):
        actual = self.raiz
        while actual is not None:
            if id_ == actual.est["id"]:
                return actual.est
            actual = actual.izq if id_ < actual.est["id"] else actual.der
        return None

    def listar_rango(self, a, b):
        resultado = []
        pila = []
        actual = self.raiz
        while pila or actual:
            while actual:
                if actual.est["id"] < a:
                    actual = actual.der
                else:
                    pila.append(actual)
                    actual = actual.izq
            if not pila:
                break
            actual = pila.pop()
            if actual.est["id"] > b:
                break
            resultado.append(actual.est)
            actual = actual.der
        return resultado

    def listar_todos(self):
        resultado = []
        pila = []
        actual = self.raiz
        while pila or actual:
            while actual:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.est)
            actual = actual.der
        return resultado


class Hoja:
    def __init__(self):
        self.claves = []
        self.datos = []
        self.siguiente = None


class Interno:
    def __init__(self):
        self.claves = []
        self.hijos = []


class BMas:
    def __init__(self):
        self.raiz = Hoja()
        self.altura = 1

    def _hoja_de(self, id_):
        nodo = self.raiz
        while isinstance(nodo, Interno):
            pos = posicion_derecha(nodo.claves, id_)
            nodo = nodo.hijos[pos]
        return nodo

    def _hoja_mas_izquierda(self):
        nodo = self.raiz
        while isinstance(nodo, Interno):
            nodo = nodo.hijos[0]
        return nodo

    def buscar(self, id_):
        hoja = self._hoja_de(id_)
        pos = posicion_izquierda(hoja.claves, id_)
        if pos < len(hoja.claves) and hoja.claves[pos] == id_:
            return hoja.datos[pos]
        return None

    def insertar(self, est):
        resultado = self._insertar(self.raiz, est)
        if resultado is not None:
            clave_que_sube, nuevo_hijo = resultado
            nueva_raiz = Interno()
            nueva_raiz.claves = [clave_que_sube]
            nueva_raiz.hijos = [self.raiz, nuevo_hijo]
            self.raiz = nueva_raiz
            self.altura += 1

    def _insertar(self, nodo, est):
        id_ = est["id"]

        if isinstance(nodo, Hoja):
            pos = posicion_izquierda(nodo.claves, id_)
            nodo.claves.insert(pos, id_)
            nodo.datos.insert(pos, est)

            if len(nodo.claves) <= MAX_CLAVES:
                return None

            medio = len(nodo.claves) // 2
            nueva = Hoja()
            nueva.claves = nodo.claves[medio:]
            nueva.datos = nodo.datos[medio:]
            nodo.claves = nodo.claves[:medio]
            nodo.datos = nodo.datos[:medio]

            nueva.siguiente = nodo.siguiente
            nodo.siguiente = nueva

            return nueva.claves[0], nueva

        pos = posicion_derecha(nodo.claves, id_)
        resultado = self._insertar(nodo.hijos[pos], est)
        if resultado is None:
            return None

        clave_que_sube, nuevo_hijo = resultado
        nodo.claves.insert(pos, clave_que_sube)
        nodo.hijos.insert(pos + 1, nuevo_hijo)

        if len(nodo.claves) <= MAX_CLAVES:
            return None

        medio = len(nodo.claves) // 2
        clave_al_padre = nodo.claves[medio]

        nuevo_interno = Interno()
        nuevo_interno.claves = nodo.claves[medio + 1:]
        nuevo_interno.hijos = nodo.hijos[medio + 1:]
        nodo.claves = nodo.claves[:medio]
        nodo.hijos = nodo.hijos[:medio + 1]

        return clave_al_padre, nuevo_interno

    def listar_rango(self, a, b):
        resultado = []
        hoja = self._hoja_de(a)
        pos = posicion_izquierda(hoja.claves, a)

        while hoja is not None:
            while pos < len(hoja.claves):
                if hoja.claves[pos] > b:
                    return resultado
                resultado.append(hoja.datos[pos])
                pos += 1
            hoja = hoja.siguiente
            pos = 0
        return resultado

    def listar_todos(self):
        resultado = []
        hoja = self._hoja_mas_izquierda()
        while hoja is not None:
            resultado.extend(hoja.datos)
            hoja = hoja.siguiente
        return resultado


def verificar():
    datos = generar_estudiantes(2000)
    for clase in (Lista, ABB, BMas):
        estructura = clase()
        for est in datos:
            estructura.insertar(est)
        for e in datos:
            assert estructura.buscar(e["id"]) == e
        assert estructura.buscar(99999) is None
        rango = [e["id"] for e in estructura.listar_rango(500, 600)]
        assert rango == list(range(500, 601))
        todos = [e["id"] for e in estructura.listar_todos()]
        assert todos == sorted(e["id"] for e in datos)
        estructura.insertar({"id": 5000, "nombre": "Nuevo", "edad": 20, "promedio": 9.0})
        assert estructura.buscar(5000)["nombre"] == "Nuevo"
    print("Verificacion basica OK")
    print("--------")


def verificar_separadoras():
    bm = BMas()
    for i in range(1, 2001):
        bm.insertar({"id": i, "nombre": f"E{i}", "edad": 20, "promedio": 8.0})
    todas = bm.listar_rango(1, 2000)
    assert len(todas) == 2000
    for e in todas:
        encontrado = bm.buscar(e["id"])
        assert encontrado is not None, f"No encontro el id {e['id']}"
        assert encontrado == e, f"Devolvio otro estudiante para el id {e['id']}"
    print("Verificacion de claves separadoras OK")
    print("-----------")


def guardar_entorno():
    info = {
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "procesador": platform.processor(),
        "nucleos": os.cpu_count(),
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "nota": "RAM debe anotarse manualmente en el README",
    }
    os.makedirs("resultados", exist_ok=True)
    with open("resultados/entorno.json", "w") as f:
        json.dump(info, f, indent=2)
    print("Entorno guardado en resultados/entorno.json")
    print("---------")


def _calentamiento_global():
    print("Calentamiento global")
    for clase in (Lista, ABB, BMas):
        est = clase()
        for i in range(200):
            est.insertar({"id": i, "nombre": "x", "edad": 20, "promedio": 5.0})
        est.buscar(1)
        est.listar_rango(1, 50)
        est.listar_todos()
    print("Calentamiento OK")
    print("----------")


def _medir(accion):
    gc.collect()
    gc.disable()
    try:
        inicio = time.perf_counter()
        resultado = accion()
        duracion = time.perf_counter() - inicio
    finally:
        gc.enable()
    return duracion, resultado


def _correr_una_vez(clase_estructura, datos, ids_a_buscar, rango_a, rango_b):
    def construir():
        estructura = clase_estructura()
        for est in datos:
            estructura.insertar(est)
        return estructura

    t_construir, estructura = _medir(construir)

    def buscar_todos():
        for id_ in ids_a_buscar:
            estructura.buscar(id_)
    t_buscar, _ = _medir(buscar_todos)

    t_rango, _ = _medir(lambda: estructura.listar_rango(rango_a, rango_b))

    t_todos, _ = _medir(lambda: estructura.listar_todos())

    altura = getattr(estructura, "altura", None)
    return t_construir, t_buscar, t_rango, t_todos, altura


def ejecutar_experimento():
    print("-----------")
    print("EXPERIMENTO 1: ESCALABILIDAD CON N")
    print("------------")
    print(f"Tamanos de N: {TAMANOS_N}")
    print(f"Repeticiones: {REPETICIONES}")
    print(f"Busquedas por corrida (M fijo): {M_BUSQUEDAS}")
    print("-----------")

    os.makedirs("resultados", exist_ok=True)

    resultados = []

    for ordenado in (True, False):
        modo = "ORDENADO" if ordenado else "ALEATORIO"
        print(f"Modo: {modo}")

        for N_actual in TAMANOS_N:
            rango_ancho = min(100, N_actual)
            rango_a = max(1, (N_actual - rango_ancho) // 2 + 1)
            rango_b = rango_a + rango_ancho - 1

            print(f"N = {N_actual} (rango {rango_a}-{rango_b}, ancho {rango_ancho})")

            acum = {nombre: {"c": [], "b": [], "r": [], "t": [], "alt": None}
                    for nombre in ["Lista", "ABB", "B+"]}

            for rep in range(REPETICIONES):
                seed = BASE_SEED + N_actual * 1000 + rep * 100 + (1 if ordenado else 0)
                random.seed(seed)

                datos = generar_estudiantes(N_actual, ordenado)
                ids_a_buscar = random.choices(range(1, N_actual + 1), k=M_BUSQUEDAS)

                for nombre, clase in (("Lista", Lista), ("ABB", ABB), ("B+", BMas)):
                    t_c, t_b, t_r, t_t, alt = _correr_una_vez(
                        clase, datos, ids_a_buscar, rango_a, rango_b
                    )
                    acum[nombre]["c"].append(t_c)
                    acum[nombre]["b"].append(t_b)
                    acum[nombre]["r"].append(t_r)
                    acum[nombre]["t"].append(t_t)
                    acum[nombre]["alt"] = alt

            for nombre in ["Lista", "ABB", "B+"]:
                d = acum[nombre]
                resultados.append({
                    "N": N_actual,
                    "Orden": modo,
                    "Estructura": nombre,
                    "M": M_BUSQUEDAS,
                    "Rango_Ancho": rango_ancho,
                    "Altura": d["alt"] if d["alt"] is not None else "N/A",
                    "Construir_Prom": statistics.mean(d["c"]),
                    "Construir_Std": statistics.stdev(d["c"]) if REPETICIONES > 1 else 0,
                    "Construir_Mediana": statistics.median(d["c"]),
                    "Construir_Min": min(d["c"]),
                    "Buscar_Prom": statistics.mean(d["b"]),
                    "Buscar_Std": statistics.stdev(d["b"]) if REPETICIONES > 1 else 0,
                    "Buscar_Mediana": statistics.median(d["b"]),
                    "Buscar_Min": min(d["b"]),
                    "Rango_Prom": statistics.mean(d["r"]),
                    "Rango_Std": statistics.stdev(d["r"]) if REPETICIONES > 1 else 0,
                    "Rango_Mediana": statistics.median(d["r"]),
                    "Rango_Min": min(d["r"]),
                    "Todos_Prom": statistics.mean(d["t"]),
                    "Todos_Std": statistics.stdev(d["t"]) if REPETICIONES > 1 else 0,
                    "Todos_Mediana": statistics.median(d["t"]),
                    "Todos_Min": min(d["t"]),
                })
                print(f"  {nombre:<6} "
                      f"construir={statistics.mean(d['c']):.6f}s | "
                      f"buscar={statistics.mean(d['b']):.6f}s | "
                      f"rango={statistics.mean(d['r']):.6f}s | "
                      f"todos={statistics.mean(d['t']):.6f}s"
                      + (f" | altura={d['alt']}" if d["alt"] is not None else ""))

    archivo = "resultados/resultados_lab3.csv"
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        campos = list(resultados[0].keys())
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print("--------")
    print(f"Experimento 1 terminado. Datos en: {archivo}")
    print("--------")


def ejecutar_experimento_M():
    print("--------")
    print("EXPERIMENTO 2: VARIACION DE M (numero de busquedas)")
    print("--------")
    print(f"N fijo = {N_FIJO_PARA_M}, M en {VALORES_M}")
    print("--------")

    resultados = []

    for M_actual in VALORES_M:
        print(f"M = {M_actual}")
        for nombre, clase in (("Lista", Lista), ("ABB", ABB), ("B+", BMas)):
            tiempos = []
            for rep in range(REPETICIONES):
                seed = BASE_SEED + 9999 + M_actual * 100 + rep
                random.seed(seed)
                datos = generar_estudiantes(N_FIJO_PARA_M, ordenado=False)
                ids_a_buscar = random.choices(range(1, N_FIJO_PARA_M + 1), k=M_actual)

                gc.collect()
                gc.disable()
                try:
                    estructura = clase()
                    for est in datos:
                        estructura.insertar(est)
                    inicio = time.perf_counter()
                    for id_ in ids_a_buscar:
                        estructura.buscar(id_)
                    tiempos.append(time.perf_counter() - inicio)
                finally:
                    gc.enable()

            resultados.append({
                "N": N_FIJO_PARA_M,
                "M": M_actual,
                "Estructura": nombre,
                "Buscar_Prom": statistics.mean(tiempos),
                "Buscar_Std": statistics.stdev(tiempos) if REPETICIONES > 1 else 0,
                "Buscar_Mediana": statistics.median(tiempos),
                "Buscar_Min": min(tiempos),
            })
            print(f"  {nombre:<6} buscar({M_actual}) = "
                  f"{statistics.mean(tiempos):.6f}s "
                  f"(std={statistics.stdev(tiempos):.6f}, "
                  f"mediana={statistics.median(tiempos):.6f})")

    archivo = "resultados/resultados_M.csv"
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        campos = list(resultados[0].keys())
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print("----------")
    print(f"Experimento 2 terminado. Datos en: {archivo}")
    print("-----------")


if __name__ == "__main__":
    verificar()
    verificar_separadoras()
    guardar_entorno()
    _calentamiento_global()
    ejecutar_experimento()
    ejecutar_experimento_M()