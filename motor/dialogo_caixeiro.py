"""Dupla Caixeiro + passageiro com DOIS modelos de voz realmente distintos.

Caixeiro: Kokoro (identidade original). Passageiro: Piper Faber (pt_BR,
voz masculina medium, CC0). Sem voz alterada por pitch, sem Edge 403 e sem
fallback silencioso para pm_santa. Se o modelo Faber falhar, o preview falha
explicitamente e nao publica um video com dublagem ruim.

Mantem a timeline palavra a palavra para o lip sync e o SFX de risadas.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.request
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from gerar_voz_kokoro import SR, garantir_modelo, estilo, resample_44100

VOZ_CAIXEIRO = "pm_alex:0.62+pm_santa:0.38"
VOZ_PASSAGEIRO = "pt_BR-faber-medium"
PIPER_MODEL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
    "pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx"
)


def baixar_voz_passageiro() -> Path:
    """Cache do modelo ONNX e config. Downloads nunca entram no repositório."""
    raiz = Path(os.environ.get("CAIXEIRO_PIPER_CACHE",
                              str(Path.home() / ".cache/caixeiro_piper")))
    raiz.mkdir(parents=True, exist_ok=True)
    modelo = raiz / (VOZ_PASSAGEIRO + ".onnx")
    cfg = raiz / (VOZ_PASSAGEIRO + ".onnx.json")
    for alvo, url, tam_min in [
        (modelo, PIPER_MODEL, 10_000_000),
        (cfg, PIPER_MODEL + ".json", 100),
    ]:
        if alvo.is_file() and alvo.stat().st_size >= tam_min:
            continue
        temporario = alvo.with_suffix(alvo.suffix + ".part")
        try:
            requisicao = urllib.request.Request(
                url, headers={"User-Agent": "CaixeiroPreview/1.0"})
            with urllib.request.urlopen(requisicao, timeout=90) as resposta:
                with temporario.open("wb") as dst:
                    while True:
                        parte = resposta.read(1024 * 1024)
                        if not parte:
                            break
                        dst.write(parte)
            if temporario.stat().st_size < tam_min:
                raise RuntimeError(f"Modelo de voz incompleto: {alvo.name}")
            temporario.replace(alvo)
        finally:
            temporario.unlink(missing_ok=True)
    cfg_obj = json.loads(cfg.read_text(encoding="utf-8"))
    if not isinstance(cfg_obj, dict) or not cfg_obj.get("audio"):
        raise RuntimeError("Configuracao do Piper Faber invalida")
    return modelo


def pausa_apos(batida, proximo):
    if batida.get("risada"):
        return 0.76
    return 0.31 if proximo != batida.get("quem") else 0.21


def suavizar_amplitude(som):
    som = np.asarray(som, dtype=np.float32)
    if not som.size:
        raise RuntimeError("TTS retornou fala vazia")
    ativo = np.abs(som) > 0.018
    rms = float(np.sqrt(np.mean(np.square(som[ativo])))) if np.any(ativo) else 0.0
    if rms > 0:
        som = som * min(2.0, 0.115 / rms)
    return (np.tanh(som * 1.08) * 0.88).astype(np.float32)


def voz_piper_faber(piper, fala: str, pasta: Path, indice: int) -> np.ndarray:
    """Sintetiza sem mudar pitch nem tempo; a EQ do projeto vem depois."""
    arq = pasta / f"faber-{indice:03}.wav"
    with wave.open(str(arq), "wb") as wav:
        piper.synthesize_wav(fala, wav)
    som, taxa = sf.read(str(arq), dtype="float32", always_2d=True)
    if len(som) < taxa // 5:
        raise RuntimeError(f"Faber gerou áudio muito curto na fala {indice}")
    return resample_44100(som.mean(axis=1), taxa)


def sintetizar(ep_path: Path, destino: Path, seg_path: Path) -> None:
    from kokoro_onnx import Kokoro
    from piper import PiperVoice

    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    batidas = ep.get("batidas") or []
    if len(batidas) < 4 or not all(
        b.get("quem") in ("caixeiro", "passageiro") and
        str(b.get("fala", "")).strip() for b in batidas
    ):
        raise ValueError("Dialogo exige falas identificadas de motorista/passageiro")
    if {b["quem"] for b in batidas} != {"caixeiro", "passageiro"}:
        raise ValueError("Dialogo exige falas dos dois personagens")

    # É proposital nao usar o antigo fallback Edge -> pm_santa com pitch baixo.
    # O episodio só deve ser publicado depois de sair com dois modelos distintos.
    modelo_piper = baixar_voz_passageiro()
    passageiro = PiperVoice.load(str(modelo_piper))
    caixeiro = Kokoro(*garantir_modelo())
    blocos, segs, t = [], [], 0.0
    with tempfile.TemporaryDirectory(prefix="caixeiro-dialogo-") as d:
        pasta = Path(d)
        for i, b in enumerate(batidas):
            quem = b["quem"]
            if quem == "caixeiro":
                som, taxa = caixeiro.create(
                    b["fala"], voice=estilo(caixeiro, VOZ_CAIXEIRO),
                    speed=0.97, lang="pt-br")
                som = resample_44100(np.asarray(som, dtype=np.float32), taxa)
                voz = VOZ_CAIXEIRO
            else:
                som = voz_piper_faber(passageiro, b["fala"], pasta, i)
                voz = VOZ_PASSAGEIRO
            som = suavizar_amplitude(som)
            proximo = batidas[i+1]["quem"] if i+1 < len(batidas) else quem
            pausa = pausa_apos(b, proximo)
            silencio = np.zeros(round(pausa * SR), dtype=np.float32)
            ini, fim_fala = t, t + len(som) / SR
            t = fim_fala + len(silencio) / SR
            blocos.extend((som, silencio))
            segs.append({
                "i": i, "quem": quem, "voz": voz, "texto": b["fala"],
                "ini": round(ini, 3), "fim_fala": round(fim_fala, 3),
                "fim": round(t, 3),
            })
            print(f"[dupla] {quem} ({voz}): {ini:.2f} a {fim_fala:.2f}s",
                  flush=True)

    audio = np.concatenate(blocos)
    # Normalizacao nivelada e nao agressiva; equalizador/limiter aplica depois.
    pico = float(np.abs(audio).max()) or 1.0
    if pico > 0.94:
        audio = audio * (0.94 / pico)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destino), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes((np.clip(audio, -1, 1)*32767).astype(np.int16).tobytes())
    seg_path.write_text(json.dumps(segs, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    seg_path.with_name("voz_meta.json").write_text(json.dumps({
        "vozes_efetivas": {
            "caixeiro": VOZ_CAIXEIRO,
            "passageiro": VOZ_PASSAGEIRO
        },
        "motor_passageiro": "piper-tts",
        "pitch_shifting": False,
        "eq": "dialogo_suave_v2",
        "sfx_risadas": bool(any(b.get("risada") for b in batidas)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[dupla] concluido {len(segs)} falas, {t:.2f}s, Piper Faber real",
          flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("episodio")
    p.add_argument("--out", required=True)
    p.add_argument("--seg-json", required=True)
    a = p.parse_args()
    sintetizar(Path(a.episodio), Path(a.out), Path(a.seg_json))
