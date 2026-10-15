from _future_ import annotations
import argparse
import csv
import gc
import random
import statistics
import time
from pathlib import Path
import tabla_hash_encadenamiento as modulo_encadenamiento
from registro import Registro
from tabla_hash_cuadratico import TablaHashCuadratico
from tabla_hash_doble import TablaHashDoble
from tabla_hash_encadenamiento import TablaHashEncadenamiento
from tabla_hash_lineal import TablaHashLineal
from utils_hash import capacidad_rehashing

SEMILLA = 2026
TAMANOS = (100, 1000, 10000)
REPETICIONES = 5
CAPACIDAD_INICIAL = 11

ESTRATEGIAS = [
    ("Encadenamiento", TablaHashEncadenamiento),
    ("Lineal", TablaHashLineal),
    ("Cuadratico", TablaHashCuadratico),
    ("Doble hash", TablaHashDoble),
]
FASES = ("insercion", "busq_exitosa", "busq_fallida", "eliminacion")


# --------------------------------------------------------------------------
# Adaptadores: cada clase expone cantidad/capacidad con nombres distintos
# (atributo o metodo), asi que se leen sin tocar las clases.
# --------------------------------------------------------------------------
def _leer(tabla, *nombres):
    for nombre in nombres:
        if hasattr(tabla, nombre):
            valor = getattr(tabla, nombre)
            return valor() if callable(valor) else valor
    raise AttributeError(f"{type(tabla)._name_} no expone ninguno de {nombres}")


def capacidad_de(tabla) -> int:
    return _leer(tabla, "capacidad")


def cantidad_de(tabla) -> int:
    return _leer(tabla, "cantidad", "tamano")


def rehashings_nativos(tabla):
    """Contador propio de la clase si lo tiene (lineal y encadenamiento); si no, None."""
    for nombre in ("total_rehashings", "rehashings"):
        if hasattr(tabla, nombre):
            return _leer(tabla, nombre)
    return None


def rehashings_desde_capacidad(capacidad_final: int) -> int:
    """Cuantos rehashings llevan de la capacidad inicial a la final (m -> primo >= 2m+1)."""
    capacidad, contador = CAPACIDAD_INICIAL, 0
    while capacidad < capacidad_final:
        capacidad = capacidad_rehashing(capacidad)
        contador += 1
    return contador


# --------------------------------------------------------------------------
# Datos del experimento
# --------------------------------------------------------------------------
def generar_datos(azar: random.Random, n: int):
    claves = azar.sample(range(100 * n), 2 * n)          # todas distintas
    presentes, ausentes = claves[:n], claves[n:]          # ausentes: nunca se insertan
    registros = [Registro(k, f"Producto {k}") for k in presentes]
    orden_borrado = azar.sample(presentes, n)             # mismas claves, otro orden
    return registros, presentes, ausentes, orden_borrado


def _cronometrar(operacion, argumentos) -> float:
    inicio = time.perf_counter()
    for argumento in argumentos:
        operacion(argumento)
    return (time.perf_counter() - inicio) * 1000


# --------------------------------------------------------------------------
# Pasada 1: tiempos con la clase real
# --------------------------------------------------------------------------
def pasada_tiempos(clase, datos) -> dict:
    registros, presentes, ausentes, orden_borrado = datos
    n = len(registros)
    tabla = clase()
    gc.collect()
    gc.disable()
    try:
        t_insercion = _cronometrar(tabla.insertar, registros)
        factor, capacidad = tabla.factor_carga(), capacidad_de(tabla)
        if cantidad_de(tabla) != n:
            raise RuntimeError(f"{clase._name_}: cantidad {cantidad_de(tabla)} != {n}")
        t_exitosa = _cronometrar(tabla.buscar, presentes)
        t_fallida = _cronometrar(tabla.buscar, ausentes)
        t_eliminacion = _cronometrar(tabla.eliminar, orden_borrado)
    finally:
        gc.enable()
    if cantidad_de(tabla) != 0:
        raise RuntimeError(f"{clase._name_}: quedaron {cantidad_de(tabla)} registros")

    derivados = rehashings_desde_capacidad(capacidad)
    nativos = rehashings_nativos(tabla)
    if nativos is not None and nativos != derivados:
        print(f"  AVISO {clase._name_}: contador propio={nativos}, "
              f"deducido por capacidad={derivados}")
    return {
        "insercion": t_insercion, "busq_exitosa": t_exitosa,
        "busq_fallida": t_fallida, "eliminacion": t_eliminacion,
        "factor": factor, "capacidad": capacidad, "rehashings": derivados,
    }


# --------------------------------------------------------------------------
# Pasada 2: sondeos (solo cuenta; no cambia la logica de las clases)
# --------------------------------------------------------------------------
class _ListaContadora(list):
    """Lista que cuenta las lecturas tabla[i]. Iterar o escribir no cuenta."""

    def _init_(self, datos, contador):
        super()._init_(datos)
        self._contador = contador

    def _getitem_(self, indice):
        self._contador[0] += 1
        return super()._getitem_(indice)


def _clase_contadora(clase):
    """Subclase de una tabla de direccionamiento abierto que cuenta lecturas de casillas.
    El setter re-envuelve la lista cada vez que rehashing() crea una tabla nueva."""

    class Contada(clase):
        def _init_(self, *args, **kwargs):
            self.sondeos = [0]
            super()._init_(*args, **kwargs)

        @property
        def tabla(self):
            return self._tabla_contada

        @tabla.setter
        def tabla(self, valor):
            self._tabla_contada = _ListaContadora(valor, self.sondeos)

    return Contada


def _instrumentar_cadenas(contador):
    """Cuenta los nodos recorridos en ListaEnlazada (encadenamiento). Devuelve restaurar()."""
    lista = modulo_encadenamiento.ListaEnlazada
    nombres = ("insertar_o_actualizar", "buscar", "eliminar")
    originales = {nombre: getattr(lista, nombre) for nombre in nombres}

    def visitados(cadena, codigo):
        recorridos = 0
        for registro in cadena:                  # usa _iter_, que no se modifica
            recorridos += 1
            if registro.codigo == codigo:
                break
        return recorridos

    def envolver(nombre, extraer_codigo):
        original = originales[nombre]

        def instrumentada(self, argumento):
            contador[0] += max(1, visitados(self, extraer_codigo(argumento)))
            return original(self, argumento)
        return instrumentada

    lista.insertar_o_actualizar = envolver("insertar_o_actualizar", lambda r: r.codigo)
    lista.buscar = envolver("buscar", lambda codigo: codigo)
    lista.eliminar = envolver("eliminar", lambda codigo: codigo)

    def restaurar():
        for nombre, funcion in originales.items():
            setattr(lista, nombre, funcion)
    return restaurar


def pasada_sondeos(clase, datos) -> dict:
    registros, presentes, ausentes, orden_borrado = datos
    n = len(registros)
    if clase is TablaHashEncadenamiento:
        contador = [0]
        restaurar = _instrumentar_cadenas(contador)
        tabla = clase()
    else:
        restaurar = lambda: None
        tabla = _clase_contadora(clase)()
        contador = tabla.sondeos

    try:
        resultado, acumulado = {}, 0

        def fase(nombre, operacion, argumentos):
            nonlocal acumulado
            salidas = [operacion(a) for a in argumentos]
            resultado[nombre] = (contador[0] - acumulado) / n
            acumulado = contador[0]
            return salidas

        fase("insercion", tabla.insertar, registros)
        exitosas = fase("busq_exitosa", tabla.buscar, presentes)
        fallidas = fase("busq_fallida", tabla.buscar, ausentes)
        borrados = fase("eliminacion", tabla.eliminar, orden_borrado)
    finally:
        restaurar()

    # Verificacion de integridad (aprovecha esta pasada, que no se cronometra)
    if any(r is None for r in exitosas):
        raise RuntimeError(f"{clase._name_}: una clave insertada no se encontro")
    if any(r is not None for r in fallidas):
        raise RuntimeError(f"{clase._name_}: se encontro una clave ausente")
    if not all(borrados):
        raise RuntimeError(f"{clase._name_}: no se pudo eliminar una clave presente")
    return resultado


# --------------------------------------------------------------------------
# Pasada 3: costo de los rehashings dentro de la insercion
# --------------------------------------------------------------------------
def pasada_rehashing(clase, datos) -> float:
    registros = datos[0]

    class Cronometrada(clase):
        t_rehashing = 0.0
        _profundidad = 0

        def rehashing(self):
            self._profundidad += 1
            inicio = time.perf_counter()
            try:
                super().rehashing()
            finally:
                self._profundidad -= 1
                if self._profundidad == 0:       # solo la llamada mas externa
                    self.t_rehashing += time.perf_counter() - inicio

    tabla = Cronometrada()
    gc.collect()
    gc.disable()
    try:
        for registro in registros:
            tabla.insertar(registro)
    finally:
        gc.enable()
    return tabla.t_rehashing * 1000


# --------------------------------------------------------------------------
# Ejecucion y reporte
# --------------------------------------------------------------------------
def ejecutar(tamanos, repeticiones):
    azar = random.Random(SEMILLA)
    medidas = {(nombre, n): [] for nombre, _ in ESTRATEGIAS for n in tamanos}
    for n in tamanos:
        for repeticion in range(1, repeticiones + 1):
            print(f"  n={n:>6}  repeticion {repeticion}/{repeticiones}")
            datos = generar_datos(azar, n)       # las 4 estrategias usan los mismos datos
            for nombre, clase in ESTRATEGIAS:
                medida = pasada_tiempos(clase, datos)
                medida["sondeos"] = pasada_sondeos(clase, datos)
                medida["ms_rehashing"] = pasada_rehashing(clase, datos)
                medidas[(nombre, n)].append(medida)
    return medidas


def promedios(lista):
    def media(extraer):
        return statistics.mean(extraer(m) for m in lista)

    def desviacion(extraer):
        return statistics.stdev(extraer(m) for m in lista) if len(lista) > 1 else 0.0

    resumen = {
        fase: media(lambda m, f=fase: m[f]) for fase in FASES
    }
    resumen.update({f"{fase}_desv": desviacion(lambda m, f=fase: m[f]) for fase in FASES})
    resumen.update({f"sondeos_{fase}": media(lambda m, f=fase: m["sondeos"][f]) for fase in FASES})
    resumen["rehashings"] = media(lambda m: m["rehashings"])
    resumen["ms_rehashing"] = media(lambda m: m["ms_rehashing"])
    resumen["factor"] = media(lambda m: m["factor"])
    resumen["capacidad"] = media(lambda m: m["capacidad"])
    return resumen


def imprimir_tablas(medidas, tamanos):
    resumen = {clave: promedios(valores) for clave, valores in medidas.items()}

    print("\nTABLA 1. Tiempo medio en ms para n operaciones (incluye rehashing en la insercion)")
    print(f"{'Estrategia':<15}{'n':>7}{'Insercion':>12}{'Busq +':>11}{'Busq -':>11}"
          f"{'Eliminacion':>13}{'Rehash':>8}{'Rehash ms':>11}{'Factor':>8}{'Capacidad':>11}")
    print("-" * 107)
    for nombre, _ in ESTRATEGIAS:
        for n in tamanos:
            r = resumen[(nombre, n)]
            print(f"{nombre:<15}{n:>7}{r['insercion']:>12.3f}{r['busq_exitosa']:>11.3f}"
                  f"{r['busq_fallida']:>11.3f}{r['eliminacion']:>13.3f}"
                  f"{r['rehashings']:>8.0f}{r['ms_rehashing']:>11.3f}"
                  f"{r['factor']:>8.3f}{r['capacidad']:>11.0f}")
        print()

    print("TABLA 2. Sondeos medios por operacion")
    print(f"{'Estrategia':<15}{'n':>7}{'Insercion':>12}{'Busq +':>11}{'Busq -':>11}{'Eliminacion':>13}")
    print("-" * 69)
    for nombre, _ in ESTRATEGIAS:
        for n in tamanos:
            r = resumen[(nombre, n)]
            print(f"{nombre:<15}{n:>7}{r['sondeos_insercion']:>12.2f}{r['sondeos_busq_exitosa']:>11.2f}"
                  f"{r['sondeos_busq_fallida']:>11.2f}{r['sondeos_eliminacion']:>13.2f}")
        print()
    return resumen


def guardar_csv(resumen, tamanos, ruta: Path):
    columnas = (
        ["estrategia", "n"]
        + [f"{fase}_ms" for fase in FASES] + [f"{fase}_ms_desv" for fase in FASES]
        + [f"sondeos_{fase}" for fase in FASES]
        + ["rehashings", "rehashing_ms", "factor_carga", "capacidad_final"]
    )
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)
        for nombre, _ in ESTRATEGIAS:
            for n in tamanos:
                r = resumen[(nombre, n)]
                escritor.writerow(
                    [nombre, n]
                    + [round(r[fase], 4) for fase in FASES]
                    + [round(r[f"{fase}_desv"], 4) for fase in FASES]
                    + [round(r[f"sondeos_{fase}"], 4) for fase in FASES]
                    + [round(r["rehashings"], 2), round(r["ms_rehashing"], 4),
                       round(r["factor"], 4), round(r["capacidad"])]
                )


def main() -> None:
    analizador = argparse.ArgumentParser(description="Experimento comparativo de tablas hash")
    analizador.add_argument("--rapido", action="store_true",
                            help="solo 100 y 1000 claves con 2 repeticiones (para probar)")
    argumentos = analizador.parse_args()
    tamanos = TAMANOS[:2] if argumentos.rapido else TAMANOS
    repeticiones = 2 if argumentos.rapido else REPETICIONES

    print(f"Experimento hash | semilla={SEMILLA} | n={list(tamanos)} | "
          f"repeticiones={repeticiones}")
    medidas = ejecutar(tamanos, repeticiones)
    resumen = imprimir_tablas(medidas, tamanos)

    ruta = Path(_file_).with_name("resultados_experimento.csv")
    guardar_csv(resumen, tamanos, ruta)
    print(f"Resultados guardados en {ruta.name}")
    print("Nota: los tiempos de insercion incluyen el rehashing que ocurra durante la insercion.")

if _name_ == "_main_":
    main()
