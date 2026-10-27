"""Fila de publicação do Caixeiro na Corrida.

Regras
- Cada episódio é uma história completa num vídeo só (~3 min): episodios/cxNNN.json.
- 3 horários por dia (8h, 12h, 20h). Sai sempre o menor episódio pronto ainda
  não publicado. O das 20h também vai pros Stories.
- Um vídeo só está "pronto" se foi renderizado a partir da versão ATUAL do
  roteiro (reels/<id>.hash). Roteiro editado = volta pro estúdio.
- Nunca publica o mesmo id duas vezes (ledger conteudo/publicados.json).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta

from src import config
from motor.render_version import versao

BRT = timezone(timedelta(hours=-3))
RX = re.compile(r"^cx(\d{3})$")


def ler_publicados() -> list[dict]:
    if config.PUBLICADOS_JSON.exists():
        return json.loads(config.PUBLICADOS_JSON.read_text(encoding="utf-8"))
    return []


def gravar_publicado(ep_id: str, media_id: str | None, dry: bool, **extra) -> None:
    pub = ler_publicados()
    pub.append({"id": ep_id, "media_id": media_id,
                "quando": datetime.now(BRT).isoformat(timespec="minutes"), "ensaio": dry, **extra})
    config.PUBLICADOS_JSON.parent.mkdir(parents=True, exist_ok=True)
    config.PUBLICADOS_JSON.write_text(json.dumps(pub, ensure_ascii=False, indent=1), encoding="utf-8")


def ids_publicados() -> set[str]:
    return {p["id"] for p in ler_publicados() if not p.get("ensaio")}


def carregar_ep(ep_id: str) -> dict:
    return json.loads((config.EPISODIOS / f"{ep_id}.json").read_text(encoding="utf-8"))


def assinatura(ep_id: str) -> str:
    """Impressão digital do roteiro + versão do motor — muda a cada edição."""
    ep = carregar_ep(ep_id)
    bruto = json.dumps({"roteiro": ep, "render": versao()}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(bruto).hexdigest()[:16]


def desatualizado(ep_id: str) -> bool:
    if not (config.REELS / f"{ep_id}.mp4").exists():
        return True
    h = config.REELS / f"{ep_id}.hash"
    if h.exists():
        return h.read_text().strip() != assinatura(ep_id)
    return ep_id not in ids_publicados()


def pronto(ep_id: str) -> bool:
    return (config.REELS / f"{ep_id}-capa.jpg").exists() and not desatualizado(ep_id)


def episodios() -> list[str]:
    ids = [f.stem for f in config.EPISODIOS.glob("cx*.json") if RX.match(f.stem)]
    # Episódios em avaliação ficam fora da produção/publicação programada.
    ids = [e for e in ids if not carregar_ep(e).get("preview_only", False)]
    return sorted(ids, key=lambda item: int(item[2:]))


def prontos_nao_publicados() -> list[str]:
    feitos = ids_publicados()
    return [e for e in episodios() if e not in feitos and pronto(e)]


def proximo(horario: str | None = None) -> str | None:
    lista = prontos_nao_publicados()
    return lista[0] if lista else None


def duracao(caminho) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(caminho)])
    return float(out.strip())


def lint() -> dict:
    problemas = []
    for ep_id in episodios():
        ep = carregar_ep(ep_id)
        if "História de ficção" not in ep.get("legenda_post", ""):
            problemas.append(f"{ep_id}: legenda sem o aviso de ficção")
        if len(ep.get("legenda_post", "")) > 2200:
            problemas.append(f"{ep_id}: legenda passa de 2200 caracteres")
        if not ep.get("legenda_tiktok"):
            problemas.append(f"{ep_id}: sem descrição do TikTok")
        mp4 = config.REELS / f"{ep_id}.mp4"
        if mp4.exists():
            d = duracao(mp4)
            if not config.DURACAO_MIN_S <= d <= config.DURACAO_MAX_S:
                problemas.append(f"{ep_id}: duração {d:.1f}s fora do limite")
    prontos = prontos_nao_publicados()
    return {"episodios": len(episodios()), "publicados": len(ids_publicados()),
            "prontos_nao_publicados": len(prontos),
            "reserva_ok": len(prontos) >= config.RESERVA_MINIMA, "problemas": problemas}


if __name__ == "__main__":
    import sys
    r = lint()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if "--resumo" in sys.argv:
        print(f"prontos={r['prontos_nao_publicados']}")
        print(f"reserva_baixa={'false' if r['reserva_ok'] else 'true'}")
    sys.exit(1 if r["problemas"] else 0)
