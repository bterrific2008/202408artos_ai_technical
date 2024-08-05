import React, { useState } from 'react';

function FileUploadSingle() {
    const [file, setFile] = useState();

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUploadClick = (e) => {
        e.preventDefault();

        if (!file) {
            return;
        }
        console.log(file.name);

        const formData = new FormData();
        formData.append("file", file);
        formData.append("name", file.name);
        console.log(formData.get("files"));

        // handle file upload
        console.log(`${file.type}, ${file.size}`);
        var download_filename = "";
        fetch('http://127.0.0.1:5000/icf', {
            method: 'POST',
            body: formData,
        }).then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to upload file and fetch response`);
            }
            const header = response.headers.get('Content-Disposition');
            const parts = header.split(';');
            download_filename = parts[1].split('=')[1].replaceAll("\"", "");

            return response.blob();
        }).then((blob) => {
            const objectUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = objectUrl;
            link.download = download_filename;
            document.body.appendChild(link);
            link.click();
            link.remove();
        }).catch((err) => {
            console.log(err);
        });

    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <div>{file && `${file.name} - ${file.type}`}</div>
            <button onClick={handleUploadClick}>Upload</button>
        </div>
    );
}

export default FileUploadSingle;
