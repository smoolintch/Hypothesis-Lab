from fastapi import APIRouter

from app.api.routes import strategy_cards_router

api_router = APIRouter()
api_router.include_router(strategy_cards_router)
