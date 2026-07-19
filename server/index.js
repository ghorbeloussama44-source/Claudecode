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

const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      const jobDir = path.join(UPLOAD_ROOT, req.jobId);
      fs.mkdirSync(jobDir, { recursive: true });
      cb(null, jobDir);
    },
    // Never trust the client-supplied filename for a path: give every
    // upload a generated name and keep only the (validated) extension.
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      cb(null, `${randomUUID()}${ext}`);
    },
  }),
  limits: { fileSize: 500 * 1024 * 1024, files: 20 },
  fileFilter: (req, file, cb) => {
    cb(null, ALLOWED_EXT.test(file.originalname));
  },
});

app.use(express.static(path.join(__dirname, '..', 'public')));
app.use('/output', express.static(OUTPUT_ROOT));

app.post(
  '/api/assemble',
  (req, res, next) => {
    req.jobId = randomUUID();
    next();
  },
  (req, res, next) => {
    upload.array('clips', 20)(req, res, (err) => {
      if (err) return res.status(400).json({ error: err.message });
      next();
    });
  },
  async (req, res) => {
    const jobId = req.jobId;
    const jobDir = path.join(UPLOAD_ROOT, jobId);

    if (!req.files || req.files.length === 0) {
      fs.rm(jobDir, { recursive: true, force: true }, () => {});
      return res.status(400).json({
        error: 'Aucun fichier vidéo valide reçu (formats acceptés : mp4, mov, mkv, webm, avi, m4v).',
      });
    }

    const outputPath = path.join(OUTPUT_ROOT, `${jobId}.mp4`);
    try {
      const inputPaths = req.files.map((f) => f.path);
      const stats = await assembleFromRushes(inputPaths, outputPath);
      res.json({ ok: true, url: `/output/${jobId}.mp4`, ...stats });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message || 'Échec du traitement vidéo.' });
    } finally {
      fs.rm(jobDir, { recursive: true, force: true }, () => {});
    }
  },
);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Erreur serveur inattendue.' });
});

app.listen(PORT, () => {
  console.log(`Video-edit landing page running on http://localhost:${PORT}`);
});
