const recordButton = document.getElementById('recordButton');
const recordLabel = document.getElementById('recordLabel');
const statusMessage = document.getElementById('statusMessage');
const transcriptOutput = document.getElementById('transcriptOutput');
const copyButton = document.getElementById('copyButton');
const metaInfo = document.getElementById('metaInfo');
const languageSelect = document.getElementById('languageSelect');

const LANGUAGE_LABELS = {
  auto: 'Auto detectar',
  pt: 'Portugues',
  en: 'Ingles',
  es: 'Espanhol',
  fr: 'Frances',
  de: 'Alemao',
  it: 'Italiano',
};

let mediaRecorder = null;
let stream = null;
let recordedChunks = [];
let isRecording = false;

function setStatus(message) {
  statusMessage.textContent = message;
}

function setRecordingState(active) {
  isRecording = active;
  recordButton.classList.toggle('recording', active);
  recordLabel.textContent = active ? 'Gravando agora' : 'Pronto para gravar';
  recordButton.setAttribute('aria-label', active ? 'Parar gravacao' : 'Iniciar gravacao');
}

function formatDuration(seconds) {
  if (!seconds) {
    return 'duracao nao informada';
  }

  return `${seconds.toFixed(1).replace('.', ',')}s`;
}

async function loadConfig() {
  const config = await window.audioIA.getConfig();

  if (config.hasApiKey) {
    setStatus(`API pronta. Modelo de transcricao: ${config.model}. Escolha o idioma e grave.`);
  } else {
    setStatus('Defina GROQ_API_KEY no arquivo .env para habilitar a transcricao.');
  }
}

async function startRecording() {
  recordedChunks = [];
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

  mediaRecorder.addEventListener('dataavailable', (event) => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  });

  mediaRecorder.addEventListener('stop', async () => {
    const audioBlob = new Blob(recordedChunks, { type: 'audio/webm' });
    const arrayBuffer = await audioBlob.arrayBuffer();
    await sendForTranscription(arrayBuffer, languageSelect.value);
  });

  mediaRecorder.start();
  transcriptOutput.value = '';
  copyButton.disabled = true;
  metaInfo.textContent = `Gravacao em andamento em ${LANGUAGE_LABELS[languageSelect.value] || 'idioma selecionado'}...`;
  setRecordingState(true);
  setStatus('Captando audio do microfone. Clique novamente para encerrar.');
}

function stopRecording() {
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    return;
  }

  mediaRecorder.stop();

  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }

  setRecordingState(false);
  setStatus('Enviando audio para a Groq e gerando transcricao...');
  metaInfo.textContent = 'Processando...';
}

async function sendForTranscription(arrayBuffer, language) {
  try {
    const result = await window.audioIA.transcribeAudio(arrayBuffer, language);
    transcriptOutput.value = result.text || '';
    copyButton.disabled = !result.text;
    metaInfo.textContent = `Idioma: ${LANGUAGE_LABELS[result.language] || result.language || 'Auto detectar'} | Duracao: ${formatDuration(result.duration)}`;
    setStatus(result.text ? 'Transcricao concluida. Voce ja pode copiar o texto.' : 'Nenhum texto foi identificado no audio.');
  } catch (error) {
    transcriptOutput.value = '';
    copyButton.disabled = true;
    metaInfo.textContent = 'Falha ao processar a gravacao.';
    setStatus(error.message || 'Nao foi possivel transcrever o audio.');
  }
}

languageSelect.addEventListener('change', () => {
  if (!isRecording) {
    setStatus(`Idioma selecionado: ${LANGUAGE_LABELS[languageSelect.value] || languageSelect.value}.`);
  }
});

recordButton.addEventListener('click', async () => {
  try {
    if (!isRecording) {
      await startRecording();
      return;
    }

    stopRecording();
  } catch (error) {
    setRecordingState(false);
    setStatus(error.message || 'Nao foi possivel acessar o microfone.');
    metaInfo.textContent = 'Permita acesso ao microfone e tente novamente.';
  }
});

copyButton.addEventListener('click', async () => {
  if (!transcriptOutput.value) {
    return;
  }

  await window.audioIA.copyText(transcriptOutput.value);
  setStatus('Texto copiado para a area de transferencia.');
});

loadConfig().catch((error) => {
  setStatus(error.message || 'Falha ao carregar a configuracao inicial.');
});
