"""Publica o episódio do horário no Instagram e manda o MP4 no Telegram.

    python -m src.publicar --horario diario     # 18h: Reel (rotina diária atual)
    python -m src.publicar --horario manha      # 08h: Reel  (agenda antiga, só manual)
    python -m src.publicar --horario almoco     # 12h: Reel  (agenda antiga, só manual)
    python -m src.publicar --horario noite      # 20h: Reel + Story (agenda antiga, só manual)

- Instagram: só publica com PUBLICAR_ATIVO=true e DRY_RUN=false.
- Telegram: manda o MP4 + a descrição pro TikTok (mesmo bot da Nina).
- WhatsApp: continua opcional (só se os secrets do CallMeBot existirem).
- O episódio conta como "saiu" quando foi pro Instagram OU, com o Instagram
  desligado, quando o WhatsApp foi entregue (assim a fila anda do mesmo jeito
  para quem posta só no TikTok).
"""
from __future__ import annotations

import argparse
import json
import sys

from src import config, fila, telegram, whatsapp
from src.instagram import Publicador


def publicar_story(pub: Publicador, cfg, ep_id: str) -> str:
    registro = fila.release(ep_id)
    if registro:
        url = registro['urls'][f'{ep_id}-story.mp4']
    else:
        url = f"{cfg.raw_base_url}/reels/{ep_id}-story.mp4" if (config.REELS / f"{ep_id}-story.mp4").exists() else f"{cfg.raw_base_url}/reels/{ep_id}.mp4"
    container = pub.criar_container_story(url)
    pub.aguardar_pronto(container)
    return pub.publicar(container)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horario", choices=list(config.HORARIOS), required=True)
    a = ap.parse_args()
    com_story = a.horario in config.COM_STORY

    dry = config._flag("DRY_RUN", "true")
    ig_ligado = config._flag("PUBLICAR_ATIVO", "false") and not dry
    hoje = fila.datetime.now(fila.BRT).date()
    if a.horario != "diario" and fila.no_teste(hoje):
        if a.horario == 'manha' or any(p.get('dia_teste') == str(hoje) and p.get('horario') == a.horario for p in fila.ler_publicados()):
            return 0
        ig_ligado = not dry
    cfg = config.carregar(exigir_credenciais=ig_ligado)
    ep_id = fila.proximo(a.horario)
    if ep_id is None:
        print(json.dumps({"ok": True, "publicado": None,
                          "motivo": f"nada pronto para o horário {config.HORARIOS[a.horario]}"},
                         ensure_ascii=False))
        if (a.horario == "diario" or fila.no_teste(hoje)) and not dry:
            raise RuntimeError("Fila sem mídia pronta para o formato deste horário")
        print("::warning::Fila vazia: nenhum episódio pronto.")
        return 0

    ep = fila.carregar_ep(ep_id)
    video = f"{cfg.raw_base_url}/reels/{ep_id}.mp4"
    capa = f"{cfg.raw_base_url}/reels/{ep_id}-capa.jpg"
    registro = fila.release(ep_id)
    if registro:
        video = registro['urls'][ep_id+'.mp4']
        capa = registro['urls'][ep_id+'-capa.jpg']
    if "ficção" not in ep["legenda_post"].lower():
        ep["legenda_post"] += "\n\nHistória de ficção."
    rel = {"horario": config.HORARIOS[a.horario], "id": ep_id, "titulo": ep["titulo"],
           "video": video, "capa": capa, "story": com_story,
           "duracao": round(registro["duracao"] if registro else fila.duracao(config.REELS / f"{ep_id}.mp4"), 1)}

    if dry:
        rel.update(ok=True, ensaio=True, motivo="DRY_RUN ligado",
                   telegram_previa=telegram.mensagem_episodio(ep, False))
        print(json.dumps(rel, ensure_ascii=False, indent=1))
        return 0

    media_id = None
    ig_erro = None
    if ig_ligado:
        pub = Publicador(cfg)
        try:
            container = pub.criar_container(video, ep["legenda_post"], capa)
            pub.aguardar_pronto(container)
            try:
                media_id = pub.publicar(container)
            except Exception:
                media_id = pub.reconciliar(container, ep["legenda_post"])
                if not media_id:
                    raise
                rel["reconciliado_apos_erro"] = True
        except Exception as e:  # noqa: BLE001 — o Telegram ainda recebe o vídeo; o erro sobe no fim
            ig_erro = e
            rel["instagram_erro"] = config.esconder(str(e))[:300]
        rel["media_id"] = media_id
        if com_story and media_id:
            try:
                sid = publicar_story(pub, cfg, ep_id)
                fila.gravar_publicado(f"{ep_id}-story", sid, dry=False)
                rel["story_id"] = sid
            except Exception as e:  # noqa: BLE001
                rel["story_erro"] = str(e)[:300]
                print(f"::warning::Story de {ep_id} não saiu: {str(e)[:200]}")
    else:
        rel["instagram"] = "desligado (PUBLICAR_ATIVO=false)"

    local = config.REELS / f"{ep_id}.mp4"
    try:
        tg = telegram.enviar_video(str(local) if local.exists() else video, ep_id,
                                   telegram.mensagem_episodio(ep, bool(media_id)))
    except Exception as e:  # noqa: BLE001 — Telegram não pode derrubar o registro do post
        tg = False
        print(f"::warning::Telegram falhou: {config.esconder(str(e))[:200]}")
    rel["telegram"] = tg
    zap = whatsapp.enviar(whatsapp.mensagem_episodio(ep, video)) if whatsapp.configurado() else False
    rel["whatsapp"] = zap

    # Só sai da fila se foi pro Instagram (ou, com o Instagram desligado, se o aviso chegou).
    if media_id or (not ig_ligado and (tg or zap)):
        fila.gravar_publicado(ep_id, media_id, dry=False, instagram=bool(media_id), telegram=tg, whatsapp=zap, horario=a.horario, dia_teste=str(hoje) if a.horario != "diario" and fila.no_teste(hoje) else None, formato="curto" if ep_id in fila.CURTOS else "longo", duracao=rel["duracao"])
    rel["ok"] = ig_erro is None
    print(json.dumps(rel, ensure_ascii=False, indent=1))
    if ig_erro is not None:
        raise RuntimeError(f"Instagram não publicou {ep_id}: {config.esconder(str(ig_erro))[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
