// useFileUpload.js
import { useState } from 'react';

const useFileUpload = () => {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');

  const onFileChange = (event) => {
    if (event.target.files[0]) {
      setFile(event.target.files[0]);
      setFileName(event.target.files[0].name);
    }
  };

  const removeFile = () => {
    // Clear the file input
    document.getElementById('contained-button-file').value = '';
    setFile(null);
    setFileName('');
  };

  return { file, fileName, onFileChange, removeFile };
};

export default useFileUpload;
