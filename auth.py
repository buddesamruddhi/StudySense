import re
from werkzeug.security import generate_password_hash, check_password_hash
import database as db

def validate_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))

def register_user(full_name, email, password, confirm):
    if not full_name.strip():
        raise ValueError("Please enter your full name.")
    if not validate_email(email):
        raise ValueError("Enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if password != confirm:
        raise ValueError("Passwords do not match.")
    if db.user_by_email(email):
        raise ValueError("An account with this email already exists.")
    return db.create_user(full_name, email, generate_password_hash(password))

def login_user(email, password):
    user = db.user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return None
    return user
