import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test that GET /activities returns status 200 and includes activities data."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity."""
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]


def test_signup_duplicate():
    """Test that duplicate signup is rejected."""
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    # Second signup should fail
    response = client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_remove_participant_success():
    """Test successful removal of a participant."""
    # First sign up
    client.post("/activities/Gym Class/signup?email=remove@example.com")
    # Then remove
    response = client.delete("/activities/Gym Class/signup?email=remove@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Removed remove@example.com from Gym Class" in data["message"]


def test_remove_participant_not_found():
    """Test removal of a participant not signed up."""
    response = client.delete("/activities/Art Club/signup?email=notsignedup@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]


def test_activity_not_found():
    """Test that non-existent activity returns 404."""
    response = client.post("/activities/NonExistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test that GET / redirects to /static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"