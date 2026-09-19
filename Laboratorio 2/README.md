# Laboratorio 2: Árbol de Merkle (Merkle Tree)

Este repositorio contiene la implementación funcional en Python de un Árbol de Merkle, diseñado para garantizar la integridad de un conjunto de transacciones de datos. El código utiliza únicamente funciones nativas y la librería `hashlib` para mantener la lógica clara y fácil de auditar.

## Especificaciones Implementadas
- **Hashing:** SHA-256 (retornando formato hexadecimal).
- **Concatenación:** Los nodos internos se calculan concatenando los hashes de sus dos hijos (izquierda + derecha) y aplicando SHA-256.
- **Balanceo (Nodos impares):** Si un nivel tiene un número impar de nodos, el último nodo se duplica en la lista para poder emparejarlo con éxito.
- **Merkle Root:** Hash único en la cúspide que representa de forma inmutable todas las transacciones base.

## Transacciones Base
El experimento se inicializa con las siguientes 5 transacciones:
1. `juancho paga 10 a Luis`
2. `Luis paga 5 a mariana`
3. `mariana paga 20 a fran`
4. `fran paga 8 a juancho`
5. `Carlos paga 15 a Juancho`

## Estructura Visual del Árbol
Al contar con 5 transacciones, el árbol duplica la última transacción (Tx5) en la base para hacer pares, y en el siguiente nivel vuelve a duplicar la rama resultante para poder concatenar con el bloque izquierdo, logrando así el balance perfecto.

```text
                                     [ ROOT ]
                                    /        \
                                   /          \
                       [ H_0123 ]                [ H_4444 ]
                       /        \                /        \
                      /          \              /          \
                [ H_01 ]        [ H_23 ]    [ H_44 ]       [ H_44 ]*
                /      \        /      \    /      \       (Copia)
               /        \      /        \  /        \
            [H0]        [H1] [H2]      [H3][H4]     [H4]*
             |           |    |         |   |       (Copia)
            Tx1         Tx2  Tx3       Tx4 Tx5
