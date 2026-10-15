import unittest
from contextlib import redirect_stdout
from io import StringIO

from registro import Registro
from tabla_hash_encadenamiento import TablaHashEncadenamiento
from tabla_hash_cuadratico import TablaHashCuadratico
from tabla_hash_doble import TablaHashDoble
from utils_hash import es_primo


class TestRegresionesHash(unittest.TestCase):
    def test_capacidades(self) -> None:
        for clase in (TablaHashEncadenamiento, TablaHashCuadratico, TablaHashDoble):
            with self.subTest(clase=clase.__name__):
                for valor in (True, 3.5, "11"):
                    with self.assertRaises(TypeError):
                        clase(valor)
                for valor in (-1, 0, 1):
                    with self.assertRaises(ValueError):
                        clase(valor)
                tabla = clase(8)
                for codigo in (3, 59, 115):
                    tabla.insertar(Registro(codigo, str(codigo)))
                    self.assertIsNotNone(tabla.buscar(codigo))

    def test_umbral_y_actualizacion(self) -> None:
        for clase, limite in ((TablaHashCuadratico, 4), (TablaHashDoble, 7)):
            with self.subTest(clase=clase.__name__):
                tabla = clase()
                for codigo in range(limite):
                    tabla.insertar(Registro(codigo, str(codigo)))
                tabla.insertar(Registro(0, "Actualizado"))
                self.assertEqual(tabla.capacidad, 11)
                self.assertAlmostEqual(tabla.factor_carga(), limite / 11)
                tabla.insertar(Registro(limite, "Nuevo"))
                self.assertEqual(tabla.capacidad, 23)
                self.assertLessEqual(tabla.factor_carga(), tabla.umbral)
                for codigo in range(limite + 1):
                    self.assertIsNotNone(tabla.buscar(codigo))

    def test_duplicado_despues_de_borrado(self) -> None:
        for clase in (TablaHashCuadratico, TablaHashDoble):
            with self.subTest(clase=clase.__name__):
                tabla = clase()
                for codigo in (10, 21, 32):
                    tabla.insertar(Registro(codigo, str(codigo)))
                self.assertTrue(tabla.eliminar(10))
                carga = tabla.factor_carga()
                tabla.insertar(Registro(32, "Actualizado"))
                self.assertEqual(tabla.buscar(32).nombre, "Actualizado")
                self.assertEqual(tabla.factor_carga(), carga)
                self.assertTrue(tabla.eliminar(32))
                self.assertIsNone(tabla.buscar(32))

    def test_cadena_y_borrados(self) -> None:
        tabla = TablaHashEncadenamiento()
        self.assertIsNone(tabla.buscar(10))
        self.assertFalse(tabla.eliminar(10))
        for codigo in (10, 21, 32, 43, 54):
            tabla.insertar(Registro(codigo, str(codigo)))
        tabla.insertar(Registro(32, "Actualizado"))
        self.assertEqual(tabla.cantidad(), 5)
        self.assertEqual(tabla.buscar(32).nombre, "Actualizado")
        for codigo in (10, 32, 54, 21, 43):
            self.assertTrue(tabla.eliminar(codigo))
            self.assertIsNone(tabla.buscar(codigo))
        self.assertEqual(tabla.cantidad(), 0)

    def test_rehashing_encadenamiento(self) -> None:
        tabla = TablaHashEncadenamiento()
        for codigo in range(100):
            tabla.insertar(Registro(codigo, str(codigo)))
        self.assertEqual(tabla.cantidad(), 100)
        self.assertTrue(es_primo(tabla.capacidad()))
        self.assertGreater(tabla.total_rehashings(), 0)
        self.assertLessEqual(tabla.factor_carga(), 0.75)
        anterior = tabla.capacidad()
        tabla.rehashing()
        self.assertGreaterEqual(tabla.capacidad(), 2 * anterior + 1)
        for codigo in range(100):
            self.assertEqual(tabla.buscar(codigo).nombre, str(codigo))

    def test_integracion_main_y_manual(self) -> None:
        from main import crear_tabla, submenu_inventario
        from ejercicios_manuales import ejercicio_manual_encadenamiento
        from unittest.mock import patch

        tabla = crear_tabla(1)
        salida = StringIO()
        with redirect_stdout(salida):
            with patch("builtins.input", side_effect=["1", "10", "Mouse", "2", "10", "0"]):
                submenu_inventario(tabla)
            ejercicio_manual_encadenamiento()
        self.assertEqual(tabla.buscar(10).nombre, "Mouse")
        self.assertIn("Rehashings realizados: 0", salida.getvalue())
        self.assertIn("[10] -> [10] Producto 10 -> [32] Producto 32", salida.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
