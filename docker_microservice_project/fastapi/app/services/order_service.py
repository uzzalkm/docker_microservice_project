from datetime import datetime

from app.repositories.order_repository import (
    receive_order_by_production_record,
)

# Both REST APIs and GraphQL should call this service, avoiding duplicated
# database logic and duplicated validation rules.

REQUIRED_CURRENT_STATUS_ID = 17   # order must currently be in status 17
NEW_STATUS_ID = 19                # status after production receives it
DATE_FORMAT = "%d/%m/%Y"


def _fail(message, order_id=None, status_id=None):
    return {
        "order_id": order_id,
        "status_id": status_id,
        "msg": "fail",
        "message": message,
    }


def _to_long(value):
    """Return int(value) or None if it is missing / not numeric."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_valid_date(value):
    try:
        datetime.strptime(value.strip(), DATE_FORMAT)
        return True
    except (AttributeError, ValueError):
        return False


def receive_order_by_production(
    order_id,
    current_sts_id,
    user_id,
    remarks,
    have_issue,
    erd_date,
    rerd_date,
):
    # ------------------------------------------------------------------
    # 1. Validation
    # ------------------------------------------------------------------
    order_id = _to_long(order_id)
    if order_id is None:
        return _fail("order_id is required.")

    current_sts_id = _to_long(current_sts_id)
    if current_sts_id is None:
        return _fail("current_sts_id is required.", order_id)

    if current_sts_id != REQUIRED_CURRENT_STATUS_ID:
        return _fail(
            "current_sts_id must be %d." % REQUIRED_CURRENT_STATUS_ID,
            order_id,
        )

    user_id = _to_long(user_id)
    if user_id is None:
        return _fail("user_id is required.", order_id)

    have_issue = _to_long(have_issue)
    if have_issue not in (0, 1):
        return _fail("have_issue must be 0 or 1.", order_id)

    if not erd_date or not str(erd_date).strip():
        return _fail("erd_date is required.", order_id)

    if not rerd_date or not str(rerd_date).strip():
        return _fail("rerd_date is required.", order_id)

    erd_date = str(erd_date).strip()
    rerd_date = str(rerd_date).strip()

    if not _is_valid_date(erd_date):
        return _fail("erd_date must be in dd/mm/yyyy format.", order_id)

    if not _is_valid_date(rerd_date):
        return _fail("rerd_date must be in dd/mm/yyyy format.", order_id)

    # ------------------------------------------------------------------
    # 2. Database work (single transaction inside the repository)
    # ------------------------------------------------------------------
    try:
        result = receive_order_by_production_record(
            order_id=order_id,
            current_sts_id=current_sts_id,
            user_id=user_id,
            remarks=remarks,
            have_issue=have_issue,
            erd_date=erd_date,
            rerd_date=rerd_date,
        )
    except Exception as error:  # noqa: BLE001 - surface DB errors as msg="fail"
        return _fail("Database error: %s" % error, order_id)

    if not result["found"]:
        return _fail("Order %d not found." % order_id, order_id)

    if not result["status_matched"]:
        return _fail(
            "Order is currently in status %s, expected %d."
            % (result["status_id"], REQUIRED_CURRENT_STATUS_ID),
            order_id,
            result["status_id"],
        )

    return {
        "order_id": result["order_id"],
        "status_id": result["status_id"],
        "msg": "success",
        "message": "Order received by production.",
    }
