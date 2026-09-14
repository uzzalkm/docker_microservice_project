from app.database.oracle import get_connection

NEW_STATUS_ID = 19
SYSTEM_REMARKS = "update from production with api"


def _next_id(cursor, table_name):
    """
    ID = last id + 1 of the existing table.

    NOTE: MAX(ID)+1 is not concurrency safe. If two requests run at the same
    time they can both read the same MAX and the INSERT will fail on the
    primary key. If a sequence exists (e.g. ACCS_ORDER_LOG_SEQ), replace this
    with:  SELECT ACCS_ORDER_LOG_SEQ.NEXTVAL FROM DUAL
    """
    cursor.execute("SELECT NVL(MAX(ID), 0) + 1 FROM %s" % table_name)
    return int(cursor.fetchone()[0])


def receive_order_by_production_record(
    order_id,
    current_sts_id,
    user_id,
    remarks,
    have_issue,
    erd_date,
    rerd_date,
):
    """
    Runs the whole operation in ONE transaction:
        1. UPDATE ACCS_ORDER
        2. INSERT ACCS_PUNIT_SCHEDULE_DATE
        3. INSERT ACCS_ORDER_LOG
    Commits only if all three succeed, otherwise rolls everything back.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # ------------------------------------------------------------------
        # 0. Lock the order row and read its current status.
        #    FOR UPDATE prevents two production users from receiving the same
        #    order at the same time.
        # ------------------------------------------------------------------
        cursor.execute(
            """
            SELECT STATUS_ID
              FROM ACCS_ORDER
             WHERE ID = :order_id
               FOR UPDATE
            """,
            {"order_id": order_id},
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return {
                "found": False,
                "status_matched": False,
                "order_id": order_id,
                "status_id": None,
            }

        db_status_id = int(row[0]) if row[0] is not None else None

        if db_status_id != current_sts_id:
            connection.rollback()
            return {
                "found": True,
                "status_matched": False,
                "order_id": order_id,
                "status_id": db_status_id,
            }

        # ------------------------------------------------------------------
        # 1. UPDATE ACCS_ORDER
        # ------------------------------------------------------------------
        cursor.execute(
            """
            UPDATE ACCS_ORDER
               SET IS_ORDER_RCVD_BY_PROD        = 1,
                   ORDER_RCVD_BY_PROD_DATE      = SYSDATE,
                   PUNIT_TENTATIVE_DELV_DATE     = TO_DATE(:erd_date,  'dd/mm/yyyy'),
                   PUNIT_TENTATIVE_DELV_END_DATE = TO_DATE(:rerd_date, 'dd/mm/yyyy'),
                   HAVE_ISSUE                   = :have_issue,
                   STATUS_ID                    = :status_id,
                   IS_BACKED                    = 0,
                   REMARKS                      = :remarks,
                   LAST_MODIFIED_DATE           = SYSDATE,
                   LAST_MODIFIED_BY_ID          = :user_id
             WHERE ID = :order_id
            """,
            {
                "erd_date": erd_date,
                "rerd_date": rerd_date,
                "have_issue": have_issue,
                "status_id": NEW_STATUS_ID,
                "remarks": remarks,
                "user_id": user_id,
                "order_id": order_id,
            },
        )

        # ------------------------------------------------------------------
        # 2. INSERT ACCS_PUNIT_SCHEDULE_DATE
        # ------------------------------------------------------------------
        schedule_id = _next_id(cursor, "ACCS_PUNIT_SCHEDULE_DATE")

        cursor.execute(
            """
            INSERT INTO ACCS_PUNIT_SCHEDULE_DATE
            (
                ID,
                ACCS_ORDER_ID,
                RERD_DATE,
                CREATED_BY,
                CREATED_DATE,
                REMARKS
            )
            VALUES
            (
                :id,
                :order_id,
                TO_DATE(:rerd_date, 'dd/mm/yyyy'),
                :user_id,
                SYSDATE,
                :remarks
            )
            """,
            {
                "id": schedule_id,
                "order_id": order_id,
                "rerd_date": rerd_date,
                "user_id": user_id,
                "remarks": SYSTEM_REMARKS,
            },
        )

        # ------------------------------------------------------------------
        # 3. INSERT ACCS_ORDER_LOG
        # ------------------------------------------------------------------
        log_id = _next_id(cursor, "ACCS_ORDER_LOG")

        cursor.execute(
            """
            INSERT INTO ACCS_ORDER_LOG
            (
                ID,
                ACCS_ORDER_ID,
                PROCESS_BY_ID,
                PROCESS_DATE,
                STATUS_ID,
                REMARKS,
                IS_BACKED
            )
            VALUES
            (
                :id,
                :order_id,
                :user_id,
                SYSDATE,
                :status_id,
                :remarks,
                0
            )
            """,
            {
                "id": log_id,
                "order_id": order_id,
                "user_id": user_id,
                "status_id": NEW_STATUS_ID,
                "remarks": SYSTEM_REMARKS,
            },
        )

        connection.commit()

        # ------------------------------------------------------------------
        # 4. Read back the committed row for the response
        # ------------------------------------------------------------------
        cursor.execute(
            """
            SELECT ID,
                   STATUS_ID
              FROM ACCS_ORDER
             WHERE ID = :order_id
            """,
            {"order_id": order_id},
        )
        final_row = cursor.fetchone()

        return {
            "found": True,
            "status_matched": True,
            "order_id": int(final_row[0]),
            "status_id": int(final_row[1]) if final_row[1] is not None else None,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()
