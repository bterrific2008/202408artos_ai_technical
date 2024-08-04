"""Mock API for Azure Serverless Functions"""

import json
from flask import Flask, jsonify, send_file
app = Flask(__name__)
from typing import BinaryIO

DATA_FILE: BinaryIO = None

def process_document():
    DATA_FILE = open("ICF-template.docx", "rb")
    return DATA_FILE

@app.route('/document')
def output_file():
    response_data = process_document()
    response = send_file(
        path_or_file=response_data,
        download_name="ICF-template.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    return response
app.run()