"""
FastAPI application tests using AAA (Arrange-Act-Assert) pattern
"""
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Arrange: Prepare client
           Act: Make GET request to /activities
           Assert: Verify response contains all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                             "Basketball Team", "Tennis Club", "Art Studio",
                             "Drama Club", "Debate Team", "Science Club"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities
            assert "description" in activities[activity_name]
            assert "schedule" in activities[activity_name]
            assert "max_participants" in activities[activity_name]
            assert "participants" in activities[activity_name]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self):
        """Arrange: Prepare valid activity and email
           Act: Sign up participant
           Assert: Verify participant is added"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert f"{email} for {activity_name}" in response.json()["message"]
        
        # Verify participant was added to activities
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Cleanup: Remove the participant for other tests
        client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    def test_signup_duplicate_participant_fails(self):
        """Arrange: Get existing participant from an activity
           Act: Try to sign up same participant again
           Assert: Verify 400 error is returned"""
        # Arrange
        activity_name = "Chess Club"
        activities = client.get("/activities").json()
        existing_participant = activities[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_participant}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Arrange: Prepare invalid activity name
           Act: Try to sign up for non-existent activity
           Assert: Verify 404 error is returned"""
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_existing_participant_success(self):
        """Arrange: Add a participant, then prepare to remove
           Act: Unregister the participant
           Assert: Verify participant is removed"""
        # Arrange
        activity_name = "Tennis Club"
        email = "temp@mergington.edu"
        
        # First, sign up the participant
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert f"{email} from {activity_name}" in response.json()["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self):
        """Arrange: Prepare non-existent participant
           Act: Try to unregister them
           Assert: Verify 400 error is returned"""
        # Arrange
        activity_name = "Art Studio"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self):
        """Arrange: Prepare invalid activity name
           Act: Try to unregister from non-existent activity
           Assert: Verify 404 error is returned"""
        # Arrange
        invalid_activity = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self):
        """Arrange: Prepare client with follow_redirects=False
           Act: Make GET request to root
           Assert: Verify redirect response"""
        # Arrange & Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
