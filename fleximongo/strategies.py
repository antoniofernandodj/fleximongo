from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Type, Union
from bson import ObjectId
from fleximongo.exceptions import DocumentNotFound, InvalidIDFormat
import fleximongo.schemas as schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from fleximongo.utils import register_strategy



operation_mapping: Dict[str, Type['DatabaseOperationStrategy']] = {}

Payload = Optional[Union[List[dict], dict]]
Filters = Optional[Dict[str, Any]]
Pipeline = Optional[List[Dict[str, Any]]]


class DatabaseOperationStrategy(ABC):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    @abstractmethod
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ) -> Any:
        raise NotImplementedError


@register_strategy('create', operation_mapping)
class CreateDocumentStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):

        if not isinstance(payload, dict):
            raise ValueError("payload dict is required")

        p = payload.pop('payload', None)
        if p:
            payload = p

        payload.pop('_id', None)
        result = await self.collection.insert_one(payload)
        return {
            "message": "Document created",
            "id": str(result.inserted_id),
        }


@register_strategy('find-many', operation_mapping)
class FindManyDocumentsStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Optional[Dict[str, Any]] = {},
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):
        if filters is None:
            filters = {}

        for key, value in filters.items():
            if key == '_id':
                filters[key] = ObjectId(value)

        query = self.collection.find(filters)

        if page and limit:
            skip = (page - 1) * limit
            query = query.skip(skip).limit(limit)

        documents = await query.to_list(None)
        for document in documents:
            document["_id"] = str(document["_id"])

        print(documents)
        return documents


@register_strategy('find', operation_mapping)
class FindOneDocumentStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Optional[Dict[str, Any]] = {},
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):
        if document_id is None:
            raise ValueError("document_id is required")

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        document = await self.collection.find_one({"_id": obj_id})
        if document is None:
            raise DocumentNotFound

        document["_id"] = str(document["_id"])
        return document


@register_strategy('find-with-pagination', operation_mapping)
class FindWithPaginationStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Optional[Dict[str, Any]] = {},
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        pipeline: Pipeline = None
    ):

        if page is None:
            raise ValueError("page is required")
        if limit is None:
            raise ValueError("limit is required")

        skip = (page - 1) * limit
        documents = (
            await self.collection
                .find(filters)
                .skip(skip)
                .limit(limit)
                .to_list(None)
        )

        for document in documents:
            document["_id"] = str(document["_id"])

        return documents


@register_strategy('delete', operation_mapping)
class DeleteDocumentStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Optional[Dict[str, Any]] = {},
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        pipeline: Pipeline = None
    ):
        if document_id is None:
            raise ValueError("document_id is required")

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        result = await self.collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise DocumentNotFound

        return {"message": "Document deleted"}


@register_strategy('update', operation_mapping)
class UpdateDocumentStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):
        if document_id is None:
            raise ValueError("document_id is required")
        if payload is None:
            raise ValueError("payload is required")

        try:
            obj_id = ObjectId(document_id)
        except Exception:
            raise InvalidIDFormat

        result = await self.collection.update_one({"_id": obj_id}, {"$set": payload})
        if result.matched_count == 0:
            raise DocumentNotFound

        return {"message": "Document updated"}


@register_strategy('create-many', operation_mapping)
class CreateManyDocumentsStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):

        if not isinstance(payload, list):
            raise ValueError("payload must be a list")

        for doc in payload:
            doc.pop('_id', None)

        result = await self.collection.insert_many(payload)
        return {
            "message": "Documents created",
            "ids": [str(id) for id in result.inserted_ids],
        }


@register_strategy('count', operation_mapping)
class CountDocumentsStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = {},
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):
        if filters is None:
            filters = {}
        count = await self.collection.count_documents(filters)
        return {"count": count}


@register_strategy('aggregate', operation_mapping)
class AggregateDocumentsStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = {},
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = []
    ):
        if pipeline is None:
            pipeline = []
        result = await self.collection.aggregate(pipeline).to_list(None)
        for document in result:
            document["_id"] = str(document["_id"])
        return result


@register_strategy('drop-collection', operation_mapping)
class DropCollectionStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ):
        await self.collection.drop()
        return {"message": "Collection dropped"}


@register_strategy('clear-collection', operation_mapping)
class ClearCollectionStrategy(DatabaseOperationStrategy):
    async def executar(
        self,
        document_id: Optional[str] = None,
        payload: Payload = None,
        filters: Filters = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        pipeline: Pipeline = None
    ) -> Any:
        result = await self.collection.delete_many({})
        return {"message": f"Documentos deletados: {result.deleted_count}"}


class Operation:
    def __init__(self, strategy: DatabaseOperationStrategy) -> None:
        self.strategy = strategy
        self.options: Dict[str, Any] = {}

    async def execute_operation(self) -> Any:
        print(self.options)
        return await self.strategy.executar(**self.options)

    def set_options(
        self,
        operation_name: str,
        body: schemas.OperationSchema
    ) -> Operation:

        if operation_name == "find-many":
            data = schemas.FindManySchema(payload=body.payload)  # type: ignore
            self.options = {"filters": data.payload}

        elif operation_name == "create":
            data = schemas.CreateSchema(payload=body.payload)  # type: ignore
            self.options = {"payload": data.payload}

        elif operation_name == "find":
            data = schemas.FindOneSchema(document_id=body.document_id)  # type: ignore
            self.options = {"document_id": data.document_id}

        elif operation_name == "delete":
            data = schemas.DeleteSchema(document_id=body.document_id)  # type: ignore
            self.options = {"document_id": data.document_id}

        elif operation_name == 'find-with-pagination':
            raise NotImplementedError

        elif operation_name == 'create-many':
            raise NotImplementedError

        elif operation_name == 'count':
            raise NotImplementedError

        elif operation_name == 'aggregate':
            raise NotImplementedError

        elif operation_name == 'drop-collection':
            pass  # no args

        elif operation_name == 'clear-collection':
            pass  # no args

        elif operation_name == "update":
            data = schemas.UpdateSchema(
                document_id=body.document_id, payload=body.payload  # type: ignore
            )
            self.options = {
                "document_id": data.document_id,
                "payload": data.payload,
            }

        return self
