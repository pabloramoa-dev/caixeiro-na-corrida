import tempfile
import unittest
from pathlib import Path
from motor.uber_visual_motion import planejar, preparar

class CaixeiroMotionTest(unittest.TestCase):
    def setUp(self):
        self.ep={"batidas":[{"fala":"O passageiro abriu a mochila."},
                            {"fala":"O motorista achou um recibo."},
                            {"fala":"O telefone começou a tocar."}]}
        self.segs=[{"ini":0,"fim":6},{"ini":6,"fim":14},{"ini":14,"fim":21}]

    def test_intervalo_e_narrativa(self):
        cenas=planejar(self.ep,self.segs,21)
        self.assertEqual([x["start"] for x in cenas],[0,7,14])
        self.assertEqual([x["beat"] for x in cenas],[0,1,2])

    def test_imagens_podem_ser_geradas_sem_rede(self):
        fake=bytes.fromhex("89504e470d0a1a0a")+b"conteudo-de-teste"
        with tempfile.TemporaryDirectory() as dir:
            arqs=preparar(self.ep,self.segs,dir,21,gerador=lambda cena,ep:fake)
            self.assertEqual(len(arqs),3)
            self.assertEqual((Path(dir)/arqs[0]).read_bytes(),fake)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            planejar(self.ep,self.segs,21,0)
        with self.assertRaises(ValueError):
            planejar({"batidas":[]},self.segs,21)
        with tempfile.TemporaryDirectory() as dir:
            with self.assertRaises(ValueError):
                preparar(self.ep,self.segs,dir,21,gerador=lambda cena,ep:b"invalid")
