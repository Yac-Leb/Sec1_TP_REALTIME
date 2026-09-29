import json
import os
import time

import pytest
from fastapi.testclient import TestClient
from kafka import KafkaConsumer

from app.main import app


RUN_INTEGRATION = os.getenv(
    "RUN_INTEGRATION_TESTS", "false"
).lower() == "true"

pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=true."
)

client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_api_produces_event_to_kafka():

    consumer = KafkaConsumer(
        "sales.orders",
        bootstrap_servers="kafka:29092",
        auto_offset_reset="latest",
        group_id=f"integration-test-{time.time()}",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


    consumer.poll(timeout_ms=3000)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 49.90,
        },
    )

    assert response.status_code == 201

    created_order = response.json()

    messages = consumer.poll(timeout_ms=10000)

    consumer.close()

    received_events = [
        record.value
        for records in messages.values()
        for record in records
    ]

    matching_events = [
        event
        for event in received_events
        if event["order_id"] == created_order["order_id"]
    ]

    assert len(matching_events) == 1

    event = matching_events[0]

    assert event["customer_id"] == "C001"
    assert event["product_id"] == "P001"
    assert event["quantity"] == 2
    assert event["unit_price"] == 49.90
    assert event["total_amount"] == 99.80