"""Mock API for Azure Serverless Functions"""

from io import BytesIO
from pathlib import Path
import logging
import os
from typing import Optional

from flask import Flask, send_file, request, make_response, redirect
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from werkzeug.utils import secure_filename

from docx_writer import ICFDocument
from pypdfloader import PyPDFStreamLoader

ALLOWED_EXTENSIONS = {"pdf"}
AZURE_DEPLOYMENT_NAME = "ArtosEmbeddingDemo"

app = Flask(__name__)


class MockedLangchainLLM:
    def invoke(self, prompt_message):
        return None


def create_vectorstore(stream: BytesIO) -> Chroma:
    loader = PyPDFStreamLoader(stream)
    pages = loader.load_and_split()
    print("numpages", len(pages))

    print("text splitter")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=128, add_start_index=True
    )
    all_splits = text_splitter.split_documents(pages)

    print("Generate vectorstore")
    print(all_splits[:3])
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        embedding=AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME,
            api_version="2024-06-01",
        ),
    )

    return vectorstore


def retrieve_relevant_documents(
    query: str, vectorstore: Chroma, k: Optional[int] = 6
) -> list[Document]:
    # TODO add meaningful information based off of similarity score
    retrieved_docs = vectorstore.similarity_search_with_score(query, k)
    return [doc[0].page_content for doc in retrieved_docs]


def generated_segment(segment: str, vectorstore: Chroma, llm, N=12) -> str:
    retrieved_context = "\n".join(
        retrieve_relevant_documents(segment, vectorstore, k=N)
    )
    system_prompt = """-Goal-
    Given text snippets from a clinical study, summarize the portions that are most closely related to a user given segment.
    
    -Steps-
    1. Determine which parts of the text are relevant to the segment.
    2. Summarize those portions of the text as part of that segment.
    3. Word your summary such that an 8th grader could understand it.

    -Context-
    {context}"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )
    sample_message = prompt.invoke(
        {"context": retrieved_context, "question": f"What is the {segment.lower()}"}
    ).to_messages()
    return llm.invoke(sample_message).content


def process_document(stream: BytesIO):
    # do something with stream
    vectorstore: Chroma = create_vectorstore(stream)
    print(vectorstore)

    purpose_text: str = "\n".join(
        retrieve_relevant_documents("Clinical Study Purpose", vectorstore)
    )
    procedure_text: str = "\n".join(
        retrieve_relevant_documents("Clinical Study Procedure", vectorstore)
    )
    risks_text: str = "\n".join(
        retrieve_relevant_documents("Clinical Study Risks", vectorstore)
    )
    benefits_text: str = "\n".join(
        retrieve_relevant_documents("Clinical Study Benefits", vectorstore)
    )

    icf_doc = ICFDocument(
        purpose=purpose_text,
        procedure=procedure_text,
        risks=risks_text,
        benefits=benefits_text,
    )
    file_stream = BytesIO()
    icf_doc.to_stream(file_stream)
    file_stream.seek(0)
    return file_stream


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return "Hello world"


@app.route("/icf", methods=["POST", "OPTIONS"])
def output_file():
    logging.info("ICF endpoint trigger function processed a request.")

    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST":
        if "file" not in request.files:
            print("No file part")
            return redirect(request.url)
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        if filename == "":
            print("No selected file")
            return redirect(request.url)
        if uploaded_file and allowed_file(filename):
            download_filename = str(Path(filename).stem) + "_icf.docx"

            response_data = process_document(uploaded_file.read())
            response = send_file(
                path_or_file=response_data,
                download_name=download_filename,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                as_attachment=True,
            )

            return _corsify_actual_response(response)
        print("Unexpected error with uploaded file")
        return redirect(request.url)
    else:
        raise RuntimeError("Can't handle method {}".format(request.method))


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Expose-Headers", "Content-Disposition")
    return response


if __name__ == "__main__":
    app.secret_key = "202408 artosai secret key"
    app.config["SESSION_TYPE"] = "filesystem"

    app.debug = True
    app.run()
