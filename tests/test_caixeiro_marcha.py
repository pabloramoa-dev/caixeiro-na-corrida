import unittest

from motor.caixeiro_marcha import (
    PERIODO, PRIMEIRA_TROCA, DESCIDA, PAUSA, VOLTA, progresso
)


class TrocaMarchaTest(unittest.TestCase):
    def test_neutro_antes_da_primeira_troca(self):
        for t in (0.0, 0.5, PRIMEIRA_TROCA - .001):
            self.assertEqual(progresso(t), 0.0)

    def test_desce_para_o_cambio_sem_salto(self):
        a = progresso(PRIMEIRA_TROCA + .1)
        b = progresso(PRIMEIRA_TROCA + DESCIDA / 2)
        c = progresso(PRIMEIRA_TROCA + DESCIDA)
        self.assertTrue(0 < a < b < c)
        self.assertEqual(c, 1.0)

    def test_pausa_e_retorno(self):
        self.assertEqual(progresso(PRIMEIRA_TROCA + DESCIDA + PAUSA / 2), 1.0)
        self.assertGreater(progresso(PRIMEIRA_TROCA + DESCIDA + PAUSA + .1), 0)
        self.assertEqual(progresso(PRIMEIRA_TROCA + DESCIDA + PAUSA + VOLTA), 0.0)

    def test_periodico_e_limites(self):
        for j in range(1000):
            t = j * .13
            p = progresso(t)
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)
            if t >= PRIMEIRA_TROCA:
                self.assertAlmostEqual(p, progresso(t + PERIODO), places=9)

    def test_inicio_fim_suaves(self):
        eps = .001
        self.assertLess(progresso(PRIMEIRA_TROCA + eps), .0001)
        self.assertLess(progresso(PRIMEIRA_TROCA + DESCIDA + PAUSA + VOLTA - eps), .0001)


if __name__ == "__main__":
    unittest.main()
