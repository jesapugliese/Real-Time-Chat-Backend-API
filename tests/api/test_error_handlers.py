from fastapi.testclient import TestClient
from fastapi import status
from app.main import app


client = TestClient(app)


def assert_problem_details(response, expected_status: int):
    """
    Asserts that the error response follows the RFC 7807 Problem
    Details format.
    """

    assert response.status_code == expected_status
    assert response.headers["content-type"].startswith("application/problem+json")

    body = response.json()

    assert body["type"] == "about:blank"
    assert "title" in body
    assert body["status"] == expected_status
    assert "detail" in body
    assert "instance" in body


def test_not_found():
    response = client.get("/this-route-does-not-exist")

    assert_problem_details(
        response,
        status.HTTP_404_NOT_FOUND,
    )

    body = response.json()

    assert body["title"] == "Not Found"
    assert body["instance"] == "/this-route-does-not-exist"


def test_method_not_allowed():
    # /channels existe, pero solo tiene POST y GET.
    # PUT debería producir 405.
    response = client.put("/channels")

    assert_problem_details(
        response,
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )

    body = response.json()

    assert body["title"] == "Method Not Allowed"
    assert body["instance"] == "/channels"


def test_validation_error():
    response = client.post(
        "/channels",
        json={},
    )

    assert_problem_details(
        response,
        status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

    body = response.json()

    assert body["title"] == "Validation Error"
    assert body["instance"] == "/channels"
