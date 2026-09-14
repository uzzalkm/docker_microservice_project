from ariadne import MutationType
from app.services.customer_service import (
    create_customer,
    update_customer,
    delete_customer
)

mutation = MutationType()

@mutation.field("createCustomer")
def resolve_create_customer(_, info, CUSTOMER_NAME, EMP_NAME):
    return create_customer(
        CUSTOMER_NAME,
        EMP_NAME
    )

@mutation.field("updateCustomer")
def resolve_update_customer(_, info, id, CUSTOMER_NAME, EMP_NAME):
    return update_customer(
        id,
        CUSTOMER_NAME,
        EMP_NAME
    )

@mutation.field("deleteCustomer")
def resolve_delete_customer(_, info, id):
    return delete_customer(id)