from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from pydantic import BaseModel
from model import StankinQA
from json import load, dump


class Query(BaseModel):
    question: str



model = None
model_ready = False
app = FastAPI()

@app.on_event("startup")
async def load_model():
    global model, model_ready
    model = StankinQA()
    model_ready = True
    print("Model loaded")


@app.post("/predict/")
async def predict(query: Query):

    try:
        question = query.question
        response = model.generate_answer(question)
        return {"answer": response["answer"], "suggest": response["suggest"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
def health_check():
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {"status": "ok"}

# Для запуска использовать команду: uvicorn server:app --reload
