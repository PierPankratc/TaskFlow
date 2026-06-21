class TestAuth:
    def test_login_new_user(self, client):
        response = client.post(
            "/login",
            json={"name": "alice", "password": "secret123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "access_token" in response.cookies

    def test_login_existing_user(self, client):
        client.post("/login", json={"name": "bob", "password": "pass"})
        response = client.post(
            "/login",
            json={"name": "bob", "password": "pass"},
        )
        assert response.status_code == 200
        assert "token" in response.json()

    def test_login_wrong_password(self, client):
        client.post("/login", json={"name": "charlie", "password": "correct"})
        response = client.post(
            "/login",
            json={"name": "charlie", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_access_without_token(self, client):
        response = client.get("/projectget_all")
        assert response.status_code == 500

    def test_access_with_invalid_token(self, client):
        client.cookies.set("access_token", "invalid_token")
        response = client.get("/projectget_all")
        assert response.status_code == 500

    def test_access_with_valid_cookie(self, auth_client):
        client = auth_client
        client.post("/project/add", json={"title": "Проект"})

        response = client.get("/projectget_all")
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) == 1
        assert projects[0]["title"] == "Проект"
