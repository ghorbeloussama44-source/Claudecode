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

  assembleBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    hideResultAndError();
    statusSection.hidden = false;
    statusText.textContent = `Traitement de ${selectedFiles.length} clip${selectedFiles.length > 1 ? 's' : ''} — coupe des silences, normalisation, assemblage, équilibrage du volume…`;
    assembleBtn.disabled = true;

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append('clips', file));

    try {
      const response = await fetch('/api/assemble', { method: 'POST', body: formData });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Échec du traitement.");
      }

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
