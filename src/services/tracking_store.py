import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4


TRACKING_FILE = Path("data/tracking_requests.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_file_exists() -> None:
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not TRACKING_FILE.exists():
        TRACKING_FILE.write_text("[]", encoding="utf-8")


def _load_requests() -> list[Dict[str, Any]]:
    _ensure_file_exists()

    try:
        return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_requests(requests: list[Dict[str, Any]]) -> None:
    TRACKING_FILE.write_text(
        json.dumps(requests, indent=2),
        encoding="utf-8",
    )


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
    requests = _load_requests()

    tracking_request = {
        "id": str(uuid4()),
        "asin": asin,
        "email": email,
        "product_title": product_title,
        "image_url": image_url,
        "current_price": current_price,
        "target_price": target_price,
        "tracking_horizon": tracking_horizon,
        "notify_on_meaningful_drop": notify_on_meaningful_drop,
        "created_at": _now_iso(),
        "last_checked_at": None,
        "last_seen_price": current_price,
        "status": "active",
    }

    requests.append(tracking_request)
    _save_requests(requests)

    return tracking_request


def get_tracking_requests() -> list[Dict[str, Any]]:
    return _load_requests()


def deactivate_tracking_request(tracking_id: str) -> Dict[str, Any]:
    requests = _load_requests()

    for request in requests:
        if request.get("id") == tracking_id:
            request["status"] = "inactive"
            request["deactivated_at"] = _now_iso()
            _save_requests(requests)
            return request

    raise ValueError("Tracking request not found.")