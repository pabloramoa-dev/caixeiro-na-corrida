"""Sintese em duas vozes para os pilotos de conversa do Caixeiro.
Reaproveita Kokoro, a linha do tempo e as pausas da dupla do previsao-modelo.
Nao publica nada; so produz voz e segmentos compativeis com HyperFrames.
"""
from __future__ import annotations
import argparse
import json
import wave
from pathlib import Path
import numpy as np
from gerar_voz_kokoro import SR, garantir_modelo, estilo, resample_44100

VOZES = {
    "caixeiro": "pm_alex:0.62+pm_santa:0.38",
    "passageiro": "pm_santa",
}

def sintetizar(ep_path: Path, destino: Path, seg_path: Path) -> None:
    from kokoro_onnx import Kokoro
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    batidas = ep.get("batidas") or []
    if len(batidas) < 4 or not all(b.get("quem") in VOZES and b.get("fala", "").strip() for b in batidas):
        raise ValueError("Dialogo exige falas identificadas de caixeiro e passageiro")
    if set(b["quem"] for b in batidas) != set(VOZES):
        raise ValueError("Dialogo precisa dos dois personagens")
    modelo = Kokoro(*garantir_modelo())
    blocos, segs = [], []
    t = 0.0
    for i, b in enumerate(batidas):
        quem = b["quem"]
        wav, taxa = modelo.create(b["fala"], voice=estilo(modelo, VOZES[quem]),
                                 speed=0.97 if quem == "caixeiro" else 1.01, lang="pt-br")
        som = resample_44100(np.asarray(wav, dtype=np.float32), taxa)
        if not len(som):
            raise RuntimeError("Fala vazia no segmento " + str(i))
        proximo = batidas[i+1]["quem"] if i+1 < len(batidas) else quem
        pausa = 0.30 if proximo != quem else 0.20
        silencio = np.zeros(round(pausa * SR), dtype=np.float32)
        ini, fim_fala = t, t + len(som) / SR
        t = fim_fala + len(silencio) / SR
        blocos.extend((som, silencio))
        segs.append({"i": i, "quem": quem, "texto": b["fala"],
                     "ini": round(ini, 3), "fim_fala": round(fim_fala, 3),
                     "fim": round(t, 3)})
        print(f"[dupla] {quem}: {ini:.2f} a {fim_fala:.2f}: {b['fala']}", flush=True)
    audio = np.concatenate(blocos)
    pico = max(float(np.abs(audio).max()), 0.0001)
    audio = np.clip(audio / pico * 0.93, -1, 1)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    seg_path.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[dupla] {len(segs)} falas, {t:.2f}s, dois timbres, sem publicacao", flush=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("episodio")
    p.add_argument("--out", required=True)
    p.add_argument("--seg-json", required=True)
    a = p.parse_args()
    sintetizar(Path(a.episodio), Path(a.out), Path(a.seg_json))
