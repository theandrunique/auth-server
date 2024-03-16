from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from src.auth.dependencies import UserAuthorization
from src.mongo_helper import db

from .schemas import AppCreate, AppMongoSchema, AppSchema, AppUpdate

router = APIRouter(prefix="", tags=["apps"])


app_collection = db["apps"]


@router.post("/", response_model=AppSchema)
async def create_app(app: AppCreate, user: UserAuthorization):
    new_app = AppMongoSchema(**app.model_dump(), creator_id=user.id)
    await app_collection.insert_one(new_app.model_dump(by_alias=True))
    return new_app


@router.get("/{app_id}/")
async def get_app_by_id(app_id: UUID, user: UserAuthorization):
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise HTTPException(status_code=404, detail=f"App {app_id} not found")
    app = AppSchema(**found_app)
    if app.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return app


@router.patch("/{app_id}/")
async def update_app(app_id: UUID, data: AppUpdate, user: UserAuthorization):
    new_values = data.model_dump(exclude_defaults=True)

    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise HTTPException(status_code=404, detail=f"App {app_id} not found")

    app = AppSchema(**found_app)

    if app.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    print("im here")
    if new_values:
        updated_app = await app_collection.find_one_and_update(
            {"_id": app_id},
            {"$set": new_values},
            return_document=ReturnDocument.AFTER,
        )
        return AppSchema(**updated_app)
    else:
        return app


@router.delete("/{app_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_app(app_id: UUID, user: UserAuthorization):
    found_app = await app_collection.find_one({"_id": app_id})
    if found_app is None:
        raise HTTPException(status_code=404, detail=f"App {app_id} not found")

    app = AppSchema(**found_app)

    if app.creator_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await app_collection.delete_one({"_id": app_id})