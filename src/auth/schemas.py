import datetime
import re
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from src.config import settings
from src.users.config import settings as users_settings

from .exceptions import PasswordValidationError


class UserTokenSchema(BaseModel):
    user_id: int
    token: str


class UserTokenPayload(BaseModel):
    sub: int
    jti: UUID
    exp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=settings.USER_TOKEN_EXPIRE_HOURS),
    )


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class RegistrationSchema(BaseModel):
    username: str = Field(
        min_length=users_settings.USERNAME_MIN_LENGTH,
        max_length=users_settings.USERNAME_MAX_LENGTH,
        pattern=users_settings.USERNAME_PATTERN,
    )
    email: EmailStr
    password: str = Field(
        min_length=users_settings.PASSWORD_MIN_LENGTH,
        max_length=users_settings.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:
        if not re.match(users_settings.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v


class OtpRequestSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(BaseModel):
    login: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    password: str = Field(
        min_length=users_settings.PASSWORD_MIN_LENGTH,
        max_length=users_settings.PASSWORD_MAX_LENGTH,
    )

    @field_validator("password")
    @classmethod
    def check_pattern(cls, v: str) -> str:
        if not re.match(users_settings.PASSWORD_PATTERN, v):
            raise PasswordValidationError()
        return v
