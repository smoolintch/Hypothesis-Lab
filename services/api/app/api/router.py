from fastapi import APIRouter

from app.api.routes import backtests_router, strategy_cards_router

api_router = APIRouter()
api_router.include_router(strategy_cards_router)
api_router.include_router(backtests_router)
