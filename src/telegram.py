"""Manda o MP4 do Caixeiro + a descrição pro Telegram (mesmo bot e chat da Nina).

Secrets: TELEGRAM_BOT_TOKEN_NINA e TELEGRAM_CHAT_ID_NINA.
Sem eles, não faz nada (o resto do pipeline segue normal).

    python -m src.telegram --teste     # manda uma mensagem de teste
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

from src.config import esconder

LIMITE_BYTES = 49_000_000   # bots do Telegram aceitam até 50 MB por arquivo


def configurado() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN_NINA") and os.getenv("TELEGRAM_CHAT_ID_NINA"))


def _post(metodo: str, data: dict, arquivo: Path | None = None, campo: str = "") -> bool:
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN_NINA'].strip()}/{metodo}"
    for tentativa in range(3):
        try:
            if arquivo:
                with arquivo.open("rb") as f:
                    r = requests.post(url, data=data, files={campo: (arquivo.name, f, "video/mp4")}, timeout=600)
            else:
                r = requests.post(url, data=data, timeout=60)
            if r.ok and r.json().get("ok"):
                return True
            print(f"::warning::Telegram {metodo} HTTP {r.status_code}: {esconder(r.text)[:300]}")
        except requests.RequestException as e:
            print(f"::warning::Telegram {metodo} falhou: {esconder(str(e))[:200]}")
        time.sleep(10 * (tentativa + 1))
    return False


def _baixar(fonte: str, destino: Path) -> Path:
    if Path(fonte).exists():
        return Path(fonte)
    with requests.get(fonte, stream=True, timeout=180) as r:
        r.raise_for_status()
        with destino.open("wb") as f:
            for parte in r.iter_content(1 << 20):
                f.write(parte)
    return destino


def _caber(video: Path, pasta: Path) -> Path:
    if video.stat().st_size <= LIMITE_BYTES:
        return video
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(video)]).strip())
    kbps = max(400, int(LIMITE_BYTES * 8 / 1000 / dur * 0.9) - 128)
    menor = pasta / video.name.replace(".mp4", "-tg.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-c:v", "libx264",
                    "-b:v", f"{kbps}k", "-maxrate", f"{kbps}k", "-bufsize", f"{2 * kbps}k",
                    "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                    str(menor)], check=True)
    return menor


def mensagem_episodio(ep: dict, publicado_ig: bool) -> str:
    status = "✅ Publicado no Instagram" if publicado_ig else "⚠️ Instagram não publicou (veja o log no GitHub)"
    return (f"🚗 Caixeiro na Corrida — {ep['titulo']}\n{status}\n\n"
            f"📝 Descrição pro TikTok (copia e cola):\n\n{ep['legenda_tiktok']}")


def enviar_video(fonte: str, ep_id: str, texto: str) -> bool:
    """fonte = caminho local ou URL do MP4. Manda o vídeo com a descrição na legenda."""
    if not configurado():
        print("Telegram não configurado (TELEGRAM_BOT_TOKEN_NINA / TELEGRAM_CHAT_ID_NINA); pulando.")
        return False
    chat = os.environ["TELEGRAM_CHAT_ID_NINA"].strip()
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        video = _caber(_baixar(fonte, pasta / f"{ep_id}.mp4"), pasta)
        legenda = texto[:1024]
        ok = (_post("sendVideo", {"chat_id": chat, "caption": legenda, "supports_streaming": "true"}, video, "video")
              or _post("sendDocument", {"chat_id": chat, "caption": legenda}, video, "document"))
    if ok and len(texto) > 1024:
        _post("sendMessage", {"chat_id": chat, "text": texto[:4096]})
    print("Telegram enviado." if ok else "::warning::Telegram não recebeu o vídeo.")
    return ok


if __name__ == "__main__":
    if "--teste" in sys.argv:
        if not configurado():
            print("Telegram não configurado.")
            sys.exit(1)
        ok = _post("sendMessage", {"chat_id": os.environ["TELEGRAM_CHAT_ID_NINA"].strip(),
                                   "text": "✅ Teste do Caixeiro na Corrida: o Telegram está ligado ao GitHub."})
        sys.exit(0 if ok else 1)
