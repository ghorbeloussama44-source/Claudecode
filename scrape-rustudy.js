const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const SITES = [
  'https://rustudy.vercel.app/',
  'https://rustudyclaudev-2.vercel.app/',
  'https://landing-page-rustudy.vercel.app/',
  'https://rustudystudiov1.vercel.app/',
  'https://rustudystudiov2.vercel.app/',
  'https://rustudystudiov3.vercel.app/',
  'https://rustudystudiov4.vercel.app/',
  'https://rustudystudiov5.vercel.app/',
];

const OUTPUT_DIR = path.join(__dirname, 'rustudy-report');
const SCREENSHOTS_DIR = path.join(OUTPUT_DIR, 'screenshots');

function slugify(url) {
  return url.replace(/^https?:\/\//, '').replace(/[^a-z0-9]+/gi, '-').replace(/-+$/, '');
}

async function analyzeSite(browser, url) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 900 });

  const consoleErrors = [];
  let transferBytes = 0;

  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push(String(err)));
  page.on('response', async (res) => {
    const headers = res.headers();
    const len = parseInt(headers['content-length'] || '0', 10);
    if (!Number.isNaN(len)) transferBytes += len;
  });

  const result = { url };
  const start = Date.now();

  try {
    // 'load' plutôt que 'networkidle2' : certains déploiements gardent une
    // connexion réseau active en continu (analytics, polling) et ne
    // deviennent jamais "idle", ce qui ferait échouer la navigation.
    const response = await page.goto(url, { waitUntil: 'load', timeout: 45000 });
    result.loadTimeMs = Date.now() - start;
    result.httpStatus = response ? response.status() : null;

    // Laisse le temps à l'hydratation client (Next.js/React) de terminer
    // avant d'inspecter le DOM et de prendre la capture d'écran.
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const data = await page.evaluate(() => {
      const text = document.body ? document.body.innerText || '' : '';
      const images = Array.from(document.querySelectorAll('img'));
      const headings = {};
      for (let i = 1; i <= 6; i++) {
        headings[`h${i}`] = document.querySelectorAll(`h${i}`).length;
      }
      const links = Array.from(document.querySelectorAll('a[href]'));
      const internal = links.filter((a) => {
        try {
          return new URL(a.href, location.href).host === location.host;
        } catch {
          return false;
        }
      }).length;

      return {
        title: document.title || null,
        metaDescription: document.querySelector('meta[name="description"]')?.content || null,
        lang: document.documentElement.lang || null,
        hasViewportMeta: !!document.querySelector('meta[name="viewport"]'),
        ogTags: Array.from(document.querySelectorAll('meta[property^="og:"]')).map((m) => m.getAttribute('property')),
        headings,
        wordCount: text.trim().split(/\s+/).filter(Boolean).length,
        imagesCount: images.length,
        imagesWithoutAlt: images.filter((img) => !img.getAttribute('alt')).length,
        linksCount: links.length,
        internalLinksCount: internal,
        externalLinksCount: links.length - internal,
        buttonsCount: document.querySelectorAll('button, [role="button"]').length,
        formsCount: document.querySelectorAll('form').length,
      };
    });

    Object.assign(result, data);

    const metrics = await page.metrics();
    result.jsHeapUsedMB = +(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2);

    result.transferBytes = transferBytes;
    result.consoleErrors = consoleErrors;

    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    const screenshotPath = path.join(SCREENSHOTS_DIR, `${slugify(url)}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot = path.relative(OUTPUT_DIR, screenshotPath);
  } catch (err) {
    result.error = err.message;
  } finally {
    await page.close();
  }

  return result;
}

function toMarkdownTable(results) {
  const headers = [
    'Site', 'Status', 'Load (ms)', 'Title', 'Words', 'Images (no-alt)',
    'Links (int/ext)', 'Headings h1-h3', 'Console errors', 'Transfer (KB)', 'Erreur',
  ];
  const rows = results.map((r) => {
    if (r.error) {
      return [r.url, '-', '-', '-', '-', '-', '-', '-', '-', '-', r.error];
    }
    const headingsSummary = `${r.headings?.h1 ?? 0}/${r.headings?.h2 ?? 0}/${r.headings?.h3 ?? 0}`;
    return [
      r.url,
      r.httpStatus ?? '-',
      r.loadTimeMs ?? '-',
      r.title ?? '-',
      r.wordCount ?? '-',
      `${r.imagesCount ?? 0} (${r.imagesWithoutAlt ?? 0})`,
      `${r.internalLinksCount ?? 0}/${r.externalLinksCount ?? 0}`,
      headingsSummary,
      r.consoleErrors?.length ?? 0,
      r.transferBytes ? Math.round(r.transferBytes / 1024) : '-',
      '',
    ];
  });

  const line = (cols) => `| ${cols.join(' | ')} |`;
  const sep = `| ${headers.map(() => '---').join(' | ')} |`;
  return [line(headers), sep, ...rows.map(line)].join('\n');
}

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const launchArgs = ['--no-sandbox', '--disable-setuid-sandbox'];

  // Certains environnements (proxy de sortie interceptant le TLS) exigent
  // de router Chromium via ce proxy et de plafonner TLS à 1.2 : le
  // handshake TLS 1.3 de Chromium échoue systématiquement derrière ces
  // proxys (voir README de l'environnement d'exécution).
  if (process.env.HTTPS_PROXY || process.env.https_proxy) {
    const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;
    launchArgs.push(`--proxy-server=${proxyUrl}`, '--ignore-certificate-errors', '--ssl-version-max=tls1.2');
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: launchArgs,
  });

  const results = [];
  for (const url of SITES) {
    console.log(`Analyse de ${url} ...`);
    const result = await analyzeSite(browser, url);
    if (result.error) {
      console.log(`  -> échec: ${result.error}`);
    } else {
      console.log(`  -> ${result.httpStatus} en ${result.loadTimeMs}ms, ${result.wordCount} mots`);
    }
    results.push(result);
  }

  await browser.close();

  const jsonPath = path.join(OUTPUT_DIR, 'comparison.json');
  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2));

  const markdown = [
    '# Comparaison des versions RuStudy',
    '',
    `Généré le ${new Date().toISOString()}`,
    '',
    toMarkdownTable(results),
    '',
    '## Captures d\'écran',
    '',
    ...results
      .filter((r) => r.screenshot)
      .map((r) => `- [${r.url}](${r.screenshot})`),
  ].join('\n');

  const mdPath = path.join(OUTPUT_DIR, 'comparison.md');
  fs.writeFileSync(mdPath, markdown);

  console.log(`\nRapport JSON : ${jsonPath}`);
  console.log(`Rapport Markdown : ${mdPath}`);
  console.log(`Captures d'écran : ${SCREENSHOTS_DIR}`);
}

main().catch((err) => {
  console.error('Erreur fatale:', err);
  process.exitCode = 1;
});
