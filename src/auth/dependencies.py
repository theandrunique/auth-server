from typing import Annotated

from fastapi import Request, Security
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pydantic import ValidationError

from src.auth.models import UserSessionsInDB
from src.database import DbSession
from src.models import UserInDB

from .crud import (
    get_user_with_session_from_db,
    update_last_used,
)
from .exceptions import InactiveUser, InvalidToken, NotAuthenticated, UserNotFound
from .utils import validate_user_token


async def get_authorization_optional(request: Request) -> str | None:
    return request.headers.get("Authorization")


async def get_authorization(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise NotAuthenticated()
    return authorization


async def get_user_with_session(
    session: DbSession,
    token: str = Security(get_authorization),
) -> tuple[UserInDB, UserSessionsInDB]:
    try:
        payload = validate_user_token(token=token)
    except ExpiredSignatureError:
        # TODO: delete expired sessions
        raise InvalidToken()
    except (PyJWTError, ValidationError):
        raise InvalidToken()
    user, user_session = await get_user_with_session_from_db(
        user_id=payload.user_id,
        session_id=payload.jti,
        session=session,
    )
    if user_session is None:
        raise InvalidToken()
    if user is None:
        raise UserNotFound()
    elif not user.active:
        raise InactiveUser()
    await update_last_used(user_session=user_session, session=session)
    return user, user_session


UserAuthorizationWithSession = Annotated[
    tuple[UserInDB, UserSessionsInDB], Security(get_user_with_session)
]


async def get_user(
    user_and_session: UserAuthorizationWithSession,
) -> UserInDB:
    user, _ = user_and_session
    return user


UserAuthorization = Annotated[UserInDB, Security(get_user)]


async def get_user_authorization_optional(
    session: DbSession,
    token: str | None = Security(get_authorization_optional),
) -> UserInDB | None:
    if token is None:
        return None
    else:
        user, _ = await get_user_with_session(session=session, token=token)
        return user


UserAuthorizationOptional = Annotated[
    UserInDB | None, Security(get_user_authorization_optional)
]
