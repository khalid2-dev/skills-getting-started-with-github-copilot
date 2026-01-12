import copy
import urllib.parse
import pytest
from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)

# preserve a clean copy so tests are isolated
_original_activities = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(_original_activities)
    yield
    app_module.activities = copy.deepcopy(_original_activities)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_signup_success():
    activity = next(iter(app_module.activities.keys()))
    email = "testuser@example.com"
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup?email={urllib.parse.quote(email, safe='') }"
    r = client.post(path)
    assert r.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_duplicate():
    activity = next(iter(app_module.activities.keys()))
    email = app_module.activities[activity]["participants"][0]
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup?email={urllib.parse.quote(email, safe='') }"
    r = client.post(path)
    assert r.status_code == 400


def test_signup_full():
    activity = next(iter(app_module.activities.keys()))
    act = app_module.activities[activity]
    act["max_participants"] = len(act["participants"])  # make it full
    email = "another@example.com"
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup?email={urllib.parse.quote(email, safe='') }"
    r = client.post(path)
    assert r.status_code == 400


def test_delete_participant_success():
    activity = next(iter(app_module.activities.keys()))
    participants = app_module.activities[activity]["participants"]
    if not participants:
        pytest.skip("No participants to remove")
    email = participants[0]
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/participants?email={urllib.parse.quote(email, safe='') }"
    r = client.delete(path)
    assert r.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_delete_participant_not_found():
    activity = next(iter(app_module.activities.keys()))
    email = "notfound@example.com"
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/participants?email={urllib.parse.quote(email, safe='') }"
    r = client.delete(path)
    assert r.status_code == 404
