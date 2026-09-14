from ariadne import QueryType

from app.services.customer_service import (
find_customer,
find_customers
)

query = QueryType()

@query.field("customer")
def resolve_customer(_, info, id):
    return find_customer(id)
    
@query.field("customers")
def resolve_customers(_, info):
    return find_customers()
    
    