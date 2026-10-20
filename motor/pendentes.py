"""Lista os roteiros que precisam ir pro estúdio agora.

Mantém ALVO vídeos prontos (não publicados) na fila. O resto dos 300 roteiros
fica só como JSON até chegar a vez — o Git não precisa carregar centenas de MP4.

    python motor/pendentes.py --rel --alvo-prontos 9 --limite 9
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src import fila  # noqa: E402


def selecionar(alvo: int, limite: int) -> list[Path]:
    feitos = fila.ids_publicados()
    prontos = len(fila.prontos_nao_publicados())
    faltam = max(0, alvo - prontos)
    out: list[Path] = []
    for ep_id in fila.episodios():
        if len(out) >= min(faltam, limite):
            break
        if ep_id in feitos or not fila.desatualizado(ep_id):
            continue
        out.append(RAIZ / "episodios" / f"{ep_id}.json")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rel", action="store_true")
    ap.add_argument("--alvo-prontos", type=int, default=9)
    ap.add_argument("--limite", type=int, default=9)
    a = ap.parse_args()
    for p in selecionar(max(1, a.alvo_prontos), max(1, a.limite)):
        print(p.relative_to(RAIZ) if a.rel else p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
