from urllib.parse import quote

MEAL_ORDER = ("breakfast", "lunch", "dinner")


def build_daily_message(payload: dict) -> str:
    lines = ["🍲 *Today's meals & recipe videos*", ""]
    for meal in MEAL_ORDER:
        details = payload["meals"][meal]
        lines.append(f"*{meal.capitalize()}:* {details['dish']}")
        video = details.get("video")
        if video and video.get("url"):
            lines.append(f"▶️ {video['url']}")
        lines.append("")
    lines.append("Please prepare as per the videos. Thank you! 🙏")
    return "\n".join(lines)


def build_whatsapp_link(phone_number: str, message: str) -> str:
    normalized = "".join(char for char in phone_number if char.isdigit())
    if not normalized:
        raise ValueError("phone number must contain digits")
    return f"https://wa.me/{normalized}?text={quote(message)}"
