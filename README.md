# DeepSR Backend

## 개요

DeepSR 백엔드는 투자 데이터 수집, 분석, AI 인사이트 생성을 담당하는 API 서버입니다.

---

## 실행 방법

pip install -r requirements.txt

python -m uvicorn main:app --reload

접속:
http://127.0.0.1:8000/docs

---

## API 목록

GET /api/v1/market/ohlcv
POST /api/v1/query
POST /api/v1/analysis/indicators
POST /api/v1/analysis/insights

---

## WebSocket

/ws/market/{ticker}

---

## AI 사용 방법

Header에 API 키 추가:

X-LLM-Key: sk-본인키

---

## 폴더 구조

backend/
├── main.py
├── requirements.txt
├── README.md
├── api/
│   ├── market.py
│   ├── query.py
│   ├── websocket.py
│   └── analysis.py
└── test_ws.html

---

## 특징

* 실시간 WebSocket 지원
* RSI 기반 분석
* OpenAI 연동 (BYOK 방식)
