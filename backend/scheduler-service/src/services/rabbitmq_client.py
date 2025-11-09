from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

try:
    import pika
except Exception:  # pragma: no cover - handled gracefully at runtime
    pika = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class RabbitMQSettings:
    """RabbitMQ connection parameters sourced from environment variables."""

    host: str = os.getenv("RABBITMQ_HOST", "localhost")
    port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    username: str = os.getenv("RABBITMQ_USERNAME", "guest")
    password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    exchange: str = os.getenv("RABBITMQ_EXCHANGE", "desk_scheduler_events")
    exchange_type: str = os.getenv("RABBITMQ_EXCHANGE_TYPE", "topic")


class RabbitMQClient:
    """Thin wrapper around pika to simplify publishing events to RabbitMQ."""

    def __init__(self, settings: Optional[RabbitMQSettings] = None) -> None:
        self.settings = settings or RabbitMQSettings()
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._connected = False

    # Lifecycle management

    def connect(self) -> None:
        """Connect to the configured RabbitMQ broker if possible."""
        if pika is None:
            logger.warning("pika is not available; RabbitMQ integration disabled.")
            return

        if self._connected:
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

            # Declare the exchange
            self._channel.exchange_declare(
                exchange=self.settings.exchange,
                exchange_type=self.settings.exchange_type,
                durable=True,
            )

            self._connected = True
            logger.info(
                "Connected to RabbitMQ broker at %s:%s (exchange: %s)",
                self.settings.host,
                self.settings.port,
                self.settings.exchange,
            )
        except Exception as exc:  # pragma: no cover - network failure path
            logger.exception("Failed to connect to RabbitMQ broker: %s", exc)
            self._connected = False

    def disconnect(self) -> None:
        """Disconnect from the RabbitMQ broker if a connection exists."""
        if not self._connected:
            return

        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
            if self._connection and not self._connection.is_closed:
                self._connection.close()
        except Exception as exc:  # pragma: no cover - defensive cleanup
            logger.warning("Error while disconnecting RabbitMQ client: %s", exc)
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
            logger.info("RabbitMQ connection lost, attempting to reconnect...")
            self.connect()

        return self._connected

    # Publishing helpers

    def publish(
        self,
        routing_key: str,
        payload: object,
        persistent: bool = True,
    ) -> bool:
        """Publish ``payload`` with ``routing_key`` and return ``True`` on success."""
        if not self._ensure_connection():
            logger.warning(
                "Skipping RabbitMQ publish because the client is not connected "
                "(routing_key=%s)",
                routing_key,
            )
            return False

        payload_str = self._serialise_payload(payload)

        try:
            properties = pika.BasicProperties(
                delivery_mode=2 if persistent else 1,  # 2 = persistent
                content_type="application/json",
            )

            self._channel.basic_publish(
                exchange=self.settings.exchange,
                routing_key=routing_key,
                body=payload_str,
                properties=properties,
            )
        except Exception as exc:  # pragma: no cover - network failure path
            logger.exception(
                "RabbitMQ publish failed for routing_key %s: %s",
                routing_key,
                exc,
            )
            self._connected = False  # Mark as disconnected to trigger reconnect
            return False

        logger.debug("Published RabbitMQ message with routing_key: %s", routing_key)
        return True

    # Internal helpers

    @staticmethod
    def _serialise_payload(payload: object) -> str:
        if isinstance(payload, (dict, list)):
            return json.dumps(payload)
        if isinstance(payload, (bytes, bytearray)):
            return payload.decode("utf-8", errors="ignore")
        return str(payload)


# Shared singleton used across the service
rabbitmq_client = RabbitMQClient()
