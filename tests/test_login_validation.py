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
