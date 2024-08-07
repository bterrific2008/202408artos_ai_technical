"""
A Larger Language Model class, invokable like a Langchain chat model.
Based off of the provided Microsoft Azure Python script.
"""

import os
import requests

from typing import Optional


class LLM:
    def __init__(
        self,
        api_key: Optional[str] = None,
        openai_endpoint: Optional[str] = None,
        prompt: Optional[str] = None,
    ):

        self._API_KEY = api_key if api_key else os.environ["AZURE_OPENAI_API_KEY"]
        self._OPENAI_ENDPOINT = (
            openai_endpoint if openai_endpoint else os.environ["AZURE_OPENAI_ENDPOINT"]
        )
        self._HEADER = {
            "Content-Type": "application/json",
            "api-key": self._API_KEY,
        }
        self._PROMPT = (
            prompt
            if prompt
            else "You are an AI assistant that helps people find information."
        )

    def _format_payload(self, query: str, max_tokens: Optional[int] = 20) -> str:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": self._PROMPT,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query,
                        }
                    ],
                },
            ],
            "max_tokens": max_tokens,
        }

    def invoke(self, message: str, max_tokens: int = 20) -> dict:
        # TODO: parameterize this
        ENDPOINT = "https://artosoai01.openai.azure.com/openai/deployments/ArtosGenAIDemo/chat/completions?api-version=2024-02-15-preview"

        payload = self._format_payload(message, max_tokens=max_tokens)
        # print(payload)

        # Send request
        try:
            response = requests.post(ENDPOINT, headers=self._HEADER, json=payload)
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        except requests.RequestException as e:
            raise SystemExit(f"Failed to make the request. Error: {e}")

        return response.json()

if __name__ == "__main__":
    llm = LLM(prompt="""
    -Goal-
    Given a snipped of text from a clinical study protocol, a trained medical professional asks a question. Answer the question based on the given context.
            
    -Context-
    The potential benefit to a patient that goes onto study is a reduction in the bulk of their tumor 
    which may or may not have favorable impact on symptoms and/or survival.  Potential risks include the possible occurrence of any of a range of side effects which are listed in the Consen t 
    Document.  The procedure for protecting against or minimizing risks will be to medically evaluate patients on a regular basis as described.  
    10.4 R
    ISKS/BENEFITS ANALYSIS

    -Steps-
    1. Identify if the context answers the question or not.
    2. From the context, identify the most relevant portions to the question.
    3. Based on the context and the identified relevant sections, answer the question. Format your answer in a bullet point list.
    """)
    response = llm.invoke(
        message="For a clinical study patient, are there any risks identified in this document?",
        max_tokens=256,
    )
    print(response["choices"][0]["message"])
