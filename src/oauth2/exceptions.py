from fastapi import HTTPException, status


class RedirectUriNotAllowed(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redirect URI not allowed",
        )


class NotAllowedScope(HTTPException):
    def __init__(self, scopes: list[str]) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scopes: '{', '.join(scopes)}' not allowed by the app",
        )


class AuthorizationTypeIsNotSupported(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization type is not supported",
        )


class InvalidClientSecret(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client secret",
        )


class InvalidAuthorizationCode(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code",
        )


class InvalidSession(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid session",
        )
