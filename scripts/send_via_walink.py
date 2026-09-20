import json
import os
import shutil
import subprocess

from nutrition.delivery import build_daily_message, build_whatsapp_link


def open_link(link: str) -> None:
    termux_open = shutil.which("termux-open-url")
    if termux_open:
        subprocess.run([termux_open, link, "com.whatsapp.w4b"], check=True)
        return

    mac_open = shutil.which("open")
    if mac_open:
        subprocess.run([mac_open, link], check=True)
        return

    raise RuntimeError("no supported URL opener found")


def main() -> None:
    with open("data/today.json") as file:
        payload = json.load(file)

    message = build_daily_message(payload)
    link = build_whatsapp_link(os.environ["COOK_WHATSAPP"], message)
    with open("data/whatsapp_link.txt", "w") as file:
        file.write(link)

    print("Opening WhatsApp Business with a prefilled message; tap Send to deliver it.")
    open_link(link)


if __name__ == "__main__":
    main()
