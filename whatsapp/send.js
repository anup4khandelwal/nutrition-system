import fs from "node:fs";
import pkg from "whatsapp-web.js";
const { Client, LocalAuth } = pkg;
import qrcode from "qrcode-terminal";
import { buildMessage } from "./message.js";

const payload = JSON.parse(fs.readFileSync("../data/today.json", "utf8"));
const text = buildMessage(payload);
const cook = process.env.COOK_WHATSAPP;
if (!cook) {
  console.error("COOK_WHATSAPP is not set. Run via ./scripts/run_daily.sh, or:");
  console.error('  cd ~/nutrition-system && set -a && source .env && set +a && cd whatsapp && node send.js');
  process.exit(1);
}
const chatId = cook.replace(/[^0-9]/g, "") + "@c.us";

function fallback() {
  const link = `https://wa.me/${cook.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(text)}`;
  fs.writeFileSync("../data/whatsapp_fallback.txt", link);
  console.error("Send failed — wrote wa.me fallback link to data/whatsapp_fallback.txt");
}

console.log("Starting WhatsApp client (launching browser, first run may take 20-40s)...");
const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  },
  // Raise from the 30s default so a busy machine doesn't time out during inject.
  protocolTimeout: 120000,
  // Give WhatsApp Web up to 90s to load before falling back.
  authTimeoutMs: 90000,
});

// Safety net: if init hasn't succeeded in 100s, write the wa.me fallback and exit.
const initGuard = setTimeout(() => {
  console.error("Initialization timed out after 100s.");
  fallback();
  try { client.destroy(); } catch (_) {}
  process.exit(1);
}, 100000);
client.on("loading_screen", (p, m) => console.log(`Loading ${p}% ${m || ""}`));
client.on("qr", (qr) => {
  console.log("\nScan this QR in WhatsApp -> Linked Devices -> Link a Device:\n");
  qrcode.generate(qr, { small: true });
});
client.on("authenticated", () => console.log("Authenticated! Sending message..."));
client.on("ready", async () => {
  clearTimeout(initGuard);
  let ok = true;
  try {
    await client.sendMessage(chatId, text);
    console.log("Sent to", chatId);
  } catch (e) {
    ok = false;
    console.error("Send error:", e.message);
    fallback();
  } finally {
    try { await client.destroy(); } catch (_) {}
    process.exit(ok ? 0 : 1);
  }
});
client.on("auth_failure", () => { clearTimeout(initGuard); fallback(); process.exit(1); });
client.initialize().catch((e) => {
  clearTimeout(initGuard);
  console.error("Init failed:", e.message);
  fallback();
  try { client.destroy(); } catch (_) {}
  process.exit(1);
});
