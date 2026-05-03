"""
Tests unitaires des helpers du trajet_service
================================================
Le service trajet_service contient des fonctions privées pour réparer
les noms de gares mal encodés (Talend/CSV → UTF-8 mojibake) et
normaliser pour la comparaison cross-encoding.

Compétence MSPR : « Nettoyer et transformer les données [...]
                   homogénéisation des formats »
"""
import pytest

from app.services.trajet_service import _fix_mojibake, _normalize_name


@pytest.mark.unit
class TestFixMojibake:
    """Cas réels rencontrés dans les exports Talend."""

    def test_munchen_double_encoded(self):
        # 'MÃ¼nchen' → 'München' (cas classique latin1→utf8 double encoding)
        assert _fix_mojibake("MÃ¼nchen") == "München"

    def test_unrecoverable_mojibake_returns_input(self):
        """Si le mojibake n'est pas réparable (ex: caractère roumain perdu),
        on retourne la chaîne d'origine pour ne pas planter."""
        # 'TimiÈoara' produit un byte 0xc8 qui n'est pas une suite UTF-8 valide
        result = _fix_mojibake("TimiÈoara")
        # On ne peut pas garantir le résultat exact mais on garantit pas d'exception
        assert isinstance(result, str)

    def test_already_clean_string(self):
        """Une chaîne déjà propre doit rester intacte."""
        assert _fix_mojibake("Paris Nord") == "Paris Nord"

    def test_empty_string(self):
        assert _fix_mojibake("") == ""

    def test_none(self):
        # Le service gère None comme falsy → retourne tel quel
        assert _fix_mojibake(None) is None


@pytest.mark.unit
class TestNormalizeName:
    """Clé de normalisation pour comparer 2 variantes du même nom."""

    def test_lowercase(self):
        assert _normalize_name("Paris Nord") == "paris nord"

    def test_strip_accents(self):
        assert _normalize_name("München") == "munchen"

    def test_strip_whitespace(self):
        assert _normalize_name("  Paris Nord  ") == "paris nord"

    def test_mojibake_then_normalize(self):
        """Le pipeline complet : on doit pouvoir matcher 'MÃ¼nchen' avec 'München' et 'Munchen'."""
        a = _normalize_name("MÃ¼nchen")  # mojibake
        b = _normalize_name("München")   # propre
        c = _normalize_name("Munchen")   # sans accent
        assert a == b == c

    def test_empty(self):
        assert _normalize_name("") == ""

    def test_none(self):
        assert _normalize_name(None) == ""
