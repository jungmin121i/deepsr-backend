from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import yfinance as yf
import json
from openai import OpenAI

router = APIRouter()


class IndicatorRequest(BaseModel):
    symbol: str
    market: str = "US"
    indicators: list[str] = ["RSI"]
    period: str = "3mo"


class InsightRequest(BaseModel):
    symbol: str
    market: str = "US"
    topic: str = "market"
    compositeScore: int
    indicators: dict


def calculate_rsi(prices, period=14):
    delta = prices.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


@router.post("/analysis/indicators")
def analyze_indicators(req: IndicatorRequest):
    try:
        data = yf.download(
            req.symbol.upper(),
            period=req.period,
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            raise HTTPException(status_code=404, detail="No data found")

        close_prices = data["Close"]

        if hasattr(close_prices, "iloc") and len(close_prices.shape) > 1:
            close_prices = close_prices.iloc[:, 0]

        rsi = float(calculate_rsi(close_prices))

        if rsi >= 70:
            rsi_signal = "sell"
            rsi_description = "과매수 구간 — 단기 조정 가능성 존재"
            score = 35
            composite_signal = "sell"
            composite_label = "매도"
        elif rsi <= 30:
            rsi_signal = "buy"
            rsi_description = "과매도 구간 — 반등 가능성 존재"
            score = 75
            composite_signal = "buy"
            composite_label = "매수"
        else:
            rsi_signal = "hold"
            rsi_description = "중립 구간 — 추세 관찰 필요"
            score = 50
            composite_signal = "hold"
            composite_label = "관망"

        return {
            "status": "success",
            "data": {
                "symbol": req.symbol.upper(),
                "market": req.market,
                "name": req.symbol.upper(),
                "indicators": {
                    "RSI": {
                        "name": "RSI (14)",
                        "value": round(rsi, 2),
                        "signal": rsi_signal,
                        "weight": 0.25,
                        "description": rsi_description
                    }
                },
                "compositeScore": score,
                "compositeSignal": composite_signal,
                "compositeLabel": composite_label
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/insights")
def generate_insights(
    req: InsightRequest,
    x_llm_key: str = Header(None)
):
    if not x_llm_key:
        raise HTTPException(status_code=401, detail="X-LLM-Key header is required")

    client = OpenAI(api_key=x_llm_key)

    prompt = f"""
너는 투자 분석 AI다.
아래 데이터는 투자 대시보드 백엔드에서 전달된 분석 결과다.

반드시 아래 JSON 형식으로만 응답해라.
설명 문장, 마크다운, 코드블록은 절대 쓰지 마라.

입력 데이터:
symbol: {req.symbol}
market: {req.market}
topic: {req.topic}
compositeScore: {req.compositeScore}
indicators: {req.indicators}

응답 JSON 형식:
{{
  "insights": [
    "첫 번째 투자 요약 문장",
    "두 번째 투자 요약 문장",
    "세 번째 투자 요약 문장"
  ],
  "conflict": {{
    "detected": true 또는 false,
    "buyIndicators": ["매수 신호 지표명"],
    "sellIndicators": ["매도 신호 지표명"],
    "accuracy": 0부터 100 사이 숫자,
    "corrected": "최종 판단",
    "reasoning": "충돌 판단 이유"
  }}
}}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions="너는 투자 대시보드용 LLM 분석 엔진이다. 반드시 JSON만 출력한다.",
            input=prompt
        )

        result_text = response.output_text
        result_json = json.loads(result_text)

        return {
            "status": "success",
            "data": result_json
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="LLM response was not valid JSON"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
     