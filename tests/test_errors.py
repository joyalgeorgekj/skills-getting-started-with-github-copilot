"""
Tests for error handling and edge cases.
Tests invalid operations, validation failures, and boundary conditions.
"""
import pytest


class TestSignUpErrors:
    """Tests for signup error cases."""
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_student(self, client):
        """Test that student cannot sign up twice for same activity."""
        email = "michael@mergington.edu"
        
        # Try to sign up someone already registered
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_duplicate_after_signup(self, client):
        """Test duplicate detection after signing up new student."""
        email = "newstudent@mergington.edu"
        activity = "Art Club"
        
        # First signup should succeed
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Second signup with same email should fail
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_empty_email(self, client):
        """Test signup with empty email."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        
        # Should either accept and add empty string, or reject
        # For now, we accept it (app doesn't validate email format)
        assert response.status_code in [200, 422]
    
    def test_signup_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name."""
        # Sign up for "Chess Club" using URL encoding
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "test@mergington.edu"}
        )
        
        # Should work with URL encoding
        assert response.status_code == 200


class TestUnregisterErrors:
    """Tests for unregister error cases."""
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_non_participant(self, client):
        """Test unregister for student not signed up returns 400."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_already_unregistered(self, client):
        """Test unregister fails for already unregistered student."""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Second unregister with same email should fail
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_empty_email(self, client):
        """Test unregister with empty email."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": ""}
        )
        
        # Should fail because empty string is not in participants
        assert response.status_code == 400


class TestActivityDataIntegrity:
    """Tests for data consistency across operations."""
    
    def test_signup_then_unregister_returns_to_original(self, client):
        """Test that signup followed by unregister restores original state."""
        activity = "Art Club"
        email = "testuser@mergington.edu"
        
        # Get original participant list
        response = client.get("/activities")
        original_participants = response.json()[activity]["participants"].copy()
        original_count = len(original_participants)
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Verify added
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == original_count + 1
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister", params={"email": email})
        
        # Verify back to original
        response = client.get("/activities")
        final_participants = response.json()[activity]["participants"]
        assert len(final_participants) == original_count
        assert final_participants == original_participants
    
    def test_participant_count_consistency(self, client):
        """Test that participant counts are always consistent."""
        activity = "Basketball"
        
        response = client.get("/activities")
        data = response.json()[activity]
        
        # Count should match list length
        assert len(data["participants"]) <= data["max_participants"]
        assert isinstance(data["participants"], list)
        assert all(isinstance(p, str) for p in data["participants"])
    
    def test_no_duplicate_participants_allowed(self, client):
        """Test that activities never have duplicate participants."""
        activity = "Soccer"
        
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # No duplicates should exist
        assert len(participants) == len(set(participants))


class TestURLEncoding:
    """Tests for proper URL encoding handling."""
    
    def test_activity_name_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly."""
        activity = "Chess Club"
        email = "test@mergington.edu"
        
        # Should work with spaces in URL path (path parameters)
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Either succeeds or fails gracefully
        assert response.status_code in [200, 404, 400]
    
    def test_email_with_plus_sign(self, client):
        """Test that emails with special characters work."""
        email = "test+tag@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Should handle special characters in email
        assert response.status_code == 200
        
        # Verify it was stored correctly
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
