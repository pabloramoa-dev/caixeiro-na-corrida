"""Passageiro animado no banco traseiro para o piloto dialogado do Caixeiro.
Arte vetorial original Manim: passageiro menor e ao fundo, sem alterar o motorista.
"""
from manim import *
import numpy as np

def montar_passageiro():
    centro = np.array([2.38, 1.00, 0.0])
    tinta = "#151420"
    pele = "#be8868"
    # Banco traseiro: encosto, apoio de cabeca e cinto, com profundidade.
    banco = VGroup(
        RoundedRectangle(width=2.45, height=4.4, corner_radius=.54,
                         fill_color="#292936", fill_opacity=1, stroke_color=tinta,
                         stroke_width=13).move_to([2.35, -1.85, 0]),
        RoundedRectangle(width=1.45, height=1.05, corner_radius=.3,
                         fill_color="#41404b", fill_opacity=1, stroke_color=tinta,
                         stroke_width=9).move_to([2.35, .12, 0]))
    tronco = RoundedRectangle(width=1.8, height=2.28, corner_radius=.43,
                              fill_color="#7d3f4b", fill_opacity=1,
                              stroke_color=tinta, stroke_width=12).move_to(centro+DOWN*2.0)
    pescoco = RoundedRectangle(width=.45, height=.57, corner_radius=.13,
                               fill_color=pele, fill_opacity=1,
                               stroke_color=tinta, stroke_width=6).move_to(centro+DOWN*.81)
    orelhas = VGroup(*[
        Circle(radius=.15,fill_color=pele,fill_opacity=1,stroke_color=tinta,
               stroke_width=5).move_to(centro+np.array([s*.65,-.04,0]))
        for s in (-1,1)])
    cabeca = Ellipse(width=1.4,height=1.65,fill_color=pele,fill_opacity=1,
                     stroke_color=tinta,stroke_width=10).move_to(centro)
    cabelo = Arc(radius=.69,start_angle=0,angle=PI,arc_center=centro+UP*.15,
                 stroke_color="#30252c",stroke_width=27)
    franja = VGroup(*[
        Arc(radius=.35,start_angle=PI*.2,angle=PI*.55,
            arc_center=centro+np.array([x,.42,0]),
            stroke_color="#30252c",stroke_width=13)
        for x in (-.28,.24)])
    olhos = VGroup(*[
        Ellipse(width=.16,height=.22,fill_color="#26212b",fill_opacity=1,
                stroke_width=0).move_to(centro+np.array([x,.07,0]))
        for x in (-.27,.27)])
    sobrancelhas = VGroup(*[
        Line(centro+np.array([x-.12,.28,0]),centro+np.array([x+.12,.33,0]),
             stroke_width=8,stroke_color="#3e292b")
        for x in (-.27,.27)])
    nariz = Line(centro+DOWN*.10,centro+DOWN*.26+RIGHT*.06,
                 stroke_width=6,stroke_color="#9a6654")
    boca_centro = centro+DOWN*.44
    boca = Line(boca_centro+LEFT*.16,boca_centro+RIGHT*.16,
                stroke_width=8,stroke_color="#683c35")
    cinto = Line(centro+np.array([.50,-1.0,0]),centro+np.array([-.55,-2.9,0]),
                 stroke_color="#1b1e2e",stroke_width=25)
    grupo = VGroup(banco, tronco, pescoco, orelhas, cabeca, cabelo, franja,
                   olhos, sobrancelhas, nariz, boca, cinto)
    return {"grupo":grupo, "boca":boca, "boca_centro":boca_centro,
            "cabeca":cabeca, "olhos":olhos}


def animar_passageiro(scene, pessoa, cues):
    """Boca reage somente aos fonemas atribuídos ao passageiro."""
    atual = {"estado": None}
    boca = pessoa["boca"]
    c = pessoa["boca_centro"]
    def atualiza(m, dt):
        tempo = scene.renderer.time
        estado = "fechada"
        for cu in cues:
            if cu["start"] > tempo:
                break
            if cu["start"] <= tempo < cu["end"]:
                estado = cu["estado"]
                break
        if atual["estado"] != estado:
            if estado in ("fechada", "A", "X"):
                novo = Line(c+LEFT*.16,c+RIGHT*.16,
                             stroke_width=8,stroke_color="#683c35")
            else:
                alto = .12 if estado in ("meia","B","E","F","G") else .25
                novo = Ellipse(width=.31,height=alto,
                               fill_color="#431b25",fill_opacity=1,
                               stroke_color="#683c35",stroke_width=5).move_to(c)
            boca.become(novo)
            atual["estado"] = estado
    pessoa["grupo"].add_updater(atualiza)
