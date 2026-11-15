import json
import re
from pathlib import Path

OBJETOS = json.loads(Path(__file__).with_name("objetos_svg.json").read_text())
PADRAO = re.compile(r"\b(" + "|".join(OBJETOS) + r")(?:s|es)?\b", re.I)

def objeto(texto):
    match = PADRAO.search(texto)
    return match.group(1).lower() if match else None
