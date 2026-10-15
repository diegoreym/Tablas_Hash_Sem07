from __future__ import annotations
from typing import Iterator
from registro import Registro
from utils_hash import capacidad_rehashing, siguiente_primo

class Nodo:
    def __init__(self, dato: Registro) -> None:
        self.dato: Registro = dato
        self.siguiente: Nodo | None = None

class ListaEnlazada:
    def __init__(self) -> None:
        self.__cabeza: Nodo | None = None

    def insertar_o_actualizar(self, registro: Registro) -> bool:
        actual = self.__cabeza
        anterior: Nodo | None = None
        while actual is not None:
            if actual.dato.codigo == registro.codigo:
                actual.dato = registro
                return False
            anterior = actual
            actual = actual.siguiente

        nuevo = Nodo(registro)
        if anterior is None:
            self.__cabeza = nuevo
        else:
            anterior.siguiente = nuevo
        return True

    def buscar(self, codigo: int) -> Registro | None:
        actual = self.__cabeza
        while actual is not None:
            if actual.dato.codigo == codigo:
                return actual.dato
            actual = actual.siguiente
        return None

    def eliminar(self, codigo: int) -> bool:
        actual = self.__cabeza
        anterior: Nodo | None = None
        while actual is not None:
            if actual.dato.codigo == codigo:
                if anterior is None:
                    self.__cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def __iter__(self) -> Iterator[Registro]:
        actual = self.__cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def mostrar(self) -> None:
        actual = self.__cabeza
        while actual is not None:
            print(f"{actual.dato} -> ", end="")
            actual = actual.siguiente
        print("None")


class TablaHashEncadenamiento:
    def __init__(self, capacidad: int = 11) -> None:
        if type(capacidad) is not int:
            raise TypeError("La capacidad debe ser un entero")
        if capacidad < 2:
            raise ValueError("La capacidad debe ser al menos 2")
        self.__capacidad: int = siguiente_primo(capacidad)
        self.__cantidad: int = 0
        self.__tabla: list[ListaEnlazada] = []
        self.__rehashings: int = 0
        for _ in range(self.__capacidad):
            self.__tabla.append(ListaEnlazada())

    def __hash(self, codigo: int) -> int:
        if type(codigo) is not int:
            raise TypeError("El codigo debe ser un entero")
        if codigo < 0:
            raise ValueError("El codigo no puede ser negativo")
        return codigo % self.__capacidad

    def insertar(self, registro: Registro) -> None:
        indice = self.__hash(registro.codigo)
        se_agrego = self.__tabla[indice].insertar_o_actualizar(registro)
        if se_agrego:
            self.__cantidad += 1
            if self.factor_carga() > 0.75:
                self.rehashing()

    def buscar(self, codigo: int) -> Registro | None:
        indice = self.__hash(codigo)
        return self.__tabla[indice].buscar(codigo)

    def eliminar(self, codigo: int) -> bool:
        indice = self.__hash(codigo)
        se_elimino = self.__tabla[indice].eliminar(codigo)
        if se_elimino:
            self.__cantidad -= 1
        return se_elimino

    def mostrar(self) -> None:
        print("\n--- Tabla hash por encadenamiento ---")
        for indice, cadena in enumerate(self.__tabla):
            print(f"[{indice:02d}] -> ", end="")
            cadena.mostrar()
        print(f"Cantidad: {self.__cantidad} | Capacidad: {self.__capacidad}")
        print(f"Factor de carga: {self.factor_carga():.4f}")

    def factor_carga(self) -> float:
        return self.__cantidad / self.__capacidad

    def rehashing(self) -> None:
        tabla_anterior = self.__tabla
        self.__capacidad = capacidad_rehashing(self.__capacidad)
        self.__tabla = []
        self.__cantidad = 0
        for _ in range(self.__capacidad):
            self.__tabla.append(ListaEnlazada())
        for cadena in tabla_anterior:
            for registro in cadena:
                self.insertar(registro)
        self.__rehashings += 1

    def cantidad(self) -> int:
        return self.__cantidad

    def capacidad(self) -> int:
        return self.__capacidad

    def total_rehashings(self) -> int:
        return self.__rehashings
