"""Configuração do Caixeiro na Corrida. Nenhum segredo em código: tudo vem dos
Secrets/Variables do GitHub Actions."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EPISODIOS = RAIZ / "episodios"
REELS = RAIZ / "reels"
PUBLICADOS_JSON = RAIZ / "conteudo" / "publicados.json"

RESERVA_MINIMA = 6        # vídeos prontos = 2 dias a 3 por dia; abaixo disso abre alerta
HORARIOS = {"manha": "08h", "almoco": "12h", "noite": "20h"}
COM_STORY = {"noite"}     # o das 20h também vai pros Stories (versão de 59 s)
DURACAO_MIN_S = 60.0
DURACAO_MAX_S = 240.0     # episódios de ~3 min (Reels aceita até 15 min pela API)


@dataclass(frozen=True)
class Config:
    ig_user_id: str
    ig_token: str
    raw_base_url: str
    graph_version: str
    publicar_ativo: bool
    dry_run: bool

    HOST = "https://graph.instagram.com"   # rota "API do Instagram com login do Instagram"

    @property
    def base_conta(self) -> str:
        return f"{self.HOST}/{self.graph_version}/{self.ig_user_id}"

    @property
    def base_graph(self) -> str:
        return f"{self.HOST}/{self.graph_version}"


def _flag(nome: str, padrao: str = "false") -> bool:
    return os.getenv(nome, padrao).strip().lower() in {"1", "true", "yes", "sim"}


def carregar(exigir_credenciais: bool = True) -> Config:
    obrigatorias = ["IG_USER_ID_CAIXEIRO", "IG_ACCESS_TOKEN_CAIXEIRO", "RAW_BASE_URL"]
    if exigir_credenciais:
        faltando = [k for k in obrigatorias if not os.getenv(k)]
        if faltando:
            raise RuntimeError(f"Variáveis obrigatórias ausentes: {faltando}")
    return Config(
        ig_user_id=os.getenv("IG_USER_ID_CAIXEIRO", ""),
        ig_token=os.getenv("IG_ACCESS_TOKEN_CAIXEIRO", ""),
        raw_base_url=os.getenv("RAW_BASE_URL", "https://raw.githubusercontent.com/pabloramoa-dev/caixeiro-na-corrida/main").rstrip("/"),
        graph_version=os.getenv("GRAPH_API_VERSION", "v22.0"),
        publicar_ativo=_flag("PUBLICAR_ATIVO", "false"),
        dry_run=_flag("DRY_RUN", "true"),
    )


def esconder(texto: str) -> str:
    for nome in ("IG_ACCESS_TOKEN_CAIXEIRO", "CALLMEBOT_APIKEY"):
        tok = os.getenv(nome, "")
        if tok and len(tok) > 4:
            texto = texto.replace(tok, "***")
    return texto
