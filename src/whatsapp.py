"""Aviso no WhatsApp do Pablo com o link do vídeo e a descrição pro TikTok.

Usa o CallMeBot (grátis, só manda mensagem pro próprio número cadastrado).
Secrets: WHATSAPP_NUMERO (ex.: +5524999999999) e CALLMEBOT_APIKEY.
Sem os secrets, não faz nada (o resto do pipeline segue normal).

    python -m src.whatsapp --teste     # manda uma mensagem de teste
"""
from __future__ import annotations

import os
import sys
import time

import requests

from src.config import esconder

URL = "https://api.callmebot.com/whatsapp.php"


def configurado() -> bool:
    return bool(os.getenv("WHATSAPP_NUMERO") and os.getenv("CALLMEBOT_APIKEY"))


def enviar(texto: str) -> bool:
    if not configurado():
        print("WhatsApp não configurado (WHATSAPP_NUMERO / CALLMEBOT_APIKEY); pulando.")
        return False
    params = {"phone": os.environ["WHATSAPP_NUMERO"].strip(), "text": texto,
              "apikey": os.environ["CALLMEBOT_APIKEY"].strip()}
    for tentativa in range(3):
        try:
            r = requests.get(URL, params=params, timeout=40)
            corpo = esconder(r.text)[:300]
            if r.status_code == 200 and "ERROR" not in corpo.upper():
                print("WhatsApp enviado.")
                return True
            print(f"::warning::CallMeBot HTTP {r.status_code}: {corpo}")
        except requests.RequestException as e:
            print(f"::warning::CallMeBot falhou: {esconder(str(e))[:200]}")
        time.sleep(8 * (tentativa + 1))
    return False


def mensagem_episodio(ep: dict, link_video: str) -> str:
    return (f"🚗 *Caixeiro na Corrida* — {ep['titulo'].title()}\n\n"
            f"⬇️ Baixar o vídeo:\n{link_video}\n\n"
            f"📝 Descrição pro TikTok (copia e cola):\n\n{ep['legenda_tiktok']}")


if __name__ == "__main__":
    if "--teste" in sys.argv:
        ok = enviar("✅ Teste do Caixeiro na Corrida: o WhatsApp está ligado ao GitHub.")
        sys.exit(0 if ok else 1)
