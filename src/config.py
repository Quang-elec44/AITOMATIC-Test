import os


class Config:
    def __init__(self) -> None:
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8080"))
        self.finetuned_model = os.getenv("FINETUNED_MODEL", "gpt-3.5-turbo")
        