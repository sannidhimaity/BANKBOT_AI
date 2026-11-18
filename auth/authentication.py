
import re
import secrets
import bcrypt

from decimal import Decimal
from sqlalchemy.orm import Session

from database.models import User, Account


def validate_registration(name, email, password):
    """Validate registration details."""

    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return False, "Name must contain at least 2 characters."

    if len(name) > 100:
        return False, "Name is too long."

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must not exceed 72 UTF-8 bytes."

    return True, "Validation successful."


def hash_password(password):
    """Securely hash a password using bcrypt."""

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    """Check password against stored hash."""

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def generate_account_number(db):
    """Generate a unique simulated account number."""

    while True:
        account_number = str(
            secrets.randbelow(10**12)
        ).zfill(12)

        existing = db.query(Account).filter(
            Account.account_number == account_number
        ).first()

        if not existing:
            return account_number


def register_user(db: Session, name, email, password):
    """Register a new user and create their bank account."""

    name = name.strip()
    email = email.strip().lower()

    valid, message = validate_registration(
        name, email, password
    )

    if not valid:
        return False, message

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return False, "An account with this email already exists."

    try:
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="user"
        )

        db.add(new_user)
        db.flush()

        new_account = Account(
            user_id=new_user.id,
            account_number=generate_account_number(db),
            account_type="savings",
            balance=Decimal("0.00")
        )

        db.add(new_account)

        db.commit()
        db.refresh(new_user)

        return True, "Registration successful!"

    except Exception:
        db.rollback()
        return False, "Registration failed. Please try again."


def authenticate_user(db: Session, email, password):
    """Authenticate an existing user."""

    email = email.strip().lower()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user
