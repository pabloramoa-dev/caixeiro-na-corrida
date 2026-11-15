# Pesquisa editorial — vídeos virais e Corrida de 1 Minuto

Data da pesquisa: **11 de novembro de 2026**. Objetivo: abastecer a série diária das 12h com humor familiar original. Esta é uma análise **de formatos narrativos** e não uma autorização para copiar vídeo, voz, personagem, piada, montagem, música ou fala de terceiros.

## Referências públicas consultadas

| Referência | Sinal observado na fonte | Elemento de formato a aprender — não copiar |
|---|---|---|
| [Renata de Deus — encenação de uma distração cotidiana](https://tvsaobernardo.com/motorista-de-aplicativo-de-sao-bernardo-viraliza-ao-reproduzir-video-em-que-esquece-passageiro-no-carro/) | Reportagem de 8/8/2026 informa mais de 2 milhões de visualizações e 70 mil curtidas | Situação humana reconhecível + pequena falha engraçada + reação espontânea |
| [João Gazaniga — diálogo surpreendente no carro](https://www.conexaotvweb.com.br/noticia/video-motorista-de-aplicativo-finge-nao-falar-portugues-para-fugir-de-desabafo-mas-e-surpreendido-por-passageira) | Notícia de 26/8/2026 descreve viralização de uma conversa bem-humorada | Virada no diálogo: expectativa contradita sem maldade |
| [Herick Gamarra — humor de corridas](https://primeirapagina.com.br/comportamento/na-lingua-do-pp-e-com-motorista-de-app-e-seus-passageiros-malucos/) | Matéria de 2025 relata repercussão com milhões de visualizações | Perrengues pequenos + objetos reconhecíveis, sem humilhar passageiro |
| [Humor de passageiro com reação exagerada](https://shorti.ai/en/v/tiktok_7700023261870034207) | Indexador aponta cerca de 2,7 milhões de visualizações e vídeo de 23 s | Legenda situacional no começo, expressão imediata, resolução rápida |
| [Esquete em carro com objeto/personagem inesperado](https://darkugc.com/video/ig-DcrweShN9YE) | Painel informa 4,7 milhões de visualizações e 26 s, publicado em 31/8/2026 | Objeto estranho como gancho e conflito absurdo em ambiente conhecido |
| [Contraste entre personalidade e aparência do veículo](https://contilnetnoticias.com.br/noticia/jovem-que-odeia-chamar-atencao-pega-moto-de-app-mais-chamativa-de-rio-branco/) | Notícia de 29/6/2026 relata mais de 759 mil visualizações | Contraste visual e incongruência que se entendem rapidamente |
| [Guizin Santos — esquete de humor em Uber](https://socialcounts.org/youtube-video-analytics/JS-C6GU-9sk/growth) | Agregador registra cerca de 693 mil visualizações do vídeo de 2/11/2026 | Humor situacional de carro e títulos em forma de pergunta |
| [Porta dos Fundos — COMO É VOCÊ NO UBER?](https://www.submundos.com/servicos/youtube/portadosfundos/v/fd8bd5to1e0) | Índice registra Short publicado em 23/9/2026 com aprox. 177 mil visualizações | Tipos de comportamento reconhecíveis e contexto imediato |
| [Mãe motorista de aplicativo e filha — conversa inesperada](https://www.metropoles.com/vida-e-estilo/motorista-de-aplicativo-mae-leva-filha-para-corridas-e-menina-rouba-a-cena) | Notícia de 10/11/2026 descreve repercussão em vídeo com humor familiar | Falas naturais, química familiar, desfecho positivo |

**Observação:** números dos agregadores e reportagens são fotografias temporais de suas respectivas fontes, não métricas auditadas em tempo real. Os exemplos não comprovam causalidade nem garantem viralização.

## Orientação de produção original

- **Nunca** reutilizar mídia, áudio, imagem, legenda, trecho de roteiro, fala característica ou personagem de outro criador. Links acima são apenas pesquisa editorial, não insumos para render.
- Todos os roteiros em `conteudo/corridas_1min.json` são ficção, com aviso explícito nas legendas.
- Estrutura recomendada: 0–2 s um objeto/pedido que cause curiosidade; 3–20 s contexto em duas frases; 20–42 s inconveniente ou reação; 42–60 s virada + punchline; ao final um único CTA contextual "Manda pra quem...".
- Alternar os tipos: passageiros idosos, jovens, pais, crianças acompanhadas, profissionais e vizinhos; variar objetos, cenários, brincadeiras e tipo de desfecho. Evitar provocar ou humilhar passageiros e evitar riscos reais no trânsito.
- Preservar Caixeiro, voz Kokoro, produção HyperFrames e formato vertical do canal. A série cômica não substitui os episódios longos das 20h.
- Não usar o enquadramento de notícias ou eventos reais para afirmar que um caso fictício aconteceu.

## Estoque e programação

- **30 roteiros existentes** (`humor-001` a `humor-030`) mais **60 roteiros novos** (`humor-031` a `humor-090`).
- **90 histórias no banco**, total potencial de 90 publicações diárias — mais de dois meses. A fila começa em `cx500` e termina em `cx589`; roteiros são criados de modo incremental, não todos de uma vez.
- A pré-produção roda às 6h BRT pelo workflow `.github/workflows/caixeiro-preparar-1min.yml`. A publicação ocorre às 12h BRT pelo workflow `.github/workflows/caixeiro-diario.yml`. O longo continua às 20h.
- `motor/corridas_1min.py` valida chaves, títulos, falas (seis batidas), CTA e contagem de palavras. Não reutilizar ID publicado.
- Verificar em cada revisão semanal o número de causos não publicados; ampliar antes de ficar abaixo de 7. As 90 histórias são estoque de **roteiro**, não 90 vídeos já renderizados.

## Aprender com os resultados

Avaliar por período (7 e 14 dias) as métricas disponíveis para cada Reel: tempo médio assistido, retenção em %, compartilhamentos por alcance, visitas ao perfil e novos seguidores. Repetir os **formatos** de melhores resultados, jamais o mesmo roteiro. Documentar as métricas e a data antes de sugerir mudanças de edição.

## Direitos e ética

Não foram baixados, espelhados, enviados nem redistribuídos vídeos de terceiros. Nenhum roteiro atribui histórias fictícias às pessoas reais citadas nas fontes.
