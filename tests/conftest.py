import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the original activities data for resetting between tests
ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def reset_activities():
    """Reset activities to original state before each test."""
    # Reset to original state
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield activities
    # Cleanup after test
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client(reset_activities):
    """Provide a TestClient instance with fresh activities data."""
    return TestClient(app)
