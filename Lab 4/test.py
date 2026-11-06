"""Pruebas de geometria, insercion y busquedas del Quadtree."""
import math
import os
import random
import unittest

import matplotlib.pyplot as plt

from Quadtreetree import (
    Punto, Rectangulo, Quadtree,
    buscar_radio_fuerza_bruta, k_vecinos_fuerza_bruta,
    generar_datos_ciudad,
)

GRAFICAS_DIR = "graficas"


def radio_para_k(k, n, target=20, tam=10000):
    radios = {1: 100, 2: 800, 3: 1800, 4: 2800,
              5: 3600, 6: 4300, 7: 4900, 8: 5500}
    return radios.get(k, 3000)


class TestGeometria(unittest.TestCase):
    def test_basico(self):
        p = Punto((1.0, 2.0), id_punto=42)
        self.assertEqual(p.k, 2)
        self.assertEqual(p.coords, (1.0, 2.0))
        self.assertEqual(p.id_punto, 42)

    def test_dimensiones_2_3_5(self):
        for k in (2, 3, 5):
            p = Punto(tuple(range(k)))
            self.assertEqual(p.k, k)

    def test_distancia_3_4_5(self):
        self.assertAlmostEqual(Punto((0, 0)).distancia(Punto((3, 4))), 5.0)

    def test_distancia_kd(self):
        a = Punto((0, 0, 0, 0, 0))
        b = Punto((1, 1, 1, 1, 1))
        self.assertAlmostEqual(a.distancia(b), 5 ** 0.5)

    def test_k_mismatch(self):
        with self.assertRaises(ValueError):
            Punto((0, 0)).distancia(Punto((0, 0, 0)))

    def test_vacio(self):
        with self.assertRaises(ValueError):
            Punto(())

    def test_no_iterable(self):
        with self.assertRaises(TypeError):
            Punto(5)

    def test_contiene(self):
        caja = Rectangulo([0, 0], [10, 10])
        self.assertTrue(caja.contiene(Punto((5, 5))))
        self.assertTrue(caja.contiene(Punto((0, 0))))
        self.assertTrue(caja.contiene(Punto((10, 10))))
        self.assertFalse(caja.contiene(Punto((11, 5))))

    def test_distancia_minima(self):
        caja = Rectangulo([0, 0], [10, 10])
        self.assertAlmostEqual(caja.distancia_minima((13, 14)), 5.0)
        self.assertAlmostEqual(caja.distancia_minima((5, 5)), 0.0)

    def test_centro(self):
        self.assertEqual(Rectangulo([0, 0], [10, 20]).centro(), (5.0, 10.0))

    def test_hijos_cubren_sin_solapar(self):
        for k in (1, 2, 3, 5):
            caja = Rectangulo([0] * k, [100] * k)
            hijos = [caja.hijo(i) for i in range(2 ** k)]
            vol_padre = 100.0 ** k
            vol_hijos = 0.0
            for h in hijos:
                v = 1.0
                for lo, hi in zip(h.minimos, h.maximos):
                    v *= (hi - lo)
                vol_hijos += v
            self.assertAlmostEqual(vol_hijos, vol_padre, places=5,
                                   msg=f"K={k}: volumen hijos != padre")
            rng = random.Random(k)
            for _ in range(200):
                p = Punto(tuple(rng.uniform(0, 100) for _ in range(k)))
                idx = caja.indice_hijo(p)
                self.assertTrue(hijos[idx].contiene(p),
                                f"K={k}: punto {p.coords} no en hijo {idx}")
                for j, h in enumerate(hijos):
                    if j != idx:
                        self.assertFalse(h.contiene(p),
                                         f"K={k}: punto {p.coords} tambien en hijo {j}")

    def test_indice_hijo(self):
        caja = Rectangulo([0, 0], [10, 10])
        self.assertEqual(caja.indice_hijo(Punto((2, 3))), 0)  # SW
        self.assertEqual(caja.indice_hijo(Punto((7, 3))), 1)  # SE
        self.assertEqual(caja.indice_hijo(Punto((2, 7))), 2)  # NW
        self.assertEqual(caja.indice_hijo(Punto((7, 7))), 3)  # NE


class TestQuadtree(unittest.TestCase):
    def _arbol(self, k=2, maxs=None, capacidad=4, profundidad_max=10):
        if maxs is None:
            maxs = [100] * k
        return Quadtree(Rectangulo([0] * k, maxs), capacidad=capacidad,
                        profundidad_max=profundidad_max)

    def test_insertar_y_buscar(self):
        arbol = self._arbol(2)
        self.assertTrue(arbol.insertar(Punto((10, 20), id_punto=1)))
        res = arbol.buscar_radio((10, 20), 0.1)
        self.assertEqual(len(res), 1)

    def test_insertar_fuera(self):
        arbol = self._arbol(2)
        self.assertFalse(arbol.insertar(Punto((200, 200))))

    def test_insertar_k_mismatch(self):
        arbol = self._arbol(2)
        with self.assertRaises(ValueError):
            arbol.insertar(Punto((1, 2, 3)))

    def test_k_max(self):
        with self.assertRaises(ValueError):
            Quadtree(Rectangulo([0] * 9, [100] * 9))

    def test_buscar_radio_k_mismatch(self):
        arbol = self._arbol(2)
        with self.assertRaises(ValueError):
            arbol.buscar_radio((1, 2, 3), 100)

    def test_knn_k_mismatch(self):
        arbol = self._arbol(2)
        with self.assertRaises(ValueError):
            arbol.k_vecinos_mas_cercanos((1, 2, 3), 1)

    def test_contar_puntos(self):
        for k in (2, 3, 5):
            puntos = generar_datos_ciudad(n_puntos=200, k=k, semilla=k * 7)
            arbol = Quadtree(Rectangulo([0] * k, [10000] * k),
                             capacidad=4, profundidad_max=10)
            for punto in puntos:
                arbol.insertar(punto)
            self.assertEqual(arbol.contar_puntos(), len(puntos),
                             f"K={k}: puntos perdidos en el arbol")

    def test_radio_vs_fb(self):
        N = 1000
        total_encontrados = 0
        for k in (2, 3, 5):
            puntos = generar_datos_ciudad(n_puntos=N, k=k, semilla=k * 7)
            arbol = Quadtree(Rectangulo([0] * k, [10000] * k),
                             capacidad=4, profundidad_max=10)
            for punto in puntos:
                arbol.insertar(punto)
            r = radio_para_k(k, N, target=20)
            rng = random.Random(k)
            for _ in range(10):
                query = tuple(rng.uniform(0, 10000) for _ in range(k))
                res_a = arbol.buscar_radio(query, r)
                res_fb = buscar_radio_fuerza_bruta(puntos, query, r)
                total_encontrados += len(res_fb)
                self.assertEqual(sorted(p.id_punto for p in res_a),
                                 sorted(p.id_punto for p in res_fb),
                                 f"K={k}, query={query}, r={r:.0f}")
        self.assertGreater(total_encontrados, 20)

    def test_knn_vs_fb(self):
        for k in (2, 3, 5):
            puntos = generar_datos_ciudad(n_puntos=500, k=k, semilla=k * 13)
            arbol = Quadtree(Rectangulo([0] * k, [10000] * k),
                             capacidad=4, profundidad_max=10)
            for punto in puntos:
                arbol.insertar(punto)
            rng = random.Random(k)
            for _ in range(10):
                query = tuple(rng.uniform(0, 10000) for _ in range(k))
                for kk in (1, 3, 5):
                    res_a = arbol.k_vecinos_mas_cercanos(query, kk)
                    res_fb = k_vecinos_fuerza_bruta(puntos, query, kk)
                    d_a = [round(d, 6) for d, _ in res_a]
                    d_fb = [round(d, 6) for d, _ in res_fb]
                    self.assertEqual(d_a, d_fb, f"K={k}, k={kk}")

    def test_k1_binario(self):
        random.seed(7)
        arbol = self._arbol(1, [100], capacidad=2)
        puntos = []
        for i in range(20):
            p = Punto((random.uniform(0, 100),), id_punto=i)
            puntos.append(p)
            arbol.insertar(p)
        self.assertEqual(arbol.n_hijos, 2)
        query = (50.0,)
        p_a, d_a = arbol.vecino_mas_cercano(query)
        p_fb, d_fb = min(((p, math.dist(p.coords, query)) for p in puntos),
                          key=lambda x: x[1])
        self.assertEqual(p_a.id_punto, p_fb.id_punto)
        self.assertAlmostEqual(d_a, d_fb, places=6)

    def test_duplicados(self):
        arbol = self._arbol(2, [100, 100])
        for i in range(10):
            arbol.insertar(Punto((50, 50), id_punto=i))
        res = arbol.buscar_radio((50, 50), 0.001)
        self.assertEqual(len(res), 10)
        self.assertEqual(arbol.contar_puntos(), 10)

    def test_radio_cero(self):
        arbol = self._arbol(2, [100, 100])
        arbol.insertar(Punto((50, 50), id_punto=0))
        arbol.insertar(Punto((50.0001, 50), id_punto=1))
        res = arbol.buscar_radio((50, 50), 0)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].id_punto, 0)

    def test_radio_negativo(self):
        arbol = self._arbol(2, [100, 100])
        with self.assertRaises(ValueError):
            arbol.buscar_radio((50, 50), -1)

    def test_k_mayor_que_n(self):
        arbol = self._arbol(2, [100, 100])
        for i in range(3):
            arbol.insertar(Punto((10 * i, 10 * i), id_punto=i))
        res = arbol.k_vecinos_mas_cercanos((0, 0), k=10)
        self.assertEqual(len(res), 3)

    def test_k_cero(self):
        arbol = self._arbol(2, [100, 100])
        arbol.insertar(Punto((10, 10)))
        self.assertEqual(arbol.k_vecinos_mas_cercanos((0, 0), k=0), [])

    def test_vacio(self):
        arbol = self._arbol(2, [100, 100])
        self.assertEqual(arbol.buscar_radio((50, 50), 100), [])
        self.assertEqual(arbol.k_vecinos_mas_cercanos((50, 50), 1), [])
        p, d = arbol.vecino_mas_cercano((50, 50))
        self.assertIsNone(p)
        self.assertEqual(d, float('inf'))

    def test_query_fuera_mapa(self):
        arbol = self._arbol(2, [100, 100])
        arbol.insertar(Punto((10, 10), id_punto=1))
        res = arbol.buscar_radio((-20, 10), 40)
        self.assertEqual(len(res), 1)

    def test_punto_en_frontera_hijos(self):
        arbol = self._arbol(2, [100, 100])
        arbol.insertar(Punto((50, 50), id_punto=1))
        self.assertEqual(arbol.buscar_radio((50, 50), 0.001)[0].id_punto, 1)

    def test_punto_en_min_y_max(self):
        arbol = Quadtree(Rectangulo([0, 0], [10000, 10000]))
        self.assertTrue(arbol.insertar(Punto((0, 0), id_punto=1)))
        self.assertTrue(arbol.insertar(Punto((10000, 10000), id_punto=2)))
        res = arbol.buscar_radio((0, 0), 0.1)
        self.assertEqual([p.id_punto for p in res], [1])
        res = arbol.buscar_radio((10000, 10000), 0.1)
        self.assertEqual([p.id_punto for p in res], [2])

    def test_distancia_exactamente_al_radio(self):
        arbol = self._arbol(2, [100, 100])
        arbol.insertar(Punto((3, 4), id_punto=1))
        res = arbol.buscar_radio((0, 0), 5.0)
        self.assertEqual(len(res), 1)

    def test_hojas_que_tocan_circulo(self):
        puntos = generar_datos_ciudad(n_puntos=200, k=2, semilla=1)
        arbol = Quadtree(Rectangulo([0, 0], [10000, 10000]), capacidad=4)
        for p in puntos:
            arbol.insertar(p)
        q = (5000.0, 5000.0)
        r = 500.0
        hojas = arbol.hojas_que_tocan_circulo(q, r)
        for caja in hojas:
            self.assertLessEqual(caja.distancia_minima(q), r + 1e-9)
        for p in arbol.buscar_radio(q, r):
            self.assertTrue(any(c.contiene(p) for c in hojas),
                            f"Punto {p} fuera de todas las hojas devueltas")

    def test_hoja_que_contiene(self):
        puntos = generar_datos_ciudad(n_puntos=100, k=3, semilla=2)
        arbol = Quadtree(Rectangulo([0, 0, 0], [10000, 10000, 10000]),
                         capacidad=4)
        for punto in puntos:
            arbol.insertar(punto)
        for p in puntos:
            hoja = arbol.hoja_que_contiene(p)
            self.assertTrue(hoja.contiene(p),
                            f"Hoja no contiene al punto {p}")
        with self.assertRaises(ValueError):
            arbol.hoja_que_contiene(Punto((-1e6, -1e6, -1e6)))

class TestDatos(unittest.TestCase):
    def test_devuelve_n_exacto(self):
        for k in (2, 3):
            puntos = generar_datos_ciudad(n_puntos=100, k=k, semilla=1)
            self.assertEqual(len(puntos), 100)

    def test_n_no_divisible(self):
        """N exacto aunque N no sea divisible por 10."""
        for n in (11, 101, 999, 10001):
            for k in (2, 3):
                puntos = generar_datos_ciudad(n_puntos=n, k=k, semilla=1)
                self.assertEqual(len(puntos), n,
                                 f"N={n}, K={k}: devolvio {len(puntos)}")

    def test_determinista_sin_division(self):
        a = generar_datos_ciudad(n_puntos=101, k=2, semilla=42)
        b = generar_datos_ciudad(n_puntos=101, k=2, semilla=42)
        for pa, pb in zip(a, b):
            self.assertEqual(pa.coords, pb.coords)

    def test_dentro_de_limites(self):
        puntos = generar_datos_ciudad(n_puntos=100, k=2,
                                       tam_ciudad=10000, semilla=1)
        for p in puntos:
            for c in p.coords:
                self.assertGreaterEqual(c, 0)
                self.assertLessEqual(c, 10000)

    def test_k_consistente(self):
        for k in (2, 3, 5):
            puntos = generar_datos_ciudad(n_puntos=50, k=k, semilla=1)
            self.assertTrue(all(p.k == k for p in puntos))


def _dibujar_caja(ax, caja, **kw):
    if caja.k != 2:
        return
    ancho = caja.maximos[0] - caja.minimos[0]
    alto = caja.maximos[1] - caja.minimos[1]
    ax.add_patch(plt.Rectangle(caja.minimos, ancho, alto, fill=False, **kw))


def _arbol_2d_fijo(puntos, capacidad=4, profundidad_max=10):
    arbol = Quadtree(Rectangulo([0, 0], [10000, 10000]),
                     capacidad=capacidad, profundidad_max=profundidad_max)
    for punto in puntos:
        arbol.insertar(punto)
    return arbol


def visualizar_radio(puntos, arbol, query, radio, archivo):
    fig, ax = plt.subplots(figsize=(10, 10))
    xs = [p.coords[0] for p in puntos]
    ys = [p.coords[1] for p in puntos]
    ax.scatter(xs, ys, s=4, c="lightgray", label="Puntos")
    encontrados = arbol.buscar_radio(query, radio)
    fuerza_bruta = buscar_radio_fuerza_bruta(puntos, query, radio)
    hojas = arbol.hojas_que_tocan_circulo(query, radio)
    for caja in hojas:
        _dibujar_caja(ax, caja, edgecolor="blue", alpha=0.4, lw=0.6)
    if encontrados:
        ax.scatter([p.coords[0] for p in encontrados],
                   [p.coords[1] for p in encontrados],
                   s=20, c="green", label=f"En radio ({len(encontrados)})",
                   zorder=3)
    ax.scatter(*query, s=120, c="red", marker="*", label="Consulta", zorder=4)
    ax.add_patch(plt.Circle(query, radio, fill=False, color="red", alpha=0.6, lw=2))

    detalle = ax.inset_axes([0.58, 0.58, 0.37, 0.37])
    detalle.scatter(xs, ys, s=8, c="lightgray")
    if encontrados:
        detalle.scatter([p.coords[0] for p in encontrados],
                        [p.coords[1] for p in encontrados],
                        s=24, c="green", zorder=3)
    for caja in hojas:
        _dibujar_caja(detalle, caja, edgecolor="blue", alpha=0.6, lw=0.8)
    detalle.scatter(*query, s=90, c="red", marker="*", zorder=4)
    detalle.add_patch(plt.Circle(query, radio, fill=False, color="red", lw=2))
    margen = max(radio * 2, 1000)
    detalle.set_xlim(query[0] - margen, query[0] + margen)
    detalle.set_ylim(query[1] - margen, query[1] + margen)
    detalle.set_aspect("equal")
    detalle.set_title("Detalle de la consulta", fontsize=9)
    detalle.tick_params(labelsize=7)
    ax.indicate_inset_zoom(detalle, edgecolor="black", alpha=0.7)

    coincide = sorted(p.id_punto for p in encontrados) == \
        sorted(p.id_punto for p in fuerza_bruta)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Radio {radio} m: {len(encontrados)} puntos "
                 f"(coincide con fuerza bruta: {'si' if coincide else 'no'})")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(archivo, dpi=120)
    plt.close(fig)


def visualizar_knn(puntos, arbol, query, k, archivo):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter([p.coords[0] for p in puntos], [p.coords[1] for p in puntos],
               s=2, c="lightgray", label="Puntos")
    vecinos = arbol.k_vecinos_mas_cercanos(query, k)
    fuerza_bruta = k_vecinos_fuerza_bruta(puntos, query, k)
    for _, punto in vecinos:
        _dibujar_caja(ax, arbol.hoja_que_contiene(punto),
                      edgecolor="blue", alpha=0.4, lw=0.6)
        ax.plot([query[0], punto.coords[0]], [query[1], punto.coords[1]],
                "b-", alpha=0.5, lw=1)
    if vecinos:
        ax.scatter([p.coords[0] for _, p in vecinos],
                   [p.coords[1] for _, p in vecinos],
                   s=80, c="blue", label=f"{k} vecinos", zorder=3)
    ax.scatter(*query, s=120, c="red", marker="*", label="Consulta", zorder=4)
    coincide = [round(d, 4) for d, _ in vecinos] == \
        [round(d, 4) for d, _ in fuerza_bruta]
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"{k} vecinos mas cercanos "
                 f"(coincide con fuerza bruta: {'si' if coincide else 'no'})")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(archivo, dpi=120)
    plt.close(fig)


def visualizar_estructura(puntos, arbol, archivo):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter([p.coords[0] for p in puntos], [p.coords[1] for p in puntos],
               s=1, c="gray", alpha=0.5)
    for caja in arbol.obtener_limites_nodos():
        _dibujar_caja(ax, caja, edgecolor="blue", alpha=0.4, lw=0.3)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Estructura del Quadtree: {arbol.contar_nodos()} nodos")
    fig.tight_layout()
    fig.savefig(archivo, dpi=120)
    plt.close(fig)


def visualizar_3d(puntos, arbol, query, radio, archivo):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter([p.coords[0] for p in puntos],
               [p.coords[1] for p in puntos],
               [p.coords[2] for p in puntos], s=2, c="lightgray")
    encontrados = arbol.buscar_radio(query, radio)
    if encontrados:
        ax.scatter([p.coords[0] for p in encontrados],
                   [p.coords[1] for p in encontrados],
                   [p.coords[2] for p in encontrados],
                   s=20, c="green", label=f"{len(encontrados)} en radio")
    ax.scatter(*query, s=100, c="red", marker="*", label="Consulta")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(archivo, dpi=120)
    plt.close(fig)


def generar_visualizaciones(n=2000, semilla=42):
    os.makedirs(GRAFICAS_DIR, exist_ok=True)
    puntos = generar_datos_ciudad(n_puntos=n, k=2, semilla=semilla)
    arbol = _arbol_2d_fijo(puntos, capacidad=4, profundidad_max=10)
    query = (5000.0, 5000.0)
    visualizar_radio(puntos, arbol, query, 500,
                     os.path.join(GRAFICAS_DIR, "radio_2d.png"))
    visualizar_knn(puntos, arbol, query, 5,
                    os.path.join(GRAFICAS_DIR, "knn_2d.png"))
    visualizar_estructura(puntos, arbol,
                          os.path.join(GRAFICAS_DIR, "estructura_2d.png"))
    puntos_3d = generar_datos_ciudad(n_puntos=500, k=3, semilla=semilla)
    arbol_3d = Quadtree(Rectangulo([0, 0, 0], [10000, 10000, 10000]),
                        capacidad=4, profundidad_max=8)
    for punto in puntos_3d:
        arbol_3d.insertar(punto)
    visualizar_3d(puntos_3d, arbol_3d, (5000.0, 5000.0, 5000.0), 2000,
                  os.path.join(GRAFICAS_DIR, "radio_3d.png"))


if __name__ == '__main__':
    print("Generando visualizaciones en graficas/...")
    generar_visualizaciones()
    unittest.main(verbosity=2)