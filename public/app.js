// Pinned to the same @vercel/blob version installed server-side (package.json)
// so the client upload wire protocol matches what /api/blob-upload expects.
import { upload } from 'https://esm.sh/@vercel/blob@2.6.1/client';

(() => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileList = document.getElementById('file-list');
  const assembleBtn = document.getElementById('assemble-btn');
  const statusSection = document.getElementById('status-section');
  const statusText = document.getElementById('status-text');
  const resultSection = document.getElementById('result-section');
  const resultVideo = document.getElementById('result-video');
  const resultStats = document.getElementById('result-stats');
  const downloadLink = document.getElementById('download-link');
  const errorSection = document.getElementById('error-section');
  const errorText = document.getElementById('error-text');

  let selectedFiles = [];

  function formatSize(bytes) {
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} Ko`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  }

  function formatDuration(seconds) {
    const s = Math.round(seconds);
    const m = Math.floor(s / 60);
    const rem = s % 60;
    return `${m}m${String(rem).padStart(2, '0')}s`;
  }

  // Every reply from our own /api/finalize goes through here so a non-JSON
  // body (an infra-level error page, e.g. a gateway timeout) never crashes
  // the UI with a raw parse error — it becomes something the user can act on.
  async function parseJsonResponse(response) {
    const text = await response.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(`Réponse inattendue du serveur (HTTP ${response.status}).`);
      }
    }
    if (!response.ok || (data && data.ok === false)) {
      throw new Error((data && data.error) || `Erreur HTTP ${response.status}`);
    }
    return data;
  }

  function renderFileList() {
    fileList.innerHTML = '';
    if (selectedFiles.length === 0) {
      fileList.hidden = true;
      assembleBtn.disabled = true;
      return;
    }
    fileList.hidden = false;
    assembleBtn.disabled = false;
    selectedFiles.forEach((file) => {
      const li = document.createElement('li');
      const name = document.createElement('span');
      name.textContent = file.name;
      const size = document.createElement('span');
      size.className = 'file-size';
      size.textContent = formatSize(file.size);
      li.append(name, size);
      fileList.appendChild(li);
    });
  }

  function setFiles(fileListLike) {
    selectedFiles = Array.from(fileListLike);
    renderFileList();
    hideResultAndError();
  }

  function hideResultAndError() {
    resultSection.hidden = true;
    errorSection.hidden = true;
  }

  fileInput.addEventListener('change', () => setFiles(fileInput.files));

  ['dragenter', 'dragover'].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      setFiles(e.dataTransfer.files);
    }
  });

  async function uploadClipToBlob(file, onProgress) {
    // Goes straight from the browser to Vercel Blob storage — a Vercel
    // Function's own request body is capped at 4.5 MB, well under most video
    // clips, so the file bytes never pass through our server at all here.
    const result = await upload(file.name, file, {
      access: 'public',
      handleUploadUrl: '/api/blob-upload',
      multipart: true,
      onUploadProgress: onProgress,
    });
    return result.url;
  }

  async function finalize(clipUrls) {
    const response = await fetch('/api/finalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clipUrls }),
    });
    return parseJsonResponse(response);
  }

  assembleBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    hideResultAndError();
    statusSection.hidden = false;
    assembleBtn.disabled = true;

    try {
      const clipUrls = [];
      for (let i = 0; i < selectedFiles.length; i += 1) {
        const file = selectedFiles[i];
        statusText.textContent = `Envoi du clip ${i + 1}/${selectedFiles.length} (${file.name})…`;
        const url = await uploadClipToBlob(file, (progress) => {
          statusText.textContent = `Envoi du clip ${i + 1}/${selectedFiles.length} (${file.name}) — ${Math.round(progress.percentage)}%…`;
        });
        clipUrls.push(url);
      }

      statusText.textContent = `Assemblage de ${selectedFiles.length} clip${selectedFiles.length > 1 ? 's' : ''} — coupe des silences, normalisation, équilibrage du volume…`;
      const data = await finalize(clipUrls);

      resultVideo.src = data.url;
      downloadLink.href = data.url;
      resultStats.textContent =
        `${data.clips} clip${data.clips > 1 ? 's' : ''} → ${data.keptSegments} segment${data.keptSegments > 1 ? 's' : ''} conservé${data.keptSegments > 1 ? 's' : ''} · `
        + `${formatDuration(data.finalSeconds)} au montage final `
        + `(${formatDuration(data.droppedSeconds)} de silence retiré).`;
      resultSection.hidden = false;
    } catch (err) {
      errorText.textContent = err.message || 'Une erreur est survenue pendant le traitement.';
      errorSection.hidden = false;
    } finally {
      statusSection.hidden = true;
      assembleBtn.disabled = false;
    }
  });
})();
