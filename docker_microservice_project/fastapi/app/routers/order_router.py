"""
Optional REST endpoint. It calls the exact same service function as the
GraphQL resolver, so there is no duplicated database logic.

POST /api/order/production-update
"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.order_service import receive_order_by_production

order_router = APIRouter(prefix="/api", tags=["order"])


class ProductionOrderUpdate(BaseModel):
    order_id: Optional[int] = None
    current_sts_id: Optional[int] = None
    user_id: Optional[int] = None
    remarks: Optional[str] = None
    have_issue: Optional[str] = None
    erd_date: Optional[str] = None   # dd/mm/yyyy
    rerd_date: Optional[str] = None  # dd/mm/yyyy


@order_router.post("/order/production-update")
def production_update(payload: ProductionOrderUpdate):
    return receive_order_by_production(
        order_id=payload.order_id,
        current_sts_id=payload.current_sts_id,
        user_id=payload.user_id,
        remarks=payload.remarks,
        have_issue=payload.have_issue,
        erd_date=payload.erd_date,
        rerd_date=payload.rerd_date,
    )
