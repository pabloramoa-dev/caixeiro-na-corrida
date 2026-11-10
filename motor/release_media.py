"""Entrega arquivos imutáveis e verifica o SHA-256 informado pelo GitHub."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

def gh(*args):
    return subprocess.check_output(['gh',*map(str,args)],text=True)

def enviar(tag, arquivos):
    repo = os.environ['GITHUB_REPOSITORY']
    if subprocess.run(['gh','release','view',tag],stdout=subprocess.DEVNULL).returncode:
        gh('release','create',tag,'--title',tag,'--notes','Mídia do Caixeiro na Corrida','--latest=false')
    assets = {x['name']:x for x in json.loads(gh('api',f'repos/{repo}/releases/tags/{tag}'))['assets']}
    urls = {}
    for p in arquivos:
        with p.open('rb') as f:
            digest = 'sha256:'+hashlib.file_digest(f,'sha256').hexdigest()
        if p.name not in assets:
            gh('release','upload',tag,p)
            assets = {x['name']:x for x in json.loads(gh('api',f'repos/{repo}/releases/tags/{tag}'))['assets']}
        item = assets[p.name]
        if item.get('digest') != digest:
            raise RuntimeError(f'Digest divergente: {p}')
        urls[p.name] = item['browser_download_url']
    return urls

def salvar(pasta):
    for video in sorted(pasta.glob('cx[0-9][0-9][0-9].mp4')):
        ep = video.stem
        assinatura = (pasta/f'{ep}.hash').read_text().strip()
        with video.open('rb') as f:
            chave = hashlib.file_digest(f,'sha256').hexdigest()[:16]
        files = [video,pasta/f'{ep}-capa.jpg',pasta/f'{ep}-story.mp4']
        urls = enviar(f'midia-{ep}-{chave}',files)
        dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration',
                                             '-of','csv=p=0',str(video)]))
        dest = Path('reels')/f'{ep}-release.json'
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(dict(assinatura=assinatura,duracao=dur,urls=urls),indent=2)+'\n')
        info = pasta/f'{ep}-render.json'
        if info.exists():
            (dest.parent/info.name).write_bytes(info.read_bytes())

def migrar():
    arquivos = [Path(x) for x in gh_git().splitlines()]
    registro = {}
    for p in arquivos:
        if p.suffix.lower() in {'.mp4','.jpg','.hash'}:
            tag = 'acervo-'+subprocess.check_output(['git','rev-parse','--short=12','HEAD'],text=True).strip()+'-'+p.parent.name
            registro[str(p)] = enviar(tag,[p])[p.name]
    if registro:
        dest = Path('conteudo/acervo_releases.json')
        anterior = json.loads(dest.read_text()) if dest.exists() else {}
        dest.write_text(json.dumps(anterior|registro,ensure_ascii=False,indent=2)+'\n')
        subprocess.run(['git','rm','--',*registro],check=True)

def gh_git():
    return subprocess.check_output(['git','ls-files','reels','previews'],text=True)

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('pasta',type=Path,nargs='?')
    ap.add_argument('--migrar',action='store_true')
    args=ap.parse_args()
    if args.migrar: migrar()
    else: salvar(args.pasta)
