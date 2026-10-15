import sys
import random
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registro import Registro
from tabla_hash_cuadratico import TablaHashCuadratico
from tabla_hash_doble import TablaHashDoble
from tabla_hash_encadenamiento import TablaHashEncadenamiento
from tabla_hash_lineal import TablaHashLineal

# (nombre, clase, umbral de rehashing)
ESTRATEGIAS = [
    ("Encadenamiento", TablaHashEncadenamiento, 0.75),
    ("Lineal", TablaHashLineal, 0.65),
    ("Cuadratico", TablaHashCuadratico, 0.45),
    ("Doble hashing", TablaHashDoble, 0.65),
]


class TestIntegracionHash(unittest.TestCase):
    """Pruebas que recorren las 4 estrategias con la MISMA secuencia de operaciones.
    Solo usan la interfaz comun (insertar, buscar, eliminar, mostrar, factor_carga,
    rehashing), asi que no dependen de los nombres internos de cada clase."""

    def test_interfaz_obligatoria(self) -> None:
        """Las 6 operaciones del reparto deben existir en las 4 clases."""
        metodos = ["insertar", "buscar", "eliminar", "mostrar", "factor_carga", "rehashing"]
        for nombre, clase, _ in ESTRATEGIAS:
            for metodo in metodos:
                with self.subTest(estrategia=nombre, metodo=metodo):
                    self.assertTrue(callable(getattr(clase(), metodo, None)),
                                    f"{nombre} no tiene {metodo}()")

    def test_secuencia_del_ejercicio_manual_en_las_cuatro(self) -> None:
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                for codigo in (10, 21, 32, 43, 54):
                    tabla.insertar(Registro(codigo, f"P{codigo}"))
                self.assertEqual(tabla.buscar(43).nombre, "P43")
                self.assertTrue(tabla.eliminar(21))
                self.assertEqual(tabla.buscar(43).nombre, "P43")   # se preserva tras eliminar 21
                self.assertIsNone(tabla.buscar(21))
                tabla.insertar(Registro(65, "P65"))
                self.assertEqual(tabla.buscar(65).nombre, "P65")
                for codigo in (10, 32, 54):
                    self.assertEqual(tabla.buscar(codigo).nombre, f"P{codigo}")

    def test_oraculo_contra_dict_con_operaciones_aleatorias(self) -> None:
        """Compara cada tabla con un dict (solo en el test, no en la implementacion)."""
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                azar = random.Random(2026)
                tabla, referencia = clase(), {}
                for paso in range(3000):
                    codigo, dado = azar.randint(0, 300), azar.random()
                    if dado < 0.5:
                        tabla.insertar(Registro(codigo, f"n{paso}"))
                        referencia[codigo] = f"n{paso}"
                    elif dado < 0.75:
                        self.assertEqual(tabla.eliminar(codigo), codigo in referencia)
                        referencia.pop(codigo, None)
                    else:
                        encontrado = tabla.buscar(codigo)
                        self.assertEqual(encontrado.nombre if encontrado else None,
                                         referencia.get(codigo))
                for codigo in range(301):
                    encontrado = tabla.buscar(codigo)
                    self.assertEqual(encontrado.nombre if encontrado else None,
                                     referencia.get(codigo))

    def test_factor_de_carga_nunca_supera_el_umbral(self) -> None:
        for nombre, clase, umbral in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                for codigo in random.Random(2026).sample(range(100000), 500):
                    tabla.insertar(Registro(codigo, "x"))
                    self.assertLessEqual(tabla.factor_carga(), umbral + 1e-9)

    def test_rehashing_conserva_todos_los_registros(self) -> None:
        codigos = random.Random(2026).sample(range(100000), 1000)
        ausentes = [c for c in range(100000, 100200)]
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                for codigo in codigos:
                    tabla.insertar(Registro(codigo, f"P{codigo}"))
                for codigo in codigos:
                    self.assertEqual(tabla.buscar(codigo).nombre, f"P{codigo}")
                for codigo in ausentes:
                    self.assertIsNone(tabla.buscar(codigo))

    def test_duplicado_no_cambia_el_factor_de_carga(self) -> None:
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                for codigo in (10, 21, 32):
                    tabla.insertar(Registro(codigo, "original"))
                antes = tabla.factor_carga()
                tabla.insertar(Registro(21, "actualizado"))
                self.assertEqual(tabla.factor_carga(), antes)
                self.assertEqual(tabla.buscar(21).nombre, "actualizado")

    def test_eliminar_todo_deja_la_tabla_vacia(self) -> None:
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                codigos = random.Random(2026).sample(range(10000), 50)
                for codigo in codigos:
                    tabla.insertar(Registro(codigo, "x"))
                for codigo in codigos:
                    self.assertTrue(tabla.eliminar(codigo))
                self.assertEqual(tabla.factor_carga(), 0)
                for codigo in codigos:
                    self.assertIsNone(tabla.buscar(codigo))

    def test_busqueda_termina_aunque_no_queden_casillas_vacias(self) -> None:
        """Muchos insertar+eliminar acumulan BORRADO; buscar una clave ausente no debe
        quedarse en un bucle infinito en las tablas de direccionamiento abierto."""
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                for codigo in range(300):
                    tabla.insertar(Registro(codigo, "x"))
                    tabla.eliminar(codigo)
                self.assertIsNone(tabla.buscar(100000))
                self.assertEqual(tabla.factor_carga(), 0)

    def test_mostrar_no_falla_en_ningun_estado(self) -> None:
        for nombre, clase, _ in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                tabla = clase()
                tabla.mostrar()                                  # vacia
                for codigo in (10, 21, 32):
                    tabla.insertar(Registro(codigo, f"P{codigo}"))
                tabla.eliminar(21)
                tabla.mostrar()                                  # con un eliminado


if __name__ == "__main__":
    unittest.main(verbosity=2)
