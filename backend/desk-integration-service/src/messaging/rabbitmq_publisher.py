"""Simple RabbitMQ publisher for desk integration events."""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import pika
except Exception:
    pika = None

logger = logging.getLogger(__name__)


@dataclass
class RabbitMQSettings:
    """RabbitMQ connection parameters from environment variables."""

    host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    username: str = os.getenv("RABBITMQ_USERNAME", "guest")
    password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    exchange: str = os.getenv("RABBITMQ_EXCHANGE", "desk_events")
    exchange_type: str = os.getenv("RABBITMQ_EXCHANGE_TYPE", "topic")


class RabbitMQPublisher:
    """Simple publisher for desk integration events."""

    def __init__(self, settings: Optional[RabbitMQSettings] = None) -> None:
        """Initialize the RabbitMQ publisher."""
        self.settings = settings or RabbitMQSettings()
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._connected = False

    def connect(self) -> None:
        """Connect to RabbitMQ broker and declare exchange."""
        if pika is None:
            logger.warning("pika not available; RabbitMQ integration disabled")
            return

        if self._connected:
            logger.info("Already connected to RabbitMQ")
            return

        try:
            credentials = pika.PlainCredentials(
                self.settings.username, self.settings.password
            )
            parameters = pika.ConnectionParameters(
                host=self.settings.host,
                port=self.settings.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )

            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # Declare exchange for desk events
            self._channel.exchange_declare(
                exchange=self.settings.exchange,
                exchange_type=self.settings.exchange_type,
                durable=True,
            )

            self._connected = True
            logger.info(
                "✓ Connected to RabbitMQ: %s:%s (exchange: %s)",
                self.settings.host,
                self.settings.port,
                self.settings.exchange,
            )
        except Exception as e:
            logger.exception("Failed to connect to RabbitMQ: %s", e)
            self._connected = False

    def disconnect(self) -> None:
        """Disconnect from RabbitMQ broker."""
        if not self._connected:
            return

        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
            if self._connection and not self._connection.is_closed:
                self._connection.close()
            logger.info("✓ Disconnected from RabbitMQ")
        except Exception as e:
            logger.warning("Error disconnecting from RabbitMQ: %s", e)
        finally:
            self._connected = False
            self._channel = None
            self._connection = None

    def _ensure_connection(self) -> bool:
        """Ensure connection is active, reconnect if needed."""
        if (
            not self._connected
            or self._connection is None
            or self._connection.is_closed
        ):
            logger.info("Reconnecting to RabbitMQ...")
            self.connect()

        return self._connected

    def publish(
        self,
        routing_key: str,
        payload: Dict[str, Any],
        persistent: bool = True,
    ) -> bool:
        """Publish an event to RabbitMQ."""
        if not self._ensure_connection():
            logger.warning(
                "Skipping RabbitMQ publish (not connected): %s", routing_key
            )
            return False

        try:
            message_body = json.dumps(payload)
            properties = pika.BasicProperties(
                delivery_mode=2 if persistent else 1,
                content_type="application/json",
            )

            self._channel.basic_publish(
                exchange=self.settings.exchange,
                routing_key=routing_key,
                body=message_body,
                properties=properties,
            )

            logger.info("✓ Published event: %s", routing_key)
            return True

        except Exception as e:
            logger.exception("Failed to publish to RabbitMQ: %s", e)
            self._connected = False
            return False


# Global singleton instance
rabbitmq_publisher = RabbitMQPublisher()