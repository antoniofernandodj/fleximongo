from typing import Optional
from pydantic import BaseModel


class OperationSchema(BaseModel):
    document_id: Optional[str] = None
    payload: Optional[dict] = None


class DeleteSchema(BaseModel):
    document_id: Optional[str] = None


class FindOneSchema(BaseModel):
    document_id: Optional[str] = None


class CreateSchema(BaseModel):
    payload: dict


class FindManySchema(BaseModel):
    payload: dict


class UpdateSchema(BaseModel):
    document_id: str
    payload: dict
