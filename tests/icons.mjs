import { launch } from "./browser.mjs";
import { readFileSync } from "node:fs";

const svg = readFileSync(new URL("../app/icon.svg", import.meta.url), "utf8");
const browser = await launch();
for (const size of [192, 512]) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(`<style>*{margin:0}svg{width:${size}px;height:${size}px;display:block}</style>${svg}`);
  await page.screenshot({ path: new URL(`../app/icon-${size}.png`, import.meta.url).pathname, omitBackground: true });
}
await browser.close();
console.log("icons ok");
