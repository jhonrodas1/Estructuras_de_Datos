import pandas as pd
import matplotlib.pyplot as plt
import os

ARCHIVO_EXP1 = "resultados/resultados_lab3.csv"
ARCHIVO_EXP2 = "resultados/resultados_M.csv"
CARPETA = "graficas"
os.makedirs(CARPETA, exist_ok=True)

ESTRUCTURAS = ["Lista", "ABB", "B+"]
COLORES = {"Lista": "#e74c3c", "ABB": "#3498db", "B+": "#2ecc71"}
MARCADORES = {"Lista": "o", "ABB": "s", "B+": "^"}

df1 = pd.read_csv(ARCHIVO_EXP1)
df2 = pd.read_csv(ARCHIVO_EXP2)


def configurar(ax, titulo, xlabel, ylabel, escala_x="log", escala_y="log"):
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    if escala_x:
        ax.set_xscale(escala_x)
    if escala_y:
        ax.set_yscale(escala_y)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(fontsize=10, loc="best", framealpha=0.9)


def guardar(fig, nombre):
    ruta = os.path.join(CARPETA, nombre)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Guardada: {ruta}")


def grafica_metrica(df, metrica, orden, titulo, archivo, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    sub = df[df["Orden"] == orden]
    for est in ESTRUCTURAS:
        d = sub[sub["Estructura"] == est].sort_values("N")
        prom = d[f"{metrica}_Prom"]
        std = d[f"{metrica}_Std"]
        ax.errorbar(
            d["N"], prom, yerr=std,
            marker=MARCADORES[est], color=COLORES[est],
            label=est, linewidth=2, markersize=8, capsize=5,
        )
    configurar(ax, titulo, "Tamaño de entrada N (escala log)", ylabel)
    guardar(fig, archivo)


def grafica_comparacion_dual(df, metrica, archivo, ylabel):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, orden in zip(axes, ["ALEATORIO", "ORDENADO"]):
        sub = df[df["Orden"] == orden]
        for est in ESTRUCTURAS:
            d = sub[sub["Estructura"] == est].sort_values("N")
            ax.errorbar(
                d["N"], d[f"{metrica}_Prom"], yerr=d[f"{metrica}_Std"],
                marker=MARCADORES[est], color=COLORES[est],
                label=est, linewidth=2, markersize=7, capsize=4,
            )
        configurar(ax, f"Datos {orden.title()}", "N (log)", ylabel)
    fig.suptitle(f"Comparación de {ylabel}: Aleatorio vs Ordenado",
                 fontsize=14, fontweight="bold")
    guardar(fig, archivo)


def grafica_alturas(df, archivo):
    fig, ax = plt.subplots(figsize=(10, 6))
    for orden in ["ALEATORIO", "ORDENADO"]:
        sub = df[(df["Orden"] == orden) & (df["Estructura"].isin(["ABB", "B+"]))]
        for est in ["ABB", "B+"]:
            d = sub[sub["Estructura"] == est].sort_values("N")
            estilo = "-" if orden == "ALEATORIO" else "--"
            alturas = pd.to_numeric(d["Altura"], errors="coerce")
            ax.plot(
                d["N"], alturas,
                marker=MARCADORES[est], color=COLORES[est],
                linestyle=estilo,
                label=f"{est} ({orden.lower()})",
                linewidth=2, markersize=8,
            )
    configurar(
        ax,
        "Altura del árbol vs Tamaño N",
        "Tamaño de entrada N (escala log)",
        "Altura (número de niveles, escala log)",
    )
    guardar(fig, archivo)


def grafica_experimento_M(df, archivo):
    fig, ax = plt.subplots(figsize=(10, 6))
    for est in ESTRUCTURAS:
        d = df[df["Estructura"] == est].sort_values("M")
        ax.errorbar(
            d["M"], d["Buscar_Prom"], yerr=d["Buscar_Std"],
            marker=MARCADORES[est], color=COLORES[est],
            label=est, linewidth=2, markersize=8, capsize=5,
        )
    configurar(
        ax,
        "Tiempo total de búsqueda vs M (N=10000, datos aleatorios)",
        "Número de búsquedas M (escala log)",
        "Tiempo total (segundos, escala log)",
    )
    guardar(fig, archivo)


if __name__ == "__main__":
    grafica_metrica(
        df1, "Buscar", "ALEATORIO",
        "Búsqueda: datos aleatorios (M=1000 por corrida)",
        "busqueda_aleatorio.png",
        "Tiempo de búsqueda (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Buscar", "ORDENADO",
        "Búsqueda: datos ordenados (M=1000 por corrida)",
        "busqueda_ordenado.png",
        "Tiempo de búsqueda (segundos, escala log)",
    )
    grafica_comparacion_dual(
        df1, "Buscar", "comparacion_busqueda.png",
        "Tiempo de búsqueda (s)",
    )
    grafica_metrica(
        df1, "Construir", "ALEATORIO",
        "Construcción: datos aleatorios",
        "construccion_aleatorio.png",
        "Tiempo de construcción (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Construir", "ORDENADO",
        "Construcción: datos ordenados",
        "construccion_ordenado.png",
        "Tiempo de construcción (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Rango", "ALEATORIO",
        "Búsqueda por rango (ancho 100): datos aleatorios",
        "rango_aleatorio.png",
        "Tiempo de rango (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Rango", "ORDENADO",
        "Búsqueda por rango (ancho 100): datos ordenados",
        "rango_ordenado.png",
        "Tiempo de rango (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Todos", "ALEATORIO",
        "Listar todos: datos aleatorios",
        "todos_aleatorio.png",
        "Tiempo de listar todos (segundos, escala log)",
    )
    grafica_metrica(
        df1, "Todos", "ORDENADO",
        "Listar todos: datos ordenados",
        "todos_ordenado.png",
        "Tiempo de listar todos (segundos, escala log)",
    )
    grafica_alturas(df1, "alturas.png")
    grafica_experimento_M(df2, "experimento_M.png")
    print("Listo. Todas las graficas estan en la carpeta graficas/")