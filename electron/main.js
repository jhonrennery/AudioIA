const { app, BrowserWindow, ipcMain, clipboard } = require('electron');
const path = require('path');
const os = require('os');
const fs = require('fs');
const fsp = require('fs/promises');
const dotenv = require('dotenv');
const Groq = require('groq-sdk');

function loadEnv() {
  const envCandidates = [
    path.join(process.cwd(), '.env'),
    path.join(path.dirname(process.execPath), '.env'),
  ];

  for (const envPath of envCandidates) {
    if (fs.existsSync(envPath)) {
      dotenv.config({ path: envPath, override: false });
    }
  }
}

loadEnv();

const DEFAULT_MODEL = process.env.GROQ_TRANSCRIPTION_MODEL || 'whisper-large-v3-turbo';

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 900,
    minHeight: 640,
    backgroundColor: '#f5efe3',
    icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

function getClient() {
  if (!process.env.GROQ_API_KEY) {
    throw new Error('Defina GROQ_API_KEY no arquivo .env antes de transcrever.');
  }

  return new Groq({ apiKey: process.env.GROQ_API_KEY });
}

async function writeTempAudio(buffer) {
  const filePath = path.join(os.tmpdir(), `audioia-${Date.now()}.webm`);
  await fsp.writeFile(filePath, Buffer.from(buffer));
  return filePath;
}

async function removeTempAudio(filePath) {
  try {
    await fsp.unlink(filePath);
  } catch {
    // ignore cleanup failures
  }
}

ipcMain.handle('app:get-config', async () => {
  return {
    hasApiKey: Boolean(process.env.GROQ_API_KEY),
    model: DEFAULT_MODEL,
  };
});

ipcMain.handle('app:copy-text', async (_event, text) => {
  clipboard.writeText(text || '');
  return true;
});

ipcMain.handle('app:transcribe-audio', async (_event, payload) => {
  const audioBuffer = payload?.audioBuffer;

  if (!audioBuffer) {
    throw new Error('Nenhum audio foi recebido para transcricao.');
  }

  const tempAudioPath = await writeTempAudio(audioBuffer);

  try {
    const client = getClient();
    const transcription = await client.audio.transcriptions.create({
      file: fs.createReadStream(tempAudioPath),
      model: DEFAULT_MODEL,
      response_format: 'verbose_json',
      language: 'pt',
      temperature: 0,
    });

    return {
      text: (transcription.text || '').trim(),
      duration: transcription.duration || null,
      language: transcription.language || 'pt',
      model: DEFAULT_MODEL,
    };
  } finally {
    await removeTempAudio(tempAudioPath);
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
