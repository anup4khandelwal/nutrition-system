from urllib.parse import parse_qs, urlparse

from nutrition.delivery import build_daily_message, build_whatsapp_link


def _payload():
    return {
        "meals": {
            "breakfast": {
                "dish": "Oats upma",
                "video": {"url": "https://youtu.be/breakfast"},
            },
            "lunch": {
                "dish": "Rajma rice",
                "video": {"url": "https://youtu.be/lunch"},
            },
            "dinner": {"dish": "Palak tofu", "video": None},
        }
    }


def test_build_daily_message_lists_all_meals_and_available_videos():
    text = build_daily_message(_payload())

    assert "*Breakfast:* Oats upma" in text
    assert "https://youtu.be/breakfast" in text
    assert "*Lunch:* Rajma rice" in text
    assert "https://youtu.be/lunch" in text
    assert "*Dinner:* Palak tofu" in text
    assert "None" not in text


def test_build_whatsapp_link_normalizes_number_and_round_trips_message():
    message = "Breakfast: poha & curd\nThank you! 🙏"
    link = build_whatsapp_link("+91 81491-10148", message)

    parsed = urlparse(link)
    assert parsed.scheme == "https"
    assert parsed.netloc == "wa.me"
    assert parsed.path == "/918149110148"
    assert parse_qs(parsed.query)["text"] == [message]
