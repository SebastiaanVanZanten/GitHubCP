"""
Test suite for the Mergington High School Activity Management API.
Tests cover all three main endpoints: GET activities, POST signup, and DELETE participant.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        activities = response.json()
        
        # Should have at least the original 3 activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        
        # Should also have the 6 new activities we added
        assert "Basketball Team" in activities
        assert "Tennis Club" in activities
        assert "Art Studio" in activities
        assert "Drama Club" in activities
        assert "Robotics Club" in activities
        assert "Math Olympiad" in activities

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure with all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            
            # Verify types
            assert isinstance(details["description"], str)
            assert isinstance(details["schedule"], str)
            assert isinstance(details["max_participants"], int)
            assert isinstance(details["participants"], list)

    def test_get_activities_contains_existing_participants(self, client):
        """Test that activities show existing participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have michael@mergington.edu and daniel@mergington.edu
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Programming Class should have emma@mergington.edu and sophia@mergington.edu
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup for a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity's participants list"""
        email = "testuser@mergington.edu"
        activity = "Basketball Team"
        
        # Verify participant is not there initially
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant is now in the list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns a 400 error"""
        email = "duplicate@mergington.edu"
        activity = "Tennis%20Club"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        
        result = response2.json()
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_with_url_encoded_email(self, client):
        """Test that signup works with URL-encoded special characters in email"""
        email_encoded = "test%2Buser@mergington.edu"
        email_actual = "test+user@mergington.edu"
        
        response = client.post(f"/activities/Art%20Studio/signup?email={email_encoded}")
        assert response.status_code == 200
        
        # Verify the actual email (decoded) is in the participants list
        response = client.get("/activities")
        assert email_actual in response.json()["Art Studio"]["participants"]


class TestDeleteParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_participant_successful(self, client):
        """Test successful deletion of a participant"""
        email = "delete@mergington.edu"
        activity = "Drama%20Club"
        
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then delete
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Removed" in result["message"]

    def test_delete_removes_participant_from_list(self, client):
        """Test that delete actually removes the participant from the activity"""
        email = "removeme@mergington.edu"
        activity = "Robotics Club"
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify they're in the list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Delete
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_delete_nonexistent_activity_returns_404(self, client):
        """Test that deleting from a nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Fake%20Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_delete_nonexistent_participant_returns_404(self, client):
        """Test that deleting a nonexistent participant returns 404"""
        response = client.delete(
            "/activities/Math%20Olympiad/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Participant not found" in result["detail"]

    def test_delete_same_participant_twice_fails_on_second(self, client):
        """Test that deleting the same participant twice works first, fails second"""
        email = "onceonly@mergington.edu"
        activity = "Chess%20Club"
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # First delete should succeed
        response1 = client.delete(f"/activities/{activity}/participants/{email}")
        assert response1.status_code == 200
        
        # Second delete should fail
        response2 = client.delete(f"/activities/{activity}/participants/{email}")
        assert response2.status_code == 404

    def test_delete_existing_participant_from_chess_club(self, client):
        """Test deleting an existing participant (michael@mergington.edu from Chess Club)"""
        email = "michael%40mergington.edu"
        activity_encoded = "Chess%20Club"
        activity_name = "Chess Club"
        
        # Verify michael is in Chess Club initially
        response = client.get("/activities")
        assert "michael@mergington.edu" in response.json()[activity_name]["participants"]
        
        # Delete michael
        response = client.delete(f"/activities/{activity_encoded}/participants/{email}")
        assert response.status_code == 200
        
        # Verify michael is no longer in the list
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_signup_multiple_participants_to_same_activity(self, client):
        """Test signing up multiple different participants to the same activity"""
        activity_encoded = "Programming%20Class"
        activity_name = "Programming Class"
        emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu",
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity_encoded}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are in the list
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        for email in emails:
            assert email in participants

    def test_signup_and_delete_same_participant(self, client):
        """Test signing up and then deleting the same participant"""
        email = "roundtrip@mergington.edu"
        activity_encoded = "Gym%20Class"
        activity_name = "Gym Class"
        
        # Signup
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in list
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Delete
        response = client.delete(f"/activities/{activity_encoded}/participants/{email}")
        assert response.status_code == 200
        
        # Verify removed from list
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_signup_after_deletion(self, client):
        """Test that a participant can sign up again after being deleted"""
        email = "comeback@mergington.edu"
        activity_encoded = "Tennis%20Club"
        activity_name = "Tennis Club"
        
        # First signup
        client.post(f"/activities/{activity_encoded}/signup?email={email}")
        
        # Delete
        client.delete(f"/activities/{activity_encoded}/participants/{email}")
        
        # Second signup should work
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in list
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
