import requests
from typing import Optional
from urllib.parse import quote_plus
import re

# Try to import BeautifulSoup; fall back to a simple regex-based parser if not available.
try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None  # type: ignore

_DEFAULT_HEADERS = {
    "User-Agent": "IntegratedScienceBot/1.0 (+https://example.com) requests/2.x"
}


def is_science_relevant(text: str) -> bool:
    """
    Validate whether a web result is aligned with science topics.
    Rejects pop culture, politics, music, movies, books, sports, etc.
    """
    if not text:
        return False

    t = text.lower()

    forbidden_keywords = [
        # Music / entertainment
        "album", "song", "singer", "rapper", "band", "concert", "music",

        # Movies & TV
        "film", "movie", "series", "tv show", "actor", "actress", "director",

        # Politics / government
        "president", "minister", "government", "election", "politic",

        # Sports
        "football", "soccer", "basketball", "sports", "athlete",

        # Books / literature
        "novel", "book", "author", "story", "plot", "fiction",

        # History or biographies
        "born", "died", "biography", "historical"
    ]

    return not any(word in t for word in forbidden_keywords)


def web_search_answer(query: str, limit: int = 3) -> Optional[str]:
    """
    Fetch summary using DuckDuckGo Instant Answer API.
    Now rejects irrelevant non-science results.
    Returns a short text summary or None.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "skip_disambig": 1
    }

    try:
        resp = requests.get(url, params=params, timeout=5, headers=_DEFAULT_HEADERS)
        resp.raise_for_status()
        data = resp.json()

        # Primary abstract
        abstract = data.get("AbstractText", "").strip()
        if abstract and is_science_relevant(abstract):
            return abstract

        # Fallback: related topics
        related = data.get("RelatedTopics", [])
        texts = [t.get("Text", "") for t in related if t.get("Text")]
        valid = [txt for txt in texts if is_science_relevant(txt)]

        if valid:
            return " ".join(valid[:limit])

        return None

    except Exception as e:
        print(f"[web_search_answer] Error: {e}")
        return None


# ---------------------------------------------------------------------
# New: web_image_search(topic) — reliable image/diagram lookup fallback
# ---------------------------------------------------------------------
def _extract_image_from_html(html: str) -> Optional[str]:
    """
    Try to extract an image URL from HTML using BeautifulSoup when available,
    otherwise use regex fallbacks. Returns the first likely image URL or None.
    """
    if not html:
        return None

    # Prefer og:image meta tag or twitter:image
    if BeautifulSoup:
        try:
            soup = BeautifulSoup(html, "html.parser")
            for prop in ("og:image", "twitter:image", "image"):
                tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
                if tag and tag.get("content"):
                    url = tag.get("content").strip()
                    if url.startswith("//"):
                        url = "https:" + url
                    if url.startswith("http"):
                        return url

            # infobox / first image
            img = soup.find("img")
            if img and img.get("src"):
                src = img.get("src").strip()
                if src.startswith("//"):
                    src = "https:" + src
                if src.startswith("http"):
                    return src
        except Exception:
            # Fall through to regex approach if BS fails
            pass

    # Regex fallback (look for common image URL patterns)
    urls = re.findall(r'https?://\S+\.(?:png|jpg|jpeg|svg|gif)', html, flags=re.IGNORECASE)
    if urls:
        return urls[0]

    # Look for <img src="...">
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    if m:
        src = m.group(1)
        if src.startswith("//"):
            src = "https:" + src
        if src.startswith("http"):
            return src

    return None


def web_image_search(topic: str) -> Optional[str]:
    """
    Attempt to find a high-quality image/diagram URL for a topic with the following strategy:
      1) Try Wikipedia page for the topic: extract og:image or infobox image.
      2) Query Wikimedia Commons API for images matching "{topic} diagram".
      3) If steps above fail, return None.

    Returns:
      - direct image URL (http(s) link) or None

    Notes:
      - Uses short timeouts and tolerant error handling so failures don't break the app.
      - For local testing ensure 'requests' is installed and (optionally) 'beautifulsoup4'.
    """
    if not topic:
        return None

    try:
        # 1) Wikipedia page
        wiki_title = topic.strip().replace(" ", "_")
        wiki_url = f"https://en.wikipedia.org/wiki/{quote_plus(wiki_title)}"
        try:
            resp = requests.get(wiki_url, headers=_DEFAULT_HEADERS, timeout=6)
            if resp.status_code == 200 and resp.text:
                img = _extract_image_from_html(resp.text)
                if img:
                    return img
        except Exception:
            # ignore and continue to Commons
            pass

        # 2) Wikimedia Commons API: search for "{topic} diagram"
        commons_query = quote_plus(f"{topic} diagram")
        commons_api = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&generator=search&gsrsearch={commons_query}&gsrlimit=6"
            "&prop=imageinfo&iiprop=url&format=json"
        )
        try:
            resp2 = requests.get(commons_api, headers=_DEFAULT_HEADERS, timeout=6)
            resp2.raise_for_status()
            data = resp2.json()
            pages = data.get("query", {}).get("pages", {})
            # pages is a dict keyed by pageid
            for pageid, page in pages.items():
                imageinfo = page.get("imageinfo")
                if isinstance(imageinfo, list) and imageinfo:
                    url = imageinfo[0].get("url")
                    if url and url.startswith("http"):
                        return url
        except Exception:
            # ignore and return None at end
            pass

    except Exception:
        # keep silent on other unexpected errors
        pass

    return None