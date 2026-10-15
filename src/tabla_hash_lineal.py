from registro import Registro
from utils_hash import siguiente_primo, capacidad_rehashing


class TablaHashLineal:
    #Marca para diferenciar una posicion eliminada de una vacia
    BORRADO = object()

    def __init__(self, capacidad: int = 11) -> None:
        if(
            not isinstance(capacidad,int)
            or isinstance(capacidad,bool)
            or capacidad < 2
        ):
            raise ValueError("La capacidad debe ser un entero mayor o igual a 2")

        self.capacidad = siguiente_primo(capacidad)
        self.tabla: list[Registro | object | None] = [None] * self.capacidad
        self.cantidad: int = 0
        self.rehashings: int = 0


    def _indice(self, codigo: int) -> int:
        """Calcula el índice de la tabla para un código dado."""
        return codigo % self.capacidad

    def insertar(self, registro: Registro) -> None:
        # sourcery skip: extract-duplicate-method
        if not isinstance(registro, Registro):
            raise ValueError("El registro debe ser una instancia de la clase Registro")

        primero_borrado = None

        for j in range(self.capacidad):
            indice = (self._indice(registro.codigo) + j) % self.capacidad
            actual = self.tabla[indice]

            if actual is self.BORRADO:
                if primero_borrado is None:
                    primero_borrado = indice

            elif actual is None:
                destino = primero_borrado if primero_borrado is not None else indice

                if(self.cantidad + 1) / self.capacidad > 0.65:
                    self._rehashing()
                    self.insertar(registro)
                    return

                self.tabla[destino] = registro
                self.cantidad += 1
                return

            elif isinstance(actual, Registro) and actual.codigo == registro.codigo:
                #Si ya existe, actualiza sin incrementar la cantidad
                self.tabla[indice] = registro
                return

        if primero_borrado is not None:
            if(self.cantidad + 1) / self.capacidad >0.65:
                self._rehashing()
                self.insertar(registro)
                return

            self.tabla[primero_borrado] = registro
            self.cantidad += 1
            return

        #Si no hay posicion disponible, ampliar la tabla y reintentar la inserción
        self._rehashing()
        self.insertar(registro)

    def buscar(self, codigo: int) -> Registro | None:
        for j in range(self.capacidad):
            indice = (codigo % self.capacidad + j) % self.capacidad
            actual = self.tabla[indice]

            if actual is None:
                return None

            if isinstance(actual, Registro) and actual.codigo == codigo:
                return actual

        return None

    def eliminar(self, codigo: int) -> bool:
        for j in range(self.capacidad):
            indice = (codigo % self.capacidad + j) % self.capacidad
            actual = self.tabla[indice]

            if actual is None:
                return False

            if isinstance(actual, Registro) and actual.codigo == codigo:
                self.tabla[indice] = self.BORRADO
                self.cantidad -= 1
                return True

        return False

    def mostrar(self) -> None:
        print("\n --- TABLA HASH LINEAL ---")

        for indice, valor in enumerate(self.tabla):
            if valor is None:
                contenido = "VACIO"

            elif valor is self.BORRADO:
                contenido = "BORRADO"

            else:
                contenido = str(valor)

            print(f"[{indice}] ->{contenido}")

        print(f"Registros activos: {self.cantidad}")
        print(f"Factor de carga: {self.factor_carga():.2f}")


    def factor_carga(self) -> float:
        return self.cantidad / self.capacidad

    def _rehashing(self) -> None:
        #Guardar unicamente los registros activos
        anteriores = [
            registro
            for registro in self.tabla
            if isinstance(registro, Registro)
        ]

        #Ampliar la capacidad al siguiente primo >= 2m + 1
        self.capacidad = capacidad_rehashing(self.capacidad)
        self.tabla = [None] * self.capacidad
        self.cantidad = 0
        self.rehashings += 1

        #Reinsertar los registros activos
        for registro in anteriores:
            self.insertar(registro)
