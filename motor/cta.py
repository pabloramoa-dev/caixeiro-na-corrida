"""Um único pedido de envio depois do desfecho da corrida."""
from __future__ import annotations

import copy
import re

RX_SEGUE = re.compile(r"\bme\s+segue\b|\bsegue\s+o\s+caixeiro\b|\bsiga\s+o\s+caixeiro\b", re.I)

def eh_cta(b: dict) -> bool:
    return bool(RX_SEGUE.search(b.get("fala", ""))) or (b.get("arte") or [None])[0] == "seguir" or b.get("envio_final") or b.get("fala", "").startswith("Cinco estrelas pra essa história. E você")


def garantir_cta(ep: dict) -> dict:
    ep = copy.deepcopy(ep)
    bats = [b for b in ep["batidas"] if not eh_cta(b)]
    titulo = ep.get("titulo") or "História de passageiro"
    fala = "Manda pra quem também ouve histórias assim no carro."
    categoria = ep.get("categoria", "")
    for assunto, destinatario in (
        ("viagem", "já correu pra não perder um voo"),
        ("familia", "guarda as melhores histórias da família"),
        ("humor", "ia rir junto no banco de trás"),
        ("comida", "sempre tem uma história boa de cozinha"),
        ("misterio", "adora desvendar um mistério"),
        ("reencontro", "ainda fala daquele reencontro"),
    ):
        if assunto in categoria:
            fala = f"Manda pra quem {destinatario}."
            break
    bats.append({"fala": fala, "envio_final": True, "expr": "ironica", "arte": ["manchete", titulo],
                 "destaque": ["Manda"]})
    ep["batidas"] = bats
    return ep
