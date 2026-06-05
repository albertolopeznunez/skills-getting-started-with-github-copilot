# Backend Tests

This directory contains comprehensive tests for the Mergington High School Activities API.

## Testing Pattern: AAA (Arrange-Act-Assert)

All tests follow the **AAA (Arrange-Act-Assert)** pattern for clear, maintainable test structure:

- **Arrange**: Set up test data, fixtures, and preconditions
- **Act**: Execute the code being tested
- **Assert**: Verify the results

### Example

```python
def test_signup_adds_participant(self, client):
    """Test that signup actually adds the participant to the activity."""
    # Arrange - Set up test data
    email = "participanttest@mergington.edu"
    activity = "Soccer Team"

    # Act - Execute the code being tested
    signup_response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup",
        params={"email": email}
    )
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity]["participants"]

    # Assert - Verify the results
    assert signup_response.status_code == 200
    assert email in participants
```

This pattern makes tests:
- **Easy to read**: Clear intent and flow
- **Easy to maintain**: Each section has a specific purpose
- **Easy to debug**: Failures point to specific stages

## Running the Tests

### Run all tests:
```bash
pytest tests/
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run a specific test class:
```bash
pytest tests/test_app.py::TestGetActivities -v
```

### Run a specific test:
```bash
pytest tests/test_app.py::TestSignUpForActivity::test_signup_successful -v
```

## Test Coverage

The test suite includes 17 tests organized into 5 test classes:

### TestGetActivities
- Verify all activities are returned
- Validate activity structure (description, schedule, max_participants, participants)
- Confirm activities have initial participants

### TestSignUpForActivity  
- Successful signup for an activity
- Verify participant is added to activity list
- Prevent duplicate signups (same email/activity)
- Handle non-existent activities (404)
- Reject already registered participants
- Support various email formats

### TestRemoveParticipant
- Successfully remove a participant
- Verify participant is actually removed from the list
- Handle non-existent participants (404)
- Handle non-existent activities (404)

### TestRootEndpoint
- Verify root endpoint redirects to `/static/index.html`

### TestEdgeCases
- Document current behavior around max_participants (not enforced)
- Verify activity names are case-sensitive
- Test multiple participants in same activity

## Requirements

The tests require the following dependencies (already in `requirements.txt`):
- `pytest` - Testing framework
- `pytest-asyncio` - AsyncIO support for pytest
- `httpx` - HTTP client for testing (comes with FastAPI TestClient)

Install with:
```bash
pip install -r requirements.txt
```
