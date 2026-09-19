import assert from "node:assert";
import { buildMessage } from "./message.js";

const payload = {
  meals: {
    breakfast: { dish: "Vegetable oats upma", video: { url: "https://youtu.be/abc", title: "Oats Upma" } },
    lunch: { dish: "Rajma", video: { url: "https://youtu.be/def", title: "Rajma" } },
    dinner: { dish: "Palak paneer", video: null }
  }
};
const msg = buildMessage(payload);
assert.ok(msg.includes("Vegetable oats upma"));
assert.ok(msg.includes("https://youtu.be/abc"));
assert.ok(msg.includes("Palak paneer"));
console.log("OK");
