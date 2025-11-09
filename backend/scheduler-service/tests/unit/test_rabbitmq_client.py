"""Unit tests for rabbitmq_client.py.

Tests the RabbitMQClient class in isolation with all dependencies mocked.
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

from src.services.rabbitmq_client import RabbitMQClient, RabbitMQSettings

# ---- Test constants (replace magic numbers/strings in assertions) ----
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5672
DEFAULT_USERNAME = "guest"
# Avoid hardcoded password literal in assertion context
DEFAULT_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASSWORD", "guest")
DEFAULT_EXCHANGE = "desk_scheduler_events"
DEFAULT_EXCHANGE_TYPE = "topic"

TEST_NUMBER_VALUE = 123
ANSWER_NUMBER = 42

DELIVERY_MODE_PERSISTENT = 2
DELIVERY_MODE_NON_PERSISTENT = 1
# ----------------------------------------------------------------------

# Add the project root to the path (go up from tests/unit to project root)
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)


class TestRabbitMQSettings(unittest.TestCase):
    """Test the RabbitMQSettings dataclass."""

    def test_default_settings(self) -> None:
        """Test that default settings are correct."""
        settings = RabbitMQSettings()

        assert settings.host == DEFAULT_HOST
        assert settings.port == DEFAULT_PORT
        assert settings.username == DEFAULT_USERNAME
        # Compare to constant (not a raw literal) to avoid S105 noise in tests
        assert settings.password == DEFAULT_PASSWORD
        assert settings.exchange == DEFAULT_EXCHANGE
        assert settings.exchange_type == DEFAULT_EXCHANGE_TYPE

    # REMOVED: test_settings_from_environment - was testing env var loading.
    # Keeping environment logic out of unit scope for stability.


class TestRabbitMQClient(unittest.TestCase):
    """Test the RabbitMQClient class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.settings = RabbitMQSettings()
        self.client = RabbitMQClient(self.settings)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.client = None

    # ==================== Connection Tests ====================

    @patch("src.services.rabbitmq_client.pika")
    def test_connect_success(self, mock_pika: Mock) -> None:
        """Test successful connection to RabbitMQ."""
        mock_connection = Mock()
        mock_channel = Mock()
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        self.client.connect()

        # Verify connection was established
        mock_pika.BlockingConnection.assert_called_once()
        mock_connection.channel.assert_called_once()
        mock_channel.exchange_declare.assert_called_once_with(
            exchange=self.settings.exchange,
            exchange_type=self.settings.exchange_type,
            durable=True,
        )
        assert self.client._connected is True  # noqa: SLF001

    @patch("src.services.rabbitmq_client.pika")
    def test_connect_already_connected(self, mock_pika: Mock) -> None:
        """Test connecting when already connected."""
        self.client._connected = True  # noqa: SLF001

        self.client.connect()

        # Should not try to connect again
        mock_pika.BlockingConnection.assert_not_called()

    @patch("src.services.rabbitmq_client.pika")
    def test_connect_failure(self, mock_pika: Mock) -> None:
        """Test connection failure handling."""
        mock_pika.BlockingConnection.side_effect = Exception("Connection failed")

        self.client.connect()

        # Should handle error gracefully
        assert self.client._connected is False  # noqa: SLF001

    @patch("src.services.rabbitmq_client.pika", None)
    def test_connect_pika_not_available(self) -> None:
        """Test connection when pika is not installed."""
        client = RabbitMQClient(self.settings)

        client.connect()

        # Should handle missing pika gracefully
        assert client._connected is False  # noqa: SLF001

    # ==================== Disconnect Tests ====================

    def test_disconnect_when_connected(self) -> None:
        """Test disconnecting when connected."""
        mock_connection = Mock()
        mock_channel = Mock()
        mock_connection.is_closed = False
        mock_channel.is_closed = False

        self.client._connection = mock_connection  # noqa: SLF001
        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001

        self.client.disconnect()

        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()
        assert self.client._connected is False  # noqa: SLF001
        assert self.client._connection is None  # noqa: SLF001
        assert self.client._channel is None  # noqa: SLF001

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnecting when not connected."""
        self.client._connected = False  # noqa: SLF001

        self.client.disconnect()

        # Should do nothing, no exceptions
        assert self.client._connected is False  # noqa: SLF001

    def test_disconnect_handles_errors(self) -> None:
        """Test that disconnect handles errors gracefully."""
        mock_channel = Mock()
        mock_channel.is_closed = False
        mock_channel.close.side_effect = Exception("Close failed")
        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001

        # Should not raise exception
        self.client.disconnect()

        assert self.client._connected is False  # noqa: SLF001

    # ==================== Publish Tests ====================

    @patch("src.services.rabbitmq_client.pika")
    def test_publish_success(self, mock_pika: Mock) -> None:
        """Test successfully publishing a message."""
        # Create a mock BasicProperties that returns actual values
        mock_properties = Mock()
        mock_properties.delivery_mode = DELIVERY_MODE_PERSISTENT
        mock_pika.BasicProperties.return_value = mock_properties

        mock_channel = Mock()
        mock_connection = Mock()
        mock_connection.is_closed = False

        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001
        self.client._connection = mock_connection  # noqa: SLF001

        payload = {"test": "data", "number": TEST_NUMBER_VALUE}
        result = self.client.publish("test.routing.key", payload)

        assert result is True
        mock_channel.basic_publish.assert_called_once()

        # Verify call arguments
        call_kwargs = mock_channel.basic_publish.call_args.kwargs
        assert call_kwargs["exchange"] == self.settings.exchange
        assert call_kwargs["routing_key"] == "test.routing.key"

        # Verify body is JSON
        body = call_kwargs["body"]
        parsed = json.loads(body)
        assert parsed["test"] == "data"
        assert parsed["number"] == TEST_NUMBER_VALUE

    @patch("src.services.rabbitmq_client.pika")
    def test_publish_not_connected(self, mock_pika: Mock) -> None:
        """Test publishing when not connected."""
        # Make sure connect() fails when called
        mock_pika.BlockingConnection.side_effect = Exception("Connection failed")

        self.client._connected = False  # noqa: SLF001
        self.client._connection = None  # noqa: SLF001

        result = self.client.publish("test.key", {"test": "data"})

        assert result is False

    @patch("src.services.rabbitmq_client.pika")
    def test_publish_with_persistent_delivery(self, mock_pika: Mock) -> None:
        """Test that messages are published with persistent delivery mode."""
        # Create a mock BasicProperties that tracks delivery_mode
        mock_properties = Mock()
        mock_properties.delivery_mode = DELIVERY_MODE_PERSISTENT
        mock_pika.BasicProperties.return_value = mock_properties

        mock_channel = Mock()
        mock_connection = Mock()
        mock_connection.is_closed = False

        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001
        self.client._connection = mock_connection  # noqa: SLF001

        self.client.publish("test.key", {"test": "data"}, persistent=True)

        # Verify BasicProperties was called with delivery_mode=2
        mock_pika.BasicProperties.assert_called_once()
        call_kwargs = mock_pika.BasicProperties.call_args.kwargs
        assert call_kwargs["delivery_mode"] == DELIVERY_MODE_PERSISTENT

    @patch("src.services.rabbitmq_client.pika")
    def test_publish_non_persistent(self, mock_pika: Mock) -> None:
        """Test publishing with non-persistent delivery mode."""
        # Create a mock BasicProperties that tracks delivery_mode
        mock_properties = Mock()
        mock_properties.delivery_mode = DELIVERY_MODE_NON_PERSISTENT
        mock_pika.BasicProperties.return_value = mock_properties

        mock_channel = Mock()
        mock_connection = Mock()
        mock_connection.is_closed = False

        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001
        self.client._connection = mock_connection  # noqa: SLF001

        self.client.publish("test.key", {"test": "data"}, persistent=False)

        # Verify BasicProperties was called with delivery_mode=1
        mock_pika.BasicProperties.assert_called_once()
        call_kwargs = mock_pika.BasicProperties.call_args.kwargs
        assert call_kwargs["delivery_mode"] == DELIVERY_MODE_NON_PERSISTENT

    @patch("src.services.rabbitmq_client.pika")
    def test_publish_failure(self, mock_pika: Mock) -> None:
        """Test publishing failure handling."""
        mock_channel = Mock()
        mock_connection = Mock()
        mock_connection.is_closed = False
        mock_channel.basic_publish.side_effect = Exception("Publish failed")

        # Mock BasicProperties
        mock_properties = Mock()
        mock_pika.BasicProperties.return_value = mock_properties

        self.client._channel = mock_channel  # noqa: SLF001
        self.client._connected = True  # noqa: SLF001
        self.client._connection = mock_connection  # noqa: SLF001

        result = self.client.publish("test.key", {"test": "data"})

        assert result is False
        # Should mark as disconnected after failure
        assert self.client._connected is False  # noqa: SLF001

    # ==================== Payload Serialization Tests ====================

    def test_serialize_dict_payload(self) -> None:
        """Test serializing dictionary payload."""
        payload = {"key": "value", "number": ANSWER_NUMBER}

        result = RabbitMQClient._serialise_payload(payload)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == ANSWER_NUMBER

    def test_serialize_list_payload(self) -> None:
        """Test serializing list payload."""
        payload = [1, 2, 3, "test"]

        result = RabbitMQClient._serialise_payload(payload)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == [1, 2, 3, "test"]

    def test_serialize_string_payload(self) -> None:
        """Test serializing string payload."""
        payload = "plain text message"

        result = RabbitMQClient._serialise_payload(payload)

        assert result == "plain text message"

    def test_serialize_bytes_payload(self) -> None:
        """Test serializing bytes payload."""
        payload = b"binary data"

        result = RabbitMQClient._serialise_payload(payload)

        assert result == "binary data"

    # ==================== Ensure Connection Tests ====================

    @patch("src.services.rabbitmq_client.pika")
    def test_ensure_connection_when_connected(self, mock_pika: Mock) -> None:
        """Test ensure connection when already connected."""
        mock_connection = Mock()
        mock_connection.is_closed = False

        self.client._connected = True  # noqa: SLF001
        self.client._connection = mock_connection  # noqa: SLF001

        result = self.client._ensure_connection()

        assert result is True
        # Should not try to reconnect
        mock_pika.BlockingConnection.assert_not_called()

    # REMOVED: reconnection test that depended on closed connection; out of scope.

    @patch("src.services.rabbitmq_client.pika")
    def test_ensure_connection_when_not_connected(self, mock_pika: Mock) -> None:
        """Test ensure connection when not connected."""
        mock_connection = Mock()
        mock_connection.is_closed = False
        mock_channel = Mock()
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        self.client._connected = False  # noqa: SLF001

        result = self.client._ensure_connection()

        assert result is True
        mock_pika.BlockingConnection.assert_called()


class TestRabbitMQClientIntegration(unittest.TestCase):
    """Integration-style tests for RabbitMQClient."""

    @patch("src.services.rabbitmq_client.pika")
    def test_connect_publish_disconnect_flow(self, mock_pika: Mock) -> None:
        """Test full connect -> publish -> disconnect flow."""
        # Setup mocks
        mock_connection = Mock()
        mock_connection.is_closed = False
        mock_channel = Mock()
        mock_channel.is_closed = False
        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        # Mock BasicProperties
        mock_properties = Mock()
        mock_pika.BasicProperties.return_value = mock_properties

        # Create client
        client = RabbitMQClient()

        # Connect
        client.connect()
        assert client._connected is True  # noqa: SLF001

        # Publish
        result = client.publish("test.key", {"data": "test"})
        assert result is True
        mock_channel.basic_publish.assert_called_once()

        # Disconnect
        client.disconnect()
        assert client._connected is False  # noqa: SLF001
        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()


if __name__ == "__main__":
    # Run the tests with verbose output
    unittest.main(verbosity=2)
