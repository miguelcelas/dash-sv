#!/usr/bin/env python3
"""Atualiza data/news.json a partir de feeds RSS/Atom configurados em data/sources.json."""
import json
import re
from datetime import datetime, date, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

MIN_DATE = date.fromisoformat("2026-01-01")
MAX_SUMMARY = 180

THEME_RULES = {
    "clima": ["chuva", "seca", "clima", "temperatura", "inmet", "estiagem"],
    "água": ["reservatório", "água", "adutora", "cisterna", "barragem"],
    "políticas públicas": ["programa", "governo", "edital", "decreto", "política"],
    "economia": ["crédito", "produção", "emprego", "renda", "investimento"],
    "agricultura": ["agricultura", "agro", "safra", "agroecologia", "sementes"],
}

ROOT = Path(__file__).resolve().parent.parent
sources_path = ROOT / "data" / "sources.json"
news_path = ROOT / "data" / "news.json"


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def compact_summary(text: str) -> str:
    s = " ".join(strip_html(text).split())
    return s if len(s) <= MAX_SUMMARY else s[: MAX_SUMMARY - 1].rstrip() + "…"


def detect_themes(text: str):
    low = text.lower()
    out = [theme for theme, keys in THEME_RULES.items() if any(k in low for k in keys)]
    return out or ["geral"]


def parse_date(value: str):
    if not value:
        return None
    candidates = ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]
    for fmt in candidates:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.date().isoformat()
        except ValueError:
            continue
    return None


def fetch_xml(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "semiarido-vivo-bot/1.0"})
    with urlopen(req, timeout=25) as r:
        return r.read()


def parse_feed(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    # RSS
    for it in root.findall('.//item'):
        title = (it.findtext('title') or '').strip()
        link = (it.findtext('link') or '').strip()
        desc = (it.findtext('description') or '').strip()
        pub = parse_date((it.findtext('pubDate') or '').strip())
        if title and link:
            items.append({"title": title, "url": link, "summary": compact_summary(desc), "published_at": pub})
    # Atom
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    for ent in root.findall('.//a:entry', ns):
        title = (ent.findtext('a:title', default='', namespaces=ns) or '').strip()
        link_el = ent.find('a:link', ns)
        link = (link_el.attrib.get('href', '') if link_el is not None else '').strip()
        summary = (ent.findtext('a:summary', default='', namespaces=ns) or ent.findtext('a:content', default='', namespaces=ns) or '').strip()
        pub = parse_date((ent.findtext('a:updated', default='', namespaces=ns) or ent.findtext('a:published', default='', namespaces=ns) or '').strip())
        if title and link:
            items.append({"title": title, "url": link, "summary": compact_summary(summary), "published_at": pub})
    return items


def main():
    sources = json.loads(sources_path.read_text(encoding='utf-8')).get('sources', [])
    existing = json.loads(news_path.read_text(encoding='utf-8')).get('items', []) if news_path.exists() else []
    seen = {n.get('url') for n in existing}
    out = list(existing)

    for source in sources:
        for feed_url in source.get('feeds', []):
            try:
                xml = fetch_xml(feed_url)
                entries = parse_feed(xml)
            except Exception:
                continue
            for e in entries:
                if not e.get('published_at'):
                    continue
                if date.fromisoformat(e['published_at']) < MIN_DATE:
                    continue
                if e['url'] in seen:
                    continue
                text_for_theme = f"{e['title']} {e.get('summary','')}"
                out.append({
                    "id": f"{e['published_at']}-{abs(hash(e['url'])) % 1000000:06d}",
                    "title": e['title'],
                    "summary": compact_summary(e.get('summary', '')),
                    "source": source['name'],
                    "url": e['url'],
                    "paywall": False,
                    "state": source.get('state', 'NE'),
                    "themes": detect_themes(text_for_theme),
                    "published_at": e['published_at'],
                })
                seen.add(e['url'])

    out.sort(key=lambda x: x['published_at'], reverse=True)
    news_path.write_text(json.dumps({"items": out}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK: {len(out)} notícias salvas em {news_path}")


if __name__ == '__main__':
    main()
