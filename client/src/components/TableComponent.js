// TableComponent.js
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import React from 'react';
import TableRowComponent from './TableRowComponent';



const TableComponent = ({ batches, handleClick,handleInvokePayment }) => {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Date</TableCell>
          <TableCell>File Name</TableCell>
          <TableCell>Valid Transactions</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {batches.map((batch) => (
          <TableRowComponent key={batch._id} batch={batch} handleClick={handleClick} handleInvokePayment={handleInvokePayment} />
        ))}
      </TableBody>
    </Table>
  );
};

export default TableComponent;
