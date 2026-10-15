from registro import Registro
from utils_hash import capacidad_rehashing

# Marcador para distinguir una celda vacía de una que tuvo un elemento eliminado
BORRADO = "BORRADO"

class TablaHashDoble:
    def __init__(self, capacidad: int = 11) -> None:
        """Inicializa la tabla con capacidad 11 según las reglas comunes."""
        if self.capacidad < 0 or not isinstance(capacidad, int):
            raise ValueError("La capacidad debe ser un entero positivo.")
        self.capacidad = capacidad
        self.tabla: list[Registro | str | None] = [None] * self.capacidad
        self.tamano = 0
        self.umbral = 0.65

    def h1(self, codigo: int) -> int:
        """Función hash primaria h1(k) = k % m."""
        return codigo % self.capacidad

    def h2(self, codigo: int) -> int:
        """Función hash secundaria para evitar el cero h2(k) = 1 + (k % (m - 1))"""
        return 1 + (codigo % (self.capacidad - 1)) #tamaño de salto

    def insertar(self, registro: Registro) -> None:
        """Inserta o actualiza un registro mediante doble hashing."""
        if self.factor_carga() >= self.umbral:
            self.rehashing()

        codigo = registro.codigo
        h1_val = self.h1(codigo)
        h2_val = self.h2(codigo)
        pos_insertar = -1

        for j in range(self.capacidad):
            idx = (h1_val + j * h2_val) % self.capacidad
            actual = self.tabla[idx]

            # Encontramos la primera posición libre (None o BORRADO)
            if actual is None:
                if pos_insertar == -1:
                    pos_insertar = idx
                break
            elif actual == BORRADO:
                if pos_insertar == -1:
                    pos_insertar = idx
            # Si la clave ya existe, se actualiza el registro
            elif actual.codigo == codigo:
                self.tabla[idx] = registro
                return

        if pos_insertar != -1:
            self.tabla[pos_insertar] = registro
            self.tamano += 1
        else:
            raise RuntimeError("La tabla está llena.")

    def buscar(self, codigo: int) -> Registro | None:
        """Busca un registro sin detenerse al encontrar BORRADO."""
        h1_val = self.h1(codigo)
        h2_val = self.h2(codigo)

        for j in range(self.capacidad):
            idx = (h1_val + j * h2_val) % self.capacidad
            actual = self.tabla[idx]

            if actual is None:
                return None
            if actual != BORRADO and actual.codigo == codigo:
                return actual
        return None

    def eliminar(self, codigo: int) -> bool:
        """Reemplaza lógicamente el registro con BORRADO."""
        h1_val = self.h1(codigo)
        h2_val = self.h2(codigo)

        for j in range(self.capacidad):
            idx = (h1_val + j * h2_val) % self.capacidad
            actual = self.tabla[idx]

            if actual is None:
                return False
            if actual != BORRADO and actual.codigo == codigo:
                self.tabla[idx] = BORRADO
                self.tamano -= 1
                return True
        return False

    def mostrar(self) -> None:
        """Imprime el estado de la tabla."""
        print("--- Estado de la Tabla Hash (Doble Hashing) ---")
        for i, item in enumerate(self.tabla):
            if item is None:
                print(f"[{i}] -> None")
            elif item == BORRADO:
                print(f"[{i}] -> BORRADO")
            else:
                print(f"[{i}] -> {item}")

    def factor_carga(self) -> float:
        """Retorna el factor de carga actual."""
        return self.tamano / self.capacidad

    def rehashing(self) -> None:
        """Redimensiona la tabla al siguiente primo >= 2m+1 y reubica elementos."""
        vieja_tabla = self.tabla
        self.capacidad = capacidad_rehashing(self.capacidad)
        self.tabla = [None] * self.capacidad
        self.tamano = 0

        for item in vieja_tabla:
            if item is not None and item != BORRADO:
                self.insertar(item)