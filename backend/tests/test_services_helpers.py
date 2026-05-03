import pytest

from app.services.trajet_service import _fix_mojibake, _normalize_name


@pytest.mark.unit
class TestFixMojibake:

    def test_munchen_double_encoded(self):
        assert _fix_mojibake("MÃ¼nchen") == "München"

    def test_unrecoverable_mojibake_returns_input(self):
        result = _fix_mojibake("TimiÈoara")
        assert isinstance(result, str)

    def test_already_clean_string(self):
        assert _fix_mojibake("Paris Nord") == "Paris Nord"

    def test_empty_string(self):
        assert _fix_mojibake("") == ""

    def test_none(self):
        assert _fix_mojibake(None) is None


@pytest.mark.unit
class TestNormalizeName:

    def test_lowercase(self):
        assert _normalize_name("Paris Nord") == "paris nord"

    def test_strip_accents(self):
        assert _normalize_name("München") == "munchen"

    def test_strip_whitespace(self):
        assert _normalize_name("  Paris Nord  ") == "paris nord"

    def test_mojibake_then_normalize(self):
        a = _normalize_name("MÃ¼nchen")  
        b = _normalize_name("München")   
        c = _normalize_name("Munchen")   
        assert a == b == c

    def test_empty(self):
        assert _normalize_name("") == ""

    def test_none(self):
        assert _normalize_name(None) == ""
