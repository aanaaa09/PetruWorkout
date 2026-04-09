import re
from typing import Optional

SOCIAL_PATTERNS = {
    "instagram": [
        r"instagram\.com", r"ig\.me",
        r"com\.instagram\.android", r"com\.instagram\.iphone",
    ],
    "facebook": [
        r"facebook\.com", r"fb\.com", r"m\.facebook\.com",
        r"com\.facebook\.katana", r"com\.facebook\.lite",
        r"FBAN", r"FBAV",
    ],
    "youtube": [
        r"youtube\.com", r"youtu\.be", r"m\.youtube\.com",
        r"com\.google\.android\.youtube",
    ],
    "linkedin": [
        r"linkedin\.com", r"lnkd\.in",
        r"com\.linkedin\.android",
    ],
    "tiktok": [
        r"tiktok\.com", r"tiktokv\.com",
        r"com\.zhiliaoapp\.musically", r"com\.ss\.android\.ugc\.trill",
    ],
    "twitter": [
        r"twitter\.com", r"t\.co", r"x\.com",
        r"com\.twitter\.android",
    ],
}

SEARCH_PATTERNS = [
    r"google\.", r"bing\.com", r"yahoo\.com",
    r"duckduckgo\.com", r"baidu\.com",
    r"googlequicksearchbox",
]

OWN_DOMAINS = ["petrucalistenia\.com", "petruworkout"]


def detect_source(referrer: Optional[str], user_agent: Optional[str]) -> str:
    ref = (referrer or "").lower()
    ua  = (user_agent or "").lower()

    # 1. Referrer tiene prioridad
    if ref:
        for source, patterns in SOCIAL_PATTERNS.items():
            if any(re.search(p, ref, re.IGNORECASE) for p in patterns):
                return source
        if any(re.search(p, ref) for p in SEARCH_PATTERNS):
            return "organic_search"
        if any(re.search(p, ref) for p in OWN_DOMAINS):
            return "internal"

    # 2. Fallback a user-agent (in-app browsers sin referrer)
    for source, patterns in SOCIAL_PATTERNS.items():
        if any(re.search(p, ua, re.IGNORECASE) for p in patterns):
            return source

    # 3. Sin referrer = directo
    if not ref:
        return "direct"

    return "unknown"