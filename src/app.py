from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import Config
from src.openai_api import OpenAIAPI


class Request(BaseModel):
    question: str 


class Response(BaseModel):
    answer: str 


app = FastAPI()
client = OpenAIAPI()

@app.get(path="/")
def get() -> str:
    return "Hello AITOMATIC"


@app.post("/chat", response_model=Response)
def qa(request: Request) -> Dict[str, str]:
    text = request.question
    response = client.invoke(content=text)
    if response is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"answer": response.choices[0].message.content}


if __name__ == "__main__":
    import uvicorn
    
    from utils import setup_logging
    config = Config()
    setup_logging()

    if config.finetuned_file:
        client.set_model_from_file(path_to_finetuned_file=config.finetuned_file)
    elif config.finetuned_model:
        client.set_model(model=config.finetuned_model)
    else:
        raise ValueError("Either finetuned_file or finetuned_model must be set")
    
    uvicorn.run(app,
                host=config.host,
                port=config.port,
                log_level="debug")
    