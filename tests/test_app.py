"""
Tests for the Mergington High School Activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results

Tests cover:
- Getting all activities
- Signing up for activities
- Removing participants
- Error handling (not found, already signed up, etc.)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert len(activities) > 0
        for activity in expected_activities:
            assert activity in activities

    def test_activity_structure(self, client):
        """Test that each activity has the correct structure."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        expected_types = {
            "description": str,
            "schedule": str,
            "max_participants": int,
            "participants": list,
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            for field in required_fields:
                assert field in details, f"Missing field '{field}' in {activity_name}"
                assert isinstance(details[field], expected_types[field])

    def test_activities_have_participants(self, client):
        """Test that activities have initial participants."""
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            assert len(details["participants"]) > 0, f"{activity_name} has no participants"


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Arrange
        email = "participanttest@mergington.edu"
        activity = "Soccer Team"

        # Act
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]

        # Assert
        assert signup_response.status_code == 200
        assert email in participants

    def test_signup_duplicate_returns_error(self, client):
        """Test that signing up for the same activity twice returns an error."""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Art Club"

        # Act - First signup
        first_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        # Act - Second signup
        second_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )

        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        email = "student@mergington.edu"
        activity = "NonexistentClub"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_with_existing_participant(self, client):
        """Test signup with an email that already exists in the activity."""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_email_validation(self, client):
        """Test that various email formats work."""
        # Arrange
        test_cases = [
            ("simple@mergington.edu", "Programming Class"),
            ("with.dot@mergington.edu", "Debate Team"),
            ("with+plus@mergington.edu", "Drama Club"),
        ]

        # Act & Assert
        for email, activity in test_cases:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant."""
        # Arrange
        email = "removeme@mergington.edu"
        activity = "Swimming Club"
        
        # Add the participant first
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_remove_participant_actually_removes(self, client):
        """Test that removal actually removes the participant."""
        # Arrange
        email = "verify_removal@mergington.edu"
        activity = "Science Club"
        
        # Add participant
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )

        # Act
        client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants",
            params={"email": email}
        )
        
        # Assert - Verify removal
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing a non-existent participant returns 404."""
        # Arrange
        email = "doesntexist@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from a non-existent activity returns 404."""
        # Arrange
        email = "student@mergington.edu"
        activity = "FakeActivity"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to the static index page."""
        # Arrange
        expected_redirect_path = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert expected_redirect_path in response.headers["location"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_activity_max_participants_not_enforced_yet(self, client):
        """Test that max_participants limit is stored but not yet enforced."""
        # Arrange
        activity = "Chess Club"
        
        # Act
        activities_response = client.get("/activities")
        max_participants = activities_response.json()[activity]["max_participants"]
        
        overflow_signup = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": f"overflow{max_participants}@mergington.edu"}
        )

        # Assert
        # Currently, there's no validation preventing signup beyond max
        assert overflow_signup.status_code == 200

    def test_case_sensitive_activity_names(self, client):
        """Test that activity names are case-sensitive."""
        # Arrange
        correct_case = "Chess Club"
        wrong_case = "chess club"
        email = "test@mergington.edu"

        # Act - Correct case
        correct_response = client.post(
            f"/activities/{correct_case.replace(' ', '%20')}/signup",
            params={"email": f"correct{email}"}
        )
        
        # Act - Wrong case
        wrong_response = client.post(
            f"/activities/{wrong_case.replace(' ', '%20')}/signup",
            params={"email": f"wrong{email}"}
        )

        # Assert
        assert correct_response.status_code == 200
        assert wrong_response.status_code == 404

    def test_multiple_participants_in_activity(self, client):
        """Test that multiple different participants can sign up."""
        # Arrange
        activity = "Debate Team"
        emails = [
            "participant1@mergington.edu",
            "participant2@mergington.edu",
            "participant3@mergington.edu",
        ]

        # Act - Sign up multiple participants
        responses = [
            client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup",
                params={"email": email}
            )
            for email in emails
        ]
        
        # Get updated activities list
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"]

        # Assert
        assert all(response.status_code == 200 for response in responses)
        for email in emails:
            assert email in participants
