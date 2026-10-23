# Experimento isolado: Caixeiro + Remotion

Não altera a produção, as vozes, o lip sync, os roteiros ou a publicação.

## O que realmente é testado
- Remotion 4 + React sobre o vídeo ORIGINAL gerado por Manim/HyperFrames.
- Reenquadramento sutil (pan, zoom, inclinação), microtremor em batidas dramáticas.
- Color grading suave, vinheta, feixes, bokeh periférico e flash controlado.
- Indicador editorial pequeno e progressão lateral; SEM caixa de legenda fixa.
- Mantém som e legendas do MP4 de origem, sem dublagem artificial.

## Prévia isolada de 32 s
O workflow `.github/workflows/testar-remotion.yml` executa na branch de experimento,
baixa somente `reels/cx033.mp4` da branch principal e gera um MP4 1080x1920
no artifact `caixeiro-remotion-preview`. Não publica nada.

Para executar localmente na raiz do experimento:

```bash
mkdir -p public
curl -fL 'https://raw.githubusercontent.com/pabloramoa-dev/caixeiro-na-corrida/main/reels/cx033.mp4' -o public/source.mp4
npm install
npm run render
```

O Remotion não cria novos gestos/lip sync a partir do MP4 já achatado.
Para animar olhos, mãos, direção do olhar e interação com passageiro em camadas
independentes, é preciso exportar os personagens como camadas do motor Manim.
Esse passo NÃO está implementado e depende de teste/avaliação.

Exemplo de teste, não peça final para publicação. Checar saída antes de mesclar.
