class TestProjects:
    def test_add_project(self, auth_client):
        response = auth_client.post(
            "/project/add",
            json={"title": "Новый проект", "status": "in_progress", "priority": "high"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "Новый проект"
        assert data["status"] == "in_progress"
        assert data["user_id"] == 1
        assert "id" in data

    def test_add_project_duplicate(self, auth_client):
        auth_client.post("/project/add", json={"title": "Дубликат"})
        response = auth_client.post("/project/add", json={"title": "Дубликат"})
        assert response.status_code == 200
        data = response.json()
        assert "Error" in data
        assert data["title"] == "Дубликат"

    def test_get_all_projects(self, auth_client):
        for i in range(3):
            auth_client.post(
                "/project/add",
                json={"title": f"Проект {i}"},
            )

        response = auth_client.get("/projectget_all")
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) == 3

    def test_get_project_by_id(self, auth_client, project_id):
        response = auth_client.get(f"/project/three/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["project"]["id"] == project_id
        assert data["project"]["title"] == "Тестовый проект"
        assert "tasks" in data
        assert "subtasks" in data
        assert "summary" in data

    def test_get_project_not_found(self, auth_client):
        response = auth_client.get("/project/three/999")
        assert response.status_code == 404

    def test_delete_project_without_confirm(self, auth_client, project_id):
        response = auth_client.delete(f"/project/del/{project_id}")
        assert response.status_code == 200
        assert response.json() == {"confirm": "подтвердите удаление"}

    def test_delete_project_with_confirm(self, auth_client, project_id):
        response = auth_client.delete(f"/project/del/{project_id}?confirm=true")
        assert response.status_code == 200
        data = response.json()
        assert data["del_project_id"] == project_id
        assert data["status"] == "deleted"

        get_response = auth_client.get(f"/project/three/{project_id}")
        assert get_response.status_code == 404
