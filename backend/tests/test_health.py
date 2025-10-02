def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "ok"
