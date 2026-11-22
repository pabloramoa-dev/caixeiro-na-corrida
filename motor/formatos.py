import json
from datetime import date
from pathlib import Path

CURTOS = json.loads((Path(__file__).resolve().parents[1] / 'conteudo/curtos_teste.json').read_text())
INICIO = date(2026, 11, 10)
FIM = date(2026, 11, 23)

def no_teste(dia):
    return INICIO <= dia <= FIM

def preparar_curto(ep):
    plano = CURTOS[ep['id']]
    batidas = [dict(ep['batidas'][i]) for i in plano['batidas']]
    batidas[0]['fala'] = plano['abertura']
    batidas[plano['reenganche']]['fala'] = 'Só que tinha um detalhe. ' + batidas[plano['reenganche']]['fala']
    return dict(ep, batidas=batidas, formato='curto', reenganche_indice=plano['reenganche'])
