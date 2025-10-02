def test_cors_headers_present(client):
    # Simple request should include ACAO for allowed origin via CORS middleware
    r = client.get("/api/v1/health", headers={"Origin": "http://example.com"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://example.com"
