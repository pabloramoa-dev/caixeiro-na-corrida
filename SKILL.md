---
name: "caixeiro-na-corrida"
description: Produz vídeos verticais do personagem CAIXEIRO — motorista de aplicativo de 44 anos, casado, bom ouvinte e bem-humorado, que conta do banco do motorista histórias FICCIONAIS que os passageiros viveram ou desabafaram no carro (família, futebol, reflexão, superação, amor, amizade, curiosidades, humor do dia a dia), sempre com tema novo, feitos por código em Manim + HyperFrames no motor da Nina. Use SEMPRE que o Pablo pedir episódio, vídeo, roteiro, história, foto de perfil, capa, bio ou legenda do Caixeiro, do "Caixeiro na Corrida", do "motorista de Uber/aplicativo", ou do antigo nome "Marcão"/"Marcão na Corrida" — mesmo sem citar a skill. Entrega MP4 vertical 1080x1920 de ~3 minutos com voz, lip sync, legenda karaokê e CTA no final, sempre com a legenda de publicação em texto copiável.
---

# Caixeiro na Corrida — motorista de aplicativo

**Nome atual: CAIXEIRO.** O personagem nasceu como "Marcão" (Marcos Vieira); o
nome foi trocado para Caixeiro por decisão do Pablo. Nunca usar "Marcão" em
fala, tela, legenda ou perfil. Os arquivos de código ainda se chamam
`marcao_*` — isso é só nome interno, não aparece no vídeo.

**Toda entrega de vídeo vai com a legenda de publicação em texto copiável na resposta.**

## O personagem (versão atual)

- 44 anos, ex-metalúrgico que virou motorista de aplicativo.
- **Casado com a Rosângela, fiel e apaixonado pela família.** Fala da esposa
  com carinho e bom humor. **Não é mais o "casado safado"**: nada de aceitar
  cantada, flertar ou ir a encontro. Essa fase foi abandonada por decisão do Pablo.
- Jeito: bom ouvinte, sábio de rua, coração mole, piada pronta na hora certa.
  Sabe a hora de falar e a hora de só dirigir. Gosta de futebol, de rádio e de
  gente.
- **O protagonista da história é quase sempre o passageiro.** O Caixeiro é o
  narrador e a testemunha; às vezes participa (um conselho, um gesto, uma
  desviada de rota), mas a história é de quem estava no banco de trás.
- Visual: pele morena, barba rala grisalha, bigode, costeletas brancas,
  olheiras, boné azul-marinho, polo cinza com gola, mãos no volante.
- Boné: hoje o código desenha **estrela dourada** no escudo. A foto de perfil
  (`assets/caixeiro-perfil.png`) tem a versão **"UBIR"** que o Pablo pediu
  antes. Se pedir para unificar, confirme qual versão ele quer
  (`marcao_lib.py`, bloco "escudinho do boné", ~linha 228).
- Cenário: interior de sedan visto do banco do carona. `"cenario": "dia"`
  (sol, nuvens, prédios coloridos) ou `"noite"` (prédios acesos, chuva fina).
  Terço no retrovisor, celular com mapa e rota azul, letreiro **neon UBER (rosa)
  / 99 (âmbar)** no canto direito, piscando. Alterne dia/noite entre episódios.
- Expressões disponíveis: neutra, desconfiada, chocada, ironica, triste, brava, rindo.

## Canal

- Nome: **Caixeiro na Corrida** · usuário **@caixeironacorrida**
- Bio TikTok (≤80 caracteres):
  `🚗 Motorista de app · Histórias do banco de trás` / `🎙️ Cada corrida, uma vida · Ficção`
- Marca na tela: "CAIXEIRO NA CORRIDA · BANCO DE TRÁS"; rodapé "Cada corrida,
  uma história." + "HISTÓRIA FICTÍCIA". Paleta azul-noite com âmbar.
- Abertura: "Sobe aí, que essa corrida…" · Fecho: "Cinco estrelas pra essa história."

## Tema novo em TODO episódio (regra principal)

O Pablo quer que **o Caixeiro nunca repita assunto** e que toda história seja
interessante, bonita ou curiosa. Antes de escrever qualquer roteiro:

1. **Levante o que já foi feito.** Consulte, nesta ordem: `references/temas-usados.md`;
   a pasta `episodios/`; o arquivo de memória do canal; e as conversas
   anteriores (busca por "Caixeiro"). Monte a lista de temas, tipos de
   passageiro e reviravoltas já usados.
2. **Escolha uma categoria diferente da do episódio anterior** (catálogo em
   `references/temas.md`) e, dentro dela, um tema central que ainda não
   apareceu. Se o Pablo der o tema, use o dele — mas confira se não repete
   algo já feito e avise se repetir.
3. **Varie tudo, não só o assunto:** tipo de passageiro (idade, profissão,
   sozinho/em grupo/criança/idoso), horário e cenário, tom (emocionante,
   engraçado, curioso, reflexivo) e o tipo de virada (revelação, coincidência,
   gesto, objeto esquecido, ligação, reencontro). Não repita a mesma virada
   em episódios seguidos.
4. **Ao entregar**, mostre ao Pablo a linha pronta para o histórico
   (`nº · título · categoria · passageiro · virada`) e registre-a no arquivo
   de memória do canal, já que a pasta da skill é só leitura. Quando ele
   reenviar a skill, a linha entra em `references/temas-usados.md`.

## Regras de roteiro

1. **Cada episódio tem ~3 minutos (≈420–450 palavras), história completa com
   início, meio e fim.** Nada de parte 1/parte 2. No JSON use `"avulso": true`.
2. **Conteúdo para toda a família.** Sem conteúdo sexual, sem cantada, sem
   traição do Caixeiro, sem violência gráfica. Emoção vem de gente de verdade:
   saudade, orgulho, reconciliação, coragem, gentileza, gargalhada.
3. Estrutura que funciona: gancho forte na 1ª fala → quem entrou e um detalhe
   que intriga (um objeto, uma roupa, um pedido estranho) → o passageiro
   desabafa/conta → o Caixeiro escuta e pergunta a coisa certa → **virada**
   (revelação, coincidência ou gesto) → o que ficou pro Caixeiro → moral curta
   e verdadeira → "Cinco estrelas…".
4. Detalhes concretos fazem a história parecer real: dia da semana, horário,
   clima, valor da corrida, nome do bairro, uma frase marcante do passageiro.
   Use nomes próprios inventados; não cite pessoas reais pelo nome. Futebol
   pode citar o estádio e "o time"; nomear clubes reais é permitido, mas
   alterne para não puxar sempre a mesma torcida.
5. Moral curta, sem sermão — uma frase que dá vontade de mandar pra alguém.
6. CTA de seguir **só no final** (o pipeline insere sozinho; não escreva "me segue").
7. Legenda: gancho + emoji, pergunta pros comentários ligada ao tema (ex.:
   "Qual frase do seu pai você nunca esqueceu?"), "História de ficção.",
   hashtags do tema terminando em `#caixeironacorrida`.

## Formato do episódio (JSON)

Modelo do formato e do tom atual: `episodios/ep03-cadeira-32.json`.
(`episodios/antigos/` guarda os dois primeiros, da fase "casado safado" —
servem só como referência técnica de formato, **não** de tom.)
Cada batida: `fala` (narração), `expr`, `arte` ([tipo, texto]), `destaque`
(palavras do karaokê), opcional `tela` (texto curto na tela quando a fala é
longa) e `zoom`. Tipos de arte: titulo, relogio, conversa, carimbo, coracao,
notificacao, direct, manchete, manchete_v, porta, carro, mapa, imagem, ou null.

## Como produzir

```bash
bash scripts/instalar.sh            # clona o motor da Nina e instala tudo
export HYPERFRAMES_BROWSER_PATH=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell | head -1)
export NINA_HF_WORKERS=1 NINA_MAX_DUR=200
cd /home/claude/nina-me-contou
python3 marcao/produzir_marcao.py marcao/<episodio>.json
# saída: saida/<id>/<id>.mp4  → copiar para /mnt/user-data/outputs/caixeiro-<titulo>.mp4
```

- Rode em segundo plano (`setsid ... &`) e acompanhe com `sleep 240` — um
  episódio de 3 min leva ~40 min aqui. Antes de iniciar, confira com
  `ps aux | grep produzir` se o mesmo episódio já não está renderizando.
- Use um `id` novo para cada episódio (a pasta `saida/<id>` reaproveita a voz).
- Foto de perfil: `cd motor && manim -s -qh --media_dir /tmp/cap -o perfil cena_marcao_hf.py Perfil`,
  depois recorte quadrado 1080x1080 centrado no rosto.
- Confira um quadro do meio do vídeo (`ffmpeg -ss 95 -frames:v 1`) antes de entregar.

## Limitações deste ambiente

- Voz: aqui é Kokoro `pm_alex`. Em produção (GitHub Actions) usar
  **edge-tts `pt-BR-AntonioNeural`** (`MARCAO_VOZ`).
- Fotos de banco de imagens não baixam aqui; as batidas usam ilustração vetorial.

## Repositório e automação

O canal roda sozinho em `github.com/pabloramoa-dev/caixeiro-na-corrida`:
300 roteiros (`roteiros/loteNN.txt` → `episodios/cxNNN.json` via
`motor/compilar_roteiros.py`), renderização no GitHub Actions, 3 Reels por dia
no Instagram (08h, 12h, 20h + Story às 20h) e link + legenda do TikTok no
WhatsApp a cada vídeo. Para episódios novos, continue a partir do cx325 e
confira `references/temas-usados.md` antes — nada pode repetir.
