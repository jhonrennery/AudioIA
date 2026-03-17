const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('audioIA', {
  getConfig: () => ipcRenderer.invoke('app:get-config'),
  copyText: (text) => ipcRenderer.invoke('app:copy-text', text),
  transcribeAudio: (audioBuffer, language) => ipcRenderer.invoke('app:transcribe-audio', { audioBuffer, language }),
});
