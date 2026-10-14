from registro import Registro
from utils_hash import siguiente_primo
from utils_hash import capacidad_rehashing

class TablaHashCuadratico:
    def __init__(self, capacidad: int = 11) -> None:
        self.capacidad: int = capacidad
        self.tabla: list[Registro | str | None] = [None] * self.capacidad
        self.cantidad: int = 0
        self.BORRADO: str = "BORRADO"
        self.umbral: float = 0.45 

    def factor_carga(self) -> float:
        return self.cantidad / self.capacidad

    def _hash(self, codigo: int) -> int:
        return codigo % self.capacidad

    def insertar(self, registro: Registro) -> None:
        if self.factor_carga() > self.umbral:
            self.rehashing()

        indice_base = self._hash(registro.codigo)
        primer_borrado = -1

        for j in range(self.capacidad):
            indice = (indice_base + j * j) % self.capacidad
            casilla = self.tabla[indice]

            if casilla is None:
                if primer_borrado != -1:
                    self.tabla[primer_borrado] = registro
                else:
                    self.tabla[indice] = registro
                self.cantidad += 1
                return

            elif casilla == self.BORRADO:
                if primer_borrado == -1:
                    primer_borrado = indice

            elif isinstance(casilla, Registro) and casilla.codigo == registro.codigo:
                self.tabla[indice] = registro
                return

        if primer_borrado != -1:
            self.tabla[primer_borrado] = registro
            self.cantidad += 1
        else:
            self.rehashing()
            self.insertar(registro)

    def buscar(self, codigo: int) -> Registro | None:
        indice_base = self._hash(codigo)
        
        for j in range(self.capacidad):
            indice = (indice_base + j * j) % self.capacidad
            casilla = self.tabla[indice]

            if casilla is None:
                return None

            elif isinstance(casilla, Registro) and casilla.codigo == codigo:
                return casilla

        return None

    def eliminar(self, codigo: int) -> bool:
        indice_base = self._hash(codigo)
        
        for j in range(self.capacidad):
            indice = (indice_base + j * j) % self.capacidad
            casilla = self.tabla[indice]

            if casilla is None:
                return False
            
            elif isinstance(casilla, Registro) and casilla.codigo == codigo:
                self.tabla[indice] = self.BORRADO
                self.cantidad -= 1
                return True
        
        return False

    def rehashing(self) -> None:
        nueva_capacidad = capacidad_rehashing(self.capacidad)
        registros_antiguos = self.tabla
        
        self.capacidad = nueva_capacidad
        self.tabla = [None] * self.capacidad
        self.cantidad = 0 

        for casilla in registros_antiguos:
            if isinstance(casilla, Registro):
                self.insertar(casilla)

    def mostrar(self) -> None:
        print("\n--- Estado de la Tabla Hash Cuadrática ---")
        for i, casilla in enumerate(self.tabla):
            if casilla is None:
                print(f"[{i:02d}] -> VACÍO")
            elif casilla == self.BORRADO:
                print(f"[{i:02d}] -> {self.BORRADO}")
            else:
                print(f"[{i:02d}] -> {casilla.codigo}: {casilla.nombre}")
        print(f"Factor de carga actual: {self.factor_carga():.2f}")
