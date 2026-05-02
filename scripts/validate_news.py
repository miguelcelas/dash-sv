#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

MIN_DATE = date.fromisoformat("2026-01-01")
news_path = Path("data/news.json")

payload = json.loads(news_path.read_text(encoding="utf-8"))
errors = []

for idx, item in enumerate(payload.get("items", []), start=1):
    for key in ["title", "summary", "source", "url", "state", "themes", "published_at"]:
        if key not in item or item[key] in (None, "", []):
            errors.append(f"item {idx}: campo obrigatório ausente: {key}")

    if len(item.get("summary", "")) > 180:
        errors.append(f"item {idx}: resumo com mais de 180 caracteres")

    try:
        published = date.fromisoformat(item["published_at"])
        if published < MIN_DATE:
            errors.append(f"item {idx}: data anterior a 2026-01-01")
    except Exception:
        errors.append(f"item {idx}: data inválida em published_at")

if errors:
    print("ERROS ENCONTRADOS:")
    for err in errors:
        print("-", err)
    raise SystemExit(1)

print("OK: news.json válido para o recorte >= 2026-01-01")
