class TestSubtasks:
    def test_add_subtask(self, auth_client, task_id):
        response = auth_client.post(
            "/subtasks/add",
            json={
                "title": "Новая подзадача",
                "task_id": task_id,
                "status": "new",
                "priority": "high",
                "deadline": None,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новая подзадача"
        assert data["status"] == "new"
        assert data["priority"] == "high"
        assert data["user_id"] == 1

    def test_add_subtask_duplicate(self, auth_client, task_id):
        subtask_data = {
            "title": "Уникальная подзадача",
            "task_id": task_id,
            "deadline": None,
        }
        auth_client.post("/subtasks/add", json=subtask_data)
        response = auth_client.post("/subtasks/add", json=subtask_data)
        assert response.status_code == 409

    def test_get_all_subtasks(self, auth_client, task_id):
        for i in range(2):
            auth_client.post(
                "/subtasks/add",
                json={"title": f"Подзадача {i}", "task_id": task_id, "deadline": None},
            )

        response = auth_client.get("/subtasks/get_all")
        assert response.status_code == 200
        subtasks = response.json()
        assert isinstance(subtasks, list)
        assert len(subtasks) == 2

    def test_get_task_with_subtasks(self, auth_client, task_id, subtask_id):
        auth_client.post(
            "/subtasks/add",
            json={"title": "Вторая подзадача", "task_id": task_id, "deadline": None},
        )

        response = auth_client.get(f"/tasks/task/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_subtasks"] == 2

    def test_delete_subtask_without_confirm(self, auth_client, subtask_id):
        response = auth_client.delete(f"/subtasks/del/{subtask_id}")
        assert response.status_code == 200
        assert response.json() == {"confirm": "подтвердите удаление"}

    def test_delete_subtask_with_confirm(self, auth_client, task_id, subtask_id):
        response = auth_client.delete(f"/subtasks/del/{subtask_id}?confirm=true")
        assert response.status_code == 200
        data = response.json()
        assert data["del_subtask_id"] == subtask_id
        assert data["status"] == "deleted"

        get_response = auth_client.get(f"/tasks/task/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["summary"]["total_subtasks"] == 0
