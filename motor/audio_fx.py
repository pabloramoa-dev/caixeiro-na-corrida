"""Tratamento de áudio do Caixeiro com Spotify Pedalboard.

- masterizar_voz(): cadeia de estúdio para a voz do Caixeiro (de-esser, corpo nos
  graves, tira o embolado, dicção sem arder, compressão suave, ambiência mínima
  de carro e limitador suave). Mantém WAV mono 44,1 kHz 16-bit e a MESMA duração
  da narração bruta, então segs.json e o lip sync continuam válidos.
- tratar_trilha() / ducking(): deixa a trilha abafada e abaixa sozinha quando a
  Nina fala.
- finalizar(): limitador de saída da mixagem.

Se o pedalboard não funcionar na máquina (falta a lib, ou o binário dela
derruba o Python com "Illegal instruction" em alguns runners do GitHub), tudo
cai numa cadeia equivalente em ffmpeg + numpy. O teste do pedalboard roda num
processo separado, então um travamento dele nunca derruba a produção.
NINA_PEDALBOARD=0 força a cadeia ffmpeg/numpy.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

# Equalização da voz do Caixeiro (masculina, grave). Mesma curva nas duas cadeias:
#   70 Hz   passa-altas: tira ronco e estalo de grave
#   130 Hz  +2,0 dB: corpo e calor de locutor
#   330 Hz  -3,0 dB: tira o som "de caixa"/embolado
#   2,6 kHz +1,5 dB (largo): dicção clara no alto-falante do celular, sem arder
#   7 kHz   -1,0 dB: amacia o chiado do "s" (junto com o de-esser abaixo)
#   11 kHz  passa-baixas: corta o resíduo metálico do TTS
# Depois: compressão suave (voz firme sem "bombar"), ambiência mínima de carro.
MASTER_FFMPEG = ("highpass=f=70,equalizer=f=130:t=q:w=0.9:g=2.0,"
                 "equalizer=f=330:t=q:w=1.1:g=-3.0,equalizer=f=2600:t=q:w=0.7:g=1.5,"
                 "equalizer=f=7000:t=q:w=1.4:g=-1.0,lowpass=f=11000,"
                 "acompressor=threshold=-21dB:ratio=2.2:attack=12:release=160,"
                 "aecho=1.0:1.0:19|33:0.030|0.015")
# Acabamento especifico da conversa: calor, menos sibilancia, compressao leve.
MASTER_DIALOGO_FFMPEG = (
    "highpass=f=80,equalizer=f=180:t=q:w=0.9:g=0.7,"
    "equalizer=f=340:t=q:w=1.0:g=-2.0,equalizer=f=3100:t=q:w=0.8:g=-0.5,"
    "equalizer=f=6300:t=q:w=1.2:g=-1.8,lowpass=f=9500,"
    "acompressor=threshold=-24dB:ratio=1.65:attack=18:release=220"
)
RMS_DIALOGO = -15.0
RMS_VOZ = -13.0                      # nível da fala (dB RMS) antes do limitador suave
TETO_VOZ = 10 ** (-1.5 / 20)
TETO_MIX = 10 ** (-1.5 / 20)

_TESTE = ("import numpy as np, pedalboard as p;"
          "p.Pedalboard([p.Compressor(), p.Reverb(), p.Limiter()])"
          "(np.zeros((1, 4410), dtype=np.float32), 44100)")


def _pedalboard_seguro():
    if os.environ.get("NINA_PEDALBOARD", "1") == "0":
        return None
    try:
        ok = subprocess.run([sys.executable, "-c", _TESTE], capture_output=True,
                            timeout=120).returncode == 0
    except Exception:
        ok = False
    if not ok:
        print("audio_fx: pedalboard indisponível nesta máquina — usando ffmpeg/numpy", flush=True)
        return None
    import pedalboard
    return pedalboard


pb = _pedalboard_seguro()


def disponivel() -> bool:
    return pb is not None


def cadeia_voz():
    return pb.Pedalboard([
        pb.HighpassFilter(cutoff_frequency_hz=70),
        pb.PeakFilter(cutoff_frequency_hz=130, gain_db=2.0, q=0.9),     # corpo/calor
        pb.PeakFilter(cutoff_frequency_hz=330, gain_db=-3.0, q=1.1),    # tira o "embolado"
        pb.PeakFilter(cutoff_frequency_hz=2600, gain_db=1.5, q=0.7),    # dicção, sem arder
        pb.PeakFilter(cutoff_frequency_hz=7000, gain_db=-1.0, q=1.4),   # amacia o "s"
        pb.LowpassFilter(cutoff_frequency_hz=11000),                    # resíduo metálico do TTS
        pb.Compressor(threshold_db=-21, ratio=2.2, attack_ms=12, release_ms=160),
        pb.Reverb(room_size=0.10, damping=0.8, wet_level=0.03, dry_level=1.0, width=0.0),
    ])


def cadeia_voz_dialogo():
    """Equalizacao suave com minimo reverb, sem distorcer o timbre."""
    return pb.Pedalboard([
        pb.HighpassFilter(cutoff_frequency_hz=80),
        pb.PeakFilter(cutoff_frequency_hz=180, gain_db=0.7, q=0.9),
        pb.PeakFilter(cutoff_frequency_hz=340, gain_db=-2.0, q=1.0),
        pb.PeakFilter(cutoff_frequency_hz=3100, gain_db=-0.5, q=0.8),
        pb.PeakFilter(cutoff_frequency_hz=6300, gain_db=-1.8, q=1.2),
        pb.LowpassFilter(cutoff_frequency_hz=9500),
        pb.Compressor(threshold_db=-24, ratio=1.65, attack_ms=18, release_ms=220),
        pb.Reverb(room_size=0.08, damping=0.85, wet_level=0.015,
                  dry_level=1.0, width=0.0),
    ])


def deesser(x, sr, lo=5200.0, hi=10500.0, limiar=0.42, max_db=8.0):
    """De-esser: abaixa só a faixa do chiado, e só nos instantes em que o "s" domina.

    Compara a energia da faixa 5–10 kHz com a da voz inteira; por ser relativo,
    funciona igual em qualquer volume. Fase linear (FFT) e mesma duração."""
    n = len(x)
    if n < sr // 10:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    sobe = np.clip((f - lo * 0.85) / (lo * 0.15), 0, 1)
    desce = np.clip((hi * 1.15 - f) / (hi * 0.15), 0, 1)
    faixa = np.fft.irfft(X * (0.5 - 0.5 * np.cos(np.pi * sobe)) * (0.5 - 0.5 * np.cos(np.pi * desce)), n)

    def rms(s, ms):
        k = max(1, int(sr * ms / 1000))
        c = np.cumsum(np.concatenate([[0.0], s.astype(np.float64) ** 2]))
        m = (c[k:] - c[:-k]) / k
        return np.sqrt(np.pad(m, (k // 2, n - len(m) - k // 2), mode="edge"))

    ef, et = rms(faixa, 8), rms(x, 8) + 1e-6
    razao = ef / et
    g = np.where(razao > limiar, (limiar / np.maximum(razao, 1e-6)) ** 1.2, 1.0)
    g = np.maximum(g, 10 ** (-max_db / 20))
    k = max(1, int(sr * 0.006))                     # suaviza o ganho (6 ms)
    g = np.convolve(np.pad(g, (k // 2, k - 1 - k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    return x - faixa * (1 - g)


def masterizar_voz(entrada, saida, suave=False) -> str:
    audio, sr = sf.read(str(entrada), dtype="float32", always_2d=True)
    mono = deesser(audio.mean(axis=1).astype(np.float64), sr,
                    limiar=0.36 if suave else 0.42,
                    max_db=6.0 if suave else 8.0)
    if pb is None:
        with tempfile.TemporaryDirectory() as tmp:
            limpo, bruto = os.path.join(tmp, "d.wav"), os.path.join(tmp, "m.wav")
            sf.write(limpo, mono, sr, subtype="FLOAT")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", limpo, "-ac", "1",
                            "-af", MASTER_DIALOGO_FFMPEG if suave else MASTER_FFMPEG, "-ar", str(sr), "-c:a", "pcm_f32le", bruto], check=True)
            out, _ = sf.read(bruto, dtype="float64")
        motor = "ffmpeg"
    else:
        out = (cadeia_voz_dialogo() if suave else cadeia_voz())(mono.astype(np.float32)[np.newaxis, :], sr)[0].astype(np.float64)
        motor = "pedalboard"
    out = np.pad(out, (0, max(0, len(mono) - len(out))))[: len(mono)]       # mesma duração
    out = _nivelar(out, RMS_DIALOGO if suave else RMS_VOZ, TETO_VOZ)
    sf.write(str(saida), out, sr, subtype="PCM_16")
    return motor


def _nivelar(x, rms_db, teto):
    """Leva a fala ao RMS alvo e segura os picos com limitador suave (tanh)."""
    fala = x[np.abs(x) > 0.01]
    rms = np.sqrt(np.mean(fala ** 2)) if len(fala) else 0.0
    if rms > 0:
        x = x * (10 ** (rms_db / 20) / rms)
    joelho = 0.7 * teto
    a = np.abs(x)
    acima = a > joelho
    a[acima] = joelho + (teto - joelho) * np.tanh((a[acima] - joelho) / (teto - joelho))
    return np.sign(x) * a


def tratar_trilha(bed: np.ndarray, sr: int) -> np.ndarray:
    if pb is None:
        return _trilha_numpy(bed, sr)
    fx = pb.Pedalboard([
        pb.LowpassFilter(cutoff_frequency_hz=2600),
        pb.Chorus(rate_hz=0.25, depth=0.15, mix=0.25),
        pb.Reverb(room_size=0.55, damping=0.5, wet_level=0.30, dry_level=0.8, width=0.0),
    ])
    return fx(bed.astype(np.float32)[np.newaxis, :], sr)[0][: len(bed)]


def _trilha_numpy(bed, sr):
    """Passa-baixa 2,6 kHz + reverberação curta por convolução (FFT)."""
    n = len(bed)
    X = np.fft.rfft(bed)
    f = np.fft.rfftfreq(n, 1 / sr)
    X *= 1 / np.sqrt(1 + (f / 2600) ** 4)
    seco = np.fft.irfft(X, n)
    t = np.arange(int(1.6 * sr)) / sr
    ir = np.random.default_rng(17).normal(size=len(t)) * np.exp(-t * 4.0)
    ir /= np.sqrt(np.sum(ir ** 2)) or 1.0
    m = 1 << int(np.ceil(np.log2(n + len(ir))))
    molhado = np.fft.irfft(np.fft.rfft(seco, m) * np.fft.rfft(ir, m), m)[:n]
    return 0.8 * seco + 0.30 * molhado


def ducking(voz: np.ndarray, sr: int, profundidade: float = 0.65,
            ataque: float = 0.04, soltura: float = 0.45) -> np.ndarray:
    """Ganho 0..1 para a trilha: cai `profundidade` enquanto há voz."""
    hop = max(1, sr // 100)                       # envelope a cada 10 ms
    n = len(voz) // hop + 1
    pad = np.zeros(n * hop)
    pad[: len(voz)] = np.abs(voz)
    env = pad.reshape(n, hop).max(axis=1)
    ativo = (env > 0.02).astype(float)
    a_up = 1 - np.exp(-0.01 / ataque)
    a_dn = 1 - np.exp(-0.01 / soltura)
    sm = np.zeros(n)
    v = 0.0
    for i, x in enumerate(ativo):
        v += (a_up if x > v else a_dn) * (x - v)
        sm[i] = v
    ganho = 1 - profundidade * sm
    return np.interp(np.arange(len(voz)), np.arange(n) * hop, ganho)


def finalizar(mix: np.ndarray, sr: int) -> np.ndarray:
    if pb is None:
        pico = np.max(np.abs(mix)) or 1.0
        return mix * min(1.0, TETO_MIX / pico)
    lim = pb.Pedalboard([pb.Limiter(threshold_db=-1.5, release_ms=60)])
    return np.clip(lim(mix.astype(np.float32)[np.newaxis, :], sr)[0], -0.99, 0.99)


def normalizar_mix(arquivo, sr):
    """Normaliza a mixagem completa a -16 LUFS, com teto de -1,5 dBTP."""
    destino = arquivo.with_suffix('.normalizado.wav')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(arquivo),'-af',
                    'loudnorm=I=-16:TP=-1.5:LRA=11','-ar',str(sr),
                    '-c:a','pcm_s16le',str(destino)], check=True)
    os.replace(destino,arquivo)
