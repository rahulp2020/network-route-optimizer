def test_create_node(client):
    r = client.post("/nodes", json={"name": "ServerA"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "ServerA"}


def test_create_duplicate_node_returns_400(client):
    client.post("/nodes", json={"name": "ServerA"})
    r = client.post("/nodes", json={"name": "ServerA"})
    assert r.status_code == 400
    assert "already exists" in r.json()["error"]


def test_create_node_missing_name_returns_400(client):
    r = client.post("/nodes", json={})
    assert r.status_code == 400


def test_create_node_blank_name_returns_400(client):
    r = client.post("/nodes", json={"name": "   "})
    assert r.status_code == 400


def test_list_nodes(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})
    r = client.get("/nodes")
    assert r.status_code == 200
    assert [n["name"] for n in r.json()] == ["ServerA", "ServerB"]


def test_delete_node(client):
    client.post("/nodes", json={"name": "ServerA"})
    r = client.delete("/nodes/1")
    assert r.status_code == 204
    assert client.get("/nodes").json() == []


def test_delete_node_removes_its_edges_and_routes_through_it(client):
    for name in ("ServerA", "ServerB", "ServerC"):
        client.post("/nodes", json={"name": name})
    client.post("/edges", json={"source": "ServerA", "destination": "ServerB", "latency": 1})
    client.post("/edges", json={"source": "ServerB", "destination": "ServerC", "latency": 1})
    assert client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerC"}).status_code == 200

    assert client.delete("/nodes/2").status_code == 204

    assert client.get("/edges").json() == []
    r = client.post("/routes/shortest", json={"source": "ServerA", "destination": "ServerC"})
    assert r.status_code == 404


def test_delete_missing_node_returns_404(client):
    r = client.delete("/nodes/999")
    assert r.status_code == 404
