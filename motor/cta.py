"""Um único fecho depois do desfecho da corrida: coração + seguir."""
from __future__ import annotations

import copy
import re

CTA_FINAL = "Se essa corrida te pegou, aperta o coração aí e segue o Caixeiro pra não perder a próxima história."
PLACA_FINAL = "SEGUE PRA PRÓXIMA CORRIDA"

RX_SEGUE = re.compile(r"\bme\s+segue\b|\bsegue\s+o\s+caixeiro\b|\bsiga\s+o\s+caixeiro\b", re.I)

def eh_cta(b: dict) -> bool:
    return bool(RX_SEGUE.search(b.get("fala", ""))) or (b.get("arte") or [None])[0] == "seguir" or b.get("envio_final") or b.get("fala", "").startswith("Cinco estrelas pra essa história. E você")


def garantir_cta(ep: dict) -> dict:
    """Fecho fixo do canal: aperta o coração + segue pra não perder a próxima."""
    ep = copy.deepcopy(ep)
    bats = [b for b in ep["batidas"] if not eh_cta(b)]
    bats.append({"fala": CTA_FINAL, "envio_final": True, "expr": "ironica",
                 "arte": ["seguir", PLACA_FINAL], "destaque": ["coração", "próxima"]})
    ep["batidas"] = bats
    return ep
