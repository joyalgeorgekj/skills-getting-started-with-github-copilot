"""
Tests for the API endpoints - Happy path scenarios.
Tests successful operations: listing activities, signing up, and unregistering.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Should have 9 activities
        assert len(activities) == 9
        
        # Check known activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_structure(self, client):
        """Test that activities have correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Pick any activity and verify structure
        chess = activities["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
        assert isinstance(chess["participants"], list)
    
    def test_get_activities_participant_data(self, client):
        """Test that participant data is correct."""
        response = client.get("/activities")
        activities = response.json()
        
        chess = activities["Chess Club"]
        assert len(chess["participants"]) == 2
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignUp:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity."""
        # Get initial count
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        initial_count = len(chess["participants"])
        
        # Sign up new student
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert len(chess["participants"]) == initial_count + 1
        assert "newstudent@mergington.edu" in chess["participants"]
    
    def test_signup_multiple_students(self, client):
        """Test signing up multiple different students."""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Soccer/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        soccer = response.json()["Soccer"]
        for email in emails:
            assert email in soccer["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_participant_success(self, client):
        """Test successful unregistration of an existing participant."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]
        assert "michael@mergington.edu" in result["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from activity."""
        # Get initial count
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        initial_count = len(chess["participants"])
        
        # Unregister a student
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert len(chess["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in chess["participants"]
    
    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants from same activity."""
        # Programming Class has 2 participants initially
        response = client.get("/activities")
        prog = response.json()["Programming Class"]
        initial_emails = list(prog["participants"])
        
        # Unregister both
        for email in initial_emails:
            response = client.delete(
                "/activities/Programming Class/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were removed
        response = client.get("/activities")
        prog = response.json()["Programming Class"]
        assert len(prog["participants"]) == 0
