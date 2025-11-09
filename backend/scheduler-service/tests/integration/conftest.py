"""Pytest configuration and fixtures for unit and integration tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest


# --- Locate and add the project src/ to sys.path (robust even if moved) ---
def _find_src_dir(start: Path) -> Path:
    for p in [start, *start.parents]:
        candidate = p / "src"
        if candidate.is_dir():
            return candidate
    # Fallback: assume tests/<...>/../src
    return start.parent / "src"


_SRC_DIR = _find_src_dir(Path(__file__).resolve())
sys.path.insert(0, str(_SRC_DIR))

# --- Default env so imports don't explode at collection time ---
os.environ.setdefault("DESK_API_BASE_URL", "http://localhost:8000/api/v2")
os.environ.setdefault("DESK_API_KEY", "test-api-key-for-unit-tests")
os.environ.setdefault("DESK_API_TIMEOUT_SECONDS", "10")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("RABBITMQ_USERNAME", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")  # noqa: S105 (tests only)

# ---------------------------------------------------------------------------


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the ``--integration`` flag to enable real API tests."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that talk to external services.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Enable integration tests via the ``RUN_INTEGRATION=1`` env toggle.

    If the environment variable is set, we flip the config option so that
    integration tests are collected and executed without requiring the CLI flag.
    """
    # Also allow RUN_INTEGRATION=1 env toggle
    if os.getenv("RUN_INTEGRATION") == "1":
        config.option.integration = True  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def reset_env_and_reload() -> Iterator[None]:
    """Reset environment variables for each test and reload ``desk_service``.

    This ensures the module re-reads fresh configuration (it loads settings at
    import time), keeping tests isolated and reproducible.
    """
    original_env = os.environ.copy()

    # Ensure required env vars are set for each test
    os.environ["DESK_API_BASE_URL"] = os.environ.get(
        "DESK_API_BASE_URL", "http://localhost:8000/api/v2"
    )
    os.environ["DESK_API_KEY"] = os.environ.get(
        "DESK_API_KEY", "test-api-key-for-unit-tests"
    )
    os.environ["DESK_API_TIMEOUT_SECONDS"] = os.environ.get(
        "DESK_API_TIMEOUT_SECONDS", "10"
    )
    os.environ["RABBITMQ_HOST"] = os.environ.get("RABBITMQ_HOST", "localhost")
    os.environ["RABBITMQ_PORT"] = os.environ.get("RABBITMQ_PORT", "5672")
    os.environ["RABBITMQ_USERNAME"] = os.environ.get("RABBITMQ_USERNAME", "guest")
    os.environ["RABBITMQ_PASSWORD"] = os.environ.get("RABBITMQ_PASSWORD", "guest")

    # If desk_service was imported earlier, drop it so tests import a fresh one
    mod_name = "src.services.desk_service"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
        # Optional: also drop parent to avoid cached attributes
        sys.modules.pop("src.services", None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_desk_service() -> Mock:
    """Fixture to provide a mock of ``DeskService``."""
    return Mock()


@pytest.fixture
def mock_scheduler() -> Mock:
    """Fixture to provide a minimal mock of APScheduler."""
    mock = Mock()
    mock.state = 1  # STATE_RUNNING
    return mock


# Mark integration tests automatically unless enabled
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Mark tests tagged ``@pytest.mark.integration`` to skip by default.

    Users can opt in by passing ``--integration`` or setting
    ``RUN_INTEGRATION=1`` in the environment.
    """
    if config.getoption("--integration"):
        return  # user wants them

    reason = "use --integration flag or set RUN_INTEGRATION=1"
    skip_integration = pytest.mark.skip(reason=reason)
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
