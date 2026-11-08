"""Versão do vídeo para os Stories (a API aceita no máximo 60 s).

    python motor/story.py reels/ep006-p1.mp4 reels/ep006-p1-story.mp4

Se o vídeo já cabe em 59 s, copia igual. Se passa, mantém o começo e os
últimos FINAL_S segundos (o CTA de seguir + a placa final), com um corte seco
no meio — o CTA do fim nunca é perdido.
"""
from __future__ import annotations

import shutil
import subprocess
import sys

MAX_S = 59.0
FINAL_S = 7.5


def duracao(p: str) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", p])
    return float(out.strip())


def fazer_story(entrada: str, saida: str) -> str:
    d = duracao(entrada)
    if d <= MAX_S:
        shutil.copy(entrada, saida)
        return saida
    cabeca = MAX_S - FINAL_S - 0.3
    cauda = d - FINAL_S
    # Corta em dois pedaços pequenos (pouca memória) e junta com o concat demuxer.
    import os, tempfile
    tmp = tempfile.mkdtemp(prefix="story_")
    a, b, lista = os.path.join(tmp, "a.mp4"), os.path.join(tmp, "b.mp4"), os.path.join(tmp, "l.txt")
    enc = ["-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-threads", "2"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-t", f"{cabeca:.3f}",
                    "-af", f"afade=t=out:st={cabeca-0.15:.3f}:d=0.15", *enc, a], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{cauda:.3f}", "-i", entrada,
                    "-af", "afade=t=in:d=0.15", *enc, b], check=True)
    open(lista, "w").write(f"file '{a}'\nfile '{b}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c", "copy", "-movflags", "+faststart", saida], check=True)
    return saida


if __name__ == "__main__":
    print(fazer_story(sys.argv[1], sys.argv[2]))
