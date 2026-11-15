"""Caixeiro + carro sob a composição HyperFrames (mesmo pipeline da Nina)."""
import json, os, sys
from pathlib import Path
M = Path(__file__).resolve().parent
sys.path.insert(0, str(M))
from manim import *
import numpy as np
import marcao_lib as ML
import caixeiro_marcha as MARCHA
import dvh_vox_papel as V
import objetos as O

ARTS = bool(os.environ.get('NINA_RENDER_ARTS'))
P = Path(os.environ.get('PASTA', '/tmp'))
EPF = os.environ.get('EPISODIO')
EP = json.loads(Path(EPF).read_text()) if EPF else {'batidas': [{'fala': 'x', 'expr': 'neutra'}], 'cenario': os.environ.get('MARCAO_CEN', 'noite')}
config.frame_width = 8
config.frame_height = 2.9 if ARTS else 14.222
config.pixel_width = 960 if ARTS else int(os.environ.get('NINA_HF_BASE_WIDTH', '720'))
config.pixel_height = 348 if ARTS else round(config.pixel_width * 16 / 9)
config.frame_rate = 30


def _montar(scene, expr, cenario):
    cen = ML.carro(cenario)
    scene.add(cen['grupo'], cen['neon'])
    p = ML.posicionar(ML.marcao(expr, cenario))
    V.colar(scene, p, espessura=22)
    scene.add(p['volante'], cen['frente'])
    return cen, p


class MarcaoBase(Scene):
    def construct(self):
        V.estilo('papel')
        segs = json.loads((P / 'segs.json').read_text())
        cues = json.loads((P / 'lip.json').read_text())
        bats = EP['batidas']; cenario = EP.get('cenario', 'noite')
        cen, p = _montar(self, bats[0].get('expr', 'neutra'), cenario)
        W = config.frame_width
        # luzes da rua passando pela janela (parallax) + chuva caindo
        vel = {id(m): 0.9 + (k % 5) * 0.45 for k, m in enumerate(cen['luzes'])}

        def passar(g, dt):
            for m in g:
                m.shift(LEFT * vel[id(m)] * dt)
                if m.get_x() < -W / 2 - 1.2:
                    m.set_x(W / 2 + 1.2)
        cen['luzes'].add_updater(passar)

        def cair(g, dt):
            for m in g:
                m.shift(np.array([-0.35, -1.6, 0]) * dt)
                if m.get_y() < -2.6:
                    m.shift(UP * 8.4)
        if len(cen['chuva']):
            cen['chuva'].add_updater(cair)
        # terço balança com o carro
        piv = cen['terco'].get_top().copy()
        st_t = {'a': 0.0}

        def balanca(m, dt):
            t = self.renderer.time
            a = 0.10 * np.sin(t * 2.3) + 0.03 * np.sin(t * 7.1)
            m.rotate(a - st_t['a'], about_point=piv); st_t['a'] = a
        cen['terco'].add_updater(balanca)
        # neon piscando de leve (falha rápida de vez em quando)
        falhas = [3.7, 3.8, 11.2, 19.6, 19.72, 27.4, 34.9]
        def piscar(m, dt):
            t = self.renderer.time
            apaga = any(0 <= t - f < 0.07 for f in falhas)
            brilho = 0.0 if apaga else (0.9 + 0.1 * np.sin(t * 9))
            for letra in m[1]:
                for k, cam in enumerate(letra[0]):
                    cam.set_stroke(opacity=(0.10, 0.18, 0.32)[k] * brilho)
                letra[1].set_stroke(opacity=max(0.25, brilho))
        if len(cen['neon']):
            cen['neon'].add_updater(piscar)

        # volante mexendo de leve: ele está dirigindo
        st_v = {'a': 0.0}

        def girar(m, dt):
            t = self.renderer.time
            a = 0.07 * np.sin(t * 0.8) + 0.03 * np.sin(t * 2.1)
            m.rotate(a - st_v['a'], about_point=m[4].get_center()); st_v['a'] = a
        p['roda'].add_updater(girar)
        # Referências relativas à cabeça: permitem animar ombro, cotovelo e mão
        # sem deslocar o personagem quando a geometria do braço muda.
        home = p['cab'].get_center().copy()
        ombro_rel = p['bracos'][3][0].get_start() - home
        cotovelo_rel = p['bracos'][4][0].get_end() - home
        mao_rel = p['mao_d'].get_center() - home
        marcha_ativa = os.environ.get('CAIXEIRO_TROCA_MARCHA', '1').lower() not in ('0', 'false', 'nao')
        state = {'i': 0}

        def ajustar_membro(segmento, inicio, fim):
            for linha in segmento:
                linha.put_start_and_end_on(inicio, fim)

        def motion(m, dt):
            t = self.renderer.time
            i = max([k for k, s in enumerate(segs) if s['ini'] <= t] or [0])
            if i != state['i']:
                expr = bats[i].get('expr', 'neutra')
                if expr not in ML.EXPRESSOES: expr = 'neutra'
                p['rosto'].become(ML.rosto_alinhado(p, expr))
                p['expr'] = expr; state['i'] = i
            # balanço do carro: leve, com "buraco" de vez em quando
            bump = 0.05 * max(0, np.sin(t * 0.9)) ** 12
            pos_cab = home + np.array([.03 * np.sin(t * 1.1), .025 * np.sin(t * 3.3) + bump, 0])
            deslocamento = pos_cab - p['cab'].get_center()
            m.shift(deslocamento)
            # O adesivo adiciona 'grupo' e 'volante' separadamente à Scene.
            # Logo o updater deve estar em 'grupo' (na cena) e mover o volante também.
            p['volante'].shift(deslocamento)

            if marcha_ativa:
                # Descer a mão direita até o câmbio, pausar e voltar ao volante.
                # O braço esquerdo, volante, rosto e lip sync seguem independentes.
                f = MARCHA.progresso(t)
                cab = p['cab'].get_center()
                ombro = cab + ombro_rel
                cotovelo_neutro = cab + cotovelo_rel
                mao_neutra = cab + mao_rel
                mao_cambio = cen['manopla'].get_center()
                cotovelo_cambio = ombro + 0.53 * (mao_cambio - ombro) + np.array([.11, -.13, 0])
                cotovelo = (1 - f) * cotovelo_neutro + f * cotovelo_cambio
                mao = (1 - f) * mao_neutra + f * mao_cambio
                ajustar_membro(p['bracos'][3], ombro, ombro + .55 * (cotovelo - ombro))
                ajustar_membro(p['bracos'][4], ombro + .50 * (cotovelo - ombro), cotovelo)
                ajustar_membro(p['bracos'][5], cotovelo, mao)
                p['mao_d'].move_to(mao)
        p['grupo'].add_updater(motion)
        ML.animar(self, p, cues)
        self.wait(segs[-1]['fim'] + 2.2)


class Capa(Scene):
    def construct(self):
        config.pixel_width = 1080; config.pixel_height = 1920
        V.estilo('papel')
        _montar(self, os.environ.get('MARCAO_EXPR', 'ironica'), EP.get('cenario', 'noite'))


class Perfil(Scene):
    def construct(self):
        V.estilo('papel')
        cen, p = _montar(self, 'ironica', 'noite')
        self.camera.frame_center = p['cab'].get_center() + DOWN * 0.3


def _classe_arte(i):
    class Arte(Scene):
        def construct(self):
            V.estilo('papel'); self.camera.background_color = '#fff9ea'
            V.FONTE = 'DejaVu Sans'
            spec = EP['batidas'][i].get('arte')
            m = O.arte(spec[0], spec[1] if len(spec) > 1 else None)
            if m.width > 7.3: m.scale(7.3 / m.width)
            if m.height > 2.6: m.scale(2.6 / m.height)
            self.add(m.move_to(ORIGIN))
    Arte.__name__ = f'Arte{i}'
    return Arte


for _i in range(len(EP['batidas'])):
    globals()[f'Arte{_i}'] = _classe_arte(_i)
