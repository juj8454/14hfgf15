from fastapi.testclient import TestClient
import main


def test_login_rejects_malformed_json():
    client = TestClient(main.app)
    response = client.post(
        "/api/login",
        content='{"password":',
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid json"


def test_xray_ws_config_uses_inbound_sni_and_host():
    original_inbounds = main.INBOUNDS
    original_settings = main.SETTINGS
    main.INBOUNDS = {
        "test-inbound": {
            "name": "WS inbound",
            "protocol": "vless",
            "port": 443,
            "network": "ws",
            "security": "tls",
            "domain": "example.com",
            "sni": "cdn.example.com",
            "external_domain": "",
            "external_port": 443,
            "fingerprint": "chrome",
            "reality_settings": {},
            "xhttp_settings": {},
            "ws_settings": {"path": "/ws/test", "host": "custom.example.net"},
            "grpc_settings": {},
            "created_at": "2024-01-01T00:00:00",
        }
    }
    main.SETTINGS = {"domain": "example.com"}

    try:
        config = main.generate_xray_server_config("test-inbound")
    finally:
        main.INBOUNDS = original_inbounds
        main.SETTINGS = original_settings

    stream = config["inbounds"][0]["streamSettings"]
    assert stream["tlsSettings"]["serverName"] == "cdn.example.com"
    assert stream["wsSettings"]["headers"]["Host"] == "custom.example.net"
