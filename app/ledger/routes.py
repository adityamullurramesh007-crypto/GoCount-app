from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.ledger.service import (
    get_ledger_data,
    get_ledger_details,
    get_ledger_entry
)

ledger_bp = Blueprint("ledger", __name__)


# -------------------------
# Dashboard summary
# -------------------------
@ledger_bp.route("/summary", methods=["GET"])
@jwt_required()
def ledger_summary():
    return get_ledger_data()


# -------------------------
# View all income / expenses
# -------------------------
@ledger_bp.route("/details/<type>", methods=["GET"])
@jwt_required()
def ledger_details(type):
    return get_ledger_details(type)


# -------------------------
# Ledger voucher entries
# -------------------------
@ledger_bp.route("/entry/<ledger_name>", methods=["GET"])
@jwt_required()
def ledger_entry_route(ledger_name):

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    return get_ledger_entry(ledger_name, start_date, end_date)