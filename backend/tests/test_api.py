"""API endpoint tests using TestClient."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /api/v1/health endpoint."""

    def test_health_check(self, client):
        """GET /api/v1/health returns healthy status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data


class TestSessionsAliasRoutes:
    """Tests for /api/v1/sessions alias routes."""

    def test_list_sessions_via_alias(self, client):
        """GET /api/v1/sessions returns session list."""
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        # Should return a list
        data = response.json()
        assert isinstance(data, list)

    def test_create_session_via_alias(self, client):
        """POST /api/v1/sessions creates a new session."""
        response = client.post("/api/v1/sessions", json={
            "title": "Test Session",
            "model_profile": "anthropic",
            "permission_mode": "moderate"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session"
        assert data["status"] == "active"


class TestTasksAliasRoutes:
    """Tests for /api/v1/tasks alias routes."""

    def test_list_tasks_via_alias(self, client):
        """GET /api/v1/tasks returns task list."""
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data

    def test_create_task_via_alias(self, client):
        """POST /api/v1/tasks creates a new task."""
        response = client.post("/api/v1/tasks", json={
            "title": "Test Task",
            "description": "Test description",
            "priority": "high"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"

    def test_update_task_via_alias(self, client):
        """PATCH /api/v1/tasks/{id} updates a task."""
        # Create a task first
        create_response = client.post("/api/v1/tasks", json={
            "title": "Task to Update"
        })
        task_id = create_response.json()["id"]

        # Update it
        response = client.patch(f"/api/v1/tasks/{task_id}", json={
            "status": "completed"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_delete_task_via_alias(self, client):
        """DELETE /api/v1/tasks/{id} deletes a task."""
        # Create a task first
        create_response = client.post("/api/v1/tasks", json={
            "title": "Task to Delete"
        })
        task_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404


class TestChatEndpoint:
    """Tests for /api/v1/sessions/{id}/chat endpoint."""

    def test_chat_requires_session(self, client):
        """POST /api/v1/sessions/{id}/chat returns 404 for non-existent session."""
        response = client.post(
            "/api/v1/sessions/non-existent-session/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 404

    def test_chat_with_existing_session(self, client):
        """POST /api/v1/sessions/{id}/chat sends message and gets SSE response."""
        # Create a session first
        session_response = client.post("/api/v1/sessions", json={
            "title": "Chat Test Session"
        })
        session_id = session_response.json()["id"]

        # Send a chat message - check it returns 200 and correct content-type
        chat_response = client.post(
            f"/api/v1/sessions/{session_id}/chat",
            json={"message": "Hello"}
        )
        assert chat_response.status_code == 200
        assert "text/event-stream" in chat_response.headers.get("content-type", "")

    def test_chat_sse_has_non_empty_text_delta(self, client):
        """POST /api/v1/sessions/{id}/chat returns SSE with non-empty text_delta content."""
        session_response = client.post("/api/v1/sessions", json={
            "title": "SSE Content Test"
        })
        session_id = session_response.json()["id"]

        chat_response = client.post(
            f"/api/v1/sessions/{session_id}/chat",
            json={"message": "你好"}
        )
        assert chat_response.status_code == 200

        body = chat_response.text
        # Parse SSE events and collect text_delta content
        text_deltas = []
        for line in body.split("\n"):
            if line.startswith("data: "):
                import json
                try:
                    data = json.loads(line[6:])
                    if "content" in data:
                        text_deltas.append(data["content"])
                except json.JSONDecodeError:
                    pass

        # There should be at least one non-empty text_delta
        non_empty = [c for c in text_deltas if c]
        assert len(non_empty) > 0, f"Expected non-empty text_delta, got: {text_deltas}"
        # Full joined content should be non-empty
        assert "".join(text_deltas).strip() != "", "Assistant response text should not be empty"


class TestCapabilitiesEndpoint:
    """Tests for /api/v1/capabilities endpoint."""

    def test_list_capabilities(self, client):
        """GET /api/v1/capabilities returns capability list."""
        response = client.get("/api/v1/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)