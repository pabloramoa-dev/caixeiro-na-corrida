"""Gancho de antecipação + micro-reenganche factual para o Caixeiro.

Somente reorganiza a apresentação de fatos já narrados. Não altera desfecho,
CTA, nomes, imagens nem quantidade de batidas. Opera na compilação e no render,
com marca de versão para impedir alterações duplicadas.
"""
from __future__ import annotations

import json
from pathlib import Path
import copy
import re

GANCHOS = json.loads((Path(__file__).resolve().parents[1]/"conteudo/ganchos.json").read_text())
VERSAO = "caixeiro-antecipacao-e-reenganche-v2"
ABERTURA_COMUM = re.compile(r"^\s*(?:Sobe a[ií][,!]?|Entra a[ií][,!]?|Puxa uma cadeira[,!]?)\b", re.I)
INICIOS = re.compile(r"^(?:A[ií][, ]+|E a[ií][, ]+|Mas[, ]+|S[oó] que[, ]+|Foi quando[, ]+|Ent[aã]o[, ]+)", re.I)
EXCLUIR = re.compile(
    r"^(?:era (?:o|a|um|uma)\b|foi (?:o|a|um|uma)\b|"
    r"no fim\b|na verdade\b|descobrimos que\b|"
    r"agora me conta\b|e se voc[eê]\b|me segue\b|segue o\b)", re.I)
OBJETOS = re.compile(
    r"\b(?:mensagem|bilhete|celular|telefone|foto|papel|sacola|bolsa|chave|"
    r"documento|envelope|endereço|porta|portão|carro|pessoa|criança|"
    r"professora|menino|sogra|passageir[oa]|cart[aã]o|dinheiro|escola|"
    r"carta|viatura|motorista|recibo|flor|caderno|nome|mala|caixa|"
    r"presente|ligação|discurso|peneira|estádio|jogo)\b", re.I)
ACOES = re.compile(
    r"\b(?:encontrou|achou|mostrou|apareceu|perguntou|respondeu|"
    r"recebeu|abriu|parou|levantou|ligou|olhou|sorriu|escutou|"
    r"ficou|tirou|falou|entrou|apitou|desceu|disse|pegou|pediu|"
    r"entregou|viu|ouviu|chamou|mostraram)\b", re.I)
REVELACAO = re.compile(
    r"\b(?:era o menino|era a mulher|descobri que|foi revelado|"
    r"tudo se explicou|a verdade era|no final|no fim|a conclusão|"
    r"enfim entendi)\b", re.I)
CHAMADA = re.compile(r"\b(?:curte|compartilha|coment[aá]rios|siga|segue|like|"
                     r"me acompanha|perfil)\b", re.I)


def _frases(fala: str) -> list[str]:
    # Perguntas e frases curtas são interessantes, mas não se inventam diálogos.
    return re.split(r"(?<=[.!?])\s+", str(fala).strip())


def _limpar(frase: str) -> str:
    s = INICIOS.sub("", frase.strip()).strip()
    return s[:1].upper() + s[1:] if s else ""


def _opcoes(ep: dict, start: float, end: float) -> list[tuple[int, int, str]]:
    beats = ep["batidas"]
    n = len(beats)
    a = max(1, int(n * start))
    b = min(n - 2, max(a + 1, int(n * end)))
    found = []
    for i in range(a, b + 1):
        beat = beats[i]
        for frase in _frases(beat.get("fala", "")):
            sample = _limpar(frase)
            words = sample.split()
            if not (7 <= len(words) <= 26 and 36 <= len(sample) <= 160):
                continue
            if EXCLUIR.search(sample) or REVELACAO.search(sample) or CHAMADA.search(sample):
                continue
            action = bool(ACOES.search(sample))
            object_ = bool(OBJETOS.search(sample))
            if not (action or object_):
                continue
            score = 5 * int(action) + 4 * int(object_)
            score += 3 if beat.get("expr") in ("chocada", "desconfiada") else 0
            score += 2 if "?" in sample or ":" in sample else 0
            score += min(4, len(words) // 6)
            score -= 4 if re.match(r"^(?:eu disse|eu avisei|eu perguntei)\b", sample, re.I) else 0
            found.append((score, i, sample))
    return sorted(found, key=lambda v: (-v[0], v[1]))


def aplicar_ganchos(ep: dict) -> dict:
    """Adapta todas as histórias em edição, sem revelar o final nem duplicar CTA."""
    out = copy.deepcopy(ep)
    if out.get("gancho_versao") == VERSAO:
        return out
    beats = out.get("batidas")
    if not isinstance(beats, list) or len(beats) < 9 or out.get("preview_only"):
        return out
    if not all(isinstance(b, dict) and str(b.get("fala", "")).strip() for b in beats):
        return out

    try:
        from .objetos_fala import objeto
        from .compilar_roteiros import atuar
    except ImportError:
        from objetos_fala import objeto
        from compilar_roteiros import atuar
    pista = re.sub(r"^Sobe aí, porque ", "", beats[0]["fala"], flags=re.I)
    if not objeto(pista) or "me fez lembrar" in pista:
        for beat in beats[2:max(4, len(beats)//2)]:
            if objeto(beat["fala"]):
                pista = beat["fala"]
                break
    if "me fez lembrar" in pista:
        pista = beats[2]["fala"]
    item = objeto(pista)
    pista = pista[:1].upper() + pista[1:]
    if "?" not in pista:
        pergunta = "O que aconteceu depois disso no banco de trás?"
        pista += " " + pergunta
    beats[0]["fala"] = GANCHOS.get(out.get("id"), pista)
    beats[1]["fala"] = re.sub(r"^Eu sou o Caixeiro[,.:! ]*(?:e )?", "", beats[1]["fala"], flags=re.I).capitalize() if beats[1]["fala"].lower().startswith("eu sou o caixeiro") else beats[1]["fala"]
    idx = min(range(1, len(beats)-2), key=lambda i: abs(sum(len(b["fala"].split()) for b in beats[:i])-54))
    beats[idx]["fala"] = "Só que tinha um detalhe. " + _limpar(beats[idx]["fala"])
    out["reenganche_indice"] = idx
    atuar(beats)
    out["gancho_versao"] = VERSAO
    return out


def resumo(episodes: list[dict]) -> dict:
    stats = {"total": len(episodes), "gancho_antecipado": 0,
             "micro_reenganche": 0, "preservados": 0}
    for ep in episodes:
        adapted = aplicar_ganchos(ep)
        if adapted.get("gancho_modelo") == "antecipacao_factual":
            stats["gancho_antecipado"] += 1
        elif adapted.get("gancho_modelo") == "abertura_editorial_preservada":
            stats["preservados"] += 1
        if "reenganche_indice" in adapted:
            stats["micro_reenganche"] += 1
    return stats


if __name__ == "__main__":
    import json
    from pathlib import Path
    pasta = Path(__file__).resolve().parents[1] / "episodios"
    eps = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(pasta.glob("cx*.json"))]
    print(json.dumps(resumo(eps), ensure_ascii=False, indent=2))
