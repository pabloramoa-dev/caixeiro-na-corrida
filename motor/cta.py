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
    """Uma única chamada final; nos causos curtos, pedir compartilhamento."""
    ep = copy.deepcopy(ep)
    bats = [b for b in ep["batidas"] if not eh_cta(b)]
    if ep.get("formato") == "corrida_1min":
        fala = ep.get("cta_envio", "Manda pra quem precisa dar uma risada hoje.")
        bats.append({"fala": fala, "envio_final": True, "expr": "rindo",
                     "arte": ["manchete_v", "MANDA PRA QUEM VAI RIR"],
                     "destaque": ["Manda", "rir"]})
    else:
        bats.append({"fala": CTA_FINAL, "envio_final": True, "expr": "ironica",
                     "arte": ["seguir", PLACA_FINAL], "destaque": ["coração", "próxima"]})
    ep["batidas"] = bats
    return ep
