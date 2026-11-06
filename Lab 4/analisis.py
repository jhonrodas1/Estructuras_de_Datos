"""Compara busquedas de Quadtree con fuerza bruta."""
import os
import random
import time

import matplotlib.pyplot as plt
from Quadtreetree import Rectangulo, Quadtree, generar_datos_ciudad
from Quadtreetree import buscar_radio_fuerza_bruta, vecino_mas_cercano_fuerza_bruta

def medir(arbol, puntos, consultas, tipo, usar_arbol):
    inicio = time.perf_counter()
    for q in consultas:
        if tipo == "radio" and usar_arbol:
            arbol.buscar_radio(q, 500)
        elif tipo == "radio":
            buscar_radio_fuerza_bruta(puntos, q, 500)
        elif usar_arbol:
            arbol.vecino_mas_cercano(q)
        else:
            vecino_mas_cercano_fuerza_bruta(puntos, q)
    return (time.perf_counter() - inicio) * 1000 / len(consultas)

def guardar_grafica(x, tiempo_arbol, tiempo_bruto, archivo, titulo, etiqueta_x):
    plt.figure()
    plt.plot(x, tiempo_arbol, "o-", label="Quadtree")
    plt.plot(x, tiempo_bruto, "o-", label="Fuerza bruta")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(etiqueta_x)
    plt.ylabel("Tiempo por consulta (ms)")
    plt.title(titulo)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join("graficas", archivo))
    plt.close()


def experimento_tamano():
    tamanos = [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000]
    radio_arbol, radio_bruto = [], []
    vecino_arbol, vecino_bruto = [], []
    tiempos_construccion = []
    for n in tamanos:
        puntos = generar_datos_ciudad(n, k=2)
        arbol = Quadtree(Rectangulo([0, 0], [10000, 10000]))
        inicio = time.perf_counter()
        for punto in puntos:
            arbol.insertar(punto)
        construccion = time.perf_counter() - inicio
        consultas = []
        for _ in range(50):
            consultas.append((random.uniform(0, 10000),
                              random.uniform(0, 10000)))
        t_radio_arbol = medir(arbol, puntos, consultas, "radio", True)
        t_radio_bruto = medir(arbol, puntos, consultas, "radio", False)
        t_vecino_arbol = medir(arbol, puntos, consultas, "vecino", True)
        t_vecino_bruto = medir(arbol, puntos, consultas, "vecino", False)
        radio_arbol.append(t_radio_arbol)
        radio_bruto.append(t_radio_bruto)
        vecino_arbol.append(t_vecino_arbol)
        vecino_bruto.append(t_vecino_bruto)
        tiempos_construccion.append(construccion)
        print(f"N={n}: arbol {construccion:.3f}s, radio {t_radio_arbol:.4f}/{t_radio_bruto:.4f}ms, "
              f"vecino {t_vecino_arbol:.4f}/{t_vecino_bruto:.4f}ms (QT/FB)")

    guardar_grafica(tamanos, radio_arbol, radio_bruto, "tiempo_radio.png",
                    "Busqueda por radio (500 m)", "Numero de puntos N")
    guardar_grafica(tamanos, vecino_arbol, vecino_bruto, "tiempo_vecino.png",
                    "Vecino mas cercano", "Numero de puntos N")
    return tamanos, tiempos_construccion, radio_arbol, radio_bruto, vecino_arbol, vecino_bruto

def experimento_dimensiones():
    dimensiones = [2, 3, 4, 5, 6]
    tiempos_arbol, tiempos_brutos = [], []
    ventajas = []

    for k in dimensiones:
        puntos = generar_datos_ciudad(5000, k=k)
        arbol = Quadtree(Rectangulo([0] * k, [10000] * k))
        for punto in puntos:
            arbol.insertar(punto)
        consultas = []
        for _ in range(30):
            consulta = tuple(random.uniform(0, 10000) for _ in range(k))
            consultas.append(consulta)

        t_arbol = medir(arbol, puntos, consultas, "vecino", True)
        t_bruto = medir(arbol, puntos, consultas, "vecino", False)
        tiempos_arbol.append(t_arbol)
        tiempos_brutos.append(t_bruto)
        ventaja = t_bruto / t_arbol
        ventajas.append(ventaja)
        print(f"K={k}: vecino QT/FB {t_arbol:.4f}/{t_bruto:.4f} ms, ventaja {ventaja:.2f}x")

    guardar_grafica(dimensiones, tiempos_arbol, tiempos_brutos,
                    "tiempo_dimensiones.png", "Vecino mas cercano por dimension",
                    "Dimension K")
    return dimensiones, tiempos_arbol, tiempos_brutos, ventajas

def main():
    os.makedirs("graficas", exist_ok=True)
    datos_n = experimento_tamano()
    dimensiones = experimento_dimensiones()

    tamanos, construcciones, radios_qt, radios_fb, vecinos_qt, vecinos_fb = datos_n
    indice = tamanos.index(20000)
    construccion = construcciones[indice]
    ahorro_radio = (radios_fb[indice] - radios_qt[indice]) / 1000
    ahorro_vecino = (vecinos_fb[indice] - vecinos_qt[indice]) / 1000

    print("Graficas guardadas en graficas/")
    print("\nDISCUSION DE RESULTADOS")
    print(f"En N=20.000, radio: Quadtree {radios_qt[indice]:.4f} ms, "
          f"fuerza bruta {radios_fb[indice]:.4f} ms.")
    print(f"En N=20.000, vecino: Quadtree {vecinos_qt[indice]:.4f} ms, "
          f"fuerza bruta {vecinos_fb[indice]:.4f} ms.")
    print(f"Ventaja del Quadtree en N=20.000: radio "
          f"{radios_fb[indice] / radios_qt[indice]:.1f}x, vecino "
          f"{vecinos_fb[indice] / vecinos_qt[indice]:.1f}x.")
    print(f"Construir el arbol para N=20.000 tomo {construccion:.3f} s.")
    if ahorro_radio > 0:
        print(f"Amortizacion de la construccion: unas {construccion / ahorro_radio:.0f} "
              "consultas de radio.")
    else:
        print("La consulta por radio no recupera el costo de construccion.")
    if ahorro_vecino > 0:
        print(f"Amortizacion de la construccion: unas {construccion / ahorro_vecino:.0f} "
              "consultas de vecino cercano.")
    else:
        print("La consulta de vecino no recupera el costo de construccion.")

    ks, tiempos_kt, tiempos_kfb, ventajas = dimensiones
    print(f"Al subir K de {ks[0]} a {ks[-1]}, el tiempo del Quadtree paso de "
          f"{tiempos_kt[0]:.4f} a {tiempos_kt[-1]:.4f} ms.")
    print(f"La ventaja frente a fuerza bruta paso de {ventajas[0]:.2f}x "
          f"a {ventajas[-1]:.2f}x.")

if __name__ == "__main__":
    main()
