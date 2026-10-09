// Screenshot static HTML pages with headless Chromium (real fonts).
// usage: NODE_PATH=<dir containing puppeteer-core> node shoot.cjs <jobs.json>
// jobs.json: [{ "page": "/abs/path.html", "out": "/abs/path.png", "w": 1080, "h": 1080 }, ...]
const fs = require("fs");
const puppeteer = require("puppeteer-core");

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_BIN || "/opt/pw-browsers/chromium",
    args: ["--no-sandbox", "--allow-file-access-from-files", "--disable-gpu", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();
  for (const j of jobs) {
    await page.setViewport({ width: j.w, height: j.h, deviceScaleFactor: 1 });
    await page.goto("file://" + j.page, { waitUntil: "load" });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    });
    await page.screenshot({ path: j.out, clip: { x: 0, y: 0, width: j.w, height: j.h } });
    console.log(j.out);
  }
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
