"""Imagens de apoio gratuitas, alinhadas às falas do Caixeiro."""
from __future__ import annotations
import math
import os
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
    # O estilo cinematografico aprovado e o padrao dos novos renders.
    # Roteiros podem escolher "classic" e a variavel de ambiente oferece rollback.
    if gerador is None:
        estilo = str(ep.get("pilot_visual_style") or ep.get("visual_style") or
                     os.environ.get("CAIXEIRO_STORY_STYLE", "cinematic_2d")).strip().lower()
        if estilo == "cinematic_2d":
            try:
                from .cinematic_story_art import render as desenho_cinematico
            except ImportError:
                from cinematic_story_art import render as desenho_cinematico
            desenhista = desenho_cinematico
        elif estilo != "classic":
            raise ValueError("CAIXEIRO_STORY_STYLE deve ser cinematic_2d ou classic")
    for cena in planejar(ep, segs, dur, intervalo):
        name = f"caixeiro-cena-{cena['scene']:02d}.png"
        data = desenhista(cena, ep)
        if not isinstance(data, bytes) or not data.startswith(bytes.fromhex("89504e470d0a1a0a")):
            raise ValueError("Ilustração inválida")
        (assets / name).write_bytes(data)
        nomes.append(name)
    return nomes
