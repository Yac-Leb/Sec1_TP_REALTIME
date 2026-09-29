import pytest
from pydantic import ValidationError

from app.main import Order, build_order_event


def test_order_total():
    order = Order(
        customer_id="C001",
        product_id="P001",
        quantity=2,
        unit_price=50.0,
    )

    event = build_order_event(order)

    assert event["total_amount"] == 100.0


def test_quantity_positive():
    order = Order(
        customer_id="C001",
        product_id="P001",
        quantity=1,
        unit_price=10.0,
    )

    assert order.quantity == 1


def test_quantity_zero():
    with pytest.raises(ValidationError):
        Order(
            customer_id="C001",
            product_id="P001",
            quantity=0,
            unit_price=10.0,
        )


def test_quantity_negative():
    with pytest.raises(ValidationError):
        Order(
            customer_id="C001",
            product_id="P001",
            quantity=-1,
            unit_price=10.0,
        )


def test_price_positive():
    order = Order(
        customer_id="C001",
        product_id="P001",
        quantity=1,
        unit_price=10.0,
    )

    assert order.unit_price == 10.0


def test_price_invalid():
    with pytest.raises(ValidationError):
        Order(
            customer_id="C001",
            product_id="P001",
            quantity=1,
            unit_price=0,
        )


def test_customer_id_invalid():
    with pytest.raises(ValidationError):
        Order(
            customer_id="C",
            product_id="P001",
            quantity=1,
            unit_price=10.0,
        )


def test_product_id_invalid():
    with pytest.raises(ValidationError):
        Order(
            customer_id="C001",
            product_id="P",
            quantity=1,
            unit_price=10.0,
        )


def test_order_contains_order_id():
    order = Order(
        customer_id="C001",
        product_id="P001",
        quantity=1,
        unit_price=10.0,
    )

    event = build_order_event(order)

    assert event["order_id"].startswith("ORD-")
    assert len(event["order_id"]) == 14


def test_order_event():
    order = Order(
        customer_id="C001",
        product_id="P001",
        quantity=2,
        unit_price=49.90,
    )

    event = build_order_event(order)

    assert event["customer_id"] == "C001"
    assert event["product_id"] == "P001"
    assert event["quantity"] == 2
    assert event["unit_price"] == 49.90
    assert event["total_amount"] == 99.80
    assert "order_id" in event
    assert "timestamp" in event