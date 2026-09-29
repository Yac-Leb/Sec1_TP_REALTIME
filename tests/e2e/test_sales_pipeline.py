import os
import subprocess
import time

import httpx
import pytest


RUN_E2E = os.getenv("RUN_E2E_TESTS", "false").lower() == "true"

pytestmark = pytest.mark.skipif(
    not RUN_E2E,
    reason="E2E tests disabled. Set RUN_E2E_TESTS=true."
)


def find_order_in_postgres(order_id):
    result = subprocess.run(
        [
            "docker",
            "exec",
            "sales-postgres",
            "psql",
            "-U",
            "sales",
            "-d",
            "sales",
            "-t",
            "-A",
            "-c",
            (
                "SELECT customer_id, product_id, quantity, "
                "unit_price, total_amount "
                "FROM processed_orders "
                f"WHERE order_id = '{order_id}';"
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def test_sales_pipeline():

    response = httpx.post(
        "http://sales-api:8000/api/orders",
        json={
            "customer_id": "C100",
            "product_id": "P001",
            "quantity": 3,
            "unit_price": 100,
        },
        timeout=10,
    )

    assert response.status_code == 201

    order = response.json()
    order_id = order["order_id"]

    timeout = 30
    interval = 2
    deadline = time.time() + timeout

    database_result = ""

    while time.time() < deadline:
        database_result = find_order_in_postgres(order_id)

        if database_result:
            break

        time.sleep(interval)

    assert database_result, (
        f"La commande {order_id} n'a pas été trouvée "
        f"dans PostgreSQL après {timeout} secondes."
    )

    values = database_result.split("|")

    assert values[0] == "C100"
    assert values[1] == "P001"
    assert int(values[2]) == 3
    assert float(values[3]) == 100.0
    assert float(values[4]) == 300.0