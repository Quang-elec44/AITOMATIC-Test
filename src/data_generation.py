import json
import math
import random
import time

import jsonlines
from tqdm import tqdm 
from openai_api import OpenAIAPI


BASE_PROMPT = """Given the following paragraph which is extracted from a conference paper
### PARAGRAPH
{paragraph}

### INSTRUCTION
Assume that you are a college Professor preparing for an example
With the given paragraph. Generate ONLY {num_ques} questions and also provide the correct answers. 
NOTE:
- You must ask about the content of the paragraph and the answer should be extracted from the paragraph too 
- The questions must cover most content of the paragraph 

The output MUST be a list of Python dictionary where each record has the following structure: {{\"question\": str, \"answer\": str}}"""


def main(
        client: OpenAIAPI, 
        data_file: str, 
        max_questions: int = 100, 
        output_file: str = "train.jsonl"
):
    with open(data_file, "r", encoding="utf8") as jsf:
        data = json.load(jsf)
    
    blocks = data["blocks"]
    max_questions_per_block = math.ceil(max_questions/len(blocks))
    output = []
    for block in tqdm(blocks):
        text = block["text"]
        successful = False 

        # ChatGPT sometimes cannot generate JSON-formatted data, so we need to retry sending request
        while not successful:
            response = client.invoke(
                content=BASE_PROMPT.format(num_ques=max_questions_per_block, paragraph=text)
            )
            if response is not None:
                content = response.choices[0].message.content
                try:
                    ques_and_ans = json.loads(content)
                    successful = True 
                    for record in ques_and_ans:
                        ques = record["question"]
                        ans = record["answer"]
                        output.append({"messages": [
                            {"role": "user", "content": ques},
                            {"role": "assistant", "content": ans}
                        ]})
                    time.sleep(20)  # To avoid rate limit error
                except json.JSONDecodeError:
                    print("Cannot parse response from block id {}".format(block["id"]))
                except Exception as e:
                    print(f"Unexpected error {e}")

    random.shuffle(output)
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(output[:max_questions])
    print("Finished generating train data")


if __name__ == "__main__":
    import argparse
    import os 
    os.environ["OPENAI_API_KEY"] = "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"
    from utils import setup_logging
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", type=str)
    parser.add_argument("--output_file", type=str, default="train.jsonl")
    parser.add_argument("--max_questions", type=int, default=100)
    args = parser.parse_args()

    client = OpenAIAPI()
    setup_logging()
    main(client=client, **vars(args))