"""Icones Lucide en SVG inline.

st.html() strippe les balises <script>, donc le custom element <iconify-icon>
ne se materialise pas. On embarque les paths Lucide en dur ici.
"""

from __future__ import annotations


_LUCIDE_PATHS: dict[str, str] = {
    "train-front": (
        '<path d="M8 3.1V7a4 4 0 0 0 8 0V3.1"/>'
        '<path d="m9 15-1-1"/>'
        '<path d="m15 15 1-1"/>'
        '<path d="M9 19c-2.8 0-5-2.2-5-5v-4a8 8 0 0 1 16 0v4c0 2.8-2.2 5-5 5Z"/>'
        '<path d="m8 19-2 3"/>'
        '<path d="m16 19 2 3"/>'
    ),
    "route": (
        '<circle cx="6" cy="19" r="3"/>'
        '<path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>'
        '<circle cx="18" cy="5" r="3"/>'
    ),
    "landmark": (
        '<line x1="3" x2="21" y1="22" y2="22"/>'
        '<line x1="6" x2="6" y1="18" y2="11"/>'
        '<line x1="10" x2="10" y1="18" y2="11"/>'
        '<line x1="14" x2="14" y1="18" y2="11"/>'
        '<line x1="18" x2="18" y1="18" y2="11"/>'
        '<polygon points="12 2 20 7 4 7"/>'
    ),
    "git-fork": (
        '<circle cx="12" cy="18" r="3"/>'
        '<circle cx="6" cy="6" r="3"/>'
        '<circle cx="18" cy="6" r="3"/>'
        '<path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"/>'
        '<path d="M12 12v3"/>'
    ),
    "globe": (
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>'
        '<path d="M2 12h20"/>'
    ),
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "layers": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
        '<polyline points="2 17 12 22 22 17"/>'
        '<polyline points="2 12 12 17 22 12"/>'
    ),
    "leaf": (
        '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>'
        '<path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>'
    ),
}


def lucide(name: str, size: int = 20, color: str = "currentColor", stroke_width: float = 2) -> str:
    paths = _LUCIDE_PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
    )
