export function buildMessage(payload) {
  const lines = ["🍲 *Today's meals & recipe videos*", ""];
  for (const meal of ["breakfast", "lunch", "dinner"]) {
    const m = payload.meals[meal];
    if (!m) continue;
    const label = meal.charAt(0).toUpperCase() + meal.slice(1);
    lines.push(`*${label}:* ${m.dish}`);
    if (m.video && m.video.url) lines.push(`▶️ ${m.video.url}`);
    lines.push("");
  }
  lines.push("Please prepare as per the videos. Thank you! 🙏");
  return lines.join("\n");
}
