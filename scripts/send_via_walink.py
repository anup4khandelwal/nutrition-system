import json, urllib.parse, os, subprocess

payload = json.load(open('data/today.json'))
meals = payload['meals']
lines = ["🍲 *Today's meals & recipe videos*", '']
for meal in ['breakfast', 'lunch', 'dinner']:
    m = meals[meal]
    label = meal.capitalize()
    lines.append(f'*{label}:* {m["dish"]}')
    if m.get('video') and m['video'].get('url'):
        lines.append(f"▶️ {m['video']['url']}")
    lines.append('')
lines.append('Please prepare as per the videos. Thank you! 🙏')
text = '\n'.join(lines)
cook = os.environ['COOK_WHATSAPP'].replace('+', '').replace(' ', '')
link = f'https://wa.me/{cook}?text={urllib.parse.quote(text)}'
open('data/whatsapp_link.txt', 'w').write(link)
print('Opening WhatsApp link in browser - tap Send to deliver message')
subprocess.run(['open', link])
