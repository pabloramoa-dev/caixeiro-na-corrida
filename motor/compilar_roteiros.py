#!/usr/bin/env python3
"""Converte os lotes de roteiro em texto (roteiros/*.txt) nos JSON do estúdio
(episodios/cxNNN.json). Escrever em texto é mais rápido e fácil de revisar.

Formato de cada episódio:

    ## 025 | TÍTULO | categoria | dia|noite
    G: gancho da legenda (com emoji)
    P: pergunta pros comentários
    H: #tag1 #tag2 #tag3
    expr | arte | fala
    expr | relogio: SÁBADO · 7H | fala
    expr | - | fala                (sem arte)

expr: neutra, desconfiada, chocada, ironica, triste, brava, rindo
arte: titulo, relogio, conversa, carimbo, coracao, notificacao, direct,
      manchete, manchete_v, porta, carro, mapa, - (nenhuma)
O CTA (coração + seguir) NÃO vai no roteiro: o motor coloca sozinho no final.

    python motor/compilar_roteiros.py            # compila todos os lotes
    python motor/compilar_roteiros.py --checar   # só valida e mostra estatísticas
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ROTEIROS = RAIZ / "roteiros"
EPISODIOS = RAIZ / "episodios"

EXPRS = {"neutra", "desconfiada", "chocada", "ironica", "triste", "brava", "rindo"}
ARTES = {"titulo", "relogio", "conversa", "carimbo", "coracao", "notificacao", "direct",
         "manchete", "manchete_v", "porta", "carro", "mapa", "-"}
STOP = {"o", "a", "os", "as", "de", "do", "da", "e", "é", "um", "uma", "que", "pra", "no", "na",
        "me", "eu", "ele", "ela", "se", "com", "em", "por", "mas", "não", "tô", "ao"}
TAGS_FIXAS_IG = "#historias #motoristadeaplicativo #uber #corrida #caixeironacorrida"
TAGS_FIXAS_TT = "#historias #motoristadeaplicativo #uber #fyp #caixeironacorrida"


def destaque(fala: str) -> list[str]:
    palavras = fala.split()
    fortes = [w for w in palavras if re.sub(r"\W", "", w.lower()) not in STOP]
    return (fortes or palavras)[-2:]


def legendas(cab: dict) -> tuple[str, str]:
    g, p, h = cab["G"], cab["P"], cab["H"]
    ig = (f"{g}\n\n{p} 👇\n\n🚗 Cada corrida, uma história. Segue o Caixeiro pra não perder a próxima.\n\n"
          f"História de ficção.\n\n{h} {TAGS_FIXAS_IG}")
    tt = f"{g} {p} 👇\nHistória de ficção.\n{h} {TAGS_FIXAS_TT}"
    return ig, tt


def parse(texto: str, origem: str) -> list[dict]:
    eps, atual = [], None
    for n, linha in enumerate(texto.splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("//"):
            continue
        onde = f"{origem}:{n}"
        if linha.startswith("## "):
            partes = [x.strip() for x in linha[3:].split("|")]
            if len(partes) != 4:
                raise ValueError(f"{onde}: cabeçalho precisa de 4 campos")
            num, titulo, cat, cen = partes
            if cen not in {"dia", "noite"}:
                raise ValueError(f"{onde}: cenário deve ser dia ou noite")
            atual = {"num": int(num), "titulo": titulo.upper(), "categoria": cat, "cenario": cen,
                     "cab": {}, "batidas": [], "onde": onde}
            eps.append(atual)
            continue
        if atual is None:
            raise ValueError(f"{onde}: linha fora de episódio")
        if re.match(r"^[GPH]:", linha):
            atual["cab"][linha[0]] = linha[2:].strip()
            continue
        partes = [x.strip() for x in linha.split("|", 2)]
        if len(partes) != 3:
            raise ValueError(f"{onde}: batida precisa de 'expr | arte | fala'")
        expr, arte, fala = partes
        if expr not in EXPRS:
            raise ValueError(f"{onde}: expressão inválida '{expr}'")
        tipo, _, txt = arte.partition(":")
        tipo, txt = tipo.strip(), txt.strip()
        if tipo not in ARTES:
            raise ValueError(f"{onde}: arte inválida '{tipo}'")
        b = {"fala": fala, "expr": expr,
             "arte": None if tipo == "-" else ([tipo, txt] if txt else [tipo]),
             "destaque": destaque(fala)}
        atual["batidas"].append(b)
    return eps


def montar(e: dict) -> dict:
    for k in "GPH":
        if not e["cab"].get(k):
            raise ValueError(f"{e['onde']}: falta a linha {k}:")
    ig, tt = legendas(e["cab"])
    try:
        from .ganchos_caixeiro import aplicar_ganchos
    except ImportError:  # execução direta via python motor/compilar_roteiros.py
        from ganchos_caixeiro import aplicar_ganchos
    return aplicar_ganchos({"id": f"cx{e['num']:03d}", "ep": e["num"], "avulso": True, "titulo": e["titulo"],
            "categoria": e["categoria"], "cenario": e["cenario"],
            "legenda_post": ig, "legenda_tiktok": tt, "batidas": e["batidas"]})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checar", action="store_true")
    a = ap.parse_args()
    todos, vistos = [], {}
    for arq in sorted(ROTEIROS.glob("*.txt")):
        for e in parse(arq.read_text(encoding="utf-8"), arq.name):
            if e["num"] in vistos:
                raise ValueError(f"episódio {e['num']} repetido ({vistos[e['num']]} e {arq.name})")
            vistos[e["num"]] = arq.name
            todos.append(montar(e))
    titulos = {}
    curtos = []
    for ep in todos:
        t = ep["titulo"]
        if t in titulos:
            raise ValueError(f"título repetido: {t} ({titulos[t]} e {ep['id']})")
        titulos[t] = ep["id"]
        w = sum(len(b["fala"].split()) for b in ep["batidas"])
        if w < 330:
            curtos.append(f"{ep['id']} ({w} palavras)")
    pal = [sum(len(b["fala"].split()) for b in ep["batidas"]) for ep in todos]
    print(f"{len(todos)} episódios · palavras min {min(pal) if pal else 0} / média "
          f"{sum(pal)//max(1,len(pal))} / máx {max(pal) if pal else 0}")
    if curtos:
        print("curtos demais:", ", ".join(curtos))
    if a.checar:
        return 1 if curtos else 0
    EPISODIOS.mkdir(exist_ok=True)
    for ep in todos:
        (EPISODIOS / f"{ep['id']}.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
