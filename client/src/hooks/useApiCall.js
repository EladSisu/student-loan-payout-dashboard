import axios from 'axios';
import { useState } from 'react';

const BASE_URL = 'http://localhost:8000';

const useApiCall = (setLoading, setError, setSnackbarMessage) => {
  const [message, setMessage] = useState(null);

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      const response = await axios.post(`${BASE_URL}/upload/xml`, formData);

      if (response.status !== 200) {
        throw new Error('Upload failed');
      }
      setLoading(false);
      setSnackbarMessage({ text: "File uploaded successfully.", type: "success" });
      setMessage({ type: 'success', text: 'Upload succeeded' });
    } catch (error) {
      setLoading(false);
      setError("Error uploading file.");
      setSnackbarMessage({ text: "Error uploading file.", type: "error" });
      setMessage({ type: 'error', text: 'Upload failed' });
    }
  };

  const downloadCsvReport = async (batch_id,agg_type) => {
    try {
      const response = await axios.get(`${BASE_URL}/reports/batches/${batch_id}/${agg_type}`, {
        responseType: 'blob',
      });

      // Create a URL for the blob and initiate a download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'report.csv');
      document.body.appendChild(link);
      link.click();

      setMessage({ type: 'success', text: 'CSV report downloaded' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to download CSV report' });
    }
  };

  const fetchAllBatches = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BASE_URL}/batches`);
      setLoading(false);
      return response.data;
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to fetch batches' });
      setLoading(false);
      return [];
    }
  };

  const invokePayment = async (batchId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${BASE_URL}/invoke-payment/${batchId}`);
      if (response.status === 200) {
        setLoading(false);
        setSnackbarMessage({ text: "Invoked Payment Successfully.", type: "success" });
        setMessage({ type: 'success', text: 'Payment invoked successfully' });
      } else {
        setLoading(false);
        setSnackbarMessage({ text: "Failed to invoke payment.", type: "error" });
        setMessage({ type: 'error', text: 'Failed to invoke payment' });
      }
    } catch (error) {
      setLoading(false);
      setSnackbarMessage({ text: "Failed to invoke payment.", type: "error" });
      setMessage({ type: 'error', text: 'Failed to invoke payment' });
    }
  };

  return { message, uploadFile, downloadCsvReport, fetchAllBatches, invokePayment };
};

export default useApiCall;
