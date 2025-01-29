from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"

app = FastAPI()

class Item(BaseModel):
    prompt: str
    model: str

def parse_response(response):
    full_response = ''
    print(f'response = {response.text}')
    for line in response.text.strip().split('\n'):
        try:
            data = json.loads(line)
            print(f'data in parse = {data}')
            if not data.get('done') and data.get('message', {}).get('content'):
                full_response += data['message']['content']
        except json.JSONDecodeError:
            return 'Error decoding JSON response'
        print(f'full resonse strip :------- {full_response.strip()}')
    return full_response.strip()

def generate_response(prompt: str, model: str):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    print(f'payload = {payload}')
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return parse_response(response)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error communicating with Ollama API: {e}")

@app.post("/generate")
async def generate_text(request: Item):
    try:
        print(f"model = {request.model}")
        response = generate_response(request.prompt,request.model)
        print("------------------------------------------")
        print(f"Response in generate_text: {response}")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": f"Ollama FastAPI server is running with model!"}

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})