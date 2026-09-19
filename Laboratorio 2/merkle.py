import hashlib


def sha256(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def construir_niveles(transacciones):
    nivel_actual = []
    for tx in transacciones:
        nivel_actual.append(sha256(tx))

    niveles = [nivel_actual]

    while len(nivel_actual) > 1:

        # Hacemos una copia para combinar, sin dañar el nivel original
        # y tambien pues si es impar se duplica
        nivel_para_combinar = list(nivel_actual)
        if len(nivel_para_combinar) % 2 != 0:
            nivel_para_combinar.append(nivel_para_combinar[-1])

        siguiente_nivel = []
        for i in range(0, len(nivel_para_combinar), 2):
            izquierda = nivel_para_combinar[i]
            derecha = nivel_para_combinar[i + 1]
            hash_combinado = sha256(izquierda + derecha)
            siguiente_nivel.append(hash_combinado)

        niveles.append(siguiente_nivel)
        nivel_actual = siguiente_nivel

    return niveles


def obtener_raiz(transacciones):
    niveles = construir_niveles(transacciones)
    ultimo_nivel = niveles[-1]
    return ultimo_nivel[0]


def generar_prueba(transacciones, indice):
    """
    Genera la prueba de inclusion para la transaccion
    que este se encuentra  en la posicion "indice".
    ya con eso tenemos si indica al hermano de la derecga o isquierda 
    al combinarlo
    """
    niveles = construir_niveles(transacciones)
    prueba = []

    for nivel in niveles[:-1]:  # recorremos todos los niveles menos la raiz
        nivel_ajustado = list(nivel)
        if len(nivel_ajustado) % 2 != 0:
            nivel_ajustado.append(nivel_ajustado[-1])

        es_hijo_derecho = (indice % 2 == 1)

        if es_hijo_derecho:
            indice_hermano = indice - 1
            lado = "izquierda"
        else:
            indice_hermano = indice + 1
            lado = "derecha"

        hash_hermano = nivel_ajustado[indice_hermano]
        prueba.append((hash_hermano, lado))

        indice = indice // 2 

    return prueba


def verificar_prueba(dato, prueba, raiz_esperada):
  
    #Reconstruye el hash desde la hoja (el dato) hacia arriba usando la
    #prueba, y verifica si el resultado final coincide con la raiz.

    hash_actual = sha256(dato)

    for hash_hermano, lado in prueba:
        if lado == "izquierda":
            hash_actual = sha256(hash_hermano + hash_actual)
        else:
            hash_actual = sha256(hash_actual + hash_hermano)

    return hash_actual == raiz_esperada


def imprimir_arbol(niveles):
    #Imprime el arbol en ASCII, mostrando cada nivel desde la raiz hacia las hojas.
    total_niveles = len(niveles)

    for i in range(total_niveles - 1, -1, -1):
        nivel = niveles[i]
        hashes_cortos = [h[:8] for h in nivel]

        if i == total_niveles - 1:
            print("Raiz    :", hashes_cortos)
        else:
            print(f"Nivel {i} :", hashes_cortos)

if __name__ == "__main__":

    #  Creamos 5 transacciones simuladas para ver que todo funcione bien
    transacciones = [
        "juancho paga 10 a Luis",
        "Luis paga 5 a mariana",
        "mariana paga 20 a fran",
        "fran paga 8 a juancho",
        "Carlos paga 15 a Juancho",
    ]

    print("Transacciones")
    for i, tx in enumerate(transacciones):
        print(f"Transaccion {i + 1} (indice {i}): {tx}")

    # Construimos el arbol y mostramos la raiz
    niveles = construir_niveles(transacciones)
    raiz = niveles[-1][0]

    print("\nMerkle Root")
    print(raiz)

    print("\nDiagrama del arbol")
    imprimir_arbol(niveles)

    # Modificamos una transaccion y comprobamos que la raiz cambia
    transacciones_modificadas = transacciones.copy()
    transacciones_modificadas[1] = "Luis paga 500 a mariana"  

    raiz_modificada = obtener_raiz(transacciones_modificadas)

    print("\nModificamos la transaccion 2 ")
    print("Raiz original :", raiz)
    print("Raiz nueva    :", raiz_modificada)
    print("¿Son iguales? :", raiz == raiz_modificada)

    #  Generamos la prueba de inclusion para la transaccion 3
    prueba = generar_prueba(transacciones, 2)

    print("\nPrueba de inclusion para la transaccion 3")
    for hash_hermano, lado in prueba:
        print(f"hermano ({lado}): {hash_hermano[:8]}")

    # Verificamos con el dato correcto ==< deberia ser valido
    dato_correcto = transacciones[2]
    resultado = verificar_prueba(dato_correcto, prueba, raiz)
    print("\nVerificando dato correcto:", dato_correcto)
    print("Resultado:", "VALIDO" if resultado else "INVALIDO")

    # Verificamos con un dato incorrecto ==> deberia fallar
    dato_incorrecto = "mariana paga 2000 a fran"
    resultado = verificar_prueba(dato_incorrecto, prueba, raiz)
    print("\nVerificando dato incorrecto:", dato_incorrecto)
    print("Resultado:", "VALIDO" if resultado else "INVALIDO")