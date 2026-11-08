"""Gancho de antecipação + micro-reenganche factual para o Caixeiro.

Somente reorganiza a apresentação de fatos já narrados. Não altera desfecho,
CTA, nomes, imagens nem quantidade de batidas. Opera na compilação e no render,
com marca de versão para impedir alterações duplicadas.
"""
from __future__ import annotations

import copy
import re

VERSAO = "caixeiro-antecipacao-e-reenganche-v1"
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

    # Evita antecipar revelações da parte final: teaser somente em 30–65%.
    opener = beats[0]["fala"].strip()
    candidatos = _opcoes(out, 0.30, 0.65)
    escolhido = candidatos[0] if candidatos else None
    if ABERTURA_COMUM.search(opener) and escolhido:
        _, indice, pista = escolhido
        beats[0]["fala"] = (
            f"{pista} E eu ainda não fazia ideia de como essa corrida ia terminar."
        )
        beats[0]["expr"] = "desconfiada" if beats[0].get("expr") == "neutra" else beats[0].get("expr", "neutra")
        beats[0]["destaque"] = pista.split()[-2:]
        # O título existe para o editor, não para recontar as legendas no topo.
        out["gancho_origem"] = indice
        out["gancho_pista"] = pista
        out["gancho_modelo"] = "antecipacao_factual"
    else:
        out["gancho_modelo"] = "abertura_editorial_preservada"

    # Reengaja no meio com uma cena real que a narrativa ainda vai explicar.
    n = len(beats)
    meio = _opcoes(out, 0.48, 0.73)
    escolhido_meio = next((v for v in meio if v[1] != out.get("gancho_origem")), None)
    if escolhido_meio:
        _, indice, _ = escolhido_meio
        anterior = beats[indice]["fala"].strip()
        if not re.match(r"^(?:mas presta aten[cç][aã]o|olha o que veio depois)\b", anterior, re.I):
            categoria = str(out.get("categoria", "")).lower()
            if categoria == "humor":
                prefixo = "E olha a situação que veio agora: "
            elif categoria in {"reflexao", "superacao", "emocao"}:
                prefixo = "Mas presta atenção no detalhe dessa corrida: "
            else:
                prefixo = "Só que olha o que aconteceu depois: "
            beats[indice]["fala"] = prefixo + _limpar(anterior)
            out["reenganche_indice"] = indice
            out["reenganche_modelo"] = "mudanca_de_cena_factual"
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
