import pytest

from components.icons import lucide


@pytest.mark.unit
class TestLucide:
    def test_returns_svg_string(self):
        result = lucide("train")
        assert isinstance(result, str)
        assert "<svg" in result
        assert "</svg>" in result

    def test_default_size(self):
        result = lucide("train")
        assert 'width="20"' in result
        assert 'height="20"' in result

    def test_custom_size(self):
        result = lucide("train", size=32)
        assert 'width="32"' in result
        assert 'height="32"' in result

    def test_custom_color(self):
        result = lucide("train", color="#ff0000")
        assert "#ff0000" in result

    def test_unknown_icon_falls_back_gracefully(self):
        result = lucide("nonexistent_icon_xyz")
        assert isinstance(result, str)
