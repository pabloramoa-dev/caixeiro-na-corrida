"""Ajusta o tempo antes da virada e sincroniza os segmentos à voz processada."""
import json
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

def sincronizar(wav, arquivo, indice, curto):
    segs = json.loads(Path(arquivo).read_text())
    if not 0 < indice < len(segs):
        return
    pcm, sr = sf.read(wav, dtype='float32')
    corte = round(segs[indice]['ini'] * sr)
    partes = []
    for grupo, audio, alvo in [(segs[:indice], pcm[:corte], 22),
                               (segs[indice:], pcm[corte:], 42 if curto else None)]:
        inicio = sum(len(p) for p in partes) / sr
        origem = grupo[0]['ini']
        taxa = len(audio) / sr / alvo if alvo else 1
        if taxa != 1:
            filtros = []
            while taxa > 2:
                filtros.append('atempo=2')
                taxa /= 2
            while taxa < .5:
                filtros.append('atempo=0.5')
                taxa *= 2
            filtros.append(f'atempo={taxa}')
            raw = subprocess.run(['ffmpeg','-loglevel','error','-f','f32le','-ar',str(sr),
                 '-ac','1','-i','pipe:0','-af',','.join(filtros),'-f','f32le','pipe:1'],
                 input=audio.tobytes(),capture_output=True,check=True).stdout
            novo = np.frombuffer(raw, dtype='<f4')
        else:
            novo = audio
        for seg in grupo:
            for k in ('ini','fim_fala','fim'):
                if k in seg:
                    seg[k] = round(inicio + (seg[k]-origem)*len(novo)/len(audio), 4)
        partes.append(novo)
    sf.write(wav,np.concatenate(partes),sr)
    Path(arquivo).write_text(json.dumps(segs,ensure_ascii=False))
