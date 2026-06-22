class TestTasks:
    def test_add_task(self, auth_client, project_id):
        response = auth_client.post(
            "/tasks/add",
            json={
                "title": "Новая задача",
                "project_id": project_id,
                "status": "new",
                "priority": "high",
                "deadline": None,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новая задача"
        assert data["status"] == "new"
        assert data["priority"] == "high"
        assert data["user_id"] == 1

    def test_add_task_duplicate(self, auth_client, project_id):
        task_data = {
            "title": "Уникальная задача",
            "project_id": project_id,
            "deadline": None,
        }
        auth_client.post("/tasks/add", json=task_data)
        response = auth_client.post("/tasks/add", json=task_data)
        assert response.status_code == 409

    def test_get_all_tasks(self, auth_client, project_id):
        for i in range(2):
            auth_client.post(
                "/tasks/add",
                json={"title": f"Задача {i}", "project_id": project_id, "deadline": None},
            )

        response = auth_client.get("/tasks/get_all")
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) == 2

    def test_get_task_by_id(self, auth_client, task_id):
        response = auth_client.get(f"/tasks/task/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["id"] == task_id
        assert data["task"]["title"] == "Тестовая задача"
        assert "subtasks" in data
        assert "summary" in data

    def test_get_task_not_found(self, auth_client):
        response = auth_client.get("/tasks/task/999")
        assert response.status_code == 404

    def test_delete_task_without_confirm(self, auth_client, task_id):
        response = auth_client.delete(f"/tasks/del/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"confirm": "подтвердите удаление"}

    def test_delete_task_with_confirm(self, auth_client, task_id):
        response = auth_client.delete(f"/tasks/del/{task_id}?confirm=true")
        assert response.status_code == 200
        data = response.json()
        assert data["del_task_id"] == task_id
        assert data["status"] == "deleted"

        get_response = auth_client.get(f"/tasks/task/{task_id}")
        assert get_response.status_code == 404
