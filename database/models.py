
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from database.db import Base


# ---------------------------------
# USER TABLE
# ---------------------------------

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(String(255), nullable=False)

    role = Column(String(20), default="user", nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    chat_history = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ---------------------------------
# ACCOUNT TABLE
# ---------------------------------

class Account(Base):

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    account_number = Column(
        String(20),
        unique=True,
        nullable=False
    )

    account_type = Column(
        String(50),
        default="savings"
    )

    balance = Column(
        Numeric(12, 2),
        default=0.00,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="accounts"
    )

    transactions = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )


# ---------------------------------
# TRANSACTION TABLE
# ---------------------------------

class Transaction(Base):

    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="positive_transaction_amount"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False
    )

    transaction_type = Column(
        String(30),
        nullable=False
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    description = Column(String(255))

    reference = Column(
        String(50),
        unique=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    account = relationship(
        "Account",
        back_populates="transactions"
    )


# ---------------------------------
# CHAT HISTORY TABLE
# ---------------------------------

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    message = Column(Text, nullable=False)

    response = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship(
        "User",
        back_populates="chat_history"
    )
