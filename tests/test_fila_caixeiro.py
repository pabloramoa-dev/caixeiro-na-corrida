import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import fila

class FilaCaixeiroTest(unittest.TestCase):
    def test_ordem_e_exclusao_dos_episodios_preview(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "cx030.json").write_text(json.dumps({"id": "cx030"}))
            (folder / "cx025.json").write_text(json.dumps({"id": "cx025", "preview_only": True}))
            (folder / "cx027.json").write_text(json.dumps({"id": "cx027"}))
            with patch.object(fila.config, "EPISODIOS", folder):
                self.assertEqual(fila.episodios(), ["cx027", "cx030"])

    def test_episodios_nunca_retorna_none(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(fila.config, "EPISODIOS", Path(d)):
                self.assertEqual(fila.episodios(), [])
