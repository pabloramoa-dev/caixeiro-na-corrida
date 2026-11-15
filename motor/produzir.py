#!/usr/bin/env python3
"""produzir.py — do roteiro do Caixeiro ao MP4 pronto pra publicar.

  python motor/produzir.py episodios/cx025.json                         # tudo
  python motor/produzir.py episodios/cx025.json --publicar-em saida_reels

Etapas (pula o que já existe em saida/<id>/):
  voz   -> Microsoft pt-BR-AntonioNeural (edge-tts); se cair, Kokoro pm_alex
  lip   -> Rhubarb (boca por fonema); sem Rhubarb, lip sync por volume
  video -> Caixeiro no carro (Manim) + composição HyperFrames v4 + trilha/SFX
  final -> compressão pra caber no GitHub (< 60 MB), capa, Story, hash
"""
import argparse, json, os, shutil, subprocess, sys

MOTOR = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(MOTOR)
VOZ = os.environ.get("CAIXEIRO_VOZ", "pt-BR-AntonioNeural")
RATE = os.environ.get("CAIXEIRO_RATE", "+0%")
GAP = 0.25
LIMITE_MB = 60


def sh(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def duracao(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).strip())


def comprimir(mp4):
    tmp = mp4 + ".tmp.mp4"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c:v", "libx264", "-preset", "fast",
        "-b:v", "5400k", "-minrate", "5400k", "-maxrate", "5400k", "-bufsize", "5400k",
        "-x264-params", "nal-hrd=cbr:force-cfr=1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", tmp])
    taxa = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=bit_rate",
                                          "-of","csv=p=0",tmp]))
    if not 5_000_000 <= taxa <= 6_000_000:
        raise ValueError(f"Bitrate final fora da faixa: {taxa:.0f} bps")
    os.replace(tmp, mp4)
    return os.path.getsize(mp4) / 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episodio")
    ap.add_argument("--publicar-em", default=None)
    a = ap.parse_args()

    sys.path.insert(0, MOTOR)
    os.environ.setdefault("NINA_MAX_DUR", "240")
    os.environ.setdefault("NINA_FOTOS", "1")
    os.environ["MARCAO_VOZ"] = "pm_alex:0.62+pm_santa:0.38"
    from cta import garantir_cta
    from render_version import versao
    from ganchos_caixeiro import aplicar_ganchos
    from formatos import CURTOS, preparar_curto
    from compilar_roteiros import atuar
    ep = json.load(open(a.episodio, encoding="utf-8"))
    if ep.get("formato") == "corrida_1min":
        # Gancho/punchline escritos especificamente para o humor; sem cortes dos longos.
        pass
    else:
        ep = preparar_curto(ep) if ep["id"] in CURTOS else aplicar_ganchos(ep)
    ep = garantir_cta(ep)
    atuar(ep["batidas"])
    # Gancho de antecipação + micro-reenganche antes da voz e das ilustrações.
    # O arquivo-fonte e os registros de publicação permanecem intactos.
    ep["avulso"] = True
    ep["_render_version"] = versao()

    pasta = os.path.join(RAIZ, "saida", ep["id"])
    ep_path = os.path.join(pasta, "ep.json")
    novo = json.dumps(ep, ensure_ascii=False, indent=1)
    if os.path.exists(ep_path) and open(ep_path, encoding="utf-8").read() != novo:
        shutil.rmtree(pasta)
    os.makedirs(pasta, exist_ok=True)
    open(ep_path, "w", encoding="utf-8").write(novo)
    P = lambda n: os.path.join(pasta, n)

    if not os.path.exists(P("voz.wav")):
        open(P("roteiro.txt"), "w", encoding="utf-8").write("\n".join(b["fala"] for b in ep["batidas"]) + "\n")
        try:
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_kokoro.py"), P("roteiro.txt"),
                "--voz", os.environ["MARCAO_VOZ"], "--speed", "1.0", "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        except subprocess.CalledProcessError:
            os.environ["MARCAO_VOZ"] = VOZ
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_thalita.py"), P("roteiro.txt"),
                "--voice", VOZ, f"--rate={RATE}", "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        if "reenganche_indice" in ep:
            from ritmo import sincronizar
            sincronizar(P("bruta.wav"), P("segs.json"), ep["reenganche_indice"], ep.get("formato") == "curto")
        from audio_fx import masterizar_voz
        print("master da voz:", masterizar_voz(P("bruta.wav"), P("voz.wav")), flush=True)

    if not os.path.exists(P("lip.json")):
        lip = "lipsync_rhubarb.py" if os.environ.get("NINA_LIP", "rhubarb") == "rhubarb" else "lipsync_amplitude.py"
        sh([sys.executable, os.path.join(MOTOR, lip), P("voz.wav"), P("lip.json"), "30"])

    final = P(ep["id"] + ".mp4")
    if not os.path.exists(final):
        from hyperframes_marcao import renderizar
        renderizar(ep, pasta, RAIZ)
    print(f"tamanho final: {comprimir(final):.1f} MB", flush=True)

    if not os.path.exists(P("capa.jpg")):
        from capa_caixeiro import criar
        criar(ep, pasta)
    # O encoder do HyperFrames arredonda a duração. Causos de ~45s podem
    # resultar em 44,9s válidos; não derrube um render de dezenas de minutos.
    if ep.get("formato") in ("curto", "corrida_1min") and not 40 <= duracao(final) <= 75:
        raise ValueError("Reel de um minuto fora do limite técnico de 40–75 segundos")

    open(P("legenda.txt"), "w", encoding="utf-8").write(ep["legenda_post"] + "\n")
    open(P("legenda_tiktok.txt"), "w", encoding="utf-8").write(ep.get("legenda_tiktok", "") + "\n")

    if a.publicar_em:
        dest = os.path.abspath(a.publicar_em)
        os.makedirs(dest, exist_ok=True)
        shutil.copy(final, os.path.join(dest, ep["id"] + ".mp4"))
        shutil.copy(P("capa.jpg"), os.path.join(dest, ep["id"] + "-capa.jpg"))
        if os.path.exists(P("render.json")):
            shutil.copy(P("render.json"), os.path.join(dest, ep["id"] + "-render.json"))
        from story import fazer_story
        fazer_story(final, os.path.join(dest, ep["id"] + "-story.mp4"))
        sys.path.insert(0, RAIZ)
        from src.fila import assinatura
        open(os.path.join(dest, ep["id"] + ".hash"), "w").write(assinatura(ep["id"]) + "\n")

    print("OK", ep["id"], "->", pasta, flush=True)


if __name__ == "__main__":
    main()
