from registro import Registro
from tabla_hash_doble import TablaHashDoble

def ejercicio_manual_doble_hashing() -> None:
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