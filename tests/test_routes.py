def _build_network(client):
    for name in ("ServerA", "ServerB", "ServerC", "ServerD"):
        client.post("/nodes", json={"name": name})
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 10})
    client.post("/edges", json={"source": "ServerB", "destination": "ServerD", "latency": 13.4})
    client.post("/edges", json={"source": "ServerA", "destination": "ServerD", "latency": 100})
    client.post("/edges", json={"source": "ServerB", "destination": "ServerC", "latency": 5})


def test_shortest_route_happy_path(client):
    _build_network(client)
    r = client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    assert r.status_code == 200
    assert r.json() == {"total_latency": 23.4, "path": ["ServerA", "ServerB", "ServerD"]}


def test_shortest_route_no_path_returns_404(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    r = client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerB"})
    assert r.status_code == 404
    assert r.json() == {"error": "No path exists between ServerA and ServerB"}


def test_shortest_route_unknown_node_returns_400(client):
    client.post("/nodes", json={"name": "ServerA"})
    r = client.post("/routes/shortest", json={"source": "ServerA", "destination": "Ghost"})
    assert r.status_code == 400


def test_shortest_route_recomputes_after_new_edge_added(client):
    _build_network(client)
    client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})

    client.post("/edges", json={"source": "ServerC", "destination": "ServerD", "latency": 1})

    r = client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    assert r.json() == {"total_latency": 16.0, "path": ["ServerA", "ServerB", "ServerC", "ServerD"]}


def test_route_history_is_recorded_and_filterable(client):
    _build_network(client)
    client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerD"})
    client.post("/routes/shortest", json={"source": "ServerB", "destination": "ServerC"})

    history = client.get("/routes/history").json()
    assert len(history) == 2

    filtered = client.get("/routes/history", params={"source": "ServerB"}).json()
    assert len(filtered) == 1
    assert filtered[0]["destination"] == "ServerC"

    limited = client.get("/routes/history", params={"limit": 1}).json()
    assert len(limited) == 1
