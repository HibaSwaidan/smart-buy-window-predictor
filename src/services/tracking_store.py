import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    serialized = dict(record)

    for key, value in serialized.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()

    return serialized


def _get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set.")

    return psycopg2.connect(DATABASE_URL)


def save_tracking_request(
    *,
    asin: str,
    email: str,
    product_title: Optional[str],
    image_url: Optional[str],
    current_price: Optional[float],
    target_price: Optional[float],
    tracking_horizon: int,
    notify_on_meaningful_drop: bool,
) -> Dict[str, Any]:
    tracking_id = str(uuid4())

    query = """
        INSERT INTO tracking_requests (
            id,
            asin,
            email,
            product_title,
            image_url,
            current_price,
            target_price,
            tracking_horizon,
            notify_on_meaningful_drop,
            created_at,
            last_checked_at,
            last_seen_price,
            status
        )
        VALUES (
            %(id)s,
            %(asin)s,
            %(email)s,
            %(product_title)s,
            %(image_url)s,
            %(current_price)s,
            %(target_price)s,
            %(tracking_horizon)s,
            %(notify_on_meaningful_drop)s,
            %(created_at)s,
            NULL,
            %(last_seen_price)s,
            'active'
        )
        RETURNING *;
    """

    values = {
        "id": tracking_id,
        "asin": asin,
        "email": email,
        "product_title": product_title,
        "image_url": image_url,
        "current_price": current_price,
        "target_price": target_price,
        "tracking_horizon": tracking_horizon,
        "notify_on_meaningful_drop": notify_on_meaningful_drop,
        "created_at": _now_iso(),
        "last_seen_price": current_price,
    }

    with _get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, values)
            saved = cur.fetchone()
            conn.commit()

    return _serialize_record(saved)


def get_tracking_requests(email: str) -> list[Dict[str, Any]]:
    query = """
        SELECT *
        FROM tracking_requests
        WHERE email = %(email)s
        ORDER BY created_at DESC;
    """

    with _get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, {"email": email})
            rows = cur.fetchall()

    return [_serialize_record(row) for row in rows]


def cancel_tracking_request(tracking_id: str, email: str) -> Dict[str, Any]:
    query = """
        UPDATE tracking_requests
        SET
            status = 'cancelled',
            deactivated_at = %(deactivated_at)s
        WHERE id = %(tracking_id)s
          AND email = %(email)s
          AND status = 'active'
        RETURNING *;
    """

    with _get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                query,
                {
                    "tracking_id": tracking_id,
                    "email": email,
                    "deactivated_at": _now_iso(),
                },
            )
            updated = cur.fetchone()
            conn.commit()

    if not updated:
        raise ValueError("Active tracking request not found for this email.")

    return _serialize_record(updated)