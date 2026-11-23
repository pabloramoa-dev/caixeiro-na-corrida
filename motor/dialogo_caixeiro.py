"""Dois dubladores para o Caixeiro: voz local original e visitante Edge.

Mantem a voz da marca, usa uma voz masculina neural pt-BR distinta no
passageiro e uma contingencia offline tonalmente diferenciada.
A timeline preserva autor, boca e intervalos para as risadas discretas.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
import soundfile as sf

from gerar_voz_kokoro import SR, garantir_modelo, estilo, resample_44100

VOZES = {
    "caixeiro": "pm_alex:0.62+pm_santa:0.38",  # identidade existente
    "passageiro": "pt-BR-DonatoNeural",        # Microsoft Edge (masculina pt-BR)
}
VOZ_RESERVA_PASSAGEIRO = "pm_santa"
RATE_PASSAGEIRO = "-4%"

def pausa_apos(batida, proximo):
    if batida.get("risada"):
        return 0.76  # espaco proprio para risada leve, sem cobrir a fala seguinte
    return 0.31 if proximo != batida.get("quem") else 0.21


def suavizar_amplitude(som):
    som = np.asarray(som, dtype=np.float32)
    if not som.size:
        raise RuntimeError("TTS devolveu audio vazio")
    ativo = np.abs(som) > 0.018
    rms = float(np.sqrt(np.mean(np.square(som[ativo])))) if np.any(ativo) else 0.0
    if rms > 0:
        som = som * min(2.0, 0.115 / rms)
    return np.tanh(som * 1.08).astype(np.float32) * 0.88


def voz_local_passageiro(modelo, texto, pasta, indice):
    """Contingencia offline: voz distinta com pitch menor mantendo duracao."""
    som, taxa = modelo.create(texto, voice=estilo(modelo, VOZ_RESERVA_PASSAGEIRO),
                             speed=1.02, lang="pt-br")
    som = resample_44100(np.asarray(som, dtype=np.float32), taxa)
    anterior = pasta / f"voz-backup-{indice}.wav"
    ajustado = pasta / f"voz-backup-tom-{indice}.wav"
    sf.write(anterior, som, SR)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(anterior),
         "-af", "asetrate=37926,aresample=44100,atempo=1.162791,"
                "highpass=f=85,lowpass=f=10000",
         "-ac", "1", "-ar", str(SR), str(ajustado)],
        check=True,
    )
    retorno, _ = sf.read(ajustado, dtype="float32")
    return retorno


async def voz_remota_passageiro(texto, pasta, indice):
    import edge_tts
    mp3 = pasta / f"voz-donato-{indice}.mp3"
    wav = pasta / f"voz-donato-{indice}.wav"
    # Uma tentativa curta por fala: se a rede negar, passamos de vez ao offline.
    await asyncio.wait_for(
        edge_tts.Communicate(texto, VOZES["passageiro"],
                             rate=RATE_PASSAGEIRO).save(str(mp3)),
        timeout=25,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-ac", "1",
         "-ar", str(SR), "-c:a", "pcm_s16le", str(wav)],
        check=True,
    )
    som, _ = sf.read(wav, dtype="float32")
    return som


def sintetizar(ep_path: Path, destino: Path, seg_path: Path) -> None:
    from kokoro_onnx import Kokoro
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    batidas = ep.get("batidas") or []
    if len(batidas) < 4 or not all(
        b.get("quem") in VOZES and str(b.get("fala", "")).strip() for b in batidas
    ):
        raise ValueError("Dialogo exige falas identificadas de caixeiro e passageiro")
    if set(b["quem"] for b in batidas) != set(VOZES):
        raise ValueError("Dialogo exige motorista e passageiro")

    modelo = Kokoro(*garantir_modelo())
    blocos, segs, vozes_usadas = [], [], {}
    t = 0.0
    remota_disponivel = True

    with tempfile.TemporaryDirectory(prefix="caixeiro-dupla-") as d:
        pasta = Path(d)
        for i, b in enumerate(batidas):
            quem = b["quem"]
            if quem == "caixeiro":
                som, taxa = modelo.create(
                    b["fala"], voice=estilo(modelo, VOZES["caixeiro"]),
                    speed=0.97, lang="pt-br",
                )
                som = resample_44100(np.asarray(som, dtype=np.float32), taxa)
                voz = VOZES["caixeiro"]
            else:
                if remota_disponivel:
                    try:
                        som = asyncio.run(voz_remota_passageiro(b["fala"], pasta, i))
                        voz = VOZES["passageiro"]
                    except Exception as exc:
                        remota_disponivel = False
                        print(f"::warning::Voz Donato indisponivel: {type(exc).__name__}; "
                              "usando reserva offline de timbre mais grave", flush=True)
                if not remota_disponivel:
                    som = voz_local_passageiro(modelo, b["fala"], pasta, i)
                    voz = "pm_santa (tom diferenciado)"
            vozes_usadas[quem] = voz
            som = suavizar_amplitude(som)
            proximo = batidas[i + 1]["quem"] if i + 1 < len(batidas) else quem
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
            print(f"[dupla] {quem} / {voz}: {ini:.2f}-{fim_fala:.2f}s", flush=True)

    audio = np.concatenate(blocos)
    pico = max(float(np.abs(audio).max()), 0.0001)
    audio = np.clip(audio / pico * min(0.93, pico), -1, 1)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    seg_path.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    seg_path.with_name("voz_meta.json").write_text(
        json.dumps({"vozes_efetivas": vozes_usadas, "eq": "dialogo_suave_v2",
                    "sfx_risadas": bool(any(b.get("risada") for b in batidas))},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[dupla] {len(segs)} falas / {t:.2f}s / {vozes_usadas}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("episodio")
    p.add_argument("--out", required=True)
    p.add_argument("--seg-json", required=True)
    a = p.parse_args()
    sintetizar(Path(a.episodio), Path(a.out), Path(a.seg_json))
