import React, { useState } from 'react';

function FileUploadSingle() {
    const [file, setFile] = useState();

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUploadClick = () => {
        if (!file) {
            return;
        }

        // handle file upload
        console.log(`${file.type}, ${file.size}`);
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
