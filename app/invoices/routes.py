from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import text
from app.extensions import db
import os

invoice_bp = Blueprint("invoice", __name__)

BASE_UPLOAD_FOLDER = "uploads"


# ----------------------------
# Upload invoice
# ----------------------------
@invoice_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_invoice():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    claims = get_jwt()
    company_id = claims["company_id"]
    email = claims["sub"]

    # Create company folder
    company_folder = os.path.join(BASE_UPLOAD_FOLDER, f"company_{company_id}")
    os.makedirs(company_folder, exist_ok=True)

    file_path = os.path.join(company_folder, file.filename)

    file.save(file_path)

    # Save in database
    db.session.execute(
        text("""
        INSERT INTO invoices (user_email, file_name, file_path)
        VALUES (:email, :name, :path)
        """),
        {
            "email": email,
            "name": file.filename,
            "path": file_path
        }
    )

    db.session.commit()

    return jsonify({
        "message": "Invoice uploaded successfully",
        "file": file.filename
    })


# ----------------------------
# List uploaded invoices
# ----------------------------
@invoice_bp.route("/list", methods=["GET"])
@jwt_required()
def list_invoices():

    email = get_jwt()["sub"]

    result = db.session.execute(
        text("""
        SELECT id, file_name, uploaded_at
        FROM invoices
        WHERE user_email = :email
        ORDER BY uploaded_at DESC
        """),
        {"email": email}
    )

    invoices = [dict(row._mapping) for row in result]

    return jsonify(invoices)