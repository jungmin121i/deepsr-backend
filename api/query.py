from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
def query(data: dict):
    return {
        "target_ticker": "AAPL",
        "chart_type": "candlestick",
        "period": "3mo",
        "required_indicators": ["volume"]
    }
    