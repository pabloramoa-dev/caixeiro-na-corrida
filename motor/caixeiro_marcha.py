"""Curva temporal determinística para a troca de marcha do Caixeiro.

A mão direita fica no volante quase todo o tempo. A cada ciclo ela desce,
permanece brevemente no câmbio e retorna sem saltos entre frames.
Esta camada não depende de Manim e pode ser testada separadamente.
"""

PERIODO = 13.5
PRIMEIRA_TROCA = 3.2
DESCIDA = 0.52
PAUSA = 0.32
VOLTA = 0.68


def _suavizar(x):
    x = max(0.0, min(1.0, float(x)))
    return x * x * (3.0 - 2.0 * x)


def progresso(t):
    """0 = mão no volante; 1 = mão no câmbio."""
    if t < PRIMEIRA_TROCA:
        return 0.0
    fase = (t - PRIMEIRA_TROCA) % PERIODO
    if fase < DESCIDA:
        return _suavizar(fase / DESCIDA)
    if fase < DESCIDA + PAUSA:
        return 1.0
    if fase < DESCIDA + PAUSA + VOLTA:
        return 1.0 - _suavizar((fase - DESCIDA - PAUSA) / VOLTA)
    return 0.0
