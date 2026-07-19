const path = require('path');
const os = require('os');
const fs = require('fs');
const fsp = require('fs/promises');
const { pipeline } = require('stream/promises');
const { Readable } = require('stream');
const { randomUUID } = require('crypto');
const { put, del } = require('@vercel/blob');
const ffmpegPath = require('ffmpeg-static');
const ffprobePath = require('ffprobe-static').path;
const { assembleFromRushes } = require('../lib/pipeline');

const BLOB_HOST_SUFFIX = '.public.blob.vercel-storage.com';

function isOwnBlobUrl(url) {
  try {
    const { hostname, protocol } = new URL(url);
    return protocol === 'https:' && hostname.endsWith(BLOB_HOST_SUFFIX);
  } catch {
    return false;
  }
}

// Downloads each already-uploaded clip from Blob storage, runs the same
// silence-cut/normalize/concat/loudnorm pipeline used for local hosting
// (lib/pipeline.js), then uploads the result back to Blob storage and
// returns its URL — the response itself stays tiny JSON, well under the
// 4.5 MB Vercel Function response limit, since the video never round-trips
// through this function's own request/response bodies.
module.exports = async function handler(request) {
  if (request.method !== 'POST') {
    return Response.json({ error: 'Method not allowed' }, { status: 405 });
  }

  let clipUrls;
  try {
    ({ clipUrls } = await request.json());
  } catch {
    return Response.json({ error: 'Corps de requête JSON invalide.' }, { status: 400 });
  }

  if (!Array.isArray(clipUrls) || clipUrls.length === 0) {
    return Response.json({ error: 'Aucun clip à assembler.' }, { status: 400 });
  }
  if (clipUrls.length > 20) {
    return Response.json({ error: 'Maximum 20 clips par assemblage.' }, { status: 400 });
  }
  // Only ever fetch URLs that point at our own Blob store: without this
  // check, this endpoint would happily fetch and process any URL handed to
  // it, turning it into an open server-side-request-forgery proxy.
  if (!clipUrls.every(isOwnBlobUrl)) {
    return Response.json({ error: 'URLs de clips invalides.' }, { status: 400 });
  }

  const workdir = await fsp.mkdtemp(path.join(os.tmpdir(), 'clips-'));
  const localPaths = [];

  try {
    for (const url of clipUrls) {
      const response = await fetch(url);
      if (!response.ok || !response.body) {
        throw new Error(`Impossible de récupérer un clip uploadé (HTTP ${response.status}).`);
      }
      const ext = path.extname(new URL(url).pathname) || '.mp4';
      const localPath = path.join(workdir, `${randomUUID()}${ext}`);
      await pipeline(Readable.fromWeb(response.body), fs.createWriteStream(localPath));
      localPaths.push(localPath);
    }

    const outputPath = path.join(workdir, 'final.mp4');
    const stats = await assembleFromRushes(localPaths, outputPath, { ffmpegPath, ffprobePath });

    const blob = await put(`assembled/${randomUUID()}.mp4`, fs.createReadStream(outputPath), {
      access: 'public',
      contentType: 'video/mp4',
      multipart: true,
    });

    return Response.json({ ok: true, url: blob.url, ...stats });
  } catch (error) {
    console.error(error);
    return Response.json({ error: error.message || 'Échec du traitement vidéo.' }, { status: 500 });
  } finally {
    await fsp.rm(workdir, { recursive: true, force: true }).catch(() => {});
    try {
      await del(clipUrls);
    } catch (err) {
      console.error('Failed to delete source clips from blob storage', err);
    }
  }
};
