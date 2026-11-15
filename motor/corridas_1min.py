"""Banco autoral e abastecimento da série diária Corrida de 1 Minuto.

Cada causo recebe um ID fixo e é criado uma única vez. O script nunca reutiliza
histórias já publicadas e nunca altera roteiros existentes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "conteudo" / "corridas_1min.json"
EPISODIOS = RAIZ / "episodios"
PUBLICADOS = RAIZ / "conteudo" / "publicados.json"
ID_INICIAL = 500
FORMATO = "corrida_1min"


def montar(item: dict, indice: int) -> dict:
    """Converte um causo do banco em roteiro completo para o estúdio existente."""
    falas = item["falas"]
    if len(falas) != 6 or not all(isinstance(f, str) and f.strip() for f in falas):
        raise ValueError(f"Causo {item.get('chave')}: requer seis falas")
    total_palavras = len((" ".join(falas) + " " + item["cta_envio"]).split())
    if not 115 <= total_palavras <= 165:
        raise ValueError(f"Causo {item['chave']}: {total_palavras} palavras fora da faixa")
    if not item["cta_envio"].lower().startswith("manda pra quem"):
        raise ValueError(f"Causo {item['chave']}: CTA precisa convidar ao envio")
    n = ID_INICIAL + indice
    ep_id = f"cx{n:03d}"
    titulo = item["titulo"].strip()
    convite = item["cta_envio"].strip()
    legenda = (
        f"🚕 CORRIDA DE 1 MINUTO | {titulo}\n"
        f"{falas[0]}\n\n{convite}\n\n"
        "História de ficção.\n\n"
        "#CorridaDe1Minuto #CaixeiroNaCorrida #Humor #MotoristaDeAplicativo #ReelsBrasil"
    )
    batidas = [
        {"fala": fala.strip(),
         "expr": ("chocada", "desconfiada", "neutra", "chocada", "rindo", "ironica")[i],
         "arte": ["foto"], "destaque": []}
        for i, fala in enumerate(falas)
    ]
    return {
        "id": ep_id, "ep": n, "avulso": True, "preview_only": False,
        "formato": FORMATO, "serie": "Corrida de 1 Minuto",
        "causo_chave": item["chave"], "ficcao_original": True,
        "titulo": titulo, "categoria": "humor_cotidiano",
        "cenario": "dia" if indice % 2 == 0 else "noite",
        "visual_style": "cinematic_2d",
        "cta_envio": convite,
        "legenda_post": legenda,
        "legenda_tiktok": (
            f"🚕 Corrida de 1 Minuto: {titulo}. {convite} "
            "História de ficção. #CorridaDe1Minuto #CaixeiroNaCorrida #Humor #Storytime"
        ),
        "batidas": batidas,
    }


def validar_catalogo(catalogo: list[dict]) -> None:
    if not isinstance(catalogo, list) or not catalogo:
        raise ValueError("Catálogo vazio")
    chaves, titulos = set(), set()
    for i, item in enumerate(catalogo):
        if not all(item.get(k) for k in ("chave", "titulo", "falas", "cta_envio")):
            raise ValueError(f"Causo {i}: campos obrigatórios ausentes")
        if item["chave"] in chaves or item["titulo"] in titulos:
            raise ValueError(f"Duplicidade no catálogo: {item['titulo']}")
        chaves.add(item["chave"])
        titulos.add(item["titulo"])
        montar(item, i)


def gerar_estoque(minimo: int = 3, *, catalogo: Path = CATALOGO,
                 episodios: Path = EPISODIOS, publicados: Path = PUBLICADOS) -> list[str]:
    """Mantém N roteiros inéditos disponíveis para a fila curta.

    Nenhum episódio já presente ou publicado é reescrito. Catálogo esgotado gera
    aviso, não reutilização silenciosa de causos.
    """
    itens = json.loads(catalogo.read_text(encoding="utf-8"))
    validar_catalogo(itens)
    ledger = json.loads(publicados.read_text(encoding="utf-8")) if publicados.exists() else []
    feitos = {p["id"] for p in ledger if not p.get("ensaio")}
    episodios.mkdir(parents=True, exist_ok=True)
    ids = [f"cx{ID_INICIAL+i:03d}" for i in range(len(itens))]
    existentes = {ep_id for ep_id in ids if (episodios / f"{ep_id}.json").exists()}
    # Conflitos devem falhar, nunca substituir um roteiro do canal.
    for ep_id in existentes:
        arq = episodios / f"{ep_id}.json"
        if json.loads(arq.read_text(encoding="utf-8")).get("formato") != FORMATO:
            raise ValueError(f"ID reservado já ocupado por outro formato: {ep_id}")
    em_estoque = len((existentes - feitos))
    novos = []
    for i, item in enumerate(itens):
        if em_estoque >= minimo:
            break
        ep = montar(item, i)
        ep_id = ep["id"]
        if ep_id in feitos or ep_id in existentes:
            continue
        (episodios / f"{ep_id}.json").write_text(
            json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        novos.append(ep_id)
        em_estoque += 1
    if em_estoque < minimo:
        print(f"::warning::Estoque de Corrida de 1 Minuto baixo: {em_estoque} roteiros; "
              "amplie conteudo/corridas_1min.json antes do fim do banco.")
    print(f"Corrida de 1 Minuto: {len(novos)} novo(s); {em_estoque} inédito(s) em estoque.")
    return novos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimo", type=int, default=3)
    parser.add_argument("--checar", action="store_true")
    args = parser.parse_args()
    if args.minimo < 1:
        parser.error("--minimo precisa ser positivo")
    if args.checar:
        itens = json.loads(CATALOGO.read_text(encoding="utf-8"))
        validar_catalogo(itens)
        print(f"Catálogo válido: {len(itens)} causos inéditos.")
        return 0
    gerar_estoque(args.minimo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
