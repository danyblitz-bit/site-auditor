"""Core auditing logic — fetches page, checks SEO, performance, links."""
import time
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup


def audit_site(url: str, timeout: int = 15, max_links: int = 50, user_agent: str = "SiteAuditor/1.0") -> dict:
    result = {
        "url": url,
        "score": 100,
        "issues": [],
        "warnings": [],
        "info": [],
        "seo": {},
        "performance": {},
        "links": {"checked": 0, "broken": 0, "details": []},
        "response": {},
    }

    headers = {"User-Agent": user_agent}
    start = time.monotonic()
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        result["issues"].append(f"Connection failed: {e}")
        result["score"] = 0
        return result

    elapsed_ms = int((time.monotonic() - start) * 1000)
    result["response"] = {
        "status": resp.status_code,
        "time_ms": elapsed_ms,
        "size_bytes": len(resp.content),
        "final_url": resp.url,
        "server": resp.headers.get("Server", ""),
        "content_type": resp.headers.get("Content-Type", ""),
    }

    if resp.status_code >= 400:
        result["issues"].append(f"HTTP {resp.status_code}")
        result["score"] -= 30

    if elapsed_ms > 3000:
        result["warnings"].append(f"Slow response: {elapsed_ms}ms")
        result["score"] -= 10
    elif elapsed_ms > 1500:
        result["warnings"].append(f"Moderate response time: {elapsed_ms}ms")
        result["score"] -= 5

    if len(resp.content) > 5 * 1024 * 1024:
        result["warnings"].append(f"Large page: {len(resp.content) // 1024} KB")
        result["score"] -= 5

    if resp.url != url:
        result["info"].append(f"Redirected to {resp.url}")

    soup = BeautifulSoup(resp.text, "html.parser")
    _check_seo(soup, result)
    _check_links(soup, resp.url, result, timeout, max_links, user_agent)
    _check_performance(resp, soup, result)
    result["score"] = max(0, result["score"])
    return result


def _check_seo(soup: BeautifulSoup, result: dict):
    seo = {}

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""
    seo["title"] = title
    if not title:
        result["issues"].append("Missing <title> tag")
        result["score"] -= 15
    elif len(title) < 20:
        result["warnings"].append(f"Title too short ({len(title)} chars)")
        result["score"] -= 5
    elif len(title) > 60:
        result["warnings"].append(f"Title too long ({len(title)} chars)")
        result["score"] -= 3

    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
    seo["description"] = desc
    if not desc:
        result["issues"].append("Missing meta description")
        result["score"] -= 10
    elif len(desc) < 50:
        result["warnings"].append(f"Meta description too short ({len(desc)} chars)")
        result["score"] -= 3
    elif len(desc) > 160:
        result["warnings"].append(f"Meta description too long ({len(desc)} chars)")
        result["score"] -= 2

    h1s = soup.find_all("h1")
    seo["h1_count"] = len(h1s)
    if len(h1s) == 0:
        result["issues"].append("No <h1> tag found")
        result["score"] -= 10
    elif len(h1s) > 1:
        result["warnings"].append(f"Multiple <h1> tags ({len(h1s)})")
        result["score"] -= 3

    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    seo["open_graph"] = bool(og_title and og_desc and og_image)
    if not seo["open_graph"]:
        missing = []
        if not og_title:
            missing.append("og:title")
        if not og_desc:
            missing.append("og:description")
        if not og_image:
            missing.append("og:image")
        result["warnings"].append(f"Missing Open Graph tags: {', '.join(missing)}")
        result["score"] -= 3

    viewport = soup.find("meta", attrs={"name": "viewport"})
    seo["has_viewport"] = bool(viewport)
    if not viewport:
        result["warnings"].append("Missing viewport meta tag")
        result["score"] -= 5

    canonical = soup.find("link", rel="canonical")
    seo["has_canonical"] = bool(canonical)
    if not canonical:
        result["warnings"].append("No canonical link")
        result["score"] -= 2

    robots = soup.find("meta", attrs={"name": "robots"})
    seo["robots"] = robots["content"] if robots and robots.get("content") else "not set"

    imgs = soup.find_all("img")
    imgs_no_alt = [img for img in imgs if not img.get("alt")]
    seo["total_images"] = len(imgs)
    seo["images_missing_alt"] = len(imgs_no_alt)
    if imgs_no_alt:
        result["warnings"].append(f"{len(imgs_no_alt)} image(s) missing alt text")
        result["score"] -= min(10, len(imgs_no_alt) * 2)

    result["seo"] = seo


def _check_links(soup: BeautifulSoup, base_url: str, result: dict, timeout: int, max_links: int, user_agent: str):
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    seen = set()
    queue = deque()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != base_domain:
            continue
        clean = parsed._replace(fragment="").geturl()
        if clean not in seen:
            seen.add(clean)
            queue.append(clean)

    to_check = list(queue)[:max_links]
    checked = 0
    broken = 0
    details = []

    for link_url in to_check:
        try:
            r = requests.head(link_url, timeout=timeout, allow_redirects=True, headers={"User-Agent": user_agent})
            if r.status_code in (405, 501):
                r = requests.get(
                    link_url,
                    timeout=timeout,
                    allow_redirects=True,
                    headers={"User-Agent": user_agent},
                    stream=True,
                )
            status = r.status_code
        except requests.RequestException:
            status = 0

        is_broken = status == 0 or status >= 400
        checked += 1
        if is_broken:
            broken += 1
            details.append({"url": link_url, "status": status})

    result["links"] = {"checked": checked, "broken": broken, "details": details}
    if broken > 0:
        result["issues"].append(f"{broken}/{checked} broken link(s) found")
        result["score"] -= min(20, broken * 5)


def _check_performance(resp: requests.Response, soup: BeautifulSoup, result: dict):
    perf = {}
    perf["page_size_kb"] = len(resp.content) // 1024
    perf["total_images"] = len(soup.find_all("img"))
    perf["total_scripts"] = len(soup.find_all("script"))
    perf["total_stylesheets"] = len(soup.find_all("link", rel="stylesheet"))
    perf["inline_styles"] = len(soup.find_all("style"))

    has_gzip = "gzip" in resp.headers.get("Content-Encoding", "")
    perf["gzip_enabled"] = has_gzip
    if not has_gzip:
        result["warnings"].append("Gzip compression not detected")
        result["score"] -= 3

    has_cache = "Cache-Control" in resp.headers or "ETag" in resp.headers
    perf["caching"] = has_cache
    if not has_cache:
        result["warnings"].append("No cache headers detected")
        result["score"] -= 2

    perf["headers"] = {k: v for k, v in resp.headers.items() if k.lower() in (
        "server", "content-type", "content-encoding", "x-powered-by",
        "x-frame-options", "strict-transport-security", "content-security-policy",
    )}

    has_hsts = "Strict-Transport-Security" in resp.headers
    perf["hsts"] = has_hsts
    has_csp = "Content-Security-Policy" in resp.headers
    perf["csp"] = has_csp
    if not has_hsts:
        result["warnings"].append("Missing HSTS header")
        result["score"] -= 2
    if not has_csp:
        result["warnings"].append("Missing Content-Security-Policy header")
        result["score"] -= 1

    result["performance"] = perf
