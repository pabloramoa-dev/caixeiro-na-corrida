#!/usr/bin/env python3
"""Apaga a mídia já publicada depois de alguns dias (o link do WhatsApp fica
valendo esse tempo pra baixar e postar no TikTok) e segura o estoque.

Roteiros (episodios/) e histórico (conteudo/publicados.json) nunca são apagados.

    python motor/limpar_reels.py --dias 4 --alvo 9
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REELS = RAIZ / "reels"
PUBLICADOS = RAIZ / "conteudo" / "publicados.json"
RX = re.compile(r"^(cx\d{3})")
BRT = timezone(timedelta(hours=-3))


def limpar(dias: int = 4, alvo: int = 9, simular: bool = False) -> dict:
    dados = json.loads(PUBLICADOS.read_text(encoding="utf-8")) if PUBLICADOS.exists() else []
    quando = {}
    for x in dados:
        if x.get("ensaio") or not RX.match(str(x.get("id", ""))) or "-story" in str(x.get("id")):
            continue
        quando[x["id"]] = datetime.fromisoformat(x["quando"])
    limite = datetime.now(BRT) - timedelta(days=dias)
    grupos: dict[str, list[Path]] = {}
    for p in (REELS.iterdir() if REELS.exists() else []):
        m = RX.match(p.name)
        if p.is_file() and m:
            grupos.setdefault(m.group(1), []).append(p)
    nao_pub = sorted((i for i in grupos if i not in quando), key=lambda s: int(s[2:]))
    excesso = set(nao_pub[alvo:])
    remover = []
    for ep_id, arqs in grupos.items():
        if (ep_id in quando and quando[ep_id] < limite) or ep_id in excesso:
            remover.extend(arqs)
    total = sum(p.stat().st_size for p in remover)
    if not simular:
        for p in remover:
            p.unlink(missing_ok=True)
    return {"removidos": len(remover), "mb": round(total / 1e6, 1), "simular": simular}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=4)
    ap.add_argument("--alvo", type=int, default=9)
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    print(json.dumps(limpar(a.dias, a.alvo, a.simular), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
