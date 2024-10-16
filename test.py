import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from bson import ObjectId
from app import app


API_URL = "http://localhost:7000/"


headers = {
    "db-name": "test_db",
    "collection-name": "test_collection",
}


@pytest.mark.asyncio
async def test_invalid_operation():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:
        body = {"payload": {"name": "Test Document"}}
        response = await ac.post("/op/post/", json=body)
        assert response.status_code == 400
        assert response.json()["msg"] == "Invalid operation selected"


@pytest.mark.asyncio
async def test_create_document():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:
        body = {"payload": {"name": "Test Document"}}
        response = await ac.post("/op/create/", json=body)
        assert response.status_code == 200
        assert "id" in response.json()


@pytest.mark.asyncio
async def test_create_document_error():
    async with AsyncClient(base_url=API_URL, headers=headers) as ac:
        body = {"payload": None}
        response = await ac.post("/op/create/", json=body)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_find_many_documents():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:

        body1 = {"payload": {"name": "Document 1", "user": "Jane Doe"}}
        body2 = {"payload": {"name": "Document 2", "user": "Jane Doe"}}
        body3 = {"payload": {"name": "Document 2", "user": "John Doe"}}

        await ac.post("/op/create/", json=body1)
        await ac.post("/op/create/", json=body2)
        await ac.post("/op/create/", json=body3)

        find_body = {"payload": {"user": "Jane Doe"}}

        response = await ac.post("/op/find-many/", json=find_body)

        assert response.status_code == 200
        assert "documents" in response.json()
        assert len(response.json()["documents"]) == 2

        find_body = {"payload": {"user": "John Doe"}}

        response = await ac.post("/op/find-many/", json=find_body)

        assert response.status_code == 200
        assert "documents" in response.json()
        assert len(response.json()["documents"]) == 1


@pytest.mark.asyncio
async def test_update_document():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:
        body_create = {"payload": {"name": "Old Document"}}

        create_response = await ac.post("/op/create/", json=body_create)
        document_id = create_response.json()["id"]

        body_update = {
            "document_id": document_id,
            "payload": {"name": "Updated Document"},
        }

        response = await ac.post("/op/update/", json=body_update)

        assert response.status_code == 200
        assert response.json()["message"] == "Document updated"

        body_find_one = {"document_id": document_id}

        find_response = await ac.post("/op/find-one/", json=body_find_one)

        assert find_response.status_code == 200
        assert find_response.json()["document"]["name"] == "Updated Document"


@pytest.mark.asyncio
async def test_delete_document():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:

        body_create = {"payload": {"name": "Document to Delete"}}

        create_response = await ac.post("/op/create/", json=body_create)
        document_id = create_response.json()["id"]

        body_delete = {"document_id": document_id}

        response = await ac.post("/op/delete/", json=body_delete)

        assert response.status_code == 200
        assert response.json()["message"] == "Document deleted"

        body_find = {"document_id": document_id}

        find_response = await ac.post("/op/find-one/", json=body_find)

        assert find_response.status_code == 404


@pytest.mark.asyncio
async def test_clear_database():

    async with AsyncClient(base_url=API_URL, headers=headers) as ac:

        response = await ac.post("/op/clear-collection/", json={})

        assert response.status_code == 200
