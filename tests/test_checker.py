from app.models.service import ServiceState
from app.services.checker import classify_status


def test_classify_up():
    status = classify_status(200, 100, None, "OK", 2000)
    assert status == ServiceState.UP


def test_classify_slow():
    status = classify_status(200, 3000, None, "OK", 2000)
    assert status == ServiceState.SLOW


def test_classify_invalid_content():
    status = classify_status(200, 100, "needle", "haystack", 2000)
    assert status == ServiceState.INVALID_CONTENT


def test_classify_redirect():
    status = classify_status(302, 100, None, "Redirect", 2000)
    assert status == ServiceState.REDIRECT


def test_classify_unreachable():
    status = classify_status(None, None, None, None, 2000)
    assert status == ServiceState.UNREACHABLE


def test_classify_down():
    status = classify_status(500, 100, None, "Error", 2000)
    assert status == ServiceState.DOWN


def test_classify_limited():
    status = classify_status(429, 100, None, "Rate limit", 2000)
    assert status == ServiceState.LIMITED


def test_classify_forbidden():
    status_401 = classify_status(401, 100, None, "Unauthorized", 2000)
    status_403 = classify_status(403, 100, None, "Forbidden", 2000)
    assert status_401 == ServiceState.FORBIDDEN
    assert status_403 == ServiceState.FORBIDDEN


def test_classify_error_fallback():
    # Simulate an exception in check_service and ensure ERROR is used in poll_services
    # This would require mocking check_service to raise an exception
    pass  # You can use pytest-mock or unittest.mock for this
