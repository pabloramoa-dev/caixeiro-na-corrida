"""Testes rápidos da série de humor, sem voz, render nem postagem."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from motor.corridas_1min import CATALOGO, FORMATO, gerar_estoque, montar, validar_catalogo
from motor.cta import garantir_cta
from src import fila


class CorridaUmMinutoTest(unittest.TestCase):
    def test_catalogo_e_roteiros(self):
        itens = json.loads(CATALOGO.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(itens), 90)
        validar_catalogo(itens)
        primeiro = montar(itens[0], 0)
        self.assertEqual(primeiro["id"], "cx500")
        self.assertEqual(montar(itens[-1], len(itens) - 1)["id"], "cx589")
        self.assertEqual(primeiro["formato"], FORMATO)
        self.assertIn("História de ficção", primeiro["legenda_post"])
        self.assertEqual(len(primeiro["batidas"]), 6)
        self.assertNotIn("Sobe aí", primeiro["batidas"][0]["fala"])
        self.assertTrue(primeiro["cta_envio"].startswith("Manda pra quem"))
        self.assertEqual(garantir_cta(primeiro)["batidas"][-1]["fala"], primeiro["cta_envio"])

    def test_gerar_estoque_nao_duplica_e_respeita_publicados(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            episodios = raiz / "episodios"
            publicados = raiz / "publicados.json"
            a = gerar_estoque(3, episodios=episodios, publicados=publicados)
            self.assertEqual(a, ["cx500", "cx501", "cx502"])
            self.assertEqual(gerar_estoque(3, episodios=episodios, publicados=publicados), [])
            publicados.write_text(
                json.dumps([{"id": "cx500", "ensaio": False}, {"id": "cx501", "ensaio": True}]),
                encoding="utf-8"
            )
            self.assertEqual(gerar_estoque(3, episodios=episodios, publicados=publicados), ["cx503"])
            self.assertEqual(
                json.loads((episodios / "cx500.json").read_text())["titulo"],
                json.loads(CATALOGO.read_text())[0]["titulo"]
            )

    def test_estoque_nunca_sobrescreve_id_de_outro_formato(self):
        with tempfile.TemporaryDirectory() as d:
            pasta = Path(d) / "episodios"
            pasta.mkdir()
            (pasta / "cx500.json").write_text(json.dumps({"id": "cx500", "formato": "longo"}))
            with self.assertRaisesRegex(ValueError, "já ocupado"):
                gerar_estoque(1, episodios=pasta, publicados=Path(d) / "publicados.json")

    def test_filas_do_almoco_e_noite_nao_se_misturam(self):
        with tempfile.TemporaryDirectory() as d:
            pasta = Path(d)
            for id_, formato in (("cx500", "corrida_1min"), ("cx351", "longo")):
                (pasta / f"{id_}.json").write_text(json.dumps({"id": id_, "formato": formato}))
            with patch.object(fila.config, "EPISODIOS", pasta), patch.object(
                fila, "prontos_nao_publicados", return_value=["cx351", "cx500"]
            ):
                self.assertEqual(fila.proximo("almoco"), "cx500")
                self.assertEqual(fila.proximo("noite"), "cx351")
                self.assertEqual(fila.proximo("manha"), None)


if __name__ == "__main__":
    unittest.main()
