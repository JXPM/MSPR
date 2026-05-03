"""
Configuration des tests dashboard
====================================
Streamlit ne peut pas être importé hors de son runtime serveur, donc
on le mocke globalement avant tout import de modules dashboard qui en
dépendent.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ajout du répertoire dashboard au PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Mock de Streamlit (suffit pour la plupart des modules)
_st_mock = MagicMock()
_st_mock.cache_data = lambda *a, **kw: (a[0] if a and callable(a[0]) else (lambda f: f))
_st_mock.session_state = {}
sys.modules.setdefault("streamlit", _st_mock)
