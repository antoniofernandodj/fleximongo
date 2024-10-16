from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping
from bson import ObjectId
from fleximongo.exceptions import DocumentNotFound, InvalidIDFormat
import fleximongo.schemas as schemas


class DatabaseOperationStrategy(ABC):
    def __init__(self, collection):
        self.collection = collection

    @abstractmethod
    async def executar(self) -> Any:
        raise NotImplementedError


class CreateDocumentStrategy(DatabaseOperationStrategy):
    async def executar(self, payload: dict):

        result = await self.collection.insert_one(payload)
        return {
            "message": "Document created",
            "id": str(result.inserted_id),
        }


class FindDocumentsStrategy(DatabaseOperationStrategy):
    async def executar(self, filters: Dict[str, Any] = {}, limit: int = 100):

        documents = await self.collection.find(filters).to_list(limit)
        return {"documents": [str(doc["_id"]) for doc in documents]}


class FindDocumentStrategy(DatabaseOperationStrategy):
    async def executar(self, document_id: str):

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        document = await self.collection.find_one({"_id": obj_id})
        if document is None:
            raise DocumentNotFound

        document["_id"] = str(document["_id"])
        return {"document": document}


class DeleteDocumentStrategy(DatabaseOperationStrategy):
    async def executar(self, document_id: str):

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        result = await self.collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise DocumentNotFound

        return {"message": "Document deleted"}


class UpdateDocumentStrategy(DatabaseOperationStrategy):
    async def executar(self, document_id: str, payload: Dict[str, Any]):

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        result = await self.collection.update_one({"_id": obj_id}, {"$set": payload})

        if result.matched_count == 0:
            raise DocumentNotFound

        return {"message": "Document updated"}


class ClearCollectionStrategy(DatabaseOperationStrategy):
    async def executar(self) -> Any:
        result = await self.collection.delete_many({})
        return {"message": f"Documentos deletados: {result.deleted_count}"}


class Operation:
    def __init__(self, strategy: DatabaseOperationStrategy) -> None:
        self.strategy = strategy
        self.options: Dict[str, Any] = {}

    async def excecute_operation(self) -> Any:
        print(self.options)
        return await self.strategy.executar(**self.options)

    def set_options(
        self, operation_name: str, body: schemas.OperationSchema
    ) -> Operation:

        if operation_name == "find-many":
            data = schemas.FindManySchema(payload=body.payload)
            self.options = {"filters": data.payload}

        elif operation_name == "create":
            data = schemas.CreateSchema(payload=body.payload)
            self.options = {"payload": data.payload}

        elif operation_name == "update":
            data = schemas.UpdateSchema(
                document_id=body.document_id, payload=body.payload
            )
            self.options = {
                "document_id": data.document_id,
                "payload": data.payload,
            }

        elif operation_name == "find-one":
            data = schemas.FindOneSchema(document_id=body.document_id)
            self.options = {"document_id": data.document_id}

        elif operation_name == "delete":
            data = schemas.DeleteSchema(document_id=body.document_id)
            self.options = {"document_id": data.document_id}

        return self


operation_mapping: Mapping[str, DatabaseOperationStrategy] = {
    "clear-collection": ClearCollectionStrategy,
    "find-many": FindDocumentsStrategy,
    "create": CreateDocumentStrategy,
    "find-one": FindDocumentStrategy,
    "delete": DeleteDocumentStrategy,
    "update": UpdateDocumentStrategy,
}
