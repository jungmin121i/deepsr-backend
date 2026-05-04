from fastapi import APIRouter, WebSocket
import asyncio
import random

router = APIRouter()

@router.websocket("/ws/market/{ticker}")
async def ws_market(ws: WebSocket, ticker: str):
    await ws.accept()

    price = 170

    while True:
        price += random.uniform(-1, 1)

        await ws.send_json({
            "ticker": ticker,
            "price": round(price, 2)
        })

        await asyncio.sleep(1)
        