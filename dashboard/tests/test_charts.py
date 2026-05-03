import pandas as pd
import plotly.graph_objects as go
import pytest

from components import charts


@pytest.mark.charts
class TestJourNuitChart:
    def test_returns_figure(self):
        fig = charts.trajets_jour_nuit_chart(jour=300, nuit=110)
        assert isinstance(fig, go.Figure)

    def test_has_donut_hole(self):
        fig = charts.trajets_jour_nuit_chart(jour=300, nuit=110)
        assert fig.data[0].hole > 0

    def test_handles_zero_values(self):
        fig = charts.trajets_jour_nuit_chart(jour=0, nuit=0)
        assert isinstance(fig, go.Figure)

    def test_labels_are_jour_nuit(self):
        fig = charts.trajets_jour_nuit_chart(jour=10, nuit=5)
        assert tuple(fig.data[0].labels) == ("Jour", "Nuit")


@pytest.mark.charts
class TestCO2Chart:
    def test_returns_figure(self):
        fig = charts.co2_chart({"train": 4.5, "avion": 185.0})
        assert isinstance(fig, go.Figure)

    def test_handles_none_values(self):
        fig = charts.co2_chart({"train": None, "avion": None})
        assert isinstance(fig, go.Figure)


@pytest.mark.charts
class TestOperateursChart:
    def test_returns_figure_with_data(self):
        fig = charts.operateurs_chart([
            {"operateur": "SNCF", "trajets": 120},
            {"operateur": "Nightjet", "trajets": 80},
            {"operateur": "DB", "trajets": 60},
        ])
        assert isinstance(fig, go.Figure)

    def test_handles_empty_list(self):
        fig = charts.operateurs_chart([])
        assert isinstance(fig, go.Figure)


@pytest.mark.charts
class TestPaysBarChart:
    def test_with_pandas_series(self):
        s = pd.Series({"FR": 50, "DE": 30, "AT": 12})
        fig = charts.pays_bar_chart(s)
        assert isinstance(fig, go.Figure)

    def test_with_empty_series(self):
        fig = charts.pays_bar_chart(pd.Series(dtype=int))
        assert isinstance(fig, go.Figure)


@pytest.mark.charts
class TestLatencyChart:
    def test_with_history(self):
        history = [
            {"ts": 1700000000, "latency_ms": 32, "ok": True},
            {"ts": 1700000010, "latency_ms": 45, "ok": True},
            {"ts": 1700000020, "latency_ms": 28, "ok": True},
        ]
        fig = charts.latency_chart(history)
        assert isinstance(fig, go.Figure)

    def test_with_empty_history(self):
        fig = charts.latency_chart([])
        assert isinstance(fig, go.Figure)
