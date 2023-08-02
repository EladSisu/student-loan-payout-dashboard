import MoreVertIcon from "@mui/icons-material/MoreVert";
import SendIcon from "@mui/icons-material/Send";
import IconButton from "@mui/material/IconButton";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import React from "react";
import Button from '@mui/material/Button';
const TableRowComponent = ({ batch, handleClick, handleInvokePayment }) => {
  const renderOptions = () => {
    if (batch.status === "Completed") {
      return (
        <IconButton
          aria-label="more"
          aria-controls="long-menu"
          aria-haspopup="true"
          onClick={(event) => handleClick(event, batch._id)}
        >
          <MoreVertIcon />
        </IconButton>
      );
    } else if (batch.status === "Created") {
      return (
        // Option 2: Show the button to invoke payment for 'pending' status

        <Button
        onClick={() => handleInvokePayment(batch._id)}
        size='small' variant="contained" endIcon={<SendIcon />}>
        Invoke Payment
      </Button>
      );
    } else {
      // Option 3: No option for other statuses
      return null;
    }
  };

  return (
    <TableRow key={batch._id}>
      <TableCell>{batch.date_created}</TableCell>
      <TableCell>{batch.batch_name}</TableCell>
      <TableCell>
      {`${batch.valid_transactions} / ${batch.total_transactions}`}
      </TableCell>
      <TableCell>{batch.status}</TableCell>
      <TableCell>
        {renderOptions()} {/* Render the options based on status */}
      </TableCell>
    </TableRow>
  );
};

export default TableRowComponent;
