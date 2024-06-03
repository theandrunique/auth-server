from typing import Any
from uuid import UUID

from fastapi import APIRouter

from src.auth.dependencies import UserAuthorization, UsersServiceDep
from src.logger import logger

from .exceptions import UserNotFound
from .schemas import UserPublic

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(user: UserAuthorization) -> Any:
    return user


@router.get("/@{username}", response_model=UserPublic)
async def get_user_by_username(username: str, users_service: UsersServiceDep) -> Any:
    user = await users_service.get_by_username(username)
    if not user:
        raise UserNotFound()
    return user


@router.get("/search", response_model=list[UserPublic] | None)
async def search_users(query: str, users_service: UsersServiceDep) -> Any:
    result = await users_service.search_by_username(query)
    logger.info(result)
    return result


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: UUID, users_service: UsersServiceDep) -> Any:
    user = await users_service.get(user_id)
    if not user:
        raise UserNotFound()
    return user
