"""marcao_lib — Caixeiro, 44 anos, motorista de aplicativo (ex-metalúrgico).
Conta, do banco do motorista, as histórias que acontecem no banco de trás (ficção).

Mesma API da nina_lib (marcao(), rosto(), posicionar(), rosto_alinhado(),
animar(), trocar_expressao(), boca_fonema()), para reaproveitar o pipeline
HyperFrames + Rhubarb da Nina sem mexer nela.

Cenário: carro(cenario) — interior do sedan visto do banco do carona,
"noite" (padrão: luzes da cidade, chuva fina) ou "tarde".
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manim import *
import numpy as np
import dvh_vox_papel as V

PT = "#111111"
PELE, PELE_SOMBRA = "#b97c55", "#9a6243"
BARBA, BARBA_CL = "#4a4442", "#9b9692"
LABIO, BOCA_IN = "#7e3f30", "#3a120c"
BONE, BONE_ESC, BONE_ABA = "#22325c", "#172344", "#1a274a"
POLO, POLO_ESC = "#8b9098", "#6c717a"
IRIS = "#5a3a22"
OURO = "#e8b23a"
EXPRESSOES = ("neutra", "desconfiada", "chocada", "ironica", "triste", "brava", "rindo")

ESCALA = 1.42
CABECA = np.array([0.1, 0.18, 0])   # centro da cabeça na tela (abaixo do cartão HyperFrames)


def _curva(pts, **kw):
    m = VMobject(**kw)
    m.set_points_smoothly([np.array(p, dtype=float) for p in pts])
    return m


# =============================================================================
#  ROSTO
# =============================================================================
_ABERT = {"neutra": 0.9, "desconfiada": 0.5, "chocada": 1.2, "ironica": 0.65,
          "triste": 0.75, "brava": 0.55, "rindo": 0.45}
_SOB = {"neutra": (0.04, 0.29), "desconfiada": (-0.10, 0.20), "chocada": (0.07, 0.36),
        "ironica": None, "triste": (0.12, 0.25), "brava": (-0.17, 0.19), "rindo": (0.06, 0.32)}
BOCA_Y = 0.56


def boca_expr(expr, bc):
    if expr == "chocada":
        return Ellipse(width=0.26, height=0.30, fill_color=BOCA_IN, fill_opacity=1,
                       stroke_color=LABIO, stroke_width=8).move_to(bc)
    if expr == "ironica":   # sorriso de canto
        return _curva([bc + LEFT * 0.20 + UP * 0.02, bc + DOWN * 0.02, bc + RIGHT * 0.20 + UP * 0.11],
                      stroke_color=LABIO, stroke_width=10)
    if expr == "triste":
        return Arc(radius=0.22, start_angle=PI * 0.25, angle=PI * 0.5,
                   arc_center=bc + DOWN * 0.18).set_stroke(LABIO, 10)
    if expr in ("desconfiada", "brava"):
        return Line(bc + LEFT * 0.17, bc + RIGHT * 0.15 + DOWN * 0.02, stroke_color=LABIO, stroke_width=10)
    if expr == "rindo":     # gargalhada: boca aberta em D com dentes
        b = VGroup(Polygon(*[bc + UP * 0.07 + np.array([0.27 * np.cos(x), 0.25 * np.sin(x), 0])
                             for x in np.linspace(PI, 2 * PI, 18)], fill_color=BOCA_IN, fill_opacity=1,
                           stroke_color=LABIO, stroke_width=8))
        b.add(Rectangle(width=0.40, height=0.06, fill_color=DENTE, fill_opacity=1, stroke_width=0)
              .move_to(bc + UP * 0.02))
        b.add(Ellipse(width=0.22, height=0.08, fill_color=LINGUA, fill_opacity=1, stroke_width=0)
              .move_to(bc + DOWN * 0.13))
        return b
    # neutra = sorriso largo de quem leva a vida no bom humor
    return VGroup(Arc(radius=0.30, start_angle=PI * 1.2, angle=PI * 0.6, arc_center=bc + UP * 0.2).set_stroke(LABIO, 10),
                  *[Arc(radius=0.07, start_angle=PI * (0.9 if s < 0 else -0.1), angle=PI * 0.5,
                        arc_center=bc + np.array([s * 0.30, 0.0, 0])).set_stroke(LABIO, 6) for s in (-1, 1)])


DENTE, LINGUA = "#fffaf0", "#d9707a"


def _lab(w, h, sw=7):
    return Ellipse(width=w, height=h, fill_color=BOCA_IN, fill_opacity=1, stroke_color=LABIO, stroke_width=sw)


def _dentes(b, w, h, baixo=False):
    d = Rectangle(width=w, height=h, fill_color=DENTE, fill_opacity=1, stroke_width=0)
    return d.move_to(b.get_bottom() + UP * (h / 2 + 0.012)) if baixo else d.move_to(b.get_top() + DOWN * (h / 2 + 0.012))


def _lingua(b, w, h, cima=False):
    l = Ellipse(width=w, height=h, fill_color=LINGUA, fill_opacity=1, stroke_width=0)
    return l.move_to(b.get_top() + DOWN * (h / 2 + 0.02)) if cima else l.move_to(b.get_bottom() + UP * (h / 2 + 0.008))


def boca_fonema(letra, largura=0.32):
    w = largura
    if letra == "A":
        return Ellipse(width=w * 0.85, height=0.055, fill_color=LABIO, fill_opacity=1, stroke_color=LABIO, stroke_width=7)
    if letra == "B":
        b = _lab(w * 1.05, 0.12)
        return VGroup(b, _dentes(b, w * 0.78, 0.045), _dentes(b, w * 0.7, 0.03, baixo=True))
    if letra == "C":
        b = _lab(w, 0.18)
        return VGroup(b, _dentes(b, w * 0.66, 0.045), _lingua(b, w * 0.5, 0.06))
    if letra == "D":
        b = _lab(w * 1.08, 0.30)
        return VGroup(b, _dentes(b, w * 0.7, 0.05), _lingua(b, w * 0.6, 0.10))
    if letra == "E":
        return _lab(w * 0.72, 0.22)
    if letra == "F":
        return _lab(w * 0.42, 0.15, sw=9)
    if letra == "G":
        b = _lab(w * 0.95, 0.085)
        return VGroup(b, _dentes(b, w * 0.6, 0.05))
    if letra == "H":
        b = _lab(w, 0.20)
        return VGroup(b, _lingua(b, w * 0.55, 0.09, cima=True))
    return boca_fala("meia", largura)


def boca_fala(estado, largura=0.32):
    if estado in tuple("ABCDEFGH"):
        return boca_fonema(estado, largura)
    if estado == "meia":
        return Ellipse(width=largura, height=0.13, fill_color=BOCA_IN, fill_opacity=1, stroke_color=LABIO, stroke_width=7)
    return Ellipse(width=largura * 1.05, height=0.27, fill_color=BOCA_IN, fill_opacity=1, stroke_color=LABIO, stroke_width=7)


def rosto(expr, c):
    """VGroup(olhos, palpebras, sobrancelhas, boca)."""
    a = _ABERT[expr]

    def olho(l):
        base = c + l * 0.34 + UP * 0.0
        br = Ellipse(width=0.38, height=0.30 * a, fill_color=WHITE, fill_opacity=1,
                     stroke_color=PT, stroke_width=6).move_to(base)
        r = min(0.09 if expr == "chocada" else 0.115, 0.30 * a / 2)
        foco = base + (RIGHT * 0.06 if expr == "desconfiada" else ORIGIN) + (DOWN * 0.03 if expr == "triste" else ORIGIN)
        iris = Circle(radius=r, fill_color=IRIS, fill_opacity=1, stroke_color=PT, stroke_width=4).move_to(foco)
        pup = Dot(foco, radius=min(0.05, r * 0.5), color=PT)
        luz = Dot(foco + UP * 0.04 + RIGHT * 0.035, radius=0.026, color=WHITE)
        # pálpebra superior pesada (cansaço de quem roda a noite toda)
        lid = Arc(radius=0.24, start_angle=PI * 0.18, angle=PI * 0.64,
                  arc_center=base + DOWN * 0.13 * a).set_stroke(PT, 7)
        # pés de galinha
        pe = VGroup(*[Line(base + l * 0.24 + UP * dy, base + l * 0.34 + UP * (dy * 1.6), stroke_color=PELE_SOMBRA,
                           stroke_width=4) for dy in (-0.05, 0.02)])
        return VGroup(br, iris, pup, luz, lid, pe)

    olhos = VGroup(olho(LEFT), olho(RIGHT))
    # olheiras
    olhos.add(*[Arc(radius=0.17, start_angle=PI * 1.2, angle=PI * 0.6, arc_center=c + l * 0.34 + UP * 0.05)
                .set_stroke(PELE_SOMBRA, 4) for l in (LEFT, RIGHT)])

    palp = VGroup()
    for l in (LEFT, RIGHT):
        base = c + l * 0.34
        palp.add(VGroup(
            Ellipse(width=0.46, height=0.44, fill_color=PELE, fill_opacity=1, stroke_width=0).move_to(base),
            Arc(radius=0.2, start_angle=PI * 1.15, angle=PI * 0.7, arc_center=base + UP * 0.14).set_stroke(PT, 6)))
    for pl in palp:
        pl[0].set_fill(opacity=0); pl[1].set_stroke(opacity=0)

    def sob(l):
        s = -1 if l is LEFT else 1
        cfg = _SOB[expr]
        if cfg is None:
            cfg = (0.0, 0.33) if l is RIGHT else (-0.07, 0.21)
        incl, h = cfg
        ext = c + np.array([s * 0.56, h - 0.02, 0])
        inn = c + np.array([s * 0.14, h + incl, 0])
        return _curva([ext, (ext + inn) / 2 + UP * 0.05, inn], stroke_color="#2e2a29", stroke_width=15)

    sobs = VGroup(sob(LEFT), sob(RIGHT))
    boca = boca_expr(expr, c + DOWN * BOCA_Y)
    return VGroup(olhos, palp, sobs, boca)


# =============================================================================
#  CAIXEIRO
# =============================================================================
def marcao(expr="neutra", cenario="noite"):
    cab = Circle(radius=0.9, stroke_color=PT, stroke_width=15, fill_color=PELE, fill_opacity=1).shift(UP * 1.4)
    c = cab.get_center()

    orelhas = VGroup(*[Circle(radius=0.18, fill_color=PELE, fill_opacity=1, stroke_color=PT, stroke_width=9)
                       .move_to(c + np.array([s * 0.9, -0.05, 0])) for s in (-1, 1)])
    # cabelo curto grisalho nas laterais (costeletas)
    cost = VGroup(*[Polygon(c + np.array([s * 0.88, 0.42, 0]), c + np.array([s * 0.64, 0.40, 0]),
                            c + np.array([s * 0.70, 0.02, 0]), c + np.array([s * 0.86, -0.02, 0]),
                            fill_color="#5e5856", fill_opacity=1, stroke_width=0) for s in (-1, 1)])
    cost.add(*[Line(c + np.array([s * 0.8, 0.30, 0]), c + np.array([s * 0.78, 0.08, 0]),
                    stroke_color="#b8b2ad", stroke_width=4) for s in (-1, 1)])

    # barba rala grisalha: sombra na mandíbula + pontinhos
    jaw = []
    for ang in np.linspace(PI * 1.08, PI * 1.92, 24):
        jaw.append(c + np.array([np.cos(ang) * 0.86, np.sin(ang) * 0.86, 0]))
    inner = [c + np.array([0.52, -0.28, 0]), c + np.array([0.30, -0.36, 0]), c + np.array([0.0, -0.40, 0]),
             c + np.array([-0.30, -0.36, 0]), c + np.array([-0.52, -0.28, 0])]
    barba = Polygon(*jaw, *inner, fill_color=BARBA, fill_opacity=0.5, stroke_width=0)
    rng = np.random.default_rng(11)
    pts = []
    while len(pts) < 38:
        x, y = rng.uniform(-0.8, 0.8), rng.uniform(-0.86, -0.3)
        if x * x + y * y < 0.82 ** 2 and not (abs(x) < 0.26 and y > -0.72):
            pts.append((x, y))
    pelos = VGroup(*[Dot(c + np.array([x, y, 0]), radius=0.014,
                         color=BARBA_CL if k % 2 else "#6e6866") for k, (x, y) in enumerate(pts)])
    bigode = VGroup(
        _curva([c + np.array([-0.30, -0.44, 0]), c + np.array([-0.12, -0.36, 0]), c + np.array([0.0, -0.39, 0])],
               stroke_color=BARBA, stroke_width=16),
        _curva([c + np.array([0.0, -0.39, 0]), c + np.array([0.12, -0.36, 0]), c + np.array([0.30, -0.44, 0])],
               stroke_color=BARBA, stroke_width=16),
        _curva([c + np.array([-0.2, -0.38, 0]), c + np.array([0.2, -0.38, 0])], stroke_color=BARBA_CL, stroke_width=3))

    nariz = _curva([c + UP * 0.02 + LEFT * 0.03, c + DOWN * 0.17 + LEFT * 0.12,
                    c + DOWN * 0.26 + RIGHT * 0.0, c + DOWN * 0.22 + RIGHT * 0.13],
                   stroke_color="#7c4a30", stroke_width=8)

    # boné azul-marinho: copa + aba + botão + escudinho
    copa_pts = [c + np.array([np.cos(a) * 0.98, np.sin(a) * 0.98 + 0.06, 0]) for a in np.linspace(0.05, PI - 0.05, 20)]
    copa = Polygon(*copa_pts, c + np.array([-0.97, 0.42, 0]), c + np.array([0.97, 0.42, 0]),
                   fill_color=BONE, fill_opacity=1, stroke_color=PT, stroke_width=10)
    costuras = VGroup(*[_curva([c + np.array([x0, 1.0, 0]), c + np.array([x0 * 1.4, 0.75, 0]), c + np.array([x0 * 1.9, 0.44, 0])],
                               stroke_color=BONE_ESC, stroke_width=4) for x0 in (-0.22, 0.22)])
    botao = Circle(radius=0.07, fill_color=BONE_ESC, fill_opacity=1, stroke_color=PT, stroke_width=4).move_to(c + UP * 1.04)
    aba = _curva([c + np.array([-1.08, 0.46, 0]), c + np.array([0.0, 0.58, 0]), c + np.array([1.08, 0.46, 0]),
                  c + np.array([0.9, 0.30, 0]), c + np.array([0.0, 0.33, 0]), c + np.array([-0.9, 0.30, 0]),
                  c + np.array([-1.08, 0.46, 0])],
                 fill_color=BONE_ABA, fill_opacity=1, stroke_color=PT, stroke_width=9)
    # escudinho do boné: estrela dourada (símbolo neutro, sem marca)
    placa = Circle(radius=0.15, fill_color="#0f1830", fill_opacity=1, stroke_color=OURO, stroke_width=4).move_to(c + UP * 0.72)
    estrela = Star(n=5, outer_radius=0.11, inner_radius=0.05, fill_color=OURO, fill_opacity=1,
                   stroke_width=0).move_to(placa)
    escudo = VGroup(placa, estrela)

    # corpo: pescoço, polo cinza com gola e botões
    pesc = Rectangle(width=0.5, height=0.32, fill_color=PELE_SOMBRA, fill_opacity=1, stroke_color=PT,
                     stroke_width=10).move_to(cab.get_bottom() + DOWN * 0.08)
    t = cab.get_bottom() + DOWN * 0.22
    polo = VMobject(fill_color=POLO, fill_opacity=1, stroke_color=PT, stroke_width=11)
    polo.set_points_as_corners([t + LEFT * 0.30, t + LEFT * 0.95 + DOWN * 0.18, t + LEFT * 1.18 + DOWN * 0.6,
                                t + LEFT * 1.2 + DOWN * 2.6, t + RIGHT * 1.2 + DOWN * 2.6,
                                t + RIGHT * 1.18 + DOWN * 0.6, t + RIGHT * 0.95 + DOWN * 0.18, t + RIGHT * 0.30,
                                t + LEFT * 0.30])
    gola = VGroup(*[Polygon(t + np.array([s * 0.05, 0.06, 0]), t + np.array([s * 0.42, 0.04, 0]),
                            t + np.array([s * 0.22, -0.32, 0]), fill_color="#a4a9b0", fill_opacity=1,
                            stroke_color=PT, stroke_width=7) for s in (-1, 1)])
    vista = VGroup(Line(t + DOWN * 0.05, t + DOWN * 0.7, stroke_color=POLO_ESC, stroke_width=6),
                   *[Dot(t + DOWN * y, radius=0.045, color="#e8e6e1") for y in (0.32, 0.55)])

    # volante na frente do peito, com as DUAS mãos (10h e 2h): ele está dirigindo
    VC = t + np.array([0.0, -1.5, 0])
    R = 0.95
    mao_e = VC + R * np.array([np.cos(PI * 0.80), np.sin(PI * 0.80), 0])
    mao_d = VC + R * np.array([np.cos(PI * 0.20), np.sin(PI * 0.20), 0])
    omb_e = t + LEFT * 1.0 + DOWN * 0.35
    omb_d = t + RIGHT * 1.0 + DOWN * 0.35

    def _membro(a, b, cor, larg):
        return VGroup(Line(a, b, stroke_color=PT, stroke_width=larg + 14).set_cap_style(CapStyleType.ROUND),
                      Line(a, b, stroke_color=cor, stroke_width=larg).set_cap_style(CapStyleType.ROUND))
    bracos = VGroup()
    for omb, mao, s in ((omb_e, mao_e, -1), (omb_d, mao_d, 1)):
        cot = omb + np.array([s * 0.28, -0.95, 0])
        bracos.add(_membro(omb, omb + (cot - omb) * 0.55, POLO, 46),
                   _membro(omb + (cot - omb) * 0.5, cot, PELE, 30),
                   _membro(cot, mao, PELE, 30))
    relogio = Circle(radius=0.11, fill_color="#d9d9d9", fill_opacity=1, stroke_color=PT, stroke_width=5)
    cot_e = omb_e + np.array([-0.28, -0.95, 0])
    relogio.move_to(cot_e + (mao_e - cot_e) * 0.65)

    aro_preto = Circle(radius=R, stroke_color=PT, stroke_width=44).move_to(VC)
    aro = Circle(radius=R, stroke_color="#2b2b33", stroke_width=28).move_to(VC)
    aro_brilho = Arc(radius=R, start_angle=PI * 0.35, angle=PI * 0.3, arc_center=VC).set_stroke("#5a5a68", 8)
    raios = VGroup(*[Line(VC, VC + np.array([np.cos(a), np.sin(a), 0]) * R, stroke_color=PT, stroke_width=26)
                     for a in (PI * 0.05, PI * 0.95, PI * 1.5)],
                   *[Line(VC, VC + np.array([np.cos(a), np.sin(a), 0]) * R, stroke_color="#26262e", stroke_width=14)
                     for a in (PI * 0.05, PI * 0.95, PI * 1.5)])
    cubo = VGroup(Circle(radius=0.32, fill_color="#26262e", fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(VC),
                  Star(n=5, outer_radius=0.12, inner_radius=0.055, fill_color="#8a8a96", fill_opacity=1,
                       stroke_width=0).move_to(VC))
    roda = VGroup(raios, aro_preto, aro, aro_brilho, cubo)

    def _mao(pos, s):
        m = VGroup(Circle(radius=0.22, fill_color=PELE, fill_opacity=1, stroke_color=PT, stroke_width=8).move_to(pos))
        for k in range(3):
            d = pos + np.array([-s * 0.04 + (k - 1) * 0.09, 0.14, 0])
            m.add(Line(d, d + DOWN * 0.22, stroke_color=PT, stroke_width=4))
        return m
    maos = VGroup(_mao(mao_e, -1), _mao(mao_d, 1))
    volante = VGroup(roda, maos)
    volante.stretch(0.9, 1, about_point=VC)

    face = rosto(expr, c)
    grupo = VGroup(pesc, polo, gola, vista, bracos, relogio,
                   orelhas, cab, barba, pelos, cost, nariz, bigode, copa, costuras, botao, escudo, aba, face)
    return dict(grupo=grupo, cab=cab, rosto=face, volante=volante, roda=roda, expr=expr,
                tudo=VGroup(grupo, volante))


def posicionar(p, escala=ESCALA, cabeca=CABECA):
    p["tudo"].scale(escala)
    p["tudo"].shift(cabeca - p["cab"].get_center())
    p["escala"] = escala
    return p


def rosto_alinhado(p, expr):
    k = p.get("escala", 1.0)
    return rosto(expr, ORIGIN).scale(k, about_point=ORIGIN).shift(p["cab"].get_center())


def animar(scene, p, cues, semente=7):
    """Piscada + lip sync por fonema (Rhubarb) — mesma lógica da Nina."""
    k = p.get("escala", 1.0)
    rng = np.random.default_rng(semente)
    piscadas, t = [], 1.0
    while t < 600:
        piscadas.append(t); t += rng.uniform(2.8, 5.0)
    st = {"v": None}
    fala = VMobject()
    scene.add(fala)

    def upd(mo, dt):
        tt = scene.renderer.time
        fechado = any(0 <= tt - b < 0.13 for b in piscadas[:int(tt / 2.7) + 3])
        for pl in p["rosto"][1]:
            pl[0].set_fill(opacity=1 if fechado else 0)
            pl[1].set_stroke(opacity=1 if fechado else 0)
        v = "fechada"
        for cu in cues:
            if cu["start"] <= tt < cu["end"]:
                v = cu["estado"]; break
            if cu["start"] > tt:
                break
        boca_parada = p["rosto"][3]
        centro = p["cab"].get_center() + DOWN * BOCA_Y * k
        if v == "fechada":
            boca_parada.set_stroke(opacity=1)
            boca_parada.set_fill(opacity=1 if p["expr"] == "chocada" else 0)
            if st["v"] != v:
                mo.become(VMobject())
        else:
            boca_parada.set_stroke(opacity=0).set_fill(opacity=0)
            if st["v"] != v:
                mo.become(boca_fala(v).scale(k))
            mo.move_to(centro)
        st["v"] = v
    fala.add_updater(upd)
    return st


def trocar_expressao(scene, p, expr, dur=0.18):
    if expr == p["expr"] or expr not in EXPRESSOES:
        return 0.0
    scene.play(Transform(p["rosto"], rosto_alinhado(p, expr)), run_time=dur)
    p["expr"] = expr
    return dur


# =============================================================================
#  CENÁRIO — interior do carro, visto do banco do carona
# =============================================================================
def _faixas(g, x0, x1, y_top, cores):
    y = y_top
    for k, (cor, alt) in enumerate(cores):
        g.add(Polygon(*V._contorno_rasgado(x1 - x0 + 0.4, alt + 0.1, dente=0.05, semente=31 + k),
                      fill_color=cor, fill_opacity=1, stroke_width=0).move_to([(x0 + x1) / 2, y - alt / 2, 0]))
        y -= alt
    return y


def _neon(txt, cor, largura):
    """Letreiro de neon: núcleo claro + camadas de brilho."""
    base = Text(txt, font="DejaVu Sans", weight=BOLD).scale_to_fit_width(largura)
    camadas = VGroup()
    for w, op in ((34, 0.10), (22, 0.18), (13, 0.32)):
        camadas.add(base.copy().set_fill(opacity=0).set_stroke(cor, w, op))
    tubo = base.copy().set_fill(opacity=0).set_stroke(cor, 6, 1)
    nucleo = base.copy().set_fill(opacity=0).set_stroke("#ffffff", 2.2, 0.95)
    return VGroup(camadas, tubo, nucleo)


def letreiro_neon():
    """UBER (rosa) e 99 (âmbar) acesos no canto da janela."""
    uber = _neon("UBER", "#ff4fd8", 1.25)
    noventa = _neon("99", "#ffb020", 0.75).next_to(uber, DOWN, buff=0.22)
    g = VGroup(uber, noventa)
    fundo = RoundedRectangle(width=g.width + 0.45, height=g.height + 0.45, corner_radius=0.12,
                             fill_color="#07070f", fill_opacity=0.55, stroke_color="#2a2a3a", stroke_width=4).move_to(g)
    return VGroup(fundo, g).move_to([2.95, -0.45, 0])


def carro(cenario="noite"):
    W, H = config.frame_width, config.frame_height
    noite = cenario not in ("tarde", "dia")
    dia = cenario == "dia"
    g = VGroup()
    # forro/interior escuro de fundo
    g.add(Rectangle(width=W + 1, height=H + 1, fill_color="#1d1c26" if noite else ("#55525f" if dia else "#4a3e44"),
                    fill_opacity=1, stroke_width=0))
    # janela lateral do motorista (atrás do Caixeiro)
    jx0, jx1, jy0, jy1 = -W / 2 - 0.2, W / 2 + 0.2, -2.6, 6.2
    ceu = ([("#0f1433", 2.2), ("#1a2150", 2.0), ("#2b2a63", 1.8), ("#4a2f66", 1.6), ("#6a3a5e", 1.4)] if noite else
           [("#4fb3ef", 2.2), ("#6cc3f2", 2.0), ("#8fd2f4", 1.8), ("#b3e0f5", 1.6), ("#d6eef6", 1.4)] if dia else
           [("#f6c86a", 2.2), ("#f0a15a", 2.0), ("#e07a5f", 1.8), ("#c96a6a", 1.6), ("#9a5a6a", 1.4)])
    _faixas(g, jx0, jx1, jy1, ceu)
    if dia:   # sol e nuvens de papel
        g.add(Circle(radius=0.75, fill_color="#ffd84d", fill_opacity=1, stroke_color="#f5a623", stroke_width=10)
              .move_to([-2.2, 1.0, 0]))
        for cx, cy, k in ((1.6, 1.25, 1.0), (-0.6, 0.55, 0.8), (3.0, 0.2, 0.7)):
            g.add(VGroup(*[Circle(radius=r * k, fill_color=WHITE, fill_opacity=0.95, stroke_width=0)
                           .move_to([cx + dx * k, cy + dy * k, 0])
                           for r, dx, dy in ((0.32, -0.35, 0), (0.42, 0, 0.12), (0.3, 0.38, 0))]))
    # prédios
    rng = np.random.default_rng(4)
    luzes = VGroup()
    x = jx0
    while x < jx1:
        w = rng.uniform(0.7, 1.4); h = rng.uniform(2.0, 5.2)
        base = -2.6
        cor = "#0b0d22" if noite else (rng.choice(["#f2c7a5", "#a8d5c9", "#f4e1a1", "#cdb8e0", "#f3a9a0"]) if dia else "#5a3a4e")
        g.add(Rectangle(width=w, height=h, fill_color=cor, fill_opacity=1, stroke_color=PT, stroke_width=3)
              .move_to([x + w / 2, base + h / 2, 0]))
        for yy in np.arange(base + 0.35, base + h - 0.2, 0.42):
            for xx in np.arange(x + 0.18, x + w - 0.12, 0.3):
                if rng.random() < (0.45 if noite else 0.55 if dia else 0.2):
                    g.add(Rectangle(width=0.13, height=0.18, stroke_width=0, fill_opacity=1,
                                    fill_color=rng.choice(["#ffd27a", "#ffe9b0", "#9fd3ff"]) if noite else ("#d8f0ff" if dia else "#f6dca0"))
                          .move_to([xx, yy, 0]))
        x += w + rng.uniform(0.02, 0.25)
    # bokeh (luzes de rua/faróis) — animadas pela cena (passam pela janela)
    for k in range(26):
        cor = rng.choice(["#ffb347", "#ff6b5a", "#fff2c4", "#ffd27a", "#8fd0ff"])
        r = rng.uniform(0.14, 0.42)
        if dia:
            cor = rng.choice(["#2f9e44", "#3fb34f", "#5cc46a"]); r = rng.uniform(0.35, 0.6)
        luzes.add(Circle(radius=r, fill_color=cor, fill_opacity=0.32 if noite else (0.95 if dia else 0.18),
                         stroke_color=PT if dia else None, stroke_width=4 if dia else 0)
                  .move_to([rng.uniform(-W / 2 - 1, W / 2 + 1), rng.uniform(-2.3, -1.4) if dia else rng.uniform(-2.3, 2.0), 0]))
    chuva = VGroup()
    if noite:
        for k in range(55):
            x0, y0 = rng.uniform(-W / 2, W / 2), rng.uniform(-2.4, 6.0)
            chuva.add(Line([x0, y0, 0], [x0 - 0.12, y0 - 0.38, 0], stroke_color="#cfe3ff", stroke_width=2.5,
                           stroke_opacity=0.35))
    # moldura da janela + coluna da porta
    moldura = VGroup(
        Rectangle(width=W + 2, height=1.4, fill_color="#2a2933", fill_opacity=1, stroke_width=0).move_to([0, -3.3, 0]),
        Line([-W / 2 - 0.5, -2.6, 0], [W / 2 + 0.5, -2.6, 0], stroke_color=PT, stroke_width=14),
        Polygon([W / 2 - 0.9, -2.6, 0], [W / 2 - 0.3, 6.2, 0], [W / 2 + 0.6, 6.2, 0], [W / 2 + 0.6, -2.6, 0],
                fill_color="#2a2933", fill_opacity=1, stroke_color=PT, stroke_width=10))
    # banco/encosto do motorista (atrás dele)
    encosto = VGroup(
        RoundedRectangle(width=3.6, height=4.2, corner_radius=0.9, fill_color="#33323d", fill_opacity=1,
                         stroke_color=PT, stroke_width=12).move_to([0.15, -2.6, 0]),
        RoundedRectangle(width=2.0, height=1.2, corner_radius=0.45, fill_color="#3b3a46", fill_opacity=1,
                         stroke_color=PT, stroke_width=10).move_to([0.15, 1.05, 0]),
        *[Line([x, -0.5, 0], [x, -4.6, 0], stroke_color="#26252e", stroke_width=6) for x in (-0.7, 0.15, 1.0)])
    # painel embaixo
    painel = Polygon([-W / 2 - 1, -4.3, 0], [W / 2 + 1, -4.0, 0], [W / 2 + 1, -H / 2 - 1, 0], [-W / 2 - 1, -H / 2 - 1, 0],
                     fill_color="#232229", fill_opacity=1, stroke_color=PT, stroke_width=12)
    # celular no suporte com o mapa aberto (lado direito)
    cel_c = np.array([2.85, -2.75, 0])
    tela = RoundedRectangle(width=1.05, height=1.85, corner_radius=0.12, fill_color="#e6efe2", fill_opacity=1,
                            stroke_color=PT, stroke_width=10).move_to(cel_c)
    ruas = VGroup(*[Line(cel_c + np.array([-0.45, y, 0]), cel_c + np.array([0.45, y + 0.15, 0]),
                         stroke_color="#ffffff", stroke_width=6) for y in (-0.5, 0.1, 0.55)],
                  Line(cel_c + np.array([-0.15, -0.85, 0]), cel_c + np.array([0.1, 0.85, 0]), stroke_color="#ffffff",
                       stroke_width=7))
    rota = _curva([cel_c + np.array([-0.3, -0.75, 0]), cel_c + np.array([-0.05, -0.1, 0]),
                   cel_c + np.array([0.2, 0.25, 0]), cel_c + np.array([0.3, 0.6, 0])],
                  stroke_color="#2f7cf6", stroke_width=9)
    pino = VGroup(Circle(radius=0.09, fill_color="#e2483c", fill_opacity=1, stroke_color=PT, stroke_width=4)
                  .move_to(cel_c + np.array([0.3, 0.66, 0])))
    suporte = VGroup(Rectangle(width=0.18, height=0.9, fill_color="#16161b", fill_opacity=1, stroke_width=0)
                     .move_to(cel_c + DOWN * 1.3),
                     Rectangle(width=1.2, height=0.14, fill_color="#16161b", fill_opacity=1, stroke_width=0)
                     .move_to(cel_c + DOWN * 0.95))
    celular = VGroup(suporte, tela, ruas, rota, pino)
    # terço pendurado no retrovisor (entra pelo alto, à esquerda)
    tx = -2.85
    contas = VGroup(*[Dot([tx + 0.28 * np.sin(k / 3.0), 1.75 - k * 0.15, 0], radius=0.055, color="#7a4a2c")
                      for k in range(12)])
    cruz = VGroup(Rectangle(width=0.07, height=0.34, fill_color=OURO, fill_opacity=1, stroke_color=PT, stroke_width=3),
                  Rectangle(width=0.24, height=0.07, fill_color=OURO, fill_opacity=1, stroke_color=PT, stroke_width=3)
                  .shift(UP * 0.06)).move_to(contas[-1].get_center() + DOWN * 0.26)
    retro = VGroup(Rectangle(width=0.1, height=0.5, fill_color="#16161b", fill_opacity=1, stroke_width=0).move_to([tx, 2.35, 0]),
                   RoundedRectangle(corner_radius=0.18, width=1.9, height=0.62, fill_color="#16161b", fill_opacity=1,
                                    stroke_color=PT, stroke_width=8).move_to([tx, 2.05, 0]),
                   RoundedRectangle(corner_radius=0.12, width=1.62, height=0.4, fill_color="#3a4870", fill_opacity=1,
                                    stroke_width=0).move_to([tx, 2.05, 0]),
                   Line([tx - 0.6, 1.92, 0], [tx - 0.2, 2.2, 0], stroke_color="#8fa3d6", stroke_width=5))
    terco = VGroup(contas, cruz)
    reflexo = Polygon([-W / 2, 6, 0], [-W / 2 + 1.6, 6, 0], [-W / 2 + 4.2, -2.6, 0], [-W / 2 + 3.0, -2.6, 0],
                      fill_color=WHITE, fill_opacity=0.04, stroke_width=0)
    neon = VGroup()  # o neon UBER/99 fica no canto da tela (camada HyperFrames)
    return dict(grupo=VGroup(g, luzes, chuva, reflexo, moldura, encosto, painel, celular), neon=neon,
                frente=VGroup(retro, terco), luzes=luzes, chuva=chuva, terco=terco)
