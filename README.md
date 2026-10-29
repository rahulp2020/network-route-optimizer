# Network Route Optimizer

Backend service to manage network nodes and the latency between them, and find the fastest route from one node to another.

**Flow:** client calls the API → request is validated → node/edge data is saved in SQLite → for a route request, all edges are loaded into a graph and Dijkstra finds the lowest-latency path → result is saved to history and returned.

## Setup

### 1. Clone

```bash
git clone https://github.com/rahulp2020/network-route-optimizer.git
cd network-route-optimizer
```

### 2. Run with Docker

```bash
docker build -t route-optimizer .
docker run -p 8000:8000 -v route_data:/data route-optimizer
```

### Or run locally (Python 3.10+)

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Open the API docs

- Swagger UI: http://127.0.0.1:8000/docs

All endpoints can be tried directly from Swagger. The database file is created automatically on first start.

### 4. Run tests

```bash
pytest
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/nodes` | Add a node |
| GET | `/nodes` | List nodes |
| DELETE | `/nodes/{id}` | Delete a node (its edges are deleted too) |
| POST | `/edges` | Add a directed edge with latency |
| GET | `/edges` | List edges |
| DELETE | `/edges/{id}` | Delete an edge |
| POST | `/routes/shortest` | Find the lowest-latency path between two nodes |
| GET | `/routes/history` | Past route queries, filter by `source`, `destination`, `limit`, `date_from`, `date_to` |

Errors are returned as `{"error": "message"}` with 400 for bad input and 404 when something is not found or no path exists.

## Storage

SQLite, three tables:

```
nodes
  id              int        PK
  name            string     unique, not null, indexed
  created_at      datetime   UTC

edges
  id              int        PK
  source_id       int        FK -> nodes.id, on delete cascade
  destination_id  int        FK -> nodes.id, on delete cascade
  latency         float      not null, > 0
  created_at      datetime   UTC
  unique (source_id, destination_id)

route_queries
  id              int        PK
  source          string     node name, indexed
  destination     string     node name, indexed
  path            JSON       e.g. ["ServerA", "ServerB", "ServerD"]
  total_latency   float
  created_at      datetime   UTC, indexed
```

## Shortest Path calculation

1. Check both nodes exist.
2. Load all edges in one query and build an adjacency list (`node -> [(neighbor, latency)]`).
3. Run Dijkstra using a min-heap and keep track of the previous node for each step.
4. Rebuild the path from destination back to source.
5. Save to history and return `total_latency` and `path`.

## Design decisions

- **Directed edges**: `A -> B` does not mean `B -> A`. Direction is handled in one place (`build_graph`), so making edges two-way is a one-line change.
- **Same source and destination**: returns `200` with `path: ["A"]` and `total_latency: 0`.
- **Self-loop edge (`A -> A`)**: rejected with `400`, since it never helps a shortest path.
- **History**: only successful route queries are saved. Source and destination are stored as node names, not foreign keys, so history stays readable after a node is deleted.
- **Cascade delete**: deleting a node also deletes all its edges (SQLite foreign keys are turned on with `PRAGMA foreign_keys=ON`).
- **Dijkstra** because latency is always positive, which is the case it is built for. Complexity is O(E log V).
- **Graph cache**: the graph is built once and reused across route requests, and rebuilt only after an edge is added/deleted or a node is deleted.
- **Layered code**: routers (HTTP) → services (business rules) → repositories (database). Keeps each part small and easy to test.
- **Validation**: names are trimmed and can't be empty, latency must be > 0, and an edge can't point to itself. Unique names, unique edges and latency > 0 are also enforced as database constraints.
- **Logging**: each request is logged with method, path, status, response time and a request ID.