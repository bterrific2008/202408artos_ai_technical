"""
Given a document, try to extract the correct title

Ineffective. Raw semantic similarity doesn't do the job.
Larger Language Model is unable to determine the title based on context alone.
"""

import re
from pathlib import Path

from tqdm import tqdm
from pypdf import PdfReader

from llm import LLM

import numpy as np
from sentence_transformers import SentenceTransformer


class ExtractTitle:

    def __init__(self):
        self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self._title_centroid = None
        with open("title_centroid.bytes", "rb") as f:
            self._title_centroid = np.frombuffer(f.read(), dtype=np.float32)
        assert self._title_centroid.shape

    def rank_titles(self, titles: list[str]):
        title_embeddings = self._embedding_model.encode(titles)
        similarity_indicies = self._embedding_model.similarity(
            self._title_centroid, title_embeddings
        ).flatten().argsort(descending=True)
        return [titles[int(i)] for i in similarity_indicies]

    def extract_titles(self, pdf_fp: Path):
        reader = PdfReader(pdf_fp)
        text_first_page = reader.pages[0].extract_text()
        line_splits = re.split("([\t ][\t ][\t ]+\n)|(\n(?=\w))", text_first_page)
        potential_titles = [
            l.replace("\n", "")
            for l in line_splits
            if l and len(l.replace("  ", "").split(" ")) > 3
        ]
        reader.close()
        return potential_titles


def title(pdf_fp):
    reader = PdfReader(pdf_fp)
    text_first_page = reader.pages[0].extract_text()

    line_splits = re.split("([\t ][\t ][\t ]+\n)|(\n(?=\w))", text_first_page)
    return [l for l in line_splits if l and "title" in l.lower()]


if __name__ == "__main__":
    fp_protocols_pdf = Path("../data/protocol/").glob("**/*pdf")
    f = open("output.txt", "w", encoding="utf-8")

    llm_model = LLM(prompt="Given a study snippet, extract the study title.")
    title_extractor = ExtractTitle()

    for fp_protocol in tqdm(list(fp_protocols_pdf)[2:3]):
        potential_titles = title_extractor.extract_titles(fp_protocol)
        # ranked_titles = title_extractor.rank_titles(potential_titles)

        f.write(f"Protocol Filename: {str(fp_protocol)}\n")
        f.write(f"Potential Titles ({len(''.join(potential_titles).split(' '))}):\n")
        f.writelines(["\t" + i + "\n" for i in potential_titles])
        f.write(f"First 250 characters:")

        
        context = "\n".join(potential_titles)
        max_token_length = 2 * max([len(title) for title in potential_titles])
        response = llm_model.invoke(f"\n{context}\nBased on the context, what is the study title?:", max_tokens=max_token_length)
        f.write(f"\n{str(response)}\n")
        f.write("\n\n************\n\n")
        # time.sleep(30)
    f.close()
