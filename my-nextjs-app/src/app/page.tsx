import React, { useState } from "react";
import axios from "axios";

const Home: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string>("");

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setUploadMessage(""); // Clear the upload message when a new file is selected
    }
  };

  const onFileUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("File uploaded successfully:", response.data);
        setUploadMessage("Upload successful!"); // Set success message
      } catch (error) {
        console.error("Error uploading file:", error);
        setUploadMessage("Upload failed, please try again."); // Set error message
      }
    }
  };

  return (
    <div>
      <h1>Upload a file</h1>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload</button>
      {uploadMessage && <div>{uploadMessage}</div>}{" "}
      {/* Display upload message */}
    </div>
  );
};

export default Home;
