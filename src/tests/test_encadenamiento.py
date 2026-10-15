import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registro import Registro
from tabla_hash_encadenamiento import TablaHashEncadenamiento


class TestTablaHashEncadenamiento(unittest.TestCase):
    """Pruebas de la tabla con encadenamiento (umbral 0.75, capacidad inicial 11).
    Esta clase expone capacidad(), cantidad() y total_rehashings() como METODOS."""

    def setUp(self) -> None:
        self.tabla = TablaHashEncadenamiento(capacidad=11)

    # 1. Tabla vacia
    def test_01_tabla_vacia(self) -> None:
        self.assertIsNone(self.tabla.buscar(10))
        self.assertFalse(self.tabla.eliminar(10))
        self.assertEqual(self.tabla.factor_carga(), 0)
        self.assertEqual(self.tabla.cantidad(), 0)
        self.assertEqual(self.tabla.capacidad(), 11)

    # 2. Insercion sin colision
    def test_02_insercion_sin_colision(self) -> None:
        registro = Registro(1, "Mouse")
        self.tabla.insertar(registro)
        self.assertIs(self.tabla.buscar(1), registro)
        self.assertEqual(self.tabla.cantidad(), 1)
        self.assertAlmostEqual(self.tabla.factor_carga(), 1 / 11)

    # 3. Insercion con colision (10 y 21 caen en el indice 10 y se encadenan)
    def test_03_insercion_con_colision(self) -> None:
        r10, r21 = Registro(10, "Mouse"), Registro(21, "Teclado")
        self.tabla.insertar(r10)
        self.tabla.insertar(r21)
        self.assertIs(self.tabla.buscar(10), r10)
        self.assertIs(self.tabla.buscar(21), r21)
        self.assertEqual(self.tabla.cantidad(), 2)

    # 4. Busqueda encontrada
    def test_04_busqueda_encontrada(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"Producto {codigo}"))
        self.assertEqual(self.tabla.buscar(32).nombre, "Producto 32")

    # 5. Busqueda ausente (incluye una clave que cae en una cadena ocupada)
    def test_05_busqueda_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertIsNone(self.tabla.buscar(99))   # indice 0, cadena vacia
        self.assertIsNone(self.tabla.buscar(32))   # indice 10, cadena con otro elemento

    # 6. Eliminacion existente (se quita de la cadena, no hay BORRADO)
    def test_06_eliminacion_existente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertTrue(self.tabla.eliminar(10))
        self.assertIsNone(self.tabla.buscar(10))
        self.assertEqual(self.tabla.cantidad(), 0)

    # 7. Eliminacion ausente
    def test_07_eliminacion_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertFalse(self.tabla.eliminar(99))
        self.assertFalse(self.tabla.eliminar(32))  # misma cadena, pero no esta
        self.assertEqual(self.tabla.cantidad(), 1)

    # 8. Busqueda tras eliminar otro elemento de la misma cadena (ejercicio manual)
    def test_08_busqueda_tras_eliminar_otro_de_la_cadena(self) -> None:
        for codigo in (10, 21, 32, 43, 54):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertTrue(self.tabla.eliminar(21))
        self.assertEqual(self.tabla.buscar(43).nombre, "P43")
        self.assertEqual(self.tabla.buscar(32).nombre, "P32")
        self.assertEqual(self.tabla.buscar(54).nombre, "P54")
        self.assertIsNone(self.tabla.buscar(21))

    # 9. Reinsercion tras eliminar
    def test_09_reinsercion_tras_eliminar(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.tabla.insertar(Registro(21, "Teclado"))
        self.tabla.eliminar(21)
        self.tabla.insertar(Registro(21, "Teclado nuevo"))
        self.assertEqual(self.tabla.buscar(21).nombre, "Teclado nuevo")
        self.assertEqual(self.tabla.cantidad(), 2)

    # 10. Clave duplicada actualiza sin aumentar la cantidad
    def test_10_clave_duplicada_actualiza(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.tabla.insertar(Registro(21, "Teclado"))
        self.tabla.insertar(Registro(21, "Teclado gamer"))
        self.assertEqual(self.tabla.buscar(21).nombre, "Teclado gamer")
        self.assertEqual(self.tabla.cantidad(), 2)
        self.assertAlmostEqual(self.tabla.factor_carga(), 2 / 11)

    # 11. Factor de carga alto: con 8 de 11 (0.727) aun NO supera 0.75, no hay rehashing
    def test_11_factor_de_carga_alto(self) -> None:
        for i in range(8):
            self.tabla.insertar(Registro(10 + 11 * i, f"P{i}"))
        self.assertAlmostEqual(self.tabla.factor_carga(), 8 / 11)
        self.assertLessEqual(self.tabla.factor_carga(), 0.75)
        self.assertEqual(self.tabla.capacidad(), 11)
        self.assertEqual(self.tabla.total_rehashings(), 0)

    # 12. Rehashing: el 9.o elemento (9/11 = 0.818 > 0.75) redimensiona a 23 y conserva todo
    def test_12_rehashing_conserva_registros(self) -> None:
        codigos = [10 + 11 * i for i in range(12)]
        for codigo in codigos:
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad(), 23)
        self.assertEqual(self.tabla.total_rehashings(), 1)
        self.assertEqual(self.tabla.cantidad(), 12)
        for codigo in codigos:
            self.assertEqual(self.tabla.buscar(codigo).nombre, f"P{codigo}")
        self.assertLessEqual(self.tabla.factor_carga(), 0.75)

    # ---- Pruebas especificas de encadenamiento ----
    def test_orden_de_la_cadena_se_mantiene_al_insertar(self) -> None:
        """Los elementos se agregan al final de la cadena del indice 10."""
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        # Se recorre la cadena interna con el iterador de ListaEnlazada
        cadena = self.tabla._TablaHashEncadenamiento__tabla[10]
        self.assertEqual([r.codigo for r in cadena], [10, 21, 32])

    def test_eliminar_no_deja_marcador_en_la_cadena(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(21)
        cadena = self.tabla._TablaHashEncadenamiento__tabla[10]
        self.assertEqual([r.codigo for r in cadena], [10, 32])

    def test_capacidad_se_ajusta_a_primo(self) -> None:
        self.assertEqual(TablaHashEncadenamiento(10).capacidad(), 11)


if __name__ == "__main__":
    unittest.main(verbosity=2)
