import subprocess
import sys
from pathlib import Path
from typing import Protocol

from registro import Registro

try:
    from tabla_hash_encadenamiento import TablaHashEncadenamiento
except ImportError:
    TablaHashEncadenamiento = None  # type: ignore[assignment,misc]
try:
    from tabla_hash_lineal import TablaHashLineal
except ImportError:
    TablaHashLineal = None  # type: ignore[assignment,misc]
try:
    from tabla_hash_cuadratico import TablaHashCuadratico
except ImportError:
    TablaHashCuadratico = None  # type: ignore[assignment,misc]
try:
    from tabla_hash_doble import TablaHashDoble
except ImportError:
    TablaHashDoble = None  # type: ignore[assignment,misc]

# Módulos de ejercicios manuales y experimento (usan las cuatro tablas reales).
try:
    import ejercicios_manuales as modulo_ejercicios
except ImportError:
    modulo_ejercicios = None  # type: ignore[assignment]
try:
    import experimento_hash as modulo_experimento
except ImportError:
    modulo_experimento = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Contrato común de las tablas (solo para type hints)
# ---------------------------------------------------------------------------
class TablaHash(Protocol):
    """Interfaz que comparten las cuatro estrategias."""

    def insertar(self, registro: Registro) -> None: ...

    def buscar(self, codigo: int) -> Registro | None: ...

    def eliminar(self, codigo: int) -> bool: ...

    def mostrar(self) -> None: ...

    def factor_carga(self) -> float: ...

    def rehashing(self) -> None: ...


# ---------------------------------------------------------------------------
# Lectura segura de datos por consola
# ---------------------------------------------------------------------------
def leer_entero(mensaje: str) -> int:
    """Pide un entero por consola; repite hasta que el valor sea válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            return int(texto)
        except ValueError:
            print('  Entrada invalida: escriba un numero entero.')


def leer_cadena(mensaje: str) -> str:
    """Pide un texto no vacío por consola."""
    while True:
        texto = input(mensaje).strip()
        if texto != '':
            return texto
        print('  El texto no puede estar vacio.')


def leer_si_no(mensaje: str) -> bool:
    """Pregunta s/n y devuelve True si la respuesta es afirmativa."""
    return input(mensaje).strip().lower() in ('s', 'si', 'sí', 'y', 'yes')


# ---------------------------------------------------------------------------
# 1. Caso empresarial: control de inventario del laboratorio
# ---------------------------------------------------------------------------
def _instanciar(clase: type | None, nombre: str) -> TablaHash:
    """Crea la tabla; avisa si la clase aún no está implementada."""
    if clase is None:
        raise ImportError(f'{nombre} aun no esta implementada')
    return clase()


def crear_tabla(opcion: int) -> TablaHash:
    """Crea la tabla hash vacía de la estrategia elegida (capacidad inicial 11)."""
    match opcion:
        case 1:
            return _instanciar(TablaHashEncadenamiento, 'TablaHashEncadenamiento')
        case 2:
            return _instanciar(TablaHashLineal, 'TablaHashLineal')
        case 3:
            return _instanciar(TablaHashCuadratico, 'TablaHashCuadratico')
        case 4:
            return _instanciar(TablaHashDoble, 'TablaHashDoble')
        case _:
            raise ValueError('Estrategia invalida')


def cargar_datos_ejemplo(tabla: TablaHash) -> None:
    """Carga productos de ejemplo (todos colisionan en h(k) = k mod 11)."""
    productos = [
        (10, 'Microscopio'),
        (21, 'Pipeta graduada'),
        (32, 'Probeta 100 ml'),
        (43, 'Balanza analitica'),
        (54, 'Termometro digital'),
    ]
    for codigo, nombre in productos:
        tabla.insertar(Registro(codigo, nombre))
        print(f'  Insertado: {Registro(codigo, nombre)}')


def submenu_inventario(tabla: TablaHash) -> None:
    """Submenú de inventario; funciona con cualquier tabla hash del contrato."""
    while True:
        print('\n--- Inventario del laboratorio ---')
        print('1. Registrar producto')
        print('2. Buscar producto')
        print('3. Eliminar producto')
        print('4. Mostrar tabla')
        print('5. Ver factor de carga')
        print('6. Cargar datos de ejemplo')
        print('0. Volver')
        opcion = leer_entero('Opcion: ')

        try:
            match opcion:
                case 1:
                    codigo = leer_entero('Codigo: ')
                    nombre = leer_cadena('Nombre: ')
                    tabla.insertar(Registro(codigo, nombre))
                    print('  Producto registrado.')
                case 2:
                    codigo = leer_entero('Codigo a buscar: ')
                    encontrado = tabla.buscar(codigo)
                    print(f'  Encontrado: {encontrado}' if encontrado is not None
                          else '  No se encontro el producto (None).')
                case 3:
                    codigo = leer_entero('Codigo a eliminar: ')
                    eliminado = tabla.eliminar(codigo)
                    print(f'  Eliminado: {eliminado}')
                case 4:
                    tabla.mostrar()
                case 5:
                    print(f'  Factor de carga: {tabla.factor_carga():.4f}')
                case 6:
                    cargar_datos_ejemplo(tabla)
                case 0:
                    return
                case _:
                    print('  Opcion invalida.')
        except (ValueError, TypeError, RuntimeError) as error:
            print(f'  Error: {error}')


def caso_empresarial() -> None:
    """Pide la estrategia, crea la tabla vacía y abre el submenú de inventario."""
    print('\n=== Caso empresarial: control de inventario del laboratorio ===')
    print('1. Encadenamiento')
    print('2. Lineal')
    print('3. Cuadratico')
    print('4. Doble hashing')
    opcion = leer_entero('Seleccione estrategia: ')
    try:
        tabla = crear_tabla(opcion)
    except ValueError as error:
        print(f'  {error}')
        return
    except ImportError as error:
        print(f'  {error}.')
        return
    submenu_inventario(tabla)


# ---------------------------------------------------------------------------
# 2. Ejercicios manuales (los implementan Harold, Fernando, Samuel y Diego)
# ---------------------------------------------------------------------------
def _ejecutar_funcion(modulo: object | None, nombre_modulo: str,
                      funciones: list[str]) -> None:
    """Ejecuta la primera función de `funciones` que exista en el módulo."""
    if modulo is None:
        print(f'  No se pudo importar {nombre_modulo}.py '
              '(revise que las cuatro tablas esten implementadas).')
        return
    for nombre in funciones:
        funcion = getattr(modulo, nombre, None)
        if callable(funcion):
            funcion()
            return
    print(f'  {nombre_modulo}.py aun no define: {" / ".join(funciones)}')


def ejercicios_manuales() -> None:
    """Muestra las trazas paso a paso con m = 11 usando las tablas reales."""
    ejercicios = {
        1: ('Encadenamiento', 'ejercicio_manual_encadenamiento'),
        2: ('Lineal', 'ejercicio_manual_lineal'),
        3: ('Cuadratico', 'ejercicio_manual_cuadratico'),
        4: ('Doble hashing', 'ejercicio_manual_doble_hashing'),
    }
    while True:
        print('\n=== Ejercicios manuales (m = 11) ===')
        for numero, (titulo, _) in ejercicios.items():
            print(f'{numero}. {titulo}')
        print('5. Ejecutar los cuatro')
        print('0. Volver')
        opcion = leer_entero('Opcion: ')

        if opcion == 0:
            return
        if opcion == 5:
            for numero, (titulo, funcion) in ejercicios.items():
                print(f'\n##### Ejercicio {numero}: {titulo} #####')
                _ejecutar_funcion(modulo_ejercicios, 'ejercicios_manuales', [funcion])
        elif opcion in ejercicios:
            titulo, funcion = ejercicios[opcion]
            print(f'\n##### Ejercicio {opcion}: {titulo} #####')
            _ejecutar_funcion(modulo_ejercicios, 'ejercicios_manuales', [funcion])
        else:
            print('  Opcion invalida.')


# ---------------------------------------------------------------------------
# 3. Experimento comparativo (lo implementa Fernandito)
# ---------------------------------------------------------------------------
def experimento_comparativo() -> None:
    """Llama al experimento que usa las cuatro clases reales."""
    print('\n=== Experimento comparativo ===')
    print('n = 100, 1000 y 10000 | 5 repeticiones | random.Random(2026)')
    print('(el experimento con n = 10000 puede tardar unos segundos)')
    _ejecutar_funcion(modulo_experimento, 'experimento_hash',
                      ['ejecutar_experimento', 'main'])


# ---------------------------------------------------------------------------
# 4. Guía de pruebas
# ---------------------------------------------------------------------------
ESCENARIOS_PRUEBA: list[str] = [
    'Tabla vacia',
    'Insercion sin colision',
    'Insercion con colision',
    'Busqueda encontrada',
    'Busqueda ausente',
    'Eliminacion existente',
    'Eliminacion ausente',
    'Busqueda tras eliminar otro elemento de la misma secuencia',
    'Reinsercion tras borrado',
    'Clave duplicada y actualizacion',
    'Factor de carga alto',
    'Rehashing y conservacion integral de registros',
]


def guia_pruebas() -> None:
    """Explica cómo ejecutar unittest y qué escenarios se validan."""
    comando = [sys.executable, '-m', 'unittest', 'discover', 'tests', '-v']
    print('\n=== Guia de pruebas (unittest) ===')
    print('Archivos en tests/: test_encadenamiento.py, test_lineal.py,')
    print('test_cuadratico.py, test_doble.py y test_integracion_hash.py')
    print('\nEscenarios minimos validados en cada tabla:')
    for numero, escenario in enumerate(ESCENARIOS_PRUEBA, start=1):
        print(f'  {numero:>2}. {escenario}')
    print('\nComando de ejecucion (desde la carpeta src):')
    print('  python -m unittest discover tests -v')

    if leer_si_no('\nEjecutar las pruebas ahora? (s/n): '):
        carpeta = Path(__file__).resolve().parent
        if not (carpeta / 'tests').is_dir():
            print('  No existe la carpeta tests/ junto a main.py.')
            return
        subprocess.run(comando, cwd=carpeta, check=False)


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------
def mostrar_menu() -> None:
    print('\n==============================================')
    print('  TABLAS HASH - Inventario del laboratorio')
    print('==============================================')
    print('1. Caso empresarial')
    print('2. Ejercicios manuales')
    print('3. Experimento comparativo')
    print('4. Guia de pruebas')
    print('0. Salir')


def main() -> None:
    while True:
        mostrar_menu()
        opcion = leer_entero('Opcion: ')
        match opcion:
            case 1:
                caso_empresarial()
            case 2:
                ejercicios_manuales()
            case 3:
                experimento_comparativo()
            case 4:
                guia_pruebas()
            case 0:
                print('Hasta luego.')
                return
            case _:
                print('  Opcion invalida.')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrograma terminado.')