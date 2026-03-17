# AudioIA

Aplicativo desktop simples para transcricao de audio com a API da Groq.

O fluxo agora foi pensado para o seu caso de uso:

- um botao central de microfone;
- clique uma vez para gravar;
- clique novamente para parar;
- o audio e enviado para a Groq;
- o texto volta pronto para copiar e colar.

O projeto usa Electron para ja nascer preparado para empacotamento em `.exe` no Windows.

## Stack usada

- Electron para interface desktop;
- captura de audio com `MediaRecorder`;
- `groq-sdk` para transcricao;
- `electron-builder` para gerar instalador e versao portatil do Windows.

## Configuracao

Crie um arquivo `.env` na raiz com base em `.env.example`:

```bash
GROQ_API_KEY=sua-chave-aqui
GROQ_TRANSCRIPTION_MODEL=whisper-large-v3-turbo
```

## Rodar em desenvolvimento

```bash
npm install
npm start
```

## Como usar

1. Abra o app.
2. Clique no microfone para iniciar a gravacao.
3. Clique de novo para encerrar.
4. Aguarde a transcricao.
5. Use o botao `Copiar texto`.

## Gerar `.exe` para Windows

O projeto ja esta configurado para gerar:

- instalador `NSIS`;
- versao portatil;
- arquitetura `x64`;
- arquitetura `ia32`.
- icone proprio em `assets/icon.ico`.

Comando:

```bash
npm run dist:win
```

Os arquivos saem em `release/`.

## Observacao importante sobre build Windows

Se voce gerar o `.exe` a partir do Linux, normalmente vai precisar de dependencias extras de cross-build, como `wine`.
O caminho mais estavel e rodar `npm install` e `npm run dist:win` em uma maquina Windows para produzir os executaveis finais.

## Estrutura principal

- `electron/main.js`: processo principal, integracao com Groq e clipboard;
- `electron/preload.js`: ponte segura entre Electron e interface;
- `electron/renderer/index.html`: tela principal;
- `electron/renderer/renderer.js`: gravacao, envio e copia do texto;
- `electron/renderer/styles.css`: visual da interface;
- `assets/icon.ico`: icone do app e do instalador Windows.
