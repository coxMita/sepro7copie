"""Service for interacting with the WiFi2BLE Box Simulator API."""

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage

load_dotenv()
logger = logging.getLogger(__name__)


def _load_timeout() -> int:
    """Load timeout from environment with fallback.

    Falls back to 10 seconds if the env var is missing or invalid.
    """
    raw = os.getenv("DESK_API_TIMEOUT_SECONDS", "10")
    try:
        return int(raw)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid DESK_API_TIMEOUT_SECONDS value '%s'; falling back to 10 seconds",
            raw,
        )
        return 10


DEFAULT_TIMEOUT = _load_timeout()
HTTP_ERROR_THRESHOLD = 400  # First HTTP error status code (4xx/5xx)


class DeskServiceError(RuntimeError):
    """Base exception raised for desk service errors."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class _DeskServiceConfig:
    """Configuration container for the DeskService."""

    base_url: str
    api_key: str

    @classmethod
    def from_env(cls) -> "_DeskServiceConfig":
        """Load configuration from environment variables."""
        base = os.getenv("DESK_API_BASE_URL", "http://localhost:8000/api/v2").rstrip(
            "/"
        )
        api_key = os.getenv("DESK_API_KEY", "")

        if not api_key:
            logger.error("DESK_API_KEY environment variable is not set!")
            raise ValueError("DESK_API_KEY is required")

        logger.info(
            "DeskService initialized: base_url=%s, api_key=%s...",
            base,
            api_key[:8],
        )
        return cls(base_url=base, api_key=api_key)


class DeskService:
    """Service for interacting with the WiFi2BLE Box Simulator API."""

    _config = _DeskServiceConfig.from_env()

    @classmethod
    def _build_url(cls, *segments: str) -> str:
        """Build URL with API key in path for WiFi2BLE Box Simulator.

        Format: {base_url}/{api_key}/desks/...

        The requests library automatically handles URL encoding, so we don't need
        to encode manually.

        Examples:
            _build_url("desks/") -> http://localhost:8000/api/v2/API_KEY/desks/
            _build_url("desks", "cd:fb:1a:53:fb:e6")
                -> http://localhost:8000/api/v2/API_KEY/desks/cd:fb:1a:53:fb:e6

        """
        parts: List[str] = [cls._config.base_url, cls._config.api_key]
        parts.extend(segment.strip("/") for segment in segments if segment)
        url = "/".join(parts)

        # Ensure trailing slash for directory endpoints
        if segments and segments[-1].endswith("/"):
            url += "/"

        logger.debug("Built URL: %s", url)
        return url

    @classmethod
    def _request(
        cls,
        method: str,
        url: str,
        **kwargs: dict[str, object],
    ) -> requests.Response:
        """Make HTTP request with proper error handling."""
        headers: Dict[str, str] = kwargs.pop("headers", {}) or {}  # type: ignore[assignment]
        headers.setdefault("Content-Type", "application/json")

        logger.info("Making %s request to %s", method, url)
        if "json" in kwargs:
            logger.debug("Request payload: %s", kwargs["json"])

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
                **kwargs,  # type: ignore[arg-type]
            )
            logger.info("Response status: %s", response.status_code)
            logger.info("Response body: %s", response.text)

        except requests.exceptions.Timeout as exc:
            logger.error(
                "Request timeout after %ss for %s: %s", DEFAULT_TIMEOUT, url, exc
            )
            raise DeskServiceError(
                "Request timeout after %ss" % DEFAULT_TIMEOUT
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error to %s: %s", url, exc)
            raise DeskServiceError(
                "Failed to connect to desk API - check if simulator is running"
            ) from exc

        except requests.RequestException as exc:
            logger.exception("Request failed to %s: %s", url, exc)
            raise DeskServiceError("Failed to communicate with desk API") from exc

        if response.status_code >= HTTP_ERROR_THRESHOLD:
            error_text = response.text[:500] if response.text else "No error message"
            logger.error(
                "Desk API error %s for %s %s: %s",
                response.status_code,
                method,
                url,
                error_text,
            )
            raise DeskServiceError(
                "Desk API responded with HTTP %s: %s"
                % (response.status_code, error_text),
                status_code=response.status_code,
            )

        return response

    @classmethod
    def get_desk_by_id(cls, desk_id: str) -> Desk | None:
        """Get the data of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            Desk,
            or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk state without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id)
            response = cls._request("GET", url)
            desk = response.json()

            # Safely construct last_errors list with coercion
            last_errors: List[DeskError] = []
            errors_payload = desk.get("lastErrors") if isinstance(desk, dict) else None
            if errors_payload:
                for error in errors_payload:
                    time_s = error.get("time_s")
                    raw_code = error.get("error_code")
                    try:
                        error_code = int(raw_code) if raw_code is not None else 0
                    except (TypeError, ValueError):
                        error_code = 0
                    last_errors.append(DeskError(time_s=time_s, error_code=error_code))

            # The API returns nested sections: 'config', 'state', 'usage', so use those
            config_payload = desk.get("config", {}) or {}
            state_payload = desk.get("state", {}) or {}
            usage_payload = desk.get("usage", {}) or {}

            desk_output = Desk(
                config=DeskConfig(
                    name=config_payload.get("name"),
                    manufacturer=config_payload.get("manufacturer"),
                ),
                state=DeskState(
                    position_mm=state_payload.get("position_mm"),
                    speed_mms=state_payload.get("speed_mms"),
                    status=state_payload.get("status"),
                    is_position_lost=state_payload.get("isPositionLost"),
                    is_overload_protection_up=state_payload.get(
                        "isOverloadProtectionUp"
                    ),
                    is_overload_protection_down=state_payload.get(
                        "isOverloadProtectionDown"
                    ),
                    is_anti_collision=state_payload.get("isAntiCollision"),
                ),
                usage=DeskUsage(
                    activations_counter=usage_payload.get("activationsCounter"),
                    sit_stand_counter=usage_payload.get("sitStandCounter"),
                ),
                last_errors=last_errors,
            )
            return desk_output

        except DeskServiceError as exc:
            logger.warning("Failed to get data of desk %s: %s", desk_id, exc)
            return None
        except Exception as exc:
            logger.exception("Unexpected error fetching desk %s: %s", desk_id, exc)
            return None

    @classmethod
    def get_all_desks(cls) -> list[str]:
        """Fetch all desk identifiers from the desk API.

        Returns:
            List of MAC addresses like ["cd:fb:1a:53:fb:e6", ...]

        Raises:
            DeskServiceError: If the API request fails

        """
        logger.info("Fetching all desks from API")

        # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/
        url = cls._build_url("desks/")
        response = cls._request("GET", url)

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Failed to parse JSON response: %s", exc)
            raise DeskServiceError("Invalid JSON response from desk API") from exc

        # WiFi2BLE returns a simple list of MAC addresses (strings)
        if isinstance(payload, list):
            desk_ids = [str(item) for item in payload if item]
            logger.info("✓ Found %d desks: %s", len(desk_ids), desk_ids)
            return desk_ids

        logger.error("Unexpected payload format: %s - %s", type(payload), payload)
        raise DeskServiceError("Desk API returned an unexpected response format")

    @classmethod
    def get_desk_config(cls, desk_id: str) -> DeskConfig | None:
        """Get the current configuration of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            Dict with 'config' key,
            or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk config without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id, "config")
            response = cls._request("GET", url)
            config = response.json()
            desk_config = DeskConfig(
                name=config.get("name"),
                manufacturer=config.get("manufacturer"),
            )
            return desk_config

        except DeskServiceError as exc:
            logger.warning("Failed to get configuration for desk %s: %s", desk_id, exc)
            return None

    @classmethod
    def get_desk_state(cls, desk_id: str) -> DeskState | None:
        """Get the current state of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            DeskState,
            or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk state without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id, "state")
            response = cls._request("GET", url)
            state = response.json()
            desk_state = DeskState(
                position_mm=state.get("position_mm"),
                speed_mms=state.get("speed_mms"),
                status=state.get("status"),
                is_position_lost=state.get("isPositionLost"),
                is_overload_protection_up=state.get("isOverloadProtectionUp"),
                is_overload_protection_down=state.get("isOverloadProtectionDown"),
                is_anti_collision=state.get("isAntiCollision"),
            )
            return desk_state

        except DeskServiceError as exc:
            logger.warning("Failed to get state for desk %s: %s", desk_id, exc)
            return

    @classmethod
    def get_desk_usage(cls, desk_id: str) -> DeskUsage | None:
        """Get the usage data of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            DeskUsage,
            or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk usage without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id, "usage")
            response = cls._request("GET", url)
            usage = response.json()
            desk_usage = DeskUsage(
                activations_counter=usage.get("activationsCounter"),
                sit_stand_counter=usage.get("sitStandCounter"),
            )
            return desk_usage

        except DeskServiceError as exc:
            logger.warning("Failed to get usage for desk %s: %s", desk_id, exc)
            return None

    @classmethod
    def get_desk_errors(cls, desk_id: str) -> List[DeskError] | None:
        """Get the list of errors for a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            List[DeskError] or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk errors without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id)
            response = cls._request("GET", url)
            payload = response.json()

            last_errors: List[DeskError] = []
            errors_payload = (
                payload.get("lastErrors") if isinstance(payload, dict) else None
            )  # noqa: E501
            if errors_payload:
                for error in errors_payload:
                    time_s = error.get("time_s")
                    raw_code = error.get("error_code")
                    try:
                        error_code = int(raw_code) if raw_code is not None else 0
                    except (TypeError, ValueError):
                        error_code = 0
                    last_errors.append(DeskError(time_s=time_s, error_code=error_code))

            return last_errors

        except DeskServiceError as exc:
            logger.warning("Failed to get errors for desk %s: %s", desk_id, exc)
            return None
        except Exception as exc:
            logger.exception(
                "Unexpected error fetching errors for desk %s: %s", desk_id, exc
            )  # noqa: E501
            return None

    @classmethod
    def set_desk_position(cls, desk_id: str, position_mm: int) -> DeskState | None:
        """Set a specific desk to a target position.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")
            position_mm: Target position in millimeters

        Returns:
            DeskState object with the new desk state

        Raises:
            DeskServiceError: If the operation fails

        """
        if not desk_id:
            raise DeskServiceError("Desk identifier is required")

        if not isinstance(position_mm, int) or position_mm < 0:
            raise DeskServiceError(
                "Invalid position: %smm (must be positive integer)" % position_mm
            )

        logger.info("Setting desk %s to position %smm", desk_id, position_mm)

        # WiFi2BLE API endpoint: PUT /api/v2/{api_key}/desks/{desk_id}/state
        payload = {"position_mm": position_mm}
        url = cls._build_url("desks", desk_id, "state")

        response = cls._request("PUT", url, json=payload)
        logger.info("✓ Successfully commanded desk %s to %smm", desk_id, position_mm)

        try:
            # Parse response from WiFi2BLE API
            state_data = response.json()
            
            # Return proper DeskState object
            return DeskState(
                position_mm=state_data.get("position_mm", position_mm),
                speed_mms=state_data.get("speed_mms", 0),
                status=state_data.get("status", "moving"),
                is_position_lost=state_data.get("isPositionLost", False),
                is_overload_protection_up=state_data.get("isOverloadProtectionUp", False),
                is_overload_protection_down=state_data.get("isOverloadProtectionDown", False),
                is_anti_collision=state_data.get("isAntiCollision", False),
            )
        except (ValueError, KeyError) as e:
            logger.warning("Failed to parse desk state response: %s", e)
            # Return minimal valid DeskState
            return DeskState(
                position_mm=position_mm,
                speed_mms=0,
                status="unknown",
                is_position_lost=False,
                is_overload_protection_up=False,
                is_overload_protection_down=False,
                is_anti_collision=False,
            )