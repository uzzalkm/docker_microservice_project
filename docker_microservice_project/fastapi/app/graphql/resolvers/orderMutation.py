from ariadne import MutationType

from app.services.order_service import receive_order_by_production

order_mutation = MutationType()


@order_mutation.field("receiveOrderByProduction")
def resolve_receive_order_by_production(
    _,
    info,
    order_id,
    current_sts_id,
    user_id,
    have_issue,
    erd_date,
    rerd_date,
    remarks=None,
):
    return receive_order_by_production(
        order_id=order_id,
        current_sts_id=current_sts_id,
        user_id=user_id,
        remarks=remarks,
        have_issue=have_issue,
        erd_date=erd_date,
        rerd_date=rerd_date,
    )
