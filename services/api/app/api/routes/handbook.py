from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.handbook.service import HandbookService
from app.infrastructure.database import get_session
from app.schemas.common import SuccessResponse
from app.schemas.handbook import HandbookCreatePayload, HandbookEntryResponse

router = APIRouter(prefix="/handbook", tags=["handbook"])


def get_handbook_service(session: Session = Depends(get_session)) -> HandbookService:
    return HandbookService(session)


@router.post(
    "",
    response_model=SuccessResponse[HandbookEntryResponse],
    status_code=status.HTTP_201_CREATED,
)
def add_to_handbook(
    payload: HandbookCreatePayload,
    service: HandbookService = Depends(get_handbook_service),
) -> SuccessResponse[HandbookEntryResponse]:
    detail = service.add_to_handbook(payload)
    return SuccessResponse[HandbookEntryResponse](data=detail)
