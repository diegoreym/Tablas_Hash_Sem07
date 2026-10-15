from registro import Registro
from tabla_hash_doble import TablaHashDoble
from tabla_hash_lineal import TablaHashLineal
from tabla_hash_encadenamiento import TablaHashEncadenamiento


def ejercicio_manual_encadenamiento() -> None:
    tabla = TablaHashEncadenamiento(capacidad=11)
    print("\n=== ENCADENAMIENTO: m = 11, sin redimensionar ===")
    tabla.mostrar()
    for codigo in [10, 21, 32, 43, 54]:
        print(f"\nInsertar {codigo}: h({codigo}) = {codigo} % 11 = {codigo % 11}")
        tabla.insertar(Registro(codigo, f"Producto {codigo}"))
        tabla.mostrar()

    print("\nBuscar 43:", tabla.buscar(43))
    print("\nEliminar 21:", tabla.eliminar(21))
    tabla.mostrar()
    print("\nBuscar 43 despues de eliminar 21:", tabla.buscar(43))
    print("La cadena sigue conectada; encadenamiento no utiliza BORRADO.")
    print("\nInsertar 65: h(65) = 65 % 11 = 10")
    tabla.insertar(Registro(65, "Producto 65"))
    tabla.mostrar()
    print(f"Factor final: 5 / 11 = {tabla.factor_carga():.4f}")
    print(f"Rehashings realizados: {tabla.total_rehashings()}")

def ejercicio_manual_doble_hashing() -> None:
    # sourcery skip: extract-duplicate-method
    """Demuestra el comportamiento de la tabla con doble hashing (m=11)."""
    tabla = TablaHashDoble(capacidad=11)
    claves = [10, 21, 32, 43, 54]
    
    print("\n=== INSERCIÓN DE CLAVES (10, 21, 32, 43, 54) ===")
    for codigo in claves:
        h1 = codigo % 11
        h2 = 1 + (codigo % 10)
        
        # Simulación de las posiciones visitadas para el reporte manual
        visitadas = []
        for j in range(11):
            idx = (h1 + j * h2) % 11
            visitadas.append(idx)
            if tabla.tabla[idx] is None or tabla.tabla[idx] == "BORRADO":
                break
                
        print(f"-> Insertando {codigo}: h1={h1}, h2={h2} | Posiciones visitadas: {visitadas}")
        tabla.insertar(Registro(codigo, f'Producto {codigo}'))
        
    print("\nEstado de la tabla tras inserciones iniciales:")
    tabla.mostrar()
    
    print("\n=== BÚSQUEDA ===")
    print("Buscar clave 43:")
    print("Resultado:", tabla.buscar(43))
    
    print("\n=== ELIMINACIÓN ===")
    print("Eliminar clave 21 (generará un marcador BORRADO):")
    tabla.eliminar(21)
    tabla.mostrar()
    
    print("\n=== BÚSQUEDA TRAS BORRADO ===")
    print("Buscar clave 43 después de eliminar 21 (demostrando que BORRADO no corta el sondeo):")
    h1, h2 = 43 % 11, 1 + (43 % 10)
    print(f"Salto configurado -> h1={h1}, h2={h2}")
    print("Resultado:", tabla.buscar(43))
    
    print("\n=== NUEVA INSERCIÓN ===")
    h1, h2 = 65 % 11, 1 + (65 % 10)
    print(f"Insertar 65 (reutilizará espacio BORRADO o None): h1={h1}, h2={h2}")
    tabla.insertar(Registro(65, 'Producto 65'))
    tabla.mostrar()

def ejercicio_manual_lineal() -> None:  # sourcery skip: extract-duplicate-method
    """Demuestra el sondeo lineal con capacidad fija de 11 posiciones."""

    tabla = TablaHashLineal(capacidad=11)
    claves = [10, 21, 32, 43, 54]

    print("\n========== EJERCICIO MANUAL: SONDEO LINEAL ==========")
    print("Capacidad inicial: 11")
    print("Funcion hash: h(k) = k % 11")
    print("Sondeo lineal: (h(k) + j) % 11")

    # 1. Insercion inicial
    print("\n=== INSERCION DE CLAVES ===")

    for codigo in claves:
        indice_inicial = codigo % 11
        visitadas = []

        for j in range(11):
            indice = (indice_inicial + j) % 11
            visitadas.append(indice)

            if tabla.tabla[indice] is None:
                break

        print(f"\nInsertando codigo: {codigo}")
        print(f"Indice inicial: {indice_inicial}")
        print(f"Posiciones visitadas: {visitadas}")

        tabla.insertar(Registro(codigo, f"Producto {codigo}"))

    print("\nEstado despues de las inserciones:")
    tabla.mostrar()

    # 2. Buscar 43
    print("\n=== BUSQUEDA DEL CODIGO 43 ===")
    print("Resultado:", tabla.buscar(43))

    # 3. Eliminar 21
    print("\n=== ELIMINACION DEL CODIGO 21 ===")
    print("Eliminar 21:", tabla.eliminar(21))

    print("\nEstado despues de eliminar 21:")
    tabla.mostrar()

    # 4. Buscar 43 despues del borrado
    print("\n=== BUSQUEDA DE 43 DESPUES DEL BORRADO ===")

    print("La busqueda debe continuar al encontrar BORRADO.")
    print("Resultado:", tabla.buscar(43))

    # 5. Insertar 65
    print("\n=== INSERCION DEL CODIGO 65 ===")

    codigo = 65
    indice_inicial = codigo % 11

    print(f"Indice inicial: {indice_inicial}")
    print("Se reutilizara la posicion marcada como BORRADO.")

    tabla.insertar(Registro(65, "Producto 65"))

    # 6. Estado final
    print("\n=== ESTADO FINAL DE LA TABLA ===")
    tabla.mostrar()

    print(f"\nCantidad de registros: {tabla.cantidad}")
    print(f"Capacidad: {tabla.capacidad}")
    print(f"Factor de carga: {tabla.factor_carga():.4f}")
    print(f"Rehashings realizados: {tabla.rehashings}")

    print("\n========== FIN DEL EJERCICIO LINEAL ==========")

from registro import Registro
from tabla_hash_cuadratico import TablaHashCuadratico

def ejercicio_manual_cuadratico() -> None:
    print("\n==================================================")
    print("   EJERCICIO MANUAL: TABLA HASH CUADRÁTICA ")
    print("==================================================")
    
    tabla = TablaHashCuadratico(capacidad=11)
    tabla.umbral = 1.0
    claves = [10, 21, 32, 43, 54]
    print("\n--- 1. INSERTANDO SECUENCIA: 10, 21, 32, 43, 54 ---")
    for codigo in claves:
        print(f"Insertando {codigo} (Índice base: {codigo % 11})...")
        tabla.insertar(Registro(codigo, f"Producto {codigo}"))
    
    tabla.mostrar()

    print("\n--- 2. BUSCANDO CÓDIGO 43 ---")
    resultado = tabla.buscar(43)
    if resultado:
        print(f"ÉXITO: Encontrado -> {resultado.codigo}: {resultado.nombre}")
    else:
        print("ERROR: No encontrado")

    print("\n--- 3. ELIMINANDO CÓDIGO 21 ---")
    tabla.eliminar(21)
    print("Se ha colocado el marcador 'BORRADO' en la posición del 21.")
    tabla.mostrar()

    print("\n--- 4. BUSCANDO CÓDIGO 43 (DESPUÉS DEL BORRADO) ---")
    print("Demostración: El marcador BORRADO permite que el algoritmo siga saltando hasta hallar el 43.")
    resultado = tabla.buscar(43)
    if resultado:
        print(f"ÉXITO: Encontrado -> {resultado.codigo}: {resultado.nombre}")
    else:
        print("ERROR: No encontrado")

    print("\n--- 5. INSERTANDO CÓDIGO 65 ---")
    print("Al insertar el 65, su índice base es 10. Como está ocupado, saltará.")
    print("En el salto j=1 (posición 0), encontrará el 'BORRADO' del código 21 y reciclará el espacio.")
    tabla.insertar(Registro(65, "Producto 65"))
    tabla.mostrar()

    print("\n--- 6. DEMOSTRACIÓN: LIMITACIÓN DE COBERTURA ---")
    print("Si evaluamos los saltos j=0 hasta j=5 para un índice base de 10 con m=11:")
    for j in range(6):
        indice = (10 + j**2) % 11
        print(f"  Salto j={j} -> (10 + {j}^2) % 11 = Posición {indice}")
 
    print("==================================================\n")
