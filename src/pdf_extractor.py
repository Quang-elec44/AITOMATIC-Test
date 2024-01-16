import json
import os
import re
from typing import List, Tuple

import fitz
from thefuzz import fuzz
from tqdm import tqdm


def join_texts(page_infos: Tuple[str, Tuple[int]]):
    prev_y = 0
    output = []
    for text, bbox in page_infos:
        _, y0, _, y1 = bbox 
        if y0 >= prev_y or not output:
            output.append(text)
        else:
            output[-1] += " " + text 
        prev_y = y1 
    return output 


def is_title(text: str, table_of_content: List[str], visited: List[bool]):
    min_similarity = 80 
    text = text.lower()
    for i, header in enumerate(table_of_content):
        if visited[i]:
            continue

        if fuzz.ratio(text, header) >= min_similarity:
            visited[i] = True 
            return True 
    return False 


def is_reference(text: str) -> bool:
    return text.lower().strip() == "references"


def dehyphen(text: str) -> str:
    """
    Convert pre- process to preprocess
    """
    return re.sub(r"(\w+-\s)\w*", lambda item: item.group().replace("- ", ""), text)


def extract(file_path: str, output_dir: str) -> None:
        
    max_text_font_size = 11
    min_text_font_size = 7.1 
    print(f"Start extracting file {file_path}")
    os.makedirs(output_dir, exist_ok=True)

    pdf_file = fitz.open(file_path)
    num_pages = len(list(pdf_file.pages()))
    table_of_content = [content[1].lower() for content in pdf_file.get_toc()]

    figure_texts = []
    document_texts = []
    visited = [False]*len(table_of_content)
    for page_idx in tqdm(range(num_pages), desc="Extracting"):

        page = pdf_file[page_idx]
        page_data = page.get_text("dict", flags=64, sort=False)
        page_infos = []
        for block in page_data["blocks"]:

            block_text = []
            max_font_size = 0
            min_font_size = float("inf")
            bbox = block["bbox"]
            for line in block["lines"]:

                for span in line["spans"]:
                    max_font_size = max(span["size"], max_font_size)
                    min_font_size = min(span["size"], min_font_size)
                    span_text = span["text"]

                    if not is_reference(span_text):
                        block_text.append(span_text)
                        
            block_text = dehyphen(" ".join(block_text))

            if is_title(block_text, table_of_content, visited):
                block_text = "<new_section> " + block_text

            if max_font_size <= max_text_font_size and min_font_size >= min_text_font_size:
                if re.search(r"Figure \d+", block_text) is not None:
                    figure_texts.append(block_text)
                else:
                    page_infos.append((block_text, bbox))

        page_texts = join_texts(page_infos)

        # Join block and remove spaces
        page_texts = " ".join("\n".join(page_texts).split(" "))
        if page_texts:
            document_texts.append(page_texts)
    
    blocks =  " ".join(document_texts).split("<new_section> ")
    blocks = [block for block in blocks if block.strip()]
    result = {"blocks": [], "figures": []}
    for block_id, block in enumerate(blocks):
        result["blocks"].append({"id": block_id, "text": block, })
    
    for fig_id, figure_text in enumerate(figure_texts):
        result["figures"].append({"id": fig_id, "text": figure_text})

    output_file = os.path.join(output_dir, "data.json")
    with open(output_file, "w", encoding="utf8") as jsf:
        json.dump(result, jsf, indent=2)

    print(f"Finished ! Output file is saved at {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=str)
    parser.add_argument("--output_dir", type=str, default="extracted_result.json")
    args = parser.parse_args()

    extract(**vars(args))