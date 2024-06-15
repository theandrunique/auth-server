from typing import Any
from uuid import UUID

import bson
from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


class PyObjectId(bson.ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        def validate(value: str) -> PyObjectId:
            if not PyObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return PyObjectId(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class Scope(BaseModel):
    name: str
    description: str | None = Field(default=None)


class AuthoritativeApp(BaseModel):
    client_id: UUID
    client_secret: UUID
    redirect_uris: list[str]
    scopes: list[Scope]
