"""Testes para ganchos factuais sem spoiler nem republicação."""
import json
import unittest
from pathlib import Path
from motor.ganchos_caixeiro import aplicar_ganchos, VERSAO

ROOT = Path(__file__).resolve().parents[1]

class GanchosCaixeiroTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = [json.loads(p.read_text(encoding="utf-8"))
                        for p in sorted((ROOT / "episodios").glob("cx*.json"))]
        if not cls.examples:
            raise RuntimeError("Nenhum roteiro disponível para testes")

    def test_idempotencia_nao_muda_original_e_sem_spoiler_inventado(self):
        for ep in self.examples:
            primeiro = ep["batidas"][0]["fala"]
            ultimo = ep["batidas"][-1]["fala"]
            novo = aplicar_ganchos(ep)
            self.assertEqual(ep["batidas"][0]["fala"], primeiro)
            self.assertEqual(novo, aplicar_ganchos(novo), ep["id"])
            self.assertEqual(len(novo["batidas"]), len(ep["batidas"]), ep["id"])
            self.assertEqual(novo["batidas"][-1]["fala"], ultimo, ep["id"])
            if novo.get("gancho_modelo") == "antecipacao_factual":
                self.assertIn(novo["gancho_pista"],
                              novo["batidas"][0]["fala"], ep["id"])
                self.assertGreaterEqual(novo["gancho_origem"], 1)
                self.assertNotIn("Sobe aí", novo["batidas"][0]["fala"])
            if "reenganche_indice" in novo:
                idx = novo["reenganche_indice"]
                self.assertGreater(idx, 0)
                self.assertLess(idx, len(ep["batidas"]) - 2)
                self.assertIn(ep["batidas"][idx]["fala"].lstrip("Aí, MasSó que"),
                              novo["batidas"][idx]["fala"] + "  ", ep["id"])

    def test_nao_mexe_no_piloto(self):
        piloto = next((e for e in self.examples if e.get("preview_only")), None)
        if piloto:
            self.assertEqual(piloto, aplicar_ganchos(piloto))

    def test_cta_preservado_quando_adicionado(self):
        from motor.cta import garantir_cta
        base = next(e for e in self.examples if not e.get("preview_only"))
        com_cta = garantir_cta(base)
        out = aplicar_ganchos(com_cta)
        self.assertEqual(out["batidas"][-1]["fala"], com_cta["batidas"][-1]["fala"])
        self.assertEqual(out.get("gancho_versao"), VERSAO)

    def test_compilador_aplica_a_mesma_versao(self):
        from motor.compilar_roteiros import montar
        amostra = {"num": 998,"titulo": "CAIXA MISTERIOSA","categoria":"humor",
                    "cenario":"dia","onde":"teste","cab":{"G":"x","P":"y","H":"#teste"},
                    "batidas":next(e for e in self.examples if not e.get("preview_only"))["batidas"]}
        x = montar(amostra)
        self.assertEqual(x.get("gancho_versao"), VERSAO)

if __name__ == "__main__":
    unittest.main()
