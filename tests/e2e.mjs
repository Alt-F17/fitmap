// End-to-end checks of the three core flows at phone and tablet sizes.
// Usage: node tests/e2e.mjs   (serves ./app on a free port)
import { spawn } from "node:child_process";
import { readFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import { launch } from "./browser.mjs";

const require = createRequire(import.meta.url);
const AXE = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const ROOT = new URL("..", import.meta.url).pathname;
const PORT = 4300 + Math.floor(Math.random() * 500);
const BASE = `http://127.0.0.1:${PORT}/`;
const SHOTS = `${ROOT}tests/screens`;
mkdirSync(SHOTS, { recursive: true });

const data = JSON.parse(readFileSync(`${ROOT}app/data.json`, "utf8"));
// Pick the phone with the most reported fits so the flow has something to show.
const counts = {};
for (const e of data.edges) counts[e.u] = (counts[e.u] || 0) + 1;
const target = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || "s25fe";
const targetDev = data.devices.find((d) => d.id === target);

const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1", "--directory", `${ROOT}app`], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 800));

let failures = 0;
const check = (ok, msg) => { console.log(`${ok ? "PASS" : "FAIL"}  ${msg}`); if (!ok) failures++; };

const browser = await launch();
try {
  for (const vp of [{ name: "phone", width: 390, height: 844 }, { name: "tablet", width: 1024, height: 768 }]) {
    console.log(`\n== ${vp.name} ${vp.width}x${vp.height} ==`);
    const ctx = await browser.newContext({ viewport: vp, locale: "fr-CA" });
    const page = await ctx.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

    const t0 = Date.now();
    await page.goto(BASE);
    await page.waitForSelector(".pills .pill");
    check(true, `home ready in ${Date.now() - t0} ms`);
    check((await page.locator("html").getAttribute("lang")) === "fr", "French by default");

    // Flow 1: customer's phone (one warm-up keystroke so we time a warm search, like a real rep)
    await page.fill("#q", "a");
    await page.fill("#q", "");
    const t1 = Date.now();
    await page.fill("#q", targetDev.a[0]);
    await page.waitForSelector("#suggest li");
    check(Date.now() - t1 < 300, `suggestions in ${Date.now() - t1} ms`);
    await page.keyboard.press("Enter");
    await page.waitForSelector(".dev-head h1");
    check((await page.textContent(".dev-head h1")).includes(targetDev.n), `opened ${targetDev.n} (query "${targetDev.a[0]}")`);
    const cards = await page.locator(".card").count();
    check(cards > 0, `${cards} fit cards shown`);
    await page.screenshot({ path: `${SHOTS}/${vp.name}-phone.png`, fullPage: false });

    // Evidence sheet
    await page.locator(".card").first().click();
    await page.waitForSelector("dialog#sheet[open] blockquote");
    const href = await page.locator("dialog#sheet .ev-src a").first().getAttribute("href");
    check(/^https:\/\//.test(href), `evidence sheet shows quote + source link (${href.slice(0, 50)}…)`);
    await page.screenshot({ path: `${SHOTS}/${vp.name}-evidence.png` });
    const axeSheet = await runAxe(page);
    check(axeSheet.length === 0, `axe (sheet open): ${axeSheet.length} serious/critical issues ${fmt(axeSheet)}`);
    await page.keyboard.press("Escape");

    // Brand switch
    await page.click('#brands [data-brand="tuff8"]');
    const tuffCards = await page.locator(".card").count();
    const tuffEmpty = await page.locator(".empty").count();
    check(tuffCards > 0 || tuffEmpty > 0, `TUFF8 filter: ${tuffCards} cards / empty-state ${tuffEmpty > 0}`);
    await page.click('#brands [data-brand="all"]');

    // Language
    await page.click("#lang");
    check((await page.locator("html").getAttribute("lang")) === "en" && (await page.textContent(".dev-head h1")).includes("Accessories"), "English toggle");
    await page.click("#lang");

    // Flow 2: accessory in hand
    await page.click('.modes a[data-mode="stock"]');
    await page.fill("#q", targetDev.a[0]);
    await page.waitForSelector("#suggest li");
    await page.keyboard.press("Enter");
    await page.waitForSelector(".dev-head h1");
    check((await page.textContent(".dev-head h1")).includes(targetDev.n), "accessory-in-hand view renders");
    check((await page.url()).includes("#/stock/"), "stock route in URL");

    // Flow 3: grid
    await page.click('.modes a[data-mode="grid"]');
    await page.waitForSelector("table.grid");
    await page.selectOption("#g-fam", targetDev.f);
    await page.waitForSelector("table.grid");
    check((await page.locator("table.grid tbody tr").count()) > 3, `grid for ${targetDev.f}`);
    await page.screenshot({ path: `${SHOTS}/${vp.name}-grid.png` });

    // Report form
    await page.goto(`${BASE}#/phone/${target}`);
    await page.click(".report");
    check(await page.isVisible("form#rep"), "report-a-fit form opens");
    await page.keyboard.press("Escape");

    // a11y on main view
    const axeMain = await runAxe(page);
    check(axeMain.length === 0, `axe (device page): ${axeMain.length} serious/critical issues ${fmt(axeMain)}`);

    // Offline: service worker caches shell + data
    await page.goto(BASE);
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.reload();
    await page.waitForTimeout(300);
    await ctx.setOffline(true);
    await page.goto(`${BASE}#/phone/${target}`);
    await page.reload();
    await page.waitForSelector(".dev-head h1", { timeout: 5000 }).catch(() => {});
    check((await page.locator(".card").count()) > 0, "works offline after first visit");
    await ctx.setOffline(false);

    check(errors.length === 0, `no console errors ${errors.slice(0, 2).join(" | ")}`);
    await ctx.close();
  }
} finally {
  await browser.close();
  server.kill();
}
console.log(failures ? `\n${failures} FAILED` : "\nALL PASSED");
process.exit(failures ? 1 : 0);

async function runAxe(page) {
  await page.addScriptTag({ content: AXE });
  const res = await page.evaluate(async () => (await window.axe.run(document, { resultTypes: ["violations"] })).violations
    .filter((v) => ["serious", "critical"].includes(v.impact)).map((v) => `${v.id}(${v.nodes.length})`));
  return res;
}
function fmt(list) { return list.length ? `[${list.join(", ")}]` : ""; }
