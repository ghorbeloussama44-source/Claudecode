const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { randomUUID } = require('crypto');
const { assembleFromRushes } = require('./pipeline');

const app = express();
const PORT = process.env.PORT || 3000;

const UPLOAD_ROOT = path.join(__dirname, '..', 'tmp', 'uploads');
const OUTPUT_ROOT = path.join(__dirname, '..', 'tmp', 'output');
fs.mkdirSync(UPLOAD_ROOT, { recursive: true });
fs.mkdirSync(OUTPUT_ROOT, { recursive: true });

const ALLOWED_EXT = /\.(mp4|mov|mkv|webm|avi|m4v)$/i;
const MAX_CLIPS_PER_JOB = 20;
const JOB_TTL_MS = 60 * 60 * 1000; // abandoned jobs (created but never finalized) get swept

// Clips are uploaded one at a time (see /api/jobs/:jobId/clips) instead of
// all at once, specifically so a single HTTP request never has to carry an
// entire batch of raw footage — large multipart bodies are exactly what
// trips request-size limits on proxies/tunnels sitting in front of this
// server, and splitting the upload avoids that regardless of what limit an
// intermediary enforces.
const jobs = new Map(); // jobId -> { dir, files: string[], createdAt: number }

function sweepStaleJobs() {
  const now = Date.now();
  for (const [jobId, job] of jobs.entries()) {
    if (now - job.createdAt > JOB_TTL_MS) {
      fs.rm(job.dir, { recursive: true, force: true }, () => {});
      jobs.delete(jobId);
    }
  }
}
setInterval(sweepStaleJobs, 15 * 60 * 1000).unref();

const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      const job = jobs.get(req.params.jobId);
      if (!job) return cb(new Error('JOB_NOT_FOUND'));
      cb(null, job.dir);
    },
    // Never trust the client-supplied filename for a path: give every
    // upload a generated name and keep only the (validated) extension.
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      cb(null, `${randomUUID()}${ext}`);
    },
  }),
  limits: { fileSize: 500 * 1024 * 1024, files: 1 },
  fileFilter: (req, file, cb) => {
    cb(null, ALLOWED_EXT.test(file.originalname));
  },
});

app.use(express.static(path.join(__dirname, '..', 'public')));
app.use('/output', express.static(OUTPUT_ROOT));
app.use(express.json());

app.post('/api/jobs', (req, res) => {
  const jobId = randomUUID();
  const dir = path.join(UPLOAD_ROOT, jobId);
  fs.mkdirSync(dir, { recursive: true });
  jobs.set(jobId, { dir, files: [], createdAt: Date.now() });
  res.json({ ok: true, jobId });
});

app.post('/api/jobs/:jobId/clips', (req, res) => {
  const job = jobs.get(req.params.jobId);
  if (!job) return res.status(404).json({ error: "Session d'envoi introuvable ou expirée." });
  if (job.files.length >= MAX_CLIPS_PER_JOB) {
    return res.status(400).json({ error: `Maximum ${MAX_CLIPS_PER_JOB} clips par assemblage.` });
  }

  upload.single('clip')(req, res, (err) => {
    if (err) {
      const message = err.message === 'JOB_NOT_FOUND'
        ? "Session d'envoi introuvable ou expirée."
        : err.message;
      return res.status(400).json({ error: message });
    }
    if (!req.file) {
      return res.status(400).json({
        error: 'Format de fichier non reconnu (formats acceptés : mp4, mov, mkv, webm, avi, m4v).',
      });
    }
    job.files.push(req.file.path);
    res.json({ ok: true, received: job.files.length });
  });
});

app.post('/api/jobs/:jobId/finalize', async (req, res) => {
  const jobId = req.params.jobId;
  const job = jobs.get(jobId);
  if (!job) return res.status(404).json({ error: "Session d'envoi introuvable ou expirée." });

  if (job.files.length === 0) {
    jobs.delete(jobId);
    fs.rm(job.dir, { recursive: true, force: true }, () => {});
    return res.status(400).json({ error: 'Aucun clip reçu pour cet assemblage.' });
  }

  const outputPath = path.join(OUTPUT_ROOT, `${jobId}.mp4`);
  try {
    const stats = await assembleFromRushes(job.files, outputPath);
    res.json({ ok: true, url: `/output/${jobId}.mp4`, ...stats });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Échec du traitement vidéo.' });
  } finally {
    jobs.delete(jobId);
    fs.rm(job.dir, { recursive: true, force: true }, () => {});
  }
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Erreur serveur inattendue.' });
});

app.listen(PORT, () => {
  console.log(`Video-edit landing page running on http://localhost:${PORT}`);
});
