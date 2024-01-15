import json
import logging
from typing import Union

import openai 
from openai.types.chat.chat_completion import ChatCompletion


class OpenAIAPI:
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model 
        self.client = openai.OpenAI()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initalizing OpenAI model | model: {self.model}")

    def invoke(self, content: str) -> ChatCompletion:
        response = None 
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                model=self.model,
            )
        except openai.APIConnectionError as e:
            self.logger.error(f"Failed to connect to OpenAI API: {e}")
        except openai.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            self.logger.error(f"OpenAI API request exceeded rate limit: {e}")
        except openai.APIError as e:
            self.logger.error(f"OpenAI API returned an API Error: {e}")
        return response

    def finetune(
        self, 
        train_data_path: str, 
        finetuning_file: str, 
        base_model: str,
        batch_size: Union[str, int],
        n_epochs: Union[str, int],
        learning_rate_multiplier: Union[str, float],
    ) -> None:
        data_creation_response = self.client.files.create(
            file=open(train_data_path, "rb"),
            purpose="fine-tune"
        )
        self.logger.info(
            f"Submitted file {train_data_path} for fine-tuning | Id: {data_creation_response.id}"
        )

        job_creation_response = self.client.fine_tuning.jobs.create(
            training_file=data_creation_response.id, 
            model=base_model,
            hyperparameters={
                "batch_size": batch_size,
                "n_epochs": n_epochs,
                "learning_rate_multiplier": learning_rate_multiplier
            }
        )
        self.logger.info(
            f"Created a new fine-tuning job | Id: {job_creation_response.id}"
        )

        with open(finetuning_file, "w", encoding="utf8") as jsf:
            json.dump(
                {
                    "content": {
                        "data_creation_response": data_creation_response.model_dump(),
                        "job_creation_response": job_creation_response.model_dump()
                    }
                },
                jsf,
                indent=2
            )
        self.logger.info(f"Saved fine-tuning result to {finetuning_file}")
    
    def set_model_from_file(self, path_to_finetuned_file: str) -> None:
        
        with open(path_to_finetuned_file, "r", encoding="utf8") as jsf:
            data = json.load(jsf)["content"]
        
        target_id = data["job_creation_response"]["id"]
        finetuning_jobs = self.client.fine_tuning.jobs.list()
        for job in finetuning_jobs:
            if job.id == target_id:
                self.model = job.fine_tuned_model
                if self.model is None:
                    raise ValueError("Fine-tune job has not finished yet. Please wait for a while")
                break 

        self.logger.info(f"Set model to {self.model}")

    def set_model(self, model: str) -> None:
        self.model = model 
