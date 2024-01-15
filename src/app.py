from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai_api import OpenAIAPI


class Request(BaseModel):
    question: str 


class Response(BaseModel):
    answer: str 


app = FastAPI()
client = None 


@app.get(path="/")
def get():
    return "Hello AITOMATIC"


@app.post("/chat", response_model=Response)
def qa(request: Request):
    text = request.question
    response = client.invoke(content=text)
    if response is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"answer": response.choices[0].message.content}


if __name__ == "__main__":
    import os 
    os.environ["OPENAI_API_KEY"] = "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"
    import uvicorn
    import argparse
    from utils import setup_logging

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--finetuned_file", type=str, default="")
    parser.add_argument("--finetuned_model", type=str, default="")
    args = parser.parse_args()
    
    client = OpenAIAPI()
    setup_logging()

    if args.finetuned_file:
        client.set_model_from_file(path_to_finetuned_file=args.finetuned_file)
    elif args.finetuned_model:
        client.set_model(model=args.finetuned_model)
    else:
        raise ValueError("Either finetuned_file or finetuned_model must be set")
    
    uvicorn.run(app,
                host=args.host,
                port=args.port,
                log_level="debug")
    