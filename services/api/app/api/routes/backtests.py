from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.backtests.service import BacktestRunService
from app.infrastructure.database import get_session
from app.schemas.backtests import (
    BacktestResultResponse,
    BacktestRunResponse,
    RecentExperimentsResponse,
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/backtests", tags=["backtests"])


def get_backtest_run_service(session: Session = Depends(get_session)) -> BacktestRunService:
    return BacktestRunService(session)


@router.get(
    "/recent",
    response_model=SuccessResponse[RecentExperimentsResponse],
    status_code=status.HTTP_200_OK,
)
def list_recent_experiments(
    service: BacktestRunService = Depends(get_backtest_run_service),
) -> SuccessResponse[RecentExperimentsResponse]:
    detail = service.list_recent_experiments()
    return SuccessResponse[RecentExperimentsResponse](data=detail)


@router.get(
    "/{run_id}",
    response_model=SuccessResponse[BacktestRunResponse],
    status_code=status.HTTP_200_OK,
)
def get_backtest_run(
    run_id: UUID,
    service: BacktestRunService = Depends(get_backtest_run_service),
) -> SuccessResponse[BacktestRunResponse]:
    detail = service.get_run(run_id)
    return SuccessResponse[BacktestRunResponse](data=detail)


@router.get(
    "/{run_id}/result",
    response_model=SuccessResponse[BacktestResultResponse],
    status_code=status.HTTP_200_OK,
)
def get_backtest_result(
    run_id: UUID,
    service: BacktestRunService = Depends(get_backtest_run_service),
) -> SuccessResponse[BacktestResultResponse]:
    detail = service.get_result(run_id)
    return SuccessResponse[BacktestResultResponse](data=detail)
