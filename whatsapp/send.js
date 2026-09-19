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

const client = new Client({ authStrategy: new LocalAuth() });
client.on("qr", (qr) => qrcode.generate(qr, { small: true }));
client.on("ready", async () => {
  try {
    await client.sendMessage(chatId, text);
    console.log("Sent to", chatId);
  } catch (e) {
    fallback();
  } finally {
    await client.destroy();
    process.exit(0);
  }
});
client.on("auth_failure", () => { fallback(); process.exit(1); });
client.initialize();
