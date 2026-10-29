import tempfile
import unittest
from pathlib import Path
from PIL import Image
from motor.render_version import versao
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

    def test_novo_estilo_cinematografico_padrao(self):
        with tempfile.TemporaryDirectory() as tmp:
            imagens=preparar(self.ep,self.segs,tmp,21)
            self.assertEqual(len(imagens),3)
            with Image.open(Path(tmp)/imagens[0]) as imagem:
                self.assertEqual(imagem.size,(1440,900))
                self.assertEqual(imagem.format,"PNG")

    def test_estilo_antigo_pode_ser_reativado(self):
        ep={**self.ep, "visual_style":"classic"}
        with tempfile.TemporaryDirectory() as tmp:
            imagens=preparar(ep,self.segs,tmp,21)
            self.assertEqual(len(imagens),3)

    def test_cinema_escolhe_objeto_da_historia(self):
        from motor.cinematic_story_art import tipo_objeto
        cena={"scene":0,"text":"Uma mensagem chegou no celular."}
        self.assertEqual(tipo_objeto(cena,{"titulo":"Uma conversa inesperada"}),"phone")
        self.assertEqual(tipo_objeto(cena,{"titulo":"O radio misterioso"}),"radio")

    def test_versao_registra_o_novo_estilo(self):
        self.assertIn("cinematic_2d",versao())

    def test_validacao(self):
        with self.assertRaises(ValueError):
            planejar(self.ep,self.segs,21,0)
        with self.assertRaises(ValueError):
            planejar({"batidas":[]},self.segs,21)
        with tempfile.TemporaryDirectory() as dir:
            with self.assertRaises(ValueError):
                preparar(self.ep,self.segs,dir,21,gerador=lambda cena,ep:b"invalid")
