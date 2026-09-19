from unittest.mock import patch, MagicMock
from nutrition.youtube import search_video

def _fake_response():
    m = MagicMock()
    m.json.return_value = {"items": [
        {"id": {"videoId": "abc123"},
         "snippet": {"title": "Best Rajma Recipe", "channelTitle": "Cook With Me"}}
    ]}
    m.raise_for_status.return_value = None
    return m

@patch("nutrition.youtube.requests.get")
def test_search_video_returns_top_hit(mock_get):
    mock_get.return_value = _fake_response()
    result = search_video("Rajma with brown rice", api_key="KEY")
    assert result["videoId"] == "abc123"
    assert result["url"] == "https://www.youtube.com/watch?v=abc123"
    assert "Rajma" in result["title"]

@patch("nutrition.youtube.requests.get")
def test_search_video_none_when_empty(mock_get):
    empty = MagicMock(); empty.json.return_value = {"items": []}
    empty.raise_for_status.return_value = None
    mock_get.return_value = empty
    assert search_video("Nonexistent dish", api_key="KEY") is None
