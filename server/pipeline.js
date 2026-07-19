const { spawn } = require('child_process');
const fs = require('fs/promises');
const path = require('path');
const os = require('os');

const DEFAULTS = {
  resolution: '1920x1080',
  fps: 30,
  audioRate: 48000,
  silenceNoise: '-30dB',
  silenceMinDuration: 0.6,
  // Seconds of a detected silence kept at each edge before cutting the middle
  // out, so the cut doesn't land right on the first/last syllable.
  silencePadding: 0.15,
  // Segments shorter than this after cutting are dropped rather than kept as
  // a jarring sub-second clip.
  minKeepSegment: 0.3,
  loudnorm: { I: -16, TP: -1.5, LRA: 11 },
};

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args);
    let stderr = '';
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('error', reject);
    proc.on('close', (code) => {
      if (code === 0) resolve(stderr);
      else reject(new Error(`${cmd} ${args[0] || ''} exited with code ${code}: ${stderr.slice(-1500)}`));
    });
  });
}

function runCapture(cmd, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args);
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('error', reject);
    proc.on('close', (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(`${cmd} exited with code ${code}: ${stderr.slice(-1500)}`));
    });
  });
}

async function probeDuration(file) {
  const out = await runCapture('ffprobe', [
    '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1',
    file,
  ]);
  const duration = parseFloat(out.trim());
  if (!Number.isFinite(duration)) throw new Error(`Impossible de lire la durée de ${path.basename(file)}`);
  return duration;
}

// Runs ffmpeg's silencedetect filter and parses silence spans from stderr.
// ffmpeg exits non-zero-ish behavior varies by version when writing to -f null,
// but silencedetect always logs to stderr regardless of exit code, so we read
// it directly rather than relying on `run`'s success check.
async function detectSilences(file, { noise, minDuration }) {
  let stderr = '';
  await new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', [
      '-i', file,
      '-af', `silencedetect=noise=${noise}:d=${minDuration}`,
      '-f', 'null', '-',
    ]);
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('error', reject);
    proc.on('close', () => resolve());
  });

  const starts = [...stderr.matchAll(/silence_start:\s*([\d.]+)/g)].map((m) => parseFloat(m[1]));
  const endMatches = [...stderr.matchAll(/silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)/g)];

  const silences = [];
  for (let i = 0; i < starts.length && i < endMatches.length; i += 1) {
    silences.push({ start: starts[i], end: parseFloat(endMatches[i][1]) });
  }
  return silences;
}

// Turns silence spans into the complementary "keep" spans, padding each
// silence so the cut lands inside the dead air rather than on real content.
function computeKeepSegments(duration, silences, { silencePadding, minKeepSegment }) {
  const cuts = silences
    .map((s) => ({ start: s.start + silencePadding, end: s.end - silencePadding }))
    .filter((c) => c.end > c.start);

  const keep = [];
  let cursor = 0;
  for (const cut of cuts) {
    if (cut.start > cursor) keep.push({ start: cursor, end: cut.start });
    cursor = Math.max(cursor, cut.end);
  }
  if (duration - cursor > 0) keep.push({ start: cursor, end: duration });

  return keep.filter((seg) => seg.end - seg.start >= minKeepSegment);
}

async function normalizeSegment(file, start, end, outPath, { resolution, fps, audioRate }) {
  const [w, h] = resolution.split('x');
  const vf = `scale=${w}:${h}:force_original_aspect_ratio=decrease,pad=${w}:${h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${fps}`;
  await run('ffmpeg', [
    '-y', '-i', file,
    '-ss', String(start), '-t', String(end - start),
    '-vf', vf,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
    '-ar', String(audioRate), '-c:a', 'aac',
    outPath,
  ]);
}

async function concatSegments(segmentPaths, listPath, outPath) {
  const listContent = segmentPaths.map((p) => `file '${p.replace(/'/g, "'\\''")}'`).join('\n');
  await fs.writeFile(listPath, listContent, 'utf8');
  await run('ffmpeg', ['-y', '-f', 'concat', '-safe', '0', '-i', listPath, '-c', 'copy', outPath]);
}

async function applyLoudnorm(inPath, outPath, cfg) {
  const af = `loudnorm=I=${cfg.I}:TP=${cfg.TP}:LRA=${cfg.LRA}`;
  // Explicit -map: default stream selection can silently drop streams when
  // more than one is present, so pin video + audio rather than trust it.
  await run('ffmpeg', ['-y', '-i', inPath, '-map', '0:v', '-map', '0:a', '-af', af, '-c:v', 'copy', outPath]);
}

/**
 * Turns a list of raw footage files into one assembled, silence-trimmed,
 * loudness-normalized video. Clips are processed in the order given and
 * concatenated in that order.
 */
async function assembleFromRushes(inputPaths, outputPath, overrides = {}) {
  const opts = { ...DEFAULTS, ...overrides };
  const workdir = await fs.mkdtemp(path.join(os.tmpdir(), 'video-edit-'));
  const stats = { clips: inputPaths.length, keptSegments: 0, totalSourceSeconds: 0 };

  try {
    const normalizedParts = [];
    let segmentIndex = 0;

    for (const file of inputPaths) {
      const duration = await probeDuration(file);
      stats.totalSourceSeconds += duration;

      const silences = await detectSilences(file, {
        noise: opts.silenceNoise,
        minDuration: opts.silenceMinDuration,
      });
      const keepSegments = computeKeepSegments(duration, silences, opts);

      for (const seg of keepSegments) {
        const outSeg = path.join(workdir, `seg_${String(segmentIndex).padStart(4, '0')}.mp4`);
        await normalizeSegment(file, seg.start, seg.end, outSeg, opts);
        normalizedParts.push(outSeg);
        segmentIndex += 1;
        stats.keptSegments += 1;
      }
    }

    if (normalizedParts.length === 0) {
      throw new Error(
        "Aucun passage exploitable n'a été trouvé : tout a été détecté comme silence. "
        + 'Vérifiez que les fichiers contiennent bien du son.',
      );
    }

    const concatenated = path.join(workdir, 'concatenated.mp4');
    const listPath = path.join(workdir, 'concat_list.txt');
    await concatSegments(normalizedParts, listPath, concatenated);
    await applyLoudnorm(concatenated, outputPath, opts.loudnorm);

    stats.finalSeconds = await probeDuration(outputPath);
    stats.droppedSeconds = Math.max(0, stats.totalSourceSeconds - stats.finalSeconds);

    return stats;
  } finally {
    await fs.rm(workdir, { recursive: true, force: true });
  }
}

module.exports = { assembleFromRushes, detectSilences, computeKeepSegments, probeDuration };
