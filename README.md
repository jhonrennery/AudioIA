# AudioIA

Ferramenta inicial para:

- transcrever audio em texto;
- reescrever a fala com mais clareza;
- traduzir o resultado para outro idioma;
- opcionalmente gerar um novo audio traduzido.
- modo ao vivo para processar automaticamente cada nova gravacao do microfone.

## Como funciona

O prototipo usa:

- API da OpenAI para transcricao e reescrita quando `OPENAI_API_KEY` estiver definida;
- `deep-translator` como fallback para traducao de texto;
- `gTTS` para gerar o audio traduzido.

Sem `OPENAI_API_KEY`, a interface abre normalmente, mas a transcricao nao roda.

## Instalar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configurar

```bash
export OPENAI_API_KEY="sua-chave"
export OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_AUDIO_MODEL="whisper-1"
```

Ou copie os valores de `.env.example` para seu gerenciador de ambiente favorito.

## Executar

```bash
python main.py
```

Abra o endereco local mostrado pelo Gradio no navegador.

## Fluxo do app

1. Envie ou grave um audio.
2. Escolha o idioma de origem.
3. Escolha como a fala sera reescrita.
4. Escolha o idioma de destino.
5. Gere o texto traduzido e, se quiser, um novo audio.

## Modo ao vivo

Quando `Modo ao vivo` estiver ativo, o app processa automaticamente cada nova gravacao feita no microfone. Isso acelera o fluxo de uso e deixa a experiencia mais proxima de traducao em tempo real, embora ainda funcione por blocos de audio.

## Docker

Build da imagem:

```bash
docker build -t audioia .
docker run --rm -p 7860:7860 -e OPENAI_API_KEY="$OPENAI_API_KEY" audioia
```

Ou com Compose:

```bash
docker compose up --build
```

Depois abra `http://127.0.0.1:7860`.

## Proximos passos recomendados

- salvar historico de sessoes;
- adicionar selecao de voz para TTS;
- suportar traducao em tempo real;
- trocar `gTTS` por um TTS com vozes mais naturais.
