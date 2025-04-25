import random  # Import the random module

import pandas as pd
from fastapi.testclient import TestClient

# Assuming your FastAPI app instance is named 'app' in 'main.py'
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Korea GeoVariable FastAPI server is running."
    }


def test_border_endpoints():
    """Test a randomly selected border calculation endpoint."""
    # Define the list of endpoints inside the function
    endpoints = [
        "/border/river/",
        "/border/emission/",
        "/border/car_registration/",
        "/border/landuse_area/",
        "/border/coastline_distance/",
        "/border/ndvi/",
        "/border/airport_distance/",
        "/border/mdl_distance/",
        "/border/port_distance/",
        "/border/rail/",
        "/border/road/",
        "/border/topographic_model/",
        "/border/raster_emission/",
        "/border/clinic_count/",
        "/border/hospital_count/",
    ]
    # Select a random endpoint
    endpoint = random.choice(endpoints)
    response = client.post(f"{endpoint}?border_type=sgg&year=2020")
    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert "task_id" in response_json
    assert isinstance(response_json["task_id"], str)


# We can add a basic test for the status endpoint structure,
# but testing its full functionality requires a running Celery setup and tasks.
def test_get_job_status_structure():
    # Use a dummy task_id for structure testing
    dummy_task_id = "85b21fbb-3e54-42c6-8f30-504f18f9bbfe"
    response = client.get(f"/job_status/{dummy_task_id}")
    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert "task_id" in response_json
    assert response_json["task_id"] == dummy_task_id
    df = pd.DataFrame(response_json["result"])
    print(df)
    assert "status" in response_json
    assert "result" in response_json
