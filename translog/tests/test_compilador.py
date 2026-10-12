import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from compilador import compilar, AFDS


class PruebasCompilador(unittest.TestCase):
    def test_afd_anio(self):
        self.assertEqual(AFDS["ANIO"].mas_largo("2026", 0), 4)
        self.assertEqual(AFDS["ANIO"].mas_largo("202", 0), -1)
        self.assertEqual(AFDS["ANIO"].mas_largo("1999", 0), -1)

    def test_afd_sede(self):
        for s in ("LIM", "CAL", "ATE", "SJL", "SMP", "VES"):
            self.assertEqual(AFDS["SEDE"].mas_largo(s, 0), 3)
        self.assertEqual(AFDS["SEDE"].mas_largo("LMA", 0), -1)

    def test_validas_e_invalidas(self):
        casos = {
            "Guia: GR-LIM-2026-000123": True,
            "Guia: GR-LMA-2026-000126": False,    # sede inexistente
            "Guia: GR-ATE-202-000127": False,     # año incompleto
            "Guia: GR-VES-2026-00012A": False,    # correlativo con carácter inválido
            "GR-LIM-2026-000123": False,          # falta Guia:
            "Guia: GR-LIM-2026-": False,          # incompleto
            "Guia: GR-LIM-2026-000123 x": False,  # texto sobrante
        }
        for linea, esperado in casos.items():
            r = compilar(linea)
            self.assertEqual(r["lineas"][0]["valida"], esperado, linea)

    def test_ignora_comentarios_y_vacias(self):
        self.assertEqual(compilar("# hola\n\n   \n")["total"], 0)


if __name__ == "__main__":
    unittest.main()
