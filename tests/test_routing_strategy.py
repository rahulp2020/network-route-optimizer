from app.services.routing_strategy import DijkstraStrategy


def test_dijkstra_finds_lowest_latency_path():
    graph = {
        "A": [("B", 10), ("D", 100)],
        "B": [("D", 13.4), ("C", 5)],
        "C": [("D", 1)],
    }
    result = DijkstraStrategy().find_path(graph, "A", "D")
    assert result is not None
    assert result.total_latency == 16.0
    assert result.path == ["A", "B", "C", "D"]


def test_dijkstra_returns_none_when_no_path_exists():
    graph = {"A": [("B", 1)], "C": [("D", 1)]}
    assert DijkstraStrategy().find_path(graph, "A", "D") is None


def test_dijkstra_same_source_and_destination():
    result = DijkstraStrategy().find_path({}, "A", "A")
    assert result is not None
    assert result.total_latency == 0.0
    assert result.path == ["A"]


def test_dijkstra_unknown_source_returns_none():
    assert DijkstraStrategy().find_path({}, "A", "B") is None
