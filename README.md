# 🚗 Caixeiro na Corrida

Canal automático do **Caixeiro** — motorista de aplicativo que conta, do banco do motorista,
histórias de ficção que os passageiros viveram. Vídeos verticais de ~3 minutos feitos por
código (Manim + HyperFrames, motor da Nina), com voz, lip sync, legenda karaokê e CTA no final.

## Como funciona

| Etapa | Workflow | Quando |
|---|---|---|
| Mantém reservas separadas de curtos e longos | `produzir.yml` | chamado pelo workflow dos Reels |
| Publica Reel curto às 12h e longo às 20h, entrega pelo Telegram | `caixeiro-diario.yml` | 12h e 20h (Brasília); Story às 20h |
| Renova o token do Instagram | `renovar-token.yml` | toda segunda |
| Abre issue se a fila estiver baixa | `vigia-fila.yml` | todo dia |
| Compacta o histórico do Git (vídeos velhos) | `compactar-historico.yml` | domingo |
| Teste do WhatsApp | `testar-whatsapp.yml` | manual |

- **Roteiros:** `roteiros/lote01.txt … lote30.txt` → 300 episódios (`cx025`–`cx324`).
  Depois de editar um lote: `python motor/compilar_roteiros.py` (gera `episodios/*.json`).
- **Vídeos:** `reels/cxNNN.mp4` (+ capa, story e legenda). Apagados 4 dias depois de publicados.
- **Publicados:** `conteudo/publicados.json`.

## Configuração (uma vez só)

O repositório precisa ser **público** (o Instagram baixa o vídeo pelo link raw do GitHub).

### Secrets — Settings → Secrets and variables → Actions → *New repository secret*

| Nome | O que é |
|---|---|
| `IG_USER_ID_CAIXEIRO` | ID da conta profissional do Instagram do Caixeiro |
| `IG_ACCESS_TOKEN_CAIXEIRO` | Token de longa duração do Instagram (API com login do Instagram) |
| `GH_PAT` | Token do GitHub com permissão de *Secrets: write* neste repo (para a renovação automática do token) |
| `WHATSAPP_NUMERO` | Seu número com DDI, ex.: `5524999999999` |
| `CALLMEBOT_APIKEY` | Chave do CallMeBot (veja abaixo) |
| `PEXELS_API_KEY` / `PIXABAY_API_KEY` | Opcionais — fotos de banco de imagens |

**CallMeBot (WhatsApp):** adicione o número do CallMeBot nos contatos e mande a mensagem
`I allow callmebot to send me messages`. Ele responde com a sua apikey.
(Instruções atualizadas em callmebot.com → WhatsApp.) Depois rode o workflow
**Testar WhatsApp** pra conferir.

### Variables — aba *Variables*

| Nome | Valor |
|---|---|
| `PUBLICAR_ATIVO` | `false` até o primeiro teste dar certo; depois `true` |
| `GRAPH_API_VERSION` | `v22.0` (opcional) |
| `RAW_BASE_URL` | `https://raw.githubusercontent.com/pabloramoa-dev/caixeiro-na-corrida/main` (opcional) |

### Primeira vez

1. Actions → **Produzir episódios** → *Run workflow* (renderiza os 9 primeiros, ~1–2 h).
2. Actions → **Caixeiro — 12h curto / 20h longo** → *Run workflow* com `dry_run = true` — confere a prévia e o WhatsApp.
3. Tudo certo? A rotina `caixeiro-diario.yml` publica automaticamente às 12h (curto) e 20h (longo), usando as credenciais da conta. O workflow `publicar.yml` antigo é apenas manual.

## Regras do personagem

Família-friendly, tema nunca repetido (`references/temas-usados.md`), CTA só no fim
(coração + seguir), nunca o nome antigo na tela. Detalhes em `SKILL.md`.

## Visual com imagens em movimento (outubro/2026)

O motor HyperFrames agora utiliza, por padrão, ilustrações originais geradas
localmente com Pillow a cada **7 segundos**, alinhadas às falas reais. Elas
ganham zoom e deslocamento suaves (efeito Ken Burns) na área superior,
substituindo os antigos cartões que repetiam legendas. As legendas continuam
na parte inferior, preservando Caixeiro, voz masculina e lip sync.

O vídeo não chama API paga de imagens. Episódios que já incluem uma sequência
`visual_sequence` preservam suas imagens e também recebem movimento.
Use `CAIXEIRO_MOTION_IMAGES=0` para restaurar o visual anterior.
A mudança visual não publica nada por conta própria e não altera
`conteudo/publicados.json`.


## Aberturas com antecipação e micro-reenganches (outubro/2026)

A partir da versão v3, todos os roteiros que entram na renderização são tratados
por `motor/ganchos_caixeiro.py`: o início de cada história pode antecipar uma
pista real encontrada entre 30% e 65% do roteiro; uma segunda cena da história
recebe um micro-reenganche por volta da metade. Nunca são inventados fatos,
alterados nomes/desfechos ou duplicados CTAs. Histórias com abertura editorial
já adequada são preservadas. Vídeos já publicados não são republicados.

O módulo é idempotente: aplica uma versão única no compilador dos lotes e
também no renderizador, para os JSONs antigos ainda na fila. A versão de render
mudou para reavaliar somente os episódios pendentes. Consulte
`python motor/ganchos_caixeiro.py` para uma auditoria local sem renderizar.

## Cenas cinematograficas 2D — producao (29/10/2026)

Aprovado no piloto **O radio que tocou antes da surpresa**. Agora os episodios
novos usam, por padrao, `motor/cinematic_story_art.py` para criar, em CPU/Pillow,
ilustracoes cinematograficas originais com personagens, cenarios em profundidade,
objetos tematicos (radio, presente, celular, bilhete, mala, carro etc.) e textura.
As imagens acompanham a fala e recebem movimentos suaves de camera no HyperFrames,
sem mudar Caixeiro, voz, lip sync, legendas inferiores, ganchos nem publicacao.

- Estilo default: `CAIXEIRO_STORY_STYLE=cinematic_2d` (nenhuma chave ou GPU necessaria).
- Retrocesso imediato: `CAIXEIRO_STORY_STYLE=classic`.
- Ainda e possivel usar `CAIXEIRO_MOTION_IMAGES=0` para tirar imagens em movimento.
- Um roteiro pode optar por `"visual_style": "classic"`.
- Sequencias explicitamente aprovadas (`visual_sequence`) continuam prioritarias.
- A assinatura de render muda somente para os videos pendentes; ja publicados
  nao sao republicados. Nenhuma conta de rede social e acionada por esta mudanca.

O visual das ilustracoes e de **animacao de camera sobre quadros 2D**:
nao deve ser confundido com animacao de membros independente por personagem.

## Animação da mão direita e câmbio (novembro/2026)

No motor Manim (`motor/marcao_lib.py` e `motor/cena_marcao_hf.py`),
o Caixeiro mantém a mão esquerda no volante. A direita sai do volante,
desce até o câmbio desenhado no console, faz uma pausa curta e retorna.
O ombro, cotovelo e antebraço acompanham a mão, com interpolação suave.
O gesto acontece aproximadamente a cada 13,5 segundos, sem loop acelerado.
A animação integra a camada-base do HyperFrames e preserva voz, lipsync,
ilustrações, legendas e horários da publicação.

- Padrão em novos renders: `CAIXEIRO_TROCA_MARCHA=1`.
- Para voltar ao braço estático: `CAIXEIRO_TROCA_MARCHA=0`.
- A versão do render foi atualizada apenas para vídeos ainda pendentes;
  vídeos já publicados não são republicados automaticamente.
- Teste rápido: `python -m unittest tests.test_caixeiro_marcha -v`.
- Prévia isolada sem publicar: workflow `caixeiro-marcha-preview.yml`.

## Vozes e encerramento dos Reels

O Caixeiro usa Kokoro `pm_alex:0.62+pm_santa:0.38`. AntonioNeural é a reserva se a síntese local falhar.

A narração termina com um único convite de envio ligado ao assunto do vídeo.


## Experimento de retenção — 10 a 23 de novembro de 2026

- Às **12h BRT**, publicar um Reel curto de **45–75 segundos**.
- Às **20h BRT**, publicar um Reel longo completo (com Story, como antes).
- Agendamento no GitHub Actions: `0 15 * * *` e `0 23 * * *` (UTC).
- O abastecimento de estoque escolhe roteiros curtos e longos separadamente.
- O banco atual de curtos (`conteudo/curtos_teste.json`) contém **14 episódios**; para manter a publicação diária após o teste, é necessário ampliar esse banco e remover a janela limitada em `motor/formatos.py`.
