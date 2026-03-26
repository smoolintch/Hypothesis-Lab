from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.application.errors import AppError


def _error_payload(*, code: str, message: str, details: dict[str, object]) -> dict[str, object]:
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": str(uuid4()),
        },
    }


def register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code=exc.code,
                message=exc.message,
                details=jsonable_encoder(exc.details),
            ),
        )

    @application.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                code="STRATEGY_CARD_VALIDATION_FAILED",
                message="Strategy card validation failed.",
                details={"validation_errors": jsonable_encoder(exc.errors())},
            ),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                code="INTERNAL_SERVER_ERROR",
                message="Unexpected server error.",
                details={"error_type": exc.__class__.__name__},
            ),
        )
