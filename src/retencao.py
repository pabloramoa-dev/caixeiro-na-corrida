"""Coleta uma amostra por Reel, no dia seguinte à publicação."""
from datetime import datetime, timedelta
import json
from pathlib import Path
from statistics import mean
import requests
from src import config, fila
from motor.formatos import FIM, INICIO

def main():
    hoje = datetime.now(fila.BRT).date()
    if not INICIO < hoje <= FIM + timedelta(days=2):
        return
    destino = Path('conteudo/retencao_teste.json')
    dados = json.loads(destino.read_text())['reels'] if destino.exists() else {}
    cfg = config.carregar(exigir_credenciais=False)
    for post in fila.ler_publicados():
        mid = post.get('media_id')
        if not mid or not post.get('dia_teste') or mid in dados:
            continue
        idade = datetime.now(fila.BRT) - datetime.fromisoformat(post['quando'])
        if not timedelta(hours=23) <= idade < timedelta(hours=27):
            continue
        resp = requests.get(f'{cfg.base_graph}/{mid}/insights',params={'metric':'ig_reels_avg_watch_time'},
                            headers={'Authorization':f'Bearer {cfg.ig_token}'},timeout=30)
        if not resp.ok:
            raise RuntimeError(f'Insights {post["id"]}: HTTP {resp.status_code}')
        linhas = resp.json().get('data',[])
        if not linhas or not linhas[0].get('values'):
            continue
        segundos = linhas[0]['values'][0]['value']/1000
        dados[mid] = dict(id=post['id'],formato=post['formato'],segundos=segundos,
                          duracao=post['duracao'],fracao=segundos/post['duracao'],
                          idade_horas=round(idade.total_seconds()/3600,2))
    resumo = {}
    for formato in ('curto','longo'):
        grupo=[r for r in dados.values() if r['formato']==formato]
        resumo[formato]={'amostras':len(grupo),'segundos_medios':mean(r['segundos'] for r in grupo) if grupo else None,
                         'percentual_medio':100*mean(r['fracao'] for r in grupo) if grupo else None}
    destino.write_text(json.dumps(dict(resumo=resumo,reels=dados),indent=2)+'\n')
    print(json.dumps(resumo,ensure_ascii=False))

if __name__ == '__main__':
    main()
