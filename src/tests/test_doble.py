import sys
import unittest
from pathlib import Path
# Permite importar los archivos desde la carpeta principal del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registro import Registro
from tabla_hash_doble import BORRADO, TablaHashDoble


class TestTablaHashDoble(unittest.TestCase):
    """Pruebas del doble hashing (umbral 0.65, capacidad inicial 11).
    Esta clase llama 'tamano' a la cantidad de registros activos."""

    def setUp(self) -> None:
        self.tabla = TablaHashDoble(capacidad=11)

    # 1. Tabla vacia
    def test_01_tabla_vacia(self) -> None:
        self.assertIsNone(self.tabla.buscar(10))
        self.assertFalse(self.tabla.eliminar(10))
        self.assertEqual(self.tabla.factor_carga(), 0)
        self.assertEqual(self.tabla.tamano, 0)
        self.assertEqual(self.tabla.capacidad, 11)

    # 2. Insercion sin colision
    def test_02_insercion_sin_colision(self) -> None:
        registro = Registro(1, "Mouse")
        self.tabla.insertar(registro)
        self.assertIs(self.tabla.buscar(1), registro)
        self.assertIs(self.tabla.tabla[1], registro)
        self.assertAlmostEqual(self.tabla.factor_carga(), 1 / 11)

    # 3. Insercion con colision: 21 -> h1 = 10, h2 = 1 + 21 % 10 = 2 -> (10 + 2) % 11 = 1
    def test_03_insercion_con_colision(self) -> None:
        r10, r21 = Registro(10, "Mouse"), Registro(21, "Teclado")
        self.tabla.insertar(r10)
        self.tabla.insertar(r21)
        self.assertIs(self.tabla.tabla[10], r10)
        self.assertIs(self.tabla.tabla[1], r21)

    # 4. Busqueda encontrada
    def test_04_busqueda_encontrada(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"Producto {codigo}"))
        self.assertEqual(self.tabla.buscar(32).nombre, "Producto 32")

    # 5. Busqueda ausente
    def test_05_busqueda_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertIsNone(self.tabla.buscar(99))
        self.assertIsNone(self.tabla.buscar(32))

    # 6. Eliminacion existente: deja BORRADO
    def test_06_eliminacion_existente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertTrue(self.tabla.eliminar(10))
        self.assertIsNone(self.tabla.buscar(10))
        self.assertEqual(self.tabla.tabla[10], BORRADO)
        self.assertEqual(self.tamano(), 0)

    # 7. Eliminacion ausente
    def test_07_eliminacion_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertFalse(self.tabla.eliminar(99))
        self.assertFalse(self.tabla.eliminar(32))
        self.assertEqual(self.tamano(), 1)

    # 8. BORRADO no corta la busqueda: 10, 21, 32, 43, 54 caen en 10, 1, 2, 3, 4
    def test_08_busqueda_tras_eliminar_otro_de_la_secuencia(self) -> None:
        for codigo in (10, 21, 32, 43, 54):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertTrue(self.tabla.eliminar(21))
        self.assertEqual(self.tabla.tabla[1], BORRADO)
        self.assertEqual(self.tabla.buscar(43).nombre, "P43")
        self.assertEqual(self.tabla.buscar(54).nombre, "P54")
        self.assertIsNone(self.tabla.buscar(21))

    # 9. Reinsercion tras borrado: 21 vuelve a su secuencia (10, 1) y reutiliza el BORRADO del indice 1
    def test_09_reinsercion_tras_borrado(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(21)
        self.tabla.insertar(Registro(21, "P21 nuevo"))   # su secuencia empieza en 10, 1 (BORRADO)
        self.assertEqual(self.tabla.buscar(21).nombre, "P21 nuevo")
        self.assertEqual(self.tabla.tabla[1].codigo, 21)  # reutiliza el BORRADO
        self.assertEqual(self.tamano(), 3)

    # 10. Clave duplicada actualiza; tambien con un BORRADO antes en su secuencia
    def test_10_clave_duplicada_actualiza(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.tabla.insertar(Registro(10, "Mouse gamer"))
        self.assertEqual(self.tabla.buscar(10).nombre, "Mouse gamer")
        self.assertEqual(self.tamano(), 1)

    def test_10b_duplicado_con_borrado_previo_en_la_secuencia(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(10)
        self.tabla.insertar(Registro(32, "P32 nuevo"))
        self.assertEqual(self.tabla.buscar(32).nombre, "P32 nuevo")
        self.assertEqual(self.tamano(), 2)

    # 11. Factor de carga alto: 7 de 11 (0.636) esta dentro de 0.65, sin rehashing
    def test_11_factor_de_carga_alto(self) -> None:
        for i in range(7):
            self.tabla.insertar(Registro(10 + 11 * i, f"P{i}"))
        self.assertAlmostEqual(self.tabla.factor_carga(), 7 / 11)
        self.assertLessEqual(self.tabla.factor_carga(), 0.65)
        self.assertEqual(self.tabla.capacidad, 11)

    # 12. Rehashing: el 8.o elemento (8/11 = 0.727 > 0.65) redimensiona a 23 y conserva todo
    def test_12_rehashing_conserva_registros(self) -> None:
        codigos = [10 + 11 * i for i in range(12)]
        for codigo in codigos:
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 23)
        self.assertEqual(self.tamano(), 12)
        for codigo in codigos:
            self.assertEqual(self.tabla.buscar(codigo).nombre, f"P{codigo}")
        self.assertLessEqual(self.tabla.factor_carga(), 0.65)

    # ---- Pruebas especificas de doble hashing ----
    def test_h2_nunca_es_cero_y_es_menor_que_m(self) -> None:
        for codigo in range(0, 500):
            self.assertGreaterEqual(self.tabla.h2(codigo), 1)
            self.assertLess(self.tabla.h2(codigo), self.tabla.capacidad)

    def test_h2_del_ejercicio_manual(self) -> None:
        """Para m = 11, h2(k) = 1 + k % 10 en las claves del ejercicio manual."""
        esperado = {10: 1, 21: 2, 32: 3, 43: 4, 54: 5, 65: 6}
        for codigo, valor in esperado.items():
            self.assertEqual(self.tabla.h2(codigo), valor)

    def test_secuencia_de_sondeo_recorre_toda_la_tabla(self) -> None:
        """Como m es primo y 1 <= h2 < m, la secuencia visita las m casillas."""
        for codigo in (10, 21, 32, 43, 54, 65):
            h1, h2, m = self.tabla.h1(codigo), self.tabla.h2(codigo), self.tabla.capacidad
            self.assertEqual(len({(h1 + j * h2) % m for j in range(m)}), m)

    def test_capacidad_se_ajusta_a_primo(self) -> None:
        self.assertEqual(TablaHashDoble(10).capacidad, 11)

    def tamano(self) -> int:
        return self.tabla.tamano


if __name__ == "__main__":
    unittest.main(verbosity=2)
