from fastapi.testclient import TestClient

import pytest

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def manufacturer_headers() -> dict[str, str]:
    return {"X-Role": "manufacturer", "X-User-Id": "mfg-1"}


@pytest.fixture
def consumer_headers() -> dict[str, str]:
    return {"X-Role": "consumer", "X-User-Id": "cons-1"}


@pytest.fixture
def recycler_headers() -> dict[str, str]:
    return {"X-Role": "recycler", "X-User-Id": "rec-1"}


@pytest.fixture
def regulator_headers() -> dict[str, str]:
    return {"X-Role": "regulator", "X-User-Id": "reg-1"}
