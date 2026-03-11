import random
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from app.extensions import db, bcrypt
from app.models import OTPVerification
from app.utils.email import send_email


OTP_EXPIRY_MINUTES = 5


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_service(email):

    # Delete old OTPs for this email
    OTPVerification.query.filter_by(email=email).delete()

    otp = generate_otp()
    otp_hash = bcrypt.generate_password_hash(otp).decode("utf-8")

    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp_entry = OTPVerification(
        email=email,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        created_at=datetime.utcnow(),
    )

    db.session.add(otp_entry)
    db.session.commit()

    # Send email
    send_email(
        subject="Your OTP Code",
        recipients=[email],
        body=f"Your OTP is {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
    )

    return {"message": "OTP sent successfully"}, 200


def verify_otp_service(email, otp_input):

    otp_entry = OTPVerification.query.filter_by(email=email).first()

    if not otp_entry:
        return {"error": "OTP not found"}, 400

    if otp_entry.expires_at < datetime.utcnow():
        return {"error": "OTP expired"}, 400

    if otp_entry.attempts >= 5:
        return {"error": "Too many attempts"}, 400

    if not bcrypt.check_password_hash(otp_entry.otp_hash, otp_input):
        otp_entry.attempts += 1
        db.session.commit()
        return {"error": "Invalid OTP"}, 400

    # OTP valid → delete it
    db.session.delete(otp_entry)
    db.session.commit()

    # 🔹 Fetch company_id from users table
    result = db.session.execute(
        text("SELECT company_id FROM users WHERE email = :email"),
        {"email": email}
    )

    user = result.fetchone()

    if not user:
        return {"error": "User not registered"}, 404

    company_id = user.company_id

    # 🔹 Create JWT token with company_id
    access_token = create_access_token(
        identity=email,
        additional_claims={
            "company_id": company_id
        }
    )

    return {
        "message": "Login successful",
        "token": access_token
    }, 200