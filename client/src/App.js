import AddIcon from "@mui/icons-material/Add";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import Snackbar from "@mui/material/Snackbar";
import TableContainer from "@mui/material/TableContainer";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material/styles";
import React, { useEffect, useState } from "react";
import Modal from "react-modal";
import LoadingSpinner from "./components/LoadingSpinner";
import MenuComponent from "./components/MenuComponent";
import ModalComponent from "./components/ModalComponent";
import TableComponent from "./components/TableComponent";
import useApiCall from "./hooks/useApiCall";
import useFileUpload from "./hooks/useFileUpload";

Modal.setAppElement("#root");

const StyledButton = styled(Button)({
  marginRight: "1rem",
});

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedBatchId, setSelectedBatchId] = useState(null);
  const [batches, setBatches] = useState([]);
  const [snackbarMessage, setSnackbarMessage] = useState(false);
  const { file, fileName, onFileChange, removeFile } = useFileUpload();
  const { message, uploadFile, fetchAllBatches, invokePayment } = useApiCall(
    setLoading,
    setError,
    setSnackbarMessage
  );
  const handleInvokePayment = async (batchId) => {
    await invokePayment(batchId);
    // After invoking the payment, refresh the batch list
    const batchesData = await fetchAllBatches();
    setBatches(batchesData);
  };

  const handleFileUploadAndRefresh = async () => {
    closeModal();
    // Refresh the batch list after uploading the file and closing the modal
    const batchesData = await fetchAllBatches();
    setBatches(batchesData);
  };

  useEffect(() => {
    const fetchBatches = async () => {
      const batchesData = await fetchAllBatches();
      setBatches(batchesData);
    };
    fetchBatches();
  }, []);

  const openModal = () => {
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
  };

  const handleClick = (event, id) => {
    setAnchorEl(event.currentTarget);
    setSelectedBatchId(id);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div className="App">
      {loading && <LoadingSpinner />}

      <Typography variant="h3" align="center" gutterBottom>
        Payment Management System
      </Typography>

      <Container maxWidth="md">
        <TableContainer component={Paper}>
          <TableComponent
            batches={batches}
            handleClick={handleClick}
            handleInvokePayment={handleInvokePayment}
          />
        </TableContainer>

        <MenuComponent
          anchorEl={anchorEl}
          handleClose={handleClose}
          selectedBatchId={selectedBatchId}
        />

        <Box display="flex" justifyContent="flex-end" marginTop={2}>
          <StyledButton
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={openModal}
          >
            Add
          </StyledButton>
        </Box>

        <ModalComponent
          isOpen={isOpen}
          closeModal={handleFileUploadAndRefresh}
          onFileChange={onFileChange}
          file={file}
          fileName={fileName}
          removeFile={removeFile}
          uploadFile={() => uploadFile(file)}
          loading={loading}
        />

        <Snackbar
          open={!!snackbarMessage}
          autoHideDuration={6000}
          onClose={() => setSnackbarMessage(null)}
        >
          <Alert
            onClose={() => setSnackbarMessage(null)}
            severity={snackbarMessage?.type}
            sx={{ width: "100%" }}
          >
            {snackbarMessage?.text}
          </Alert>
        </Snackbar>
      </Container>
    </div>
  );
}

export default App;
