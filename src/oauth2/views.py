from enum import Enum

from fastapi import APIRouter

from src.apps.exceptions import AppNotFound
from src.apps.registry import AppsRegistry
from src.dependencies import DbSession, UserAuthorization
from src.oauth2.crud import OAuth2SessionsDB
from src.redis_helper import redis_client

from .config import settings
from .exceptions import (
    AuthorizationTypeIsNotSupported,
    InvalidAuthorizationCode,
    InvalidClientSecret,
    InvalidSession,
    NotAllowedScope,
    RedirectUriNotAllowed,
)
from .schemas import (
    OAuth2AuthorizeRequest,
    OAuth2AuthorizeResponse,
    OAuth2CodeExchangeRequest,
    OAuth2CodeExchangeResponse,
    RefreshTokenRequest,
)
from .utils import (
    gen_authorization_code,
    gen_token_pair_and_create_session,
    get_bytes_from_token,
    hash_token,
    update_session_and_gen_new_token,
)

router = APIRouter(prefix="", tags=["oauth2"])


class ResponseType(Enum):
    CODE = "code"


@router.post("/authorize/", response_model_exclude_none=True)
async def oauth2_authorize(
    data: OAuth2AuthorizeRequest,
    user: UserAuthorization,
) -> OAuth2AuthorizeResponse:
    app = await AppsRegistry.get_by_client_id(data.client_id)
    if not app:
        raise AppNotFound()

    if data.redirect_uri not in app.redirect_uris:
        raise RedirectUriNotAllowed()

    disallowed_scopes = [scope for scope in data.scopes if scope not in app.scopes]
    if disallowed_scopes:
        raise NotAllowedScope(disallowed_scopes)

    if data.response_type != ResponseType.CODE.value:
        raise AuthorizationTypeIsNotSupported()

    auth_code = gen_authorization_code()

    await redis_client.set(
        f"auth_code_{app.client_id}_{auth_code}",
        user.id,
        ex=settings.AUTHORIZATION_CODE_EXPIRE_SECONDS,
    )

    return OAuth2AuthorizeResponse(
        code=auth_code,
        state=data.state,
    )


@router.post("/token/")
async def oauth2_exchange_code(
    data: OAuth2CodeExchangeRequest, session: DbSession
) -> OAuth2CodeExchangeResponse:
    app = await AppsRegistry.get_by_client_id(data.client_id)
    if not app:
        raise AppNotFound()
    if data.client_secret != app.client_secret:
        raise InvalidClientSecret()

    user_id = await redis_client.get(f"auth_code_{app.client_id}_{data.code}")
    if not user_id:
        raise InvalidAuthorizationCode()

    await redis_client.delete(f"auth_code_{app.client_id}_{data.code}")

    return await gen_token_pair_and_create_session(
        scopes=app.scopes,
        user_id=user_id,
        app_id=app.id,
        session=session,
    )


@router.post("/refresh/")
async def refresh_token(
    data: RefreshTokenRequest, session: DbSession
) -> OAuth2CodeExchangeResponse:
    oauth2_session = await OAuth2SessionsDB.get_by_token(
        hash_token(get_bytes_from_token(data.refresh_token)), session=session
    )
    if not oauth2_session:
        raise InvalidSession()
    return await update_session_and_gen_new_token(oauth2_session, session)
