from app.extensions import db
from sqlalchemy import text
from flask_jwt_extended import get_jwt


# -------------------------
# Dashboard summary
# -------------------------
def get_ledger_data():

    claims = get_jwt()
    company_id = claims["company_id"]

    income_query = """
    SELECT 
        g.name AS group_name,
        l.name AS ledger_name,
        SUM(
            CASE 
                WHEN le.amount_is_debit = 0 
                THEN le.amount_amount
                ELSE -le.amount_amount
            END
        ) AS amount
    FROM vch_ledger_entries le
    JOIN vouchers v ON v.guid = le.voucher_guid
    JOIN ledgers l ON l.guid = le.ledger_id
    JOIN master.groups g ON g.guid = l.group_id
    WHERE 
        v.company_id = :company_id
        AND (v.is_deleted = 0 OR v.is_deleted IS NULL)
        AND g.name IN ('Sales Accounts','Direct Incomes','Indirect Incomes')
    GROUP BY g.name, l.name
    ORDER BY amount DESC
    """

    expense_query = """
    SELECT 
        g.name AS group_name,
        l.name AS ledger_name,
        SUM(
            CASE 
                WHEN le.amount_is_debit = 1 
                THEN le.amount_amount
                ELSE -le.amount_amount
            END
        ) AS amount
    FROM vch_ledger_entries le
    JOIN vouchers v ON v.guid = le.voucher_guid
    JOIN ledgers l ON l.guid = le.ledger_id
    JOIN master.groups g ON g.guid = l.group_id
    WHERE 
        v.company_id = :company_id
        AND (v.is_deleted = 0 OR v.is_deleted IS NULL)
        AND g.name IN ('Direct Expenses','Indirect Expenses')
    GROUP BY g.name, l.name
    ORDER BY amount DESC
    """

    income_result = db.session.execute(
        text(income_query),
        {"company_id": company_id}
    )

    expense_result = db.session.execute(
        text(expense_query),
        {"company_id": company_id}
    )

    income = []
    expenses = []

    for r in income_result:
        income.append({
            "group": r.group_name,
            "ledger": r.ledger_name,
            "amount": float(r.amount)
        })

    for r in expense_result:
        expenses.append({
            "group": r.group_name,
            "ledger": r.ledger_name,
            "amount": float(r.amount)
        })

    return {
        "income": income,
        "expenses": expenses
    }


# -------------------------
# View all income / expenses
# -------------------------
def get_ledger_details(type):

    claims = get_jwt()
    company_id = claims["company_id"]

    if type == "income":

        query = """
        SELECT 
            v.date,
            v.voucher_number,
            l.name AS ledger,
            le.amount_amount AS amount
        FROM vch_ledger_entries le
        JOIN vouchers v ON v.guid = le.voucher_guid
        JOIN ledgers l ON l.guid = le.ledger_id
        JOIN master.groups g ON g.guid = l.group_id
        WHERE 
            v.company_id = :company_id
            AND g.name IN ('Sales Accounts','Direct Incomes','Indirect Incomes')
        ORDER BY v.date DESC
        """

    else:

        query = """
        SELECT 
            v.date,
            v.voucher_number,
            l.name AS ledger,
            le.amount_amount AS amount
        FROM vch_ledger_entries le
        JOIN vouchers v ON v.guid = le.voucher_guid
        JOIN ledgers l ON l.guid = le.ledger_id
        JOIN master.groups g ON g.guid = l.group_id
        WHERE 
            v.company_id = :company_id
            AND g.name IN ('Direct Expenses','Indirect Expenses')
        ORDER BY v.date DESC
        """

    result = db.session.execute(
        text(query),
        {"company_id": company_id}
    )

    data = []

    for r in result:
        data.append({
            "date": str(r.date),
            "voucher": r.voucher_number,
            "ledger": r.ledger,
            "amount": float(r.amount)
        })

    return data


# -------------------------
# Voucher entries of ledger
# -------------------------
def get_ledger_entry(ledger_name, start_date=None, end_date=None):

    claims = get_jwt()
    company_id = claims["company_id"]

    query = """
    SELECT 
        l.name AS ledger_name,
        g.name AS expense_group,
        v.date,
        le.amount_amount AS total,
        cp.name AS counterparty
    FROM vch_ledger_entries le

    JOIN vouchers v 
        ON v.guid = le.voucher_guid

    JOIN ledgers l 
        ON l.guid = le.ledger_id

    JOIN master.groups g 
        ON g.guid = l.group_id

    JOIN vch_ledger_entries le2
        ON le2.voucher_guid = v.guid
        AND le2.ledger_id != le.ledger_id

    JOIN ledgers cp
        ON cp.guid = le2.ledger_id

    WHERE 
        v.company_id = :company_id
        AND (v.is_deleted = 0 OR v.is_deleted IS NULL)
        AND l.name = :ledger_name
    """

    params = {
        "ledger_name": ledger_name,
        "company_id": company_id
    }

    if start_date and end_date:
        query += " AND v.date BETWEEN :start_date AND :end_date "
        params["start_date"] = start_date
        params["end_date"] = end_date

    query += " ORDER BY v.date DESC "

    result = db.session.execute(text(query), params)

    rows = []

    for r in result:
        rows.append({
            "ledger_name": r.ledger_name,
            "expense_group": r.expense_group,
            "date": str(r.date),
            "total": float(r.total),
            "counterparty": r.counterparty
        })

    return rows