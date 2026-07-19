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

  // Every server reply goes through here so a non-JSON body (an infra-level
  // error page from a proxy/tunnel in front of this server, e.g. a plain
  // "Request Entity Too Large") never crashes the UI with a raw parse error
  // — it gets translated into something the user can actually act on.
  async function parseJsonResponse(response) {
    const text = await response.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        const looksTooLarge = response.status === 413 || /request entity too large/i.test(text);
        throw new Error(
          looksTooLarge
            ? 'Ce fichier est trop volumineux pour être envoyé. Essayez avec un clip plus court ou compressé.'
            : `Réponse inattendue du serveur (HTTP ${response.status}).`,
        );
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

  async function createJob() {
    const response = await fetch('/api/jobs', { method: 'POST' });
    const data = await parseJsonResponse(response);
    return data.jobId;
  }

  async function uploadClip(jobId, file) {
    const formData = new FormData();
    formData.append('clip', file);
    const response = await fetch(`/api/jobs/${jobId}/clips`, { method: 'POST', body: formData });
    return parseJsonResponse(response);
  }

  async function finalizeJob(jobId) {
    const response = await fetch(`/api/jobs/${jobId}/finalize`, { method: 'POST' });
    return parseJsonResponse(response);
  }

  assembleBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    hideResultAndError();
    statusSection.hidden = false;
    assembleBtn.disabled = true;

    try {
      statusText.textContent = 'Préparation de l’envoi…';
      const jobId = await createJob();

      // Uploaded one clip per request, sequentially, so no single request
      // ever has to carry the whole batch — and so progress is visible
      // instead of one long blind spinner.
      for (let i = 0; i < selectedFiles.length; i += 1) {
        const file = selectedFiles[i];
        statusText.textContent = `Envoi du clip ${i + 1}/${selectedFiles.length} (${file.name})…`;
        await uploadClip(jobId, file);
      }

      statusText.textContent = `Assemblage de ${selectedFiles.length} clip${selectedFiles.length > 1 ? 's' : ''} — coupe des silences, normalisation, équilibrage du volume…`;
      const data = await finalizeJob(jobId);

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
