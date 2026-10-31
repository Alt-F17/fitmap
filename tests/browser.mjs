// Shared launcher: reuse the Chromium already cached on this machine.
import { chromium } from "playwright";
import { existsSync } from "node:fs";
import { homedir } from "node:os";

const CACHED = `${homedir()}/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome`;
export const launch = () => chromium.launch(existsSync(CACHED) ? { executablePath: CACHED } : {});
