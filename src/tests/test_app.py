from typing import Any, Dict
from fastapi import Response
import pytest
from src.openai_api import OpenAIAPI
from datetime import datetime
from fastapi.testclient import TestClient
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice

from src.app import app 

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_get(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello AITOMATIC"


def test_app_with_fake_data(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    completion = ChatCompletion(
        id="foo",
        model="gpt-3.5-turbo",
        object="chat.completion",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Hello! My name is Quang.",
                    role="assistant",
                ),
            )
        ],
            created=int(datetime.now().timestamp()),
    )

    def mock_openai_successful_response(*args: Any, **kwargs: Dict[str, Any]) -> None:
        return completion
    
    def mock_openai_failed_response(*args: Any, **kwargs: Dict[str, Any]) -> None:
        return None

    def get_reponse() -> Response:
        return client.post("/chat", json={"question": "What is your name ?"})
        
    monkeypatch.setattr(OpenAIAPI, 'invoke', mock_openai_successful_response)
    response = get_reponse()
    assert response.status_code == 200
    assert response.json()["answer"] == completion.choices[0].message.content

    monkeypatch.setattr(OpenAIAPI, 'invoke', mock_openai_failed_response)
    response = response = get_reponse()
    assert response.status_code == 500, print(response.json())