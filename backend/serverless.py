"""Mock API for Azure Serverless Functions"""

from io import BytesIO
from pathlib import Path

from flask import Flask, send_file, request, make_response, redirect
from werkzeug.utils import secure_filename

from docx_writer import ICFDocument


ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)


def process_document(stream: BytesIO):
    icf_doc = ICFDocument()
    file_stream = BytesIO()
    icf_doc.to_stream(file_stream)
    file_stream.seek(0)
    return file_stream


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/icf", methods=["POST", "OPTIONS"])
def output_file():
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
            print(filename)
            download_filename = str(Path(filename).stem) + "_icf.docx"
            response_data = process_document(uploaded_file.stream)
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
