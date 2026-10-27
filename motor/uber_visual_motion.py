"""Imagens de apoio gratuitas, alinhadas às falas do Caixeiro."""
from __future__ import annotations
import math
from pathlib import Path
try:
    from .local_story_art import render as desenhar
except ImportError:
    from local_story_art import render as desenhar

INTERVALO = 7.0

def planejar(ep, segs, dur, intervalo=INTERVALO):
    if not 1 <= intervalo <= 30:
        raise ValueError("Intervalo visual inválido")
    if not segs or len(segs) != len(ep.get("batidas", [])):
        raise ValueError("Número de batidas incompatível com a timeline")
    cenas = []
    for i in range(math.ceil(dur / intervalo)):
        start = i * intervalo
        if start >= dur:
            break
        beat = next((j for j, s in enumerate(segs) if start < float(s["fim"])), len(segs) - 1)
        cenas.append({"scene": i, "start": start, "end": min(dur, start + intervalo),
                      "beat": beat, "text": ep["batidas"][beat]["fala"]})
    return cenas

def preparar(ep, segs, assets, dur, intervalo=INTERVALO, gerador=None):
    assets = Path(assets)
    assets.mkdir(parents=True, exist_ok=True)
    nomes = []
    desenhista = gerador or desenhar
    for cena in planejar(ep, segs, dur, intervalo):
        name = f"caixeiro-cena-{cena['scene']:02d}.png"
        data = desenhista(cena, ep)
        if not isinstance(data, bytes) or not data.startswith(bytes.fromhex("89504e470d0a1a0a")):
            raise ValueError("Ilustração inválida")
        (assets / name).write_bytes(data)
        nomes.append(name)
    return nomes
