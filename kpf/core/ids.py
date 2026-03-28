from __future__ import annotations

import re
import uuid


_SLUG_SANITIZER = re.compile(r"[^a-z0-9]+")


def short_uuid() -> str:
    return uuid.uuid4().hex[:8]


def slugify(value: str) -> str:
    normalized = value.strip().lower()
    slug = _SLUG_SANITIZER.sub("-", normalized).strip("-")
    return slug[:48] or "niche"
