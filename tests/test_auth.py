import jwt
import pytest
from conftest import client, db_helper

from src.auth.crud import get_user_from_db_by_username, get_user_session_from_db
from src.config import settings


def test_register():
    response = client.post(
        "/auth/register/",
        json={
            "username": "johndoe",
            "password": "12345",
            "email": "test@test.com",
        },
    )
    assert response.status_code == 201, response.json()


def test_register_name_exists_error():
    response = client.post(
        "/auth/register/",
        json={
            "username": "johndoe",
            "password": "12345",
            "email": "test@test.com",
        },
    )
    assert response.status_code == 400, response.json()


def test_get_token():
    # by username
    response = client.post(
        "/auth/login/",
        json={
            "login": "johndoe",
            "password": "12345",
        },
    )
    assert response.status_code == 200, response.json()
    # by email
    response = client.post(
        "/auth/login/",
        json={
            "login": "test@test.com",
            "password": "12345",
        },
    )
    assert response.status_code == 200, response.json()


@pytest.mark.asyncio
async def test_get_sessions(jwt_user_token):
    token = jwt_user_token

    response = client.get(
        "/auth/sessions/",
        headers={"Authorization": f"{token}"},
    )
    assert response.status_code == 200, response.json()

    async with db_helper.session_factory() as session:
        user = await get_user_from_db_by_username(username="johndoe", session=session)
        assert user is not None


@pytest.mark.asyncio
async def test_logout_token(jwt_user_token):
    token = jwt_user_token

    response = client.delete(
        "/auth/logout/",
        headers={"Authorization": f"{token}"},
    )
    assert response.status_code == 204, response.json()

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    async with db_helper.session_factory() as session:
        prev_token = await get_user_session_from_db(
            user_id=payload["user_id"],
            session_id=payload["jti"],
            session=session,
        )
        assert prev_token is None, prev_token

