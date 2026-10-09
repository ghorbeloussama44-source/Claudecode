// Measure text widths in headless Chromium with the real fonts and the series stylesheet.
// usage: NODE_PATH=<dir containing puppeteer-core> node measure.cjs <page dir> <out.json>
// The page (written by build.py) holds one <span data-m="key"> per string at font-size 100px;
// the result maps key -> width in px (widths scale linearly with font-size).
const path = require("path");
const fs = require("fs");
const puppeteer = require("puppeteer-core");

(async () => {
  const [dir, out] = process.argv.slice(2);
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_BIN || "/opt/pw-browsers/chromium",
    args: ["--no-sandbox", "--allow-file-access-from-files", "--disable-gpu", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920 });
  await page.goto("file://" + path.resolve(dir, "index.html"), { waitUntil: "load" });
  const res = await page.evaluate(async () => {
    const loads = [];
    for (const w of [500, 600, 700]) loads.push(document.fonts.load(`${w} 100px "Space Grotesk"`, "Aa"));
    for (const w of [600, 700, 800]) loads.push(document.fonts.load(`${w} 100px "Cairo"`, "عربي"));
    await Promise.all(loads);
    await document.fonts.ready;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const w = {};
    document.querySelectorAll("[data-m]").forEach((el) => (w[el.dataset.m] = el.getBoundingClientRect().width));
    const fonts = Array.from(document.fonts).map((f) => `${f.family} ${f.weight} ${f.status}`);
    return { w, fonts };
  });
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
