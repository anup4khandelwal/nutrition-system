import requests

API = "https://www.googleapis.com/youtube/v3/search"

def search_video(dish: str, api_key: str) -> dict | None:
    params = {
        "part": "snippet", "type": "video", "maxResults": 1,
        "q": f"{dish} recipe indian", "relevanceLanguage": "en",
        "videoEmbeddable": "true", "key": api_key,
    }
    r = requests.get(API, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    top = items[0]
    vid = top["id"]["videoId"]
    return {
        "videoId": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "title": top["snippet"]["title"],
        "channel": top["snippet"]["channelTitle"],
    }
