
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registro import Registro
from tabla_hash_cuadratico import TablaHashCuadratico


class TestTablaHashCuadratico(unittest.TestCase):
    """Pruebas del sondeo cuadratico (umbral 0.45, capacidad inicial 11).
    Con umbral 0.45 y m = 11 caben como maximo 4 registros antes de redimensionar."""

    def setUp(self) -> None:
        self.tabla = TablaHashCuadratico(capacidad=11)

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
        self.assertIs(self.tabla.tabla[1], registro)
        self.assertAlmostEqual(self.tabla.factor_carga(), 1 / 11)

    # 3. Insercion con colision: 10 -> indice 10; 21 -> (10 + 1^2) % 11 = 0
    def test_03_insercion_con_colision(self) -> None:
        r10, r21 = Registro(10, "Mouse"), Registro(21, "Teclado")
        self.tabla.insertar(r10)
        self.tabla.insertar(r21)
        self.assertIs(self.tabla.tabla[10], r10)
        self.assertIs(self.tabla.tabla[0], r21)

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
        self.assertEqual(self.tabla.tabla[10], self.tabla.BORRADO)
        self.assertEqual(self.tabla.cantidad, 0)

    # 7. Eliminacion ausente
    def test_07_eliminacion_ausente(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.assertFalse(self.tabla.eliminar(99))
        self.assertFalse(self.tabla.eliminar(32))
        self.assertEqual(self.tabla.cantidad, 1)

    # 8. BORRADO no corta la busqueda: 10, 21, 32, 43 caen en indices 10, 0, 3, 8
    def test_08_busqueda_tras_eliminar_otro_de_la_secuencia(self) -> None:
        for codigo in (10, 21, 32, 43):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 11)       # 4/11 = 0.36, sin rehashing
        self.assertTrue(self.tabla.eliminar(21))
        self.assertEqual(self.tabla.tabla[0], self.tabla.BORRADO)
        self.assertEqual(self.tabla.buscar(43).nombre, "P43")
        self.assertEqual(self.tabla.buscar(32).nombre, "P32")
        self.assertIsNone(self.tabla.buscar(21))

    # 9. Reinsercion tras borrado: 65 reutiliza la casilla BORRADO del indice 0
    def test_09_reinsercion_tras_borrado(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(21)
        self.tabla.insertar(Registro(65, "P65"))
        self.assertEqual(self.tabla.buscar(65).nombre, "P65")
        self.assertEqual(self.tabla.tabla[0].codigo, 65)
        self.assertEqual(self.tabla.cantidad, 3)

    # 10. Clave duplicada actualiza; tambien con un BORRADO antes en su secuencia
    def test_10_clave_duplicada_actualiza(self) -> None:
        self.tabla.insertar(Registro(10, "Mouse"))
        self.tabla.insertar(Registro(10, "Mouse gamer"))
        self.assertEqual(self.tabla.buscar(10).nombre, "Mouse gamer")
        self.assertEqual(self.tabla.cantidad, 1)

    def test_10b_duplicado_con_borrado_previo_en_la_secuencia(self) -> None:
        for codigo in (10, 21, 32):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.tabla.eliminar(10)
        self.tabla.insertar(Registro(32, "P32 nuevo"))
        self.assertEqual(self.tabla.buscar(32).nombre, "P32 nuevo")
        self.assertEqual(self.tabla.cantidad, 2)

    # 11. Factor de carga alto: 4 de 11 (0.364) es lo maximo sin rehashing con umbral 0.45
    def test_11_factor_de_carga_alto(self) -> None:
        for i in range(4):
            self.tabla.insertar(Registro(10 + 11 * i, f"P{i}"))
        self.assertAlmostEqual(self.tabla.factor_carga(), 4 / 11)
        self.assertLessEqual(self.tabla.factor_carga(), 0.45)
        self.assertEqual(self.tabla.capacidad, 11)

    # 12. Rehashing: el 5.o elemento (5/11 = 0.4545 > 0.45) redimensiona a 23; con 12 llega a 47
    def test_12_rehashing_conserva_registros(self) -> None:
        codigos = [10 + 11 * i for i in range(12)]
        for codigo in codigos:
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 47)       # 11 -> 23 -> 47
        self.assertEqual(self.tabla.cantidad, 12)
        for codigo in codigos:
            self.assertEqual(self.tabla.buscar(codigo).nombre, f"P{codigo}")
        self.assertLessEqual(self.tabla.factor_carga(), 0.45)

    # ---- Pruebas especificas de cuadratico ----
    def test_quinto_elemento_dispara_rehashing_con_umbral_por_defecto(self) -> None:
        """Importante para el ejercicio manual: con umbral 0.45 se redimensiona al 5.o."""
        for codigo in (10, 21, 32, 43, 54):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 23)

    def test_posiciones_del_ejercicio_manual_sin_rehashing(self) -> None:
        """Con umbral subido, la secuencia 10,21,32,43,54 ocupa 10, 0, 3, 8, 4."""
        self.tabla.umbral = 1.0
        for codigo in (10, 21, 32, 43, 54):
            self.tabla.insertar(Registro(codigo, f"P{codigo}"))
        self.assertEqual(self.tabla.capacidad, 11)
        posiciones = {r.codigo: i for i, r in enumerate(self.tabla.tabla) if isinstance(r, Registro)}
        self.assertEqual(posiciones, {10: 10, 21: 0, 32: 3, 43: 8, 54: 4})

    def test_sondeo_cuadratico_no_visita_toda_la_tabla(self) -> None:
        """Con m = 11 los desplazamientos j^2 mod 11 solo producen (11+1)/2 = 6 casillas."""
        m = 11
        visitadas = {(10 + j * j) % m for j in range(m)}
        self.assertEqual(len(visitadas), 6)
        self.assertEqual(visitadas, {10, 0, 3, 8, 4, 2})

    def test_capacidad_se_ajusta_a_primo(self) -> None:
        self.assertEqual(TablaHashCuadratico(10).capacidad, 11)


if __name__ == "__main__":
    unittest.main(verbosity=2)
