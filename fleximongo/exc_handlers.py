from traceback import print_exc
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fleximongo.exceptions import InvalidOperation
import fleximongo.strategies as strategies


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(exc_class_or_status_code=strategies.DocumentNotFound)
    def document_not_found_exeption_handler(request, exc):
        return JSONResponse(status_code=404, content={"msg": "Document not found"})

    @app.exception_handler(exc_class_or_status_code=strategies.InvalidIDFormat)
    def invalid_id_format_exception_handler(request, exc):
        return JSONResponse(status_code=400, content={"msg": "Invalid ID format"})

    @app.exception_handler(exc_class_or_status_code=ValidationError)
    def validation_error_exception_handler(request, exc):
        return JSONResponse(status_code=422, content={"msg": str(exc)})

    @app.exception_handler(exc_class_or_status_code=strategies.InvalidIDFormat)
    def exc(request, exc):
        print_exc()
        return JSONResponse(status_code=500, content={"msg": str(exc)})

    @app.exception_handler(exc_class_or_status_code=KeyError)
    def invalid_operation_handler_1(request, exc):
        print_exc()
        return JSONResponse(
            status_code=400, content={"msg": "Invalid operation selected"}
        )

    @app.exception_handler(exc_class_or_status_code=InvalidOperation)
    def invalid_operation_handler_2(request, exc):
        return JSONResponse(
            status_code=400, content={"msg": "Invalid operation selected"}
        )
