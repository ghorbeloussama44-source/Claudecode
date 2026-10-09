// Measure the layout constants that hyperframes/index.html hardcodes (no DOM measuring is
// allowed at render time). Re-run after changing "en Russie.", "Change ta vie" or the logo,
// then paste the printed values back into index.html.
//
// Usage: node scripts/measure_glyphs.js
const path = require("path");
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  ({ chromium } = require("/opt/node22/lib/node_modules/playwright"));
}

(async () => {
  const file = path.resolve(__dirname, "../hyperframes/index.html");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + file);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const r = await page.evaluate(() => {
    const c = (sel) => {
      const q = document.querySelector(sel).getBoundingClientRect();
      return { x: +(q.x + q.width / 2).toFixed(1), y: +(q.y + q.height / 2).toFixed(1) };
    };
    return {
      fontLoaded: document.fonts.check('700 100px "Space Grotesk"'),
      iris: c("#dot0"), // period of "en Russie." -> circular portal origin
      dot5: c("#dot5"), // period of "Change ta vie"
      lgdot: c("#lg-dot"), // period of "RusStudy"
    };
  });
  if (!r.fontLoaded) console.warn("WARNING: Space Grotesk not loaded, values are wrong");
  console.log(`#s1 clip-path / clipPath tween centre : ${r.iris.x}px ${r.iris.y}px`);
  console.log(`const DOT5 = { x: ${r.dot5.x}, y: ${r.dot5.y} };`);
  console.log(`const LGDOT = { x: ${r.lgdot.x}, y: ${r.lgdot.y} };`);
  await browser.close();
})();
