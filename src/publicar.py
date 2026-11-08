"""Publica o episódio do horário no Instagram e avisa no WhatsApp.

    python -m src.publicar --horario manha      # 08h: Reel
    python -m src.publicar --horario almoco     # 12h: Reel
    python -m src.publicar --horario noite      # 20h: Reel + Story

- Instagram: só publica com PUBLICAR_ATIVO=true e DRY_RUN=false.
- WhatsApp: manda o link do MP4 + a descrição pro TikTok (se configurado).
- O episódio conta como "saiu" quando foi pro Instagram OU, com o Instagram
  desligado, quando o WhatsApp foi entregue (assim a fila anda do mesmo jeito
  para quem posta só no TikTok).
"""
from __future__ import annotations

import argparse
import json
import sys

from src import config, fila, whatsapp
from src.instagram import Publicador


def publicar_story(pub: Publicador, cfg, ep_id: str) -> str:
    arq = f"{ep_id}-story.mp4" if (config.REELS / f"{ep_id}-story.mp4").exists() else f"{ep_id}.mp4"
    container = pub.criar_container_story(f"{cfg.raw_base_url}/reels/{arq}")
    pub.aguardar_pronto(container)
    return pub.publicar(container)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horario", choices=list(config.HORARIOS), required=True)
    a = ap.parse_args()
    com_story = a.horario in config.COM_STORY

    dry = config._flag("DRY_RUN", "true")
    ig_ligado = config._flag("PUBLICAR_ATIVO", "false") and not dry
    cfg = config.carregar(exigir_credenciais=ig_ligado)
    ep_id = fila.proximo(a.horario)
    if ep_id is None:
        print(json.dumps({"ok": True, "publicado": None,
                          "motivo": f"nada pronto para o horário {config.HORARIOS[a.horario]}"},
                         ensure_ascii=False))
        print("::warning::Fila vazia: nenhum episódio pronto.")
        return 0

    ep = fila.carregar_ep(ep_id)
    video = f"{cfg.raw_base_url}/reels/{ep_id}.mp4"
    capa = f"{cfg.raw_base_url}/reels/{ep_id}-capa.jpg"
    rel = {"horario": config.HORARIOS[a.horario], "id": ep_id, "titulo": ep["titulo"],
           "video": video, "capa": capa, "story": com_story,
           "duracao": round(fila.duracao(config.REELS / f"{ep_id}.mp4"), 1)}

    if dry:
        rel.update(ok=True, ensaio=True, motivo="DRY_RUN ligado",
                   whatsapp_previa=whatsapp.mensagem_episodio(ep, video))
        print(json.dumps(rel, ensure_ascii=False, indent=1))
        return 0

    media_id = None
    if ig_ligado:
        pub = Publicador(cfg)
        container = pub.criar_container(video, ep["legenda_post"], capa)
        pub.aguardar_pronto(container)
        try:
            media_id = pub.publicar(container)
        except Exception:
            media_id = pub.reconciliar(container, ep["legenda_post"])
            if not media_id:
                raise
            rel["reconciliado_apos_erro"] = True
        rel["media_id"] = media_id
        if com_story:
            try:
                sid = publicar_story(pub, cfg, ep_id)
                fila.gravar_publicado(f"{ep_id}-story", sid, dry=False)
                rel["story_id"] = sid
            except Exception as e:  # noqa: BLE001
                rel["story_erro"] = str(e)[:300]
                print(f"::warning::Story de {ep_id} não saiu: {str(e)[:200]}")
    else:
        rel["instagram"] = "desligado (PUBLICAR_ATIVO=false)"

    zap = whatsapp.enviar(whatsapp.mensagem_episodio(ep, video))
    rel["whatsapp"] = zap

    if media_id or zap:
        fila.gravar_publicado(ep_id, media_id, dry=False, instagram=bool(media_id), whatsapp=zap)
    rel["ok"] = True
    print(json.dumps(rel, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
