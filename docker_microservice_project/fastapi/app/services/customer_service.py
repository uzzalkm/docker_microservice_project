from app.repositories.customer_repository import (
get_customer,
get_customers,
insert_customer,
update_customer_record,
delete_customer_record
)

#Both REST APIs and GraphQL should call this service, avoiding duplicated database logic.

def find_customer(customer_id):
    return get_customer(customer_id)
    
def find_customers():
    return get_customers()
    
def create_customer(CUSTOMER_NAME, EMP_NAME):
    return insert_customer(
        CUSTOMER_NAME,
        EMP_NAME
    )

def update_customer(id, CUSTOMER_NAME, EMP_NAME):
    return update_customer_record(
        id,
        CUSTOMER_NAME,
        EMP_NAME
    )

def delete_customer(id):
    return delete_customer_record(id)