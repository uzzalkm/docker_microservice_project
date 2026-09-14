from app.database.oracle import get_connection

def get_customer(customer_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ID,
            CUSTOMER_NAME,
            EMP_NAME
        FROM ACCS_CUSTOMER
        WHERE ID = :id
    """, {"id": customer_id})

    row = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if row:
        return {
            "id": row[0],
            "CUSTOMER_NAME": row[1],
            "EMP_NAME": row[2]
        }

    return None
    
    
def get_customers():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ID,
            CUSTOMER_NAME,
            EMP_NAME
        FROM ACCS_CUSTOMER
        ORDER BY ID
    """)
    
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()

    customers = []
    for row in rows:
        customers.append({
            "id": row[0],
            "CUSTOMER_NAME": row[1],
            "EMP_NAME": row[2]
        })
        
    return customers
    
def insert_customer(CUSTOMER_NAME, EMP_NAME):
    connection = get_connection()
    cursor = connection.cursor()
    new_id = cursor.var(int)
    cursor.execute("""
        INSERT INTO ACCS_CUSTOMER
        (
          ID,
          CUSTOMER_NAME,
          EMP_NAME
        )
        VALUES
        (
          (SELECT NVL(MAX(ID), 0) + 1 FROM ACCS_CUSTOMER),
          :CUSTOMER_NAME,
          :EMP_NAME
        )
        RETURNING ID INTO :id
    """,
    {
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "EMP_NAME": EMP_NAME,
        "id": new_id
    })
    connection.commit()
    customer_id = new_id.getvalue()[0]
    cursor.close()
    connection.close()
    return {
        "id": customer_id,
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "EMP_NAME": EMP_NAME
    }
      
def update_customer_record(id,CUSTOMER_NAME,EMP_NAME):
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute("""
        UPDATE ACCS_CUSTOMER
        SET
          CUSTOMER_NAME=:CUSTOMER_NAME,
          EMP_NAME=:EMP_NAME
        WHERE ID=:id
    """,
    {
        "id":id,
        "CUSTOMER_NAME":CUSTOMER_NAME,
        "EMP_NAME":EMP_NAME
    })
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "id":id,
        "CUSTOMER_NAME":CUSTOMER_NAME,
        "EMP_NAME":EMP_NAME
    }
     
def delete_customer_record(id):
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute("""
        DELETE FROM ACCS_CUSTOMER
        WHERE ID=:id
    """,
    {
        "id":id
    })
    connection.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    connection.close()
    return deleted