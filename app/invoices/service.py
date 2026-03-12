import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import Invoice

UPLOAD_FOLDER = "uploads/invoices"

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_invoice_service(file):

    if file.filename == "":
        return {"error": "No selected file"}, 400

    if not allowed_file(file.filename):
        return {"error": "Invalid file type"}, 400

    filename = secure_filename(file.filename)

    upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)

    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    file.save(file_path)

    user_email = get_jwt_identity()

    invoice = Invoice(
        user_email=user_email,
        file_name=filename,
        file_path=file_path
    )

    db.session.add(invoice)
    db.session.commit()

    return {
        "message": "Invoice uploaded successfully",
        "file": filename
    }, 200