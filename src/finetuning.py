from typing import Literal, Union

if __name__ == "__main__":
    import argparse

    from src.openai_api import OpenAIAPI
    from utils import setup_logging

    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data_path', type=str, default="data/train.jsonl")
    parser.add_argument('--finetuning_file', type=str, default="data/finetune_log.json")
    parser.add_argument('--base_model', type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument('--batch_size', type=Union[Literal["auto"], int])
    parser.add_argument('--n_epochs', type=Union[Literal["auto"], int])
    parser.add_argument('--learning_rate_multiplier', type=Union[Literal["auto"], int])
    args = parser.parse_args()

    setup_logging()
    client = OpenAIAPI()
    client.finetune(**vars(args))