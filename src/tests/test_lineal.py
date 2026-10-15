import sys
import unittest
from pathlib import Path
# Permite importar los archivos desde la carpeta principal del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registro import Registro
from tabla_hash_lineal import TablaHashLineal


class TestTablaHashLineal(unittest.TestCase):
    """Pruebas del sondeo lineal (umbral 0.65, capacidad inicial 11).
    Esta clase guarda capacidad, cantidad y rehashings como ATRIBUTOS."""

    def setUp(self) -> None:
        self.tabla = TablaHashLineal(capacidad=11)

    # 1. Tabla vacia
    def test_01_tabla_vacia(self) -> None:
        self.assertIsNone(self.tabla.buscar(10))
        self.assertFalse(self.tabla.eliminar(10))
        self.assertEqual(self.tabla.factor_carga(), 0)
        self.assertEqual(self.tabla.cantidad, 0)
        self.assertEqual(self.tabla.capacidad, 11)

    # 2. Insercion sin colision
    def test_02_insercion_sin_colision(self) -> None:
        registro = Registro(1, "Mouse")
        self.tabla.insertar(registro)
        self.assertIs(self.tabla.buscar(1), registro)
        self.assertIs(self.tabla.tabla[1], registro)       # cae en su indice natural
        self.assertAlmostEqual(self.tabla.factor_carga(), 1 / 11)

    # 3. Insercion con colision: 21 va al siguiente libre (indice 0, por envolvimiento)
    def test_03_insercion_con_colision(self) -> None:
        r10, r21 = Registro(10, "Mouse"), Registro(21, "Teclado")
        self.tabla.insertar(r10)
        self.tabla.insertar(r21)
        self.assertIs(self.tabla.tabla[10], r10)
        self.assertIs(self.tabla.tabla[0], r21)
        self.assertEqual(self.tabla.cantidad, 2)

    # 4. Busqueda encontrada
    def test_04_busqueda_encontrada(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"Producto {codigo}"))
        self.assertEqual(self.tabla.buscar(32).nombre, "Producto 32")

    # 5. Busqueda ausente
    def test_05_busqueda_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertIsNone(self.tabla.buscar(99))
        self.assertIsNone(self.tabla.buscar(32))   # colisiona con 10 pero no esta

    # 6. Eliminacion existente: deja el marcador BORRADO
    def test_06_eliminacion_existente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertTrue(self.tabla.eliminar(10))
        self.assertIsNone(self.tabla.buscar(10))
        self.assertIs(self.tabla.tabla[10], TablaHashLineal.BORRADO)
        self.assertEqual(self.tabla.cantidad, 0)

    # 7. Eliminacion ausente
    def test_07_eliminacion_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertFalse(self.tabla.eliminar(99))
        self.assertFalse(self.tabla.eliminar(32))
        self.assertEqual(self.tabla.cantidad, 1)

    # 8. BORRADO no corta la busqueda: tras eliminar 21, 43 se sigue encontrando
    def test_08_busqueda_tras_eliminar_otro_de_la_secuencia(self) -> None:
        for codigo in (10, 21, 32, 43, 54):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertTrue(self.tabla.eliminar(21))
        self.assertIs(self.tabla.tabla[0], TablaHashLineal.BORRADO)
        self.assertEqual(self.tabla.buscar(43).nombre, "P43")
        self.assertEqual(self.tabla.buscar(54).nombre, "P54")
        self.assertIsNone(self.tabla.buscar(21))

    # 9. Reinsercion tras borrado: reutiliza el BORRADO y cuenta una sola vez
    def test_09_reinsercion_tras_borrado(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(21)
        self.tabla.insertar(Registro(65, "P65"))      # tambien cae en el indice 10
        self.assertEqual(self.tabla.buscar(65).nombre, "P65")
        self.assertEqual(self.tabla.buscar(32).nombre, "P32")
        self.assertEqual(self.tabla.cantidad, 3)
        self.assertEqual(self.tabla.capacidad, 11)

    # 10. Clave duplicada actualiza; tambien si hay un BORRADO antes en su secuencia
    def test_10_clave_duplicada_actualiza(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.tabla.insertar(Registro(10, "Mouse gamer"))
        self.assertEqual(self.tabla.buscar(10).nombre, "Mouse gamer")
        self.assertEqual(self.tabla.cantidad, 1)

    def test_10b_duplicado_con_borrado_previo_en_la_secuencia(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(10)                        # BORRADO antes de 32
        self.tabla.insertar(Registro(32, "P32 nuevo"))
        self.assertEqual(self.tabla.buscar(32).nombre, "P32 nuevo")
        self.assertEqual(self.tabla.cantidad, 2)       # no se duplico

    # 11. Factor de carga alto: 7 de 11 (0.636) esta dentro de 0.65, sin rehashing
    def test_11_factor_de_carga_alto(self) -> None:
        for i in range(7):
            self.tabla.insertar(Registro(10 + 11 * i, f"P{i}"))
        self.assertAlmostEqual(self.tabla.factor_carga(), 7 / 11)
        self.assertLessEqual(self.tabla.factor_carga(), 0.65)
        self.assertEqual(self.tabla.capacidad, 11)
        self.assertEqual(self.tabla.rehashings, 0)

    # 12. Rehashing: el 8.o elemento (8/11 = 0.727 > 0.65) redimensiona a 23 y conserva todo
    def test_12_rehashing_conserva_registros(self) -> None:
        codigos = [10 + 11 * i for i in range(12)]
        for codigo in codigos:
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 23)
        self.assertEqual(self.tabla.rehashings, 1)
        self.assertEqual(self.tabla.cantidad, 12)
        for codigo in codigos:
            self.assertEqual(self.tabla.buscar(codigo).nombre, f"P{codigo}")
        self.assertLessEqual(self.tabla.factor_carga(), 0.65)

    # ---- Pruebas especificas de lineal ----
    def test_rehashing_descarta_los_borrados(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(21)
        self.tabla.rehashing()                         # en esta clase es privado
        self.assertNotIn(TablaHashLineal.BORRADO, self.tabla.tabla)
        self.assertEqual(self.tabla.cantidad, 2)
        self.assertEqual(self.tabla.capacidad, 23)

    def test_borrado_no_es_none(self) -> None:
        self.assertIsNotNone(TablaHashLineal.BORRADO)

    def test_capacidad_se_ajusta_a_primo(self) -> None:
        self.assertEqual(TablaHashLineal(10).capacidad, 11)


if __name__ == "__main__":
    unittest.main(verbosity=2)
