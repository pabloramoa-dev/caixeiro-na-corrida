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
    """Mantém o MP4 abaixo de LIMITE_MB (o GitHub recusa arquivo > 100 MB)."""
    mb = os.path.getsize(mp4) / 1e6
    if mb <= LIMITE_MB:
        return mb
    d = duracao(mp4)
    kbps = int((LIMITE_MB * 8000 * 0.92) / d) - 160
    tmp = mp4 + ".tmp.mp4"
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c:v", "libx264", "-preset", "medium",
        "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps*1.3)}k", "-bufsize", f"{kbps*2}k",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", tmp])
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
    os.environ["MARCAO_VOZ"] = VOZ
    from cta import garantir_cta
    from render_version import versao
    from ganchos_caixeiro import aplicar_ganchos
    ep = aplicar_ganchos(garantir_cta(json.load(open(a.episodio, encoding="utf-8"))))
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
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_thalita.py"), P("roteiro.txt"),
                "--voice", VOZ, f"--rate={RATE}", "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
        except subprocess.CalledProcessError:
            print("::warning::Voz Antonio indisponível; usando Kokoro pm_alex.", flush=True)
            os.environ["MARCAO_VOZ"] = "kokoro pm_alex"
            sh([sys.executable, os.path.join(MOTOR, "gerar_voz_kokoro.py"), P("roteiro.txt"),
                "--voz", "pm_alex", "--speed", "1.0", "--gap", str(GAP),
                "--out", P("bruta.wav"), "--seg-json", P("segs.json")])
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
        # capa = quadro do título (primeiros segundos), já com a marca do canal
        sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.2", "-i", final, "-frames:v", "1",
            "-q:v", "3", P("capa.jpg")])

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
