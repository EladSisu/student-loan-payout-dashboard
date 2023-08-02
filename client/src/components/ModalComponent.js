import React from 'react';
import Modal from 'react-modal';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import LoadingSpinner from './LoadingSpinner';
const ModalComponent = ({ isOpen, closeModal, onFileChange, file, fileName, removeFile, uploadFile,loading }) => {
  return (
    <Modal isOpen={isOpen} onRequestClose={closeModal} contentLabel="File Upload">
      <h2>Upload XML file</h2>
      {loading && <LoadingSpinner />}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <input
            accept=".xml"
            style={{ display: 'none' }}
            id="contained-button-file"
            type="file"
            onChange={onFileChange}
          />
          <label htmlFor="contained-button-file">
            <Button variant="contained" component="span">
              Choose file
            </Button>
          </label>
        </Grid>
        {file && (
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="h6">{fileName}</Typography>
              <Button variant="contained" color="secondary" onClick={removeFile}>
                Remove
              </Button>
            </Box>
          </Grid>
        )}
        <Grid item xs={12}>
          <Button variant="contained" color="primary" onClick={uploadFile} disabled={!file}>
            Upload
          </Button>
        </Grid>
      </Grid>
    </Modal>
  );
};

export default ModalComponent;
