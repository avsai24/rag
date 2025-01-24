from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

app = FastAPI()

class Item(BaseModel):
    prompt: str

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

def generate_response(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
    }

    print(f'payload = {payload}')
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line)
                print(json_line['message']['content'])
        return parse_response(response)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error communicating with Ollama API: {e}")

@app.post("/generate")
async def generate_text(request: Item):
    try:
        response = generate_response(request.prompt)
        print("------------------------------------------")
        print(f"Response in generate_text: {response}")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": f"Ollama FastAPI server is running with model: {MODEL_NAME}!"}

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})