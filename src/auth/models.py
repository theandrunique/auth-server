import datetime

from models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class UserInDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[bytes]
    created_at: Mapped[datetime.datetime]
    active: Mapped[bool] = mapped_column(default=True)


class RefreshTokenInDB(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    jti: Mapped[str]
    created_at: Mapped[datetime.datetime]
    last_accessed: Mapped[datetime.datetime]
    ip_address: Mapped[str | None] = mapped_column(nullable=True)
