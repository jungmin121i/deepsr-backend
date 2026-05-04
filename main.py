from fastapi import FastAPI
from api import market, query, websocket, analysis

app = FastAPI()

app.include_router(market.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(websocket.router)

