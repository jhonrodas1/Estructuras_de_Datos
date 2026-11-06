"""Quadtree K-dimensional y metodos de busqueda para puntos."""
import math
import random


class Punto:
    def __init__(self, coords, id_punto=None):
        if not isinstance(coords, (list, tuple)):
            raise TypeError("coords debe ser lista o tupla")
        if len(coords) == 0:
            raise ValueError("El punto debe tener al menos 1 dimension")
        self.coords = tuple(float(c) for c in coords)
        self.id_punto = id_punto
        self.k = len(self.coords)

    def distancia(self, otro):
        if self.k != otro.k:
            raise ValueError(f"Dimensiones distintas: {self.k} vs {otro.k}")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.coords, otro.coords)))

    def __repr__(self):
        return f"Punto(id={self.id_punto}, coords={self.coords})"


class Rectangulo:
    def __init__(self, minimos, maximos):
        if len(minimos) != len(maximos):
            raise ValueError("minimos y maximos deben tener la misma dimension")
        if len(minimos) == 0:
            raise ValueError("La caja debe tener al menos 1 dimension")
        self.minimos = tuple(float(v) for v in minimos)
        self.maximos = tuple(float(v) for v in maximos)
        self.k = len(self.minimos)
        for lo, hi in zip(self.minimos, self.maximos):
            if lo > hi:
                raise ValueError(f"Caja invalida: min={lo} > max={hi}")

    def contiene(self, punto):
        if punto.k != self.k:
            raise ValueError(f"Punto K={punto.k}, caja K={self.k}")
        for lo, c, hi in zip(self.minimos, punto.coords, self.maximos):
            if c < lo or c > hi:
                return False
        return True

    def distancia_minima_sq(self, query):
        total = 0.0
        for lo, q, hi in zip(self.minimos, query, self.maximos):
            if q < lo:
                total += (lo - q) ** 2
            elif q > hi:
                total += (q - hi) ** 2
        return total

    def distancia_minima(self, query):
        return math.sqrt(self.distancia_minima_sq(query))

    def centro(self):
        return tuple((lo + hi) / 2.0 for lo, hi in zip(self.minimos, self.maximos))

    def indice_hijo(self, punto):
        if punto.k != self.k:
            raise ValueError(f"Punto K={punto.k}, caja K={self.k}")
        mid = self.centro()
        idx = 0
        for j, (c, m) in enumerate(zip(punto.coords, mid)):
            if c >= m:
                idx |= (1 << j)
        return idx

    def hijo(self, indice):
        if not (0 <= indice < (1 << self.k)):
            raise ValueError(f"indice {indice} fuera de rango para K={self.k}")
        mid = self.centro()
        minimos = list(self.minimos)
        maximos = list(self.maximos)
        for j in range(self.k):
            if (indice >> j) & 1:
                minimos[j] = mid[j]   # mitad superior
            else:
                maximos[j] = mid[j]   # mitad inferior
        return Rectangulo(minimos, maximos)

    def __repr__(self):
        return f"Rectangulo(min={self.minimos}, max={self.maximos})"


class Quadtree:
    K_MAX = 8

    def __init__(self, limite, capacidad=4, profundidad_max=15,
                 profundidad_actual=0):
        if limite.k > Quadtree.K_MAX:
            raise ValueError(
                f"K={limite.k} excede K_MAX={Quadtree.K_MAX}. "
                f"Cada subdivision crea 2^K={2 ** limite.k} hijos."
            )
        if capacidad < 1:
            raise ValueError("capacidad debe ser >= 1")
        if profundidad_max < 0:
            raise ValueError("profundidad_max debe ser >= 0")

        self.limite = limite
        self.capacidad = capacidad
        self.profundidad_max = profundidad_max
        self.k = limite.k
        self.n_hijos = 1 << self.k
        self._profundidad = profundidad_actual

        self.puntos = []
        self.dividido = False
        self.hijos = None  # lista de Quadtree (o None si no esta dividido)

    def insertar(self, punto):
        if punto.k != self.k:
            raise ValueError(f"Punto K={punto.k}, arbol K={self.k}")
        if not self.limite.contiene(punto):
            return False
        self._insertar_interno(punto)
        return True

    def buscar_radio(self, query, radio):
        if len(query) != self.k:
            raise ValueError(f"Query K={len(query)}, arbol K={self.k}")
        if radio < 0:
            raise ValueError("radio debe ser >= 0")
        encontrados = []
        q = tuple(float(v) for v in query)
        self._buscar_radio_interno(q, radio * radio, encontrados)
        return encontrados

    def k_vecinos_mas_cercanos(self, query, k=1):
        if len(query) != self.k:
            raise ValueError(f"Query K={len(query)}, arbol K={self.k}")
        if k <= 0:
            return []
        mejores = []
        q = tuple(float(v) for v in query)
        self._knn_interno(q, k, mejores)
        return mejores

    def vecino_mas_cercano(self, query):
        res = self.k_vecinos_mas_cercanos(query, k=1)
        if not res:
            return None, float('inf')
        return res[0][1], res[0][0]

    def obtener_limites_nodos(self):
        cajas = []
        self._limites_interno(cajas)
        return cajas

    def hojas_que_tocan_circulo(self, query, radio):
        cajas = []
        self._hojas_circulo_interno(tuple(float(v) for v in query),
                                     radio * radio, cajas)
        return cajas

    def hoja_que_contiene(self, punto):
        if not self.limite.contiene(punto):
            raise ValueError("El punto no esta dentro del arbol")
        if not self.dividido:
            return self.limite
        idx = self.limite.indice_hijo(punto)
        return self.hijos[idx].hoja_que_contiene(punto)

    def contar_puntos(self):
        if not self.dividido:
            return len(self.puntos)
        return sum(h.contar_puntos() for h in self.hijos)

    def contar_nodos(self):
        if not self.dividido:
            return 1
        return 1 + sum(h.contar_nodos() for h in self.hijos)

    def _crear_hijos(self):
        self.hijos = [
            Quadtree(self.limite.hijo(i), self.capacidad,
                     self.profundidad_max, self._profundidad + 1)
            for i in range(self.n_hijos)
        ]
        self.dividido = True

    def _insertar_interno(self, punto):
        if not self.dividido:
            if (len(self.puntos) < self.capacidad
                    or self._profundidad >= self.profundidad_max):
                self.puntos.append(punto)
                return
            self._crear_hijos()
            viejos = self.puntos
            self.puntos = []
            for p in viejos:
                self._insertar_en_hijos(p)
        self._insertar_en_hijos(punto)

    def _insertar_en_hijos(self, punto):
        idx = self.limite.indice_hijo(punto)
        self.hijos[idx]._insertar_interno(punto)

    def _buscar_radio_interno(self, query, r2, encontrados):
        if self.limite.distancia_minima_sq(query) > r2:
            return
        if not self.dividido:
            for p in self.puntos:
                d2 = sum((a - b) ** 2 for a, b in zip(p.coords, query))
                if d2 <= r2:
                    encontrados.append(p)
            return
        for h in self.hijos:
            h._buscar_radio_interno(query, r2, encontrados)

    def _knn_interno(self, query, k, mejores):
        if (len(mejores) >= k
                and self.limite.distancia_minima_sq(query) > mejores[-1][0] ** 2):
            return
        if not self.dividido:
            for p in self.puntos:
                d2 = sum((a - b) ** 2 for a, b in zip(p.coords, query))
                if len(mejores) < k:
                    mejores.append((math.sqrt(d2), p))
                    mejores.sort(key=lambda x: x[0])
                elif d2 < mejores[-1][0] ** 2:
                    mejores[-1] = (math.sqrt(d2), p)
                    mejores.sort(key=lambda x: x[0])
            return
        hijos_ord = sorted(self.hijos,
                           key=lambda h: h.limite.distancia_minima_sq(query))
        for h in hijos_ord:
            h._knn_interno(query, k, mejores)

    def _limites_interno(self, cajas):
        cajas.append(self.limite)
        if self.dividido:
            for h in self.hijos:
                h._limites_interno(cajas)

    def _hojas_circulo_interno(self, query, r2, cajas):
        if self.limite.distancia_minima_sq(query) > r2:
            return
        if not self.dividido:
            cajas.append(self.limite)
            return
        for h in self.hijos:
            h._hojas_circulo_interno(query, r2, cajas)


def buscar_radio_fuerza_bruta(puntos, query, radio):
    r2 = radio * radio
    return [p for p in puntos
            if sum((a - b) ** 2 for a, b in zip(p.coords, query)) <= r2]


def vecino_mas_cercano_fuerza_bruta(puntos, query):
    mejor = None
    mejor_d2 = float('inf')
    for p in puntos:
        d2 = sum((a - b) ** 2 for a, b in zip(p.coords, query))
        if d2 < mejor_d2:
            mejor_d2 = d2
            mejor = p
    if mejor is None:
        return None, float('inf')
    return mejor, math.sqrt(mejor_d2)


def k_vecinos_fuerza_bruta(puntos, query, k=1):
    if k <= 0:
        return []
    pares = []
    for p in puntos:
        d2 = sum((a - b) ** 2 for a, b in zip(p.coords, query))
        pares.append((d2, p))
    pares.sort(key=lambda x: x[0])
    return [(math.sqrt(d2), p) for d2, p in pares[:k]]


def generar_datos_ciudad(n_puntos=10000, k=2, tam_ciudad=10000, semilla=123):
    random.seed(semilla)
    puntos = []
    n_uniforme = int(n_puntos * 0.70)

    for i in range(n_uniforme):
        coords = tuple(random.uniform(0, tam_ciudad) for _ in range(k))
        puntos.append(Punto(coords, id_punto=i))

    centros_2d = [(3000, 3500), (7500, 7000), (5000, 8000)]
    centros = []
    for cx, cy in centros_2d:
        base = [cx, cy][:min(2, k)]
        while len(base) < k:
            base.append(tam_ciudad / 2.0)
        centros.append(tuple(base))

    n_agrupado = n_puntos - n_uniforme
    base = n_agrupado // len(centros)
    resto = n_agrupado - base * len(centros)
    counts = [base + (1 if i < resto else 0) for i in range(len(centros))]

    id_actual = n_uniforme
    for centro, cnt in zip(centros, counts):
        for _ in range(cnt):
            coords = []
            for c in centro:
                v = random.gauss(c, 600)
                v = max(0, min(tam_ciudad, v))
                coords.append(v)
            puntos.append(Punto(tuple(coords), id_punto=id_actual))
            id_actual += 1

    return puntos