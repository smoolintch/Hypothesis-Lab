from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.strategy_cards.service import StrategyCardService
from app.infrastructure.database import get_session
from app.schemas.common import SuccessResponse
from app.schemas.strategy_cards import StrategyCardDetailResponse, StrategyCardUpsertPayload

router = APIRouter(prefix="/strategy-cards", tags=["strategy-cards"])


def get_strategy_card_service(
    session: Session = Depends(get_session),
) -> StrategyCardService:
    return StrategyCardService(session)


@router.post(
    "",
    response_model=SuccessResponse[StrategyCardDetailResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_strategy_card(
    payload: StrategyCardUpsertPayload,
    service: StrategyCardService = Depends(get_strategy_card_service),
) -> SuccessResponse[StrategyCardDetailResponse]:
    detail = service.create(payload)
    return SuccessResponse[StrategyCardDetailResponse](data=detail)


@router.get(
    "/{strategy_card_id}",
    response_model=SuccessResponse[StrategyCardDetailResponse],
    status_code=status.HTTP_200_OK,
)
def get_strategy_card(
    strategy_card_id: UUID,
    service: StrategyCardService = Depends(get_strategy_card_service),
) -> SuccessResponse[StrategyCardDetailResponse]:
    detail = service.get(strategy_card_id)
    return SuccessResponse[StrategyCardDetailResponse](data=detail)


@router.put(
    "/{strategy_card_id}",
    response_model=SuccessResponse[StrategyCardDetailResponse],
    status_code=status.HTTP_200_OK,
)
def update_strategy_card(
    strategy_card_id: UUID,
    payload: StrategyCardUpsertPayload,
    service: StrategyCardService = Depends(get_strategy_card_service),
) -> SuccessResponse[StrategyCardDetailResponse]:
    detail = service.update(strategy_card_id, payload)
    return SuccessResponse[StrategyCardDetailResponse](data=detail)
