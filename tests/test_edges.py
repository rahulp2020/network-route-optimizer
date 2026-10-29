def _make_nodes(client, *names):
    for name in names:
        client.post("/nodes", json={"name": name})


def test_create_edge(client):
    _make_nodes(client, "ServerA", "ServerB")
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 12.5})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}


def test_create_edge_missing_node_returns_400(client):
    _make_nodes(client, "ServerA")
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})
    assert r.status_code == 400
    assert "ServerB" in r.json()["error"]


def test_create_duplicate_edge_returns_400(client):
    _make_nodes(client, "ServerA", "ServerB")
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 2})
    assert r.status_code == 400


def test_create_edge_non_positive_latency_returns_400(client):
    _make_nodes(client, "ServerA", "ServerB")
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 0})
    assert r.status_code == 400


def test_create_self_loop_edge_returns_400(client):
    _make_nodes(client, "ServerA")
    r = client.post("/edges", json={"source": "ServerA", "destination": "ServerA", "latency": 1})
    assert r.status_code == 400


def test_list_and_delete_edge(client):
    _make_nodes(client, "ServerA", "ServerB")
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})
    assert len(client.get("/edges").json()) == 1

    r = client.delete("/edges/1")
    assert r.status_code == 204
    assert client.get("/edges").json() == []


def test_delete_missing_edge_returns_404(client):
    r = client.delete("/edges/999")
    assert r.status_code == 404
